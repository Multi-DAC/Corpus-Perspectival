"""
Gate Detector — Classical CV Pipeline for VQ1

Detects highlighted gates from forward-facing camera feed.
VQ1 gates are highlighted with visual guidance aids, making
classical CV highly effective (high signal-to-noise ratio).

Pipeline:
    1. Color/brightness filtering (gates are highlighted)
    2. Contour detection + quadrilateral fitting
    3. Corner ordering (top-left, top-right, bottom-right, bottom-left)
    4. Optional: PnP pose estimation for 3D gate position

Designed to be swappable — replace with a learned detector for VQ2.
"""

import numpy as np
import cv2
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class GateDetection:
    """Result of gate detection from a single frame."""
    found: bool = False
    corners_2d: Optional[np.ndarray] = None      # (4, 2) pixel coords [TL, TR, BR, BL]
    center_2d: Optional[np.ndarray] = None        # (2,) pixel center
    area: float = 0.0                              # pixel area of detected gate
    confidence: float = 0.0                        # 0-1 detection confidence
    position_3d: Optional[np.ndarray] = None       # (3,) estimated 3D position (if PnP solved)
    distance: Optional[float] = None               # estimated distance to gate (if PnP solved)
    bearing_body: Optional[np.ndarray] = None      # (3,) unit vector toward gate in body frame
    normal_camera: Optional[np.ndarray] = None     # (3,) gate facing direction in camera frame
                                                   # (the gate's normal vector — what the policy needs
                                                   # for fly-through alignment, NOT bearing_body)


@dataclass
class GateDetectorConfig:
    """Tunable parameters for gate detection."""
    # HSV filtering for highlighted gates (VQ1)
    # These will need calibration once we see actual VQ1 frames
    hsv_lower: np.ndarray = field(default_factory=lambda: np.array([0, 0, 200]))     # bright
    hsv_upper: np.ndarray = field(default_factory=lambda: np.array([180, 60, 255]))   # near-white/bright

    # Alternative: detect by saturation (desaturated env + highlighted gates)
    use_brightness_mode: bool = True
    brightness_threshold: int = 200       # gates should be bright in desaturated env

    # Contour filtering
    min_contour_area: int = 200           # minimum pixel area to consider
    max_contour_area: int = 200000        # maximum pixel area
    min_aspect_ratio: float = 0.3         # width/height ratio bounds
    max_aspect_ratio: float = 3.0
    approx_epsilon_ratio: float = 0.04    # polygonal approximation tolerance

    # Gate physical dimensions (meters) — for PnP
    gate_width: float = 1.5               # physical gate width (will calibrate from SDK)
    gate_height: float = 1.5              # physical gate height

    # Multi-gate tracking
    max_gates: int = 3                    # max gates to detect per frame

    # Sub-pixel corner refinement (cv2.cornerSubPix) before PnP.
    # Reduces corner-localization noise from contour approximation, which
    # tightens PnP residuals without touching the planar-square ambiguity.
    # Stage 2 (climbing_8m) z-tilt floor was 0.10 with raw corners — the
    # IPPE_SQUARE sister-pair separation is the lower bound but corner
    # noise sits on top of it. Refinement targets that noise term.
    use_subpix_refine: bool = True
    subpix_win_size: int = 5              # half window; (2*N+1) x (2*N+1) search
    subpix_zero_zone: int = -1            # -1 = no dead zone
    subpix_max_iter: int = 30
    subpix_epsilon: float = 0.01


class GateDetector:
    """
    Detects racing gates from camera images.

    Designed for VQ1's desaturated environment with highlighted gates.
    Swappable with a learned detector for VQ2.
    """

    def __init__(self, config: Optional[GateDetectorConfig] = None):
        self.config = config or GateDetectorConfig()

        # 3D model points for PnP (gate corners in gate-local frame)
        w, h = self.config.gate_width / 2, self.config.gate_height / 2
        self.gate_model_points = np.array([
            [-w,  h, 0],   # top-left
            [ w,  h, 0],   # top-right
            [ w, -h, 0],   # bottom-right
            [-w, -h, 0],   # bottom-left
        ], dtype=np.float64)

        # Camera intrinsics placeholder — will be set from SDK
        self._camera_matrix = None
        self._dist_coeffs = np.zeros(5)

    def set_camera_params(self, fx: float, fy: float, cx: float, cy: float,
                          dist_coeffs: Optional[np.ndarray] = None):
        """Set camera intrinsic parameters (from SDK or calibration)."""
        self._camera_matrix = np.array([
            [fx, 0,  cx],
            [0,  fy, cy],
            [0,  0,  1],
        ], dtype=np.float64)
        if dist_coeffs is not None:
            self._dist_coeffs = dist_coeffs

    def set_camera_from_fov(self, image_width: int, image_height: int,
                            fov_horizontal_deg: float):
        """Set camera intrinsics from field of view (common in game engines)."""
        fov_rad = np.radians(fov_horizontal_deg)
        fx = image_width / (2 * np.tan(fov_rad / 2))
        fy = fx  # assume square pixels
        cx = image_width / 2
        cy = image_height / 2
        self.set_camera_params(fx, fy, cx, cy)

    def detect(self, image: np.ndarray) -> List[GateDetection]:
        """
        Detect gates in a camera frame.

        Args:
            image: BGR image from camera (numpy array, HxWx3)

        Returns:
            List of GateDetection objects, sorted by area (largest first)
        """
        if image is None or image.size == 0:
            return [GateDetection()]

        # Step 1: Extract gate candidate mask
        mask = self._create_gate_mask(image)

        # Step 2: Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Step 3: Filter and fit quadrilaterals
        detections = []
        for contour in contours:
            det = self._process_contour(contour, image.shape)
            if det is not None:
                detections.append(det)

        # Sort by area (largest = closest gate = current target)
        detections.sort(key=lambda d: d.area, reverse=True)

        # Limit to max_gates
        detections = detections[:self.config.max_gates]

        # Step 3.5: Sub-pixel corner refinement before PnP.
        # cv2.cornerSubPix iterates corner positions to sub-pixel accuracy
        # using local image gradients. Cheap (~µs per corner), shrinks the
        # PnP-input noise term that sits on top of the IPPE_SQUARE
        # ambiguity floor.
        if self.config.use_subpix_refine and detections:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                        self.config.subpix_max_iter, self.config.subpix_epsilon)
            win = (self.config.subpix_win_size, self.config.subpix_win_size)
            zero = (self.config.subpix_zero_zone, self.config.subpix_zero_zone)
            for det in detections:
                corners = det.corners_2d.reshape(-1, 1, 2).astype(np.float32)
                cv2.cornerSubPix(gray, corners, win, zero, criteria)
                det.corners_2d = corners.reshape(4, 2)
                det.center_2d = det.corners_2d.mean(axis=0)

        # Step 4: PnP pose estimation if camera is calibrated
        if self._camera_matrix is not None:
            for det in detections:
                self._estimate_pose(det)

        # If nothing found, return empty detection
        if not detections:
            return [GateDetection()]

        return detections

    def _create_gate_mask(self, image: np.ndarray) -> np.ndarray:
        """Create binary mask of potential gate pixels."""
        if self.config.use_brightness_mode:
            # For desaturated environment: gates are bright highlights
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, self.config.brightness_threshold,
                                    255, cv2.THRESH_BINARY)
        else:
            # HSV-based filtering
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.config.hsv_lower, self.config.hsv_upper)

        # Morphological cleanup — close gaps, then open to remove noise.
        # No initial dilation: dilating before contouring inflates the gate's
        # apparent size, which biases PnP toward shorter distances. Stage 1
        # smoke test (2026-04-25) showed 7x7 dilate caused 12-22% distance
        # under-estimate, scaling with range.
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        return mask

    def _process_contour(self, contour: np.ndarray,
                         image_shape: tuple) -> Optional[GateDetection]:
        """Process a single contour into a gate detection."""
        area = cv2.contourArea(contour)

        # Area filter
        if area < self.config.min_contour_area or area > self.config.max_contour_area:
            return None

        # Approximate to polygon
        epsilon = self.config.approx_epsilon_ratio * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # We want roughly quadrilateral shapes (gates are rectangular)
        # Accept 4-8 vertices (gates might have rounded corners or partial occlusion)
        if len(approx) < 4 or len(approx) > 8:
            return None

        # Get bounding rect for aspect ratio check
        rect = cv2.minAreaRect(contour)
        w, h = rect[1]
        if w == 0 or h == 0:
            return None

        aspect = max(w, h) / min(w, h)
        if aspect < self.config.min_aspect_ratio or aspect > self.config.max_aspect_ratio:
            return None

        # Get ordered corners
        if len(approx) == 4:
            corners = approx.reshape(4, 2).astype(np.float32)
        else:
            # More than 4 vertices — fit minimum area rectangle
            box = cv2.boxPoints(rect)
            corners = box.astype(np.float32)

        # Order corners: TL, TR, BR, BL
        corners = self._order_corners(corners)

        # Compute center
        center = corners.mean(axis=0)

        # Confidence based on how rectangular the shape is
        # Perfect rectangle would have area ≈ minAreaRect area
        rect_area = w * h
        rectangularity = area / (rect_area + 1e-6)
        confidence = min(1.0, rectangularity)

        return GateDetection(
            found=True,
            corners_2d=corners,
            center_2d=center,
            area=area,
            confidence=confidence,
        )

    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """Order corners as: top-left, top-right, bottom-right, bottom-left."""
        # Sort by sum (x+y): smallest = top-left, largest = bottom-right
        s = corners.sum(axis=1)
        # Sort by difference (y-x): smallest = top-right, largest = bottom-left
        d = np.diff(corners, axis=1).flatten()

        ordered = np.zeros_like(corners)
        ordered[0] = corners[np.argmin(s)]   # top-left
        ordered[1] = corners[np.argmin(d)]   # top-right
        ordered[2] = corners[np.argmax(s)]   # bottom-right
        ordered[3] = corners[np.argmax(d)]   # bottom-left

        return ordered

    def _estimate_pose(self, detection: GateDetection):
        """Estimate 3D pose of gate using PnP."""
        if detection.corners_2d is None or self._camera_matrix is None:
            return

        image_points = detection.corners_2d.astype(np.float64)

        # IPPE_SQUARE returns two solutions for a planar square (the inherent
        # mirror-flip ambiguity when the gate is near-coplanar with the image).
        # Use solvePnPGeneric to get both, then pick the one whose normal points
        # closest to the camera optical axis (-z direction toward camera).
        # Stage 2 smoke (2026-04-25) caught the wrong-solution case in
        # climbing_8m where PnP returned a 22° spurious tilt.
        # Move A (reproj-error tiebreak) and A' (LM refinement) both tried
        # 2026-04-25 midday — both made climbing_8m WORSE (A: 0.10 → 0.37
        # z-tilt by picking wrong sister; A': diverged to 9.2m distance
        # error because LM landscape is near-flat between sisters and
        # gradient-descended out of the physical basin). Camera-axis prior
        # is load-bearing and unrefined-IPPE-SQUARE is the floor.
        n_solutions, rvecs, tvecs, errs = cv2.solvePnPGeneric(
            self.gate_model_points,
            image_points,
            self._camera_matrix,
            self._dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )
        success = n_solutions > 0
        if success:
            best_idx = 0
            if n_solutions > 1:
                # Prefer the solution whose normal is most camera-facing.
                best_score = -np.inf
                for i in range(n_solutions):
                    R_i, _ = cv2.Rodrigues(rvecs[i])
                    n_i = R_i @ np.array([0.0, 0.0, 1.0])
                    score = -abs(n_i[0]) - abs(n_i[1])  # most |z|, least |x|+|y|
                    if score > best_score:
                        best_score = score
                        best_idx = i
            rvec = rvecs[best_idx]
            tvec = tvecs[best_idx]
        if success:
            # tvec is position of gate in camera frame
            gate_pos_camera = tvec.flatten()
            detection.position_3d = gate_pos_camera
            detection.distance = np.linalg.norm(gate_pos_camera)

            # Bearing vector (unit direction toward gate in camera/body frame)
            detection.bearing_body = gate_pos_camera / (detection.distance + 1e-6)

            # Gate "fly-through direction": the gate plane is z=0 in gate-local
            # frame; PnP's rvec rotates gate frame -> camera frame. The training
            # observation uses the direction the drone *travels through* the
            # gate (env.gate_orientations[current]), which is the back-face
            # normal — i.e. pointing AWAY from camera through the gate. We
            # therefore orient the normal so it points away from the camera.
            R, _ = cv2.Rodrigues(rvec)
            normal_cam = R @ np.array([0.0, 0.0, 1.0])
            if np.dot(normal_cam, gate_pos_camera) < 0:
                normal_cam = -normal_cam  # flip to point away from camera
            detection.normal_camera = normal_cam

    def detect_primary(self, image: np.ndarray) -> GateDetection:
        """Convenience: detect and return only the primary (largest) gate."""
        detections = self.detect(image)
        return detections[0]

    def annotate(self, image: np.ndarray, detections: List[GateDetection]) -> np.ndarray:
        """Draw detections on image for debugging/visualization."""
        vis = image.copy()

        for i, det in enumerate(detections):
            if not det.found:
                continue

            color = (0, 255, 0) if i == 0 else (0, 255, 255)

            # Draw corners
            pts = det.corners_2d.astype(np.int32)
            cv2.polylines(vis, [pts], True, color, 2)

            # Draw center
            cx, cy = int(det.center_2d[0]), int(det.center_2d[1])
            cv2.circle(vis, (cx, cy), 5, color, -1)

            # Label
            label = f"Gate {i}: conf={det.confidence:.2f}"
            if det.distance is not None:
                label += f" d={det.distance:.1f}m"
            cv2.putText(vis, label, (cx - 50, cy - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return vis
