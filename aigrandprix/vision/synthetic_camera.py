"""
Synthetic Camera — Render gates from our simulation as camera images.

Projects 3D gate positions onto a 2D camera plane to generate
synthetic frames for testing the gate detector + full pipeline.

This lets us validate the vision pipeline end-to-end before the
DCL SDK drops. Not photorealistic — just geometrically correct
gate rendering with configurable visual style.
"""

import numpy as np
import cv2
from typing import List, Optional, Tuple

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from drone_env_v2 import quat_rotate_np


class SyntheticCamera:
    """
    Renders a simplified forward-facing camera view from drone state.

    Projects gate rectangles in 3D space onto the image plane,
    mimicking VQ1's desaturated environment with highlighted gates.
    """

    def __init__(self,
                 width: int = 640,
                 height: int = 480,
                 fov_deg: float = 90.0,
                 gate_width: float = 1.5,
                 gate_height: float = 1.5):
        self.width = width
        self.height = height
        self.gate_width = gate_width
        self.gate_height = gate_height

        # Camera intrinsics from FOV
        fov_rad = np.radians(fov_deg)
        self.fx = width / (2 * np.tan(fov_rad / 2))
        self.fy = self.fx
        self.cx = width / 2
        self.cy = height / 2

        self.camera_matrix = np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1],
        ], dtype=np.float64)

        # Background color (desaturated gray, mimicking VQ1)
        self.bg_color = (40, 40, 40)
        # Gate color (bright highlight, mimicking VQ1)
        self.gate_color = (220, 240, 255)
        # Secondary gate color (dimmer for lookahead gates)
        self.gate_color_secondary = (120, 130, 140)

    def render(self,
               drone_pos: np.ndarray,
               drone_quat: np.ndarray,
               gate_positions: List[np.ndarray],
               gate_orientations: List[np.ndarray],
               current_gate_idx: int = 0,
               add_noise: bool = True) -> np.ndarray:
        """
        Render synthetic camera frame.

        Args:
            drone_pos: (3,) drone position in world frame
            drone_quat: (4,) drone quaternion [w,x,y,z]
            gate_positions: list of (3,) gate center positions
            gate_orientations: list of (3,) unit vectors (gate facing direction)
            current_gate_idx: index of the next gate to pass
            add_noise: add slight noise/texture to background

        Returns:
            BGR image (H, W, 3) uint8
        """
        # Create background
        image = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)

        if add_noise:
            noise = np.random.randint(-8, 8, image.shape, dtype=np.int16)
            image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Camera transform: world → camera frame
        # Camera looks along body z-axis (drone forward direction)
        q_conj = np.array([drone_quat[0], -drone_quat[1],
                           -drone_quat[2], -drone_quat[3]])

        # Render each visible gate
        for i, (gate_pos, gate_orient) in enumerate(zip(gate_positions, gate_orientations)):
            if i < current_gate_idx:
                continue  # don't render passed gates

            # Gate corners in world frame
            corners_world = self._gate_corners_world(gate_pos, gate_orient)

            # Transform to camera frame
            corners_camera = []
            behind_camera = False
            for corner in corners_world:
                # World → body frame
                rel_world = corner - drone_pos
                rel_body = quat_rotate_np(q_conj, rel_world)

                # Body frame: x=forward, y=left, z=up (standard drone convention)
                # Camera convention: x=right, y=down, z=forward (OpenCV)
                # Mapping: cam_x = -body_y, cam_y = -body_z, cam_z = body_x
                cam_point = np.array([-rel_body[1], -rel_body[2], rel_body[0]])

                if cam_point[2] <= 0.1:  # behind camera
                    behind_camera = True
                    break
                corners_camera.append(cam_point)

            if behind_camera or not corners_camera:
                continue

            # Project to image plane
            corners_2d = []
            for pt in corners_camera:
                px = self.fx * pt[0] / pt[2] + self.cx
                py = self.fy * pt[1] / pt[2] + self.cy
                corners_2d.append([int(px), int(py)])

            corners_2d = np.array(corners_2d, dtype=np.int32)

            # Check if any corner is on screen
            on_screen = any(
                0 <= c[0] < self.width and 0 <= c[1] < self.height
                for c in corners_2d
            )
            if not on_screen:
                continue

            # Draw gate — thick frame simulating physical gate structure
            color = self.gate_color if i == current_gate_idx else self.gate_color_secondary

            # Scale thickness with apparent size (closer = thicker frame)
            avg_depth = np.mean([c[2] for c in corners_camera])
            thickness = max(2, int(12 * 5.0 / (avg_depth + 1.0)))

            # Draw solid gate frame
            cv2.polylines(image, [corners_2d], True, color, thickness)

            # Add filled semi-transparent interior for current gate (VQ1 highlighting)
            if i == current_gate_idx:
                overlay = image.copy()
                cv2.fillPoly(overlay, [corners_2d], (160, 180, 200))
                cv2.addWeighted(overlay, 0.15, image, 0.85, 0, image)
                # Bright corner markers
                for corner in corners_2d:
                    cv2.circle(image, tuple(corner), max(3, thickness), color, -1)

        return image

    def _gate_corners_world(self, center: np.ndarray,
                            orientation: np.ndarray) -> List[np.ndarray]:
        """
        Compute 4 gate corners in world frame.

        Gate is a rectangle centered at `center`, facing along `orientation`.
        Width and height are in the plane perpendicular to orientation.
        """
        forward = orientation / (np.linalg.norm(orientation) + 1e-6)

        # Compute gate plane axes (right and up)
        up_hint = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(forward, up_hint)) > 0.99:
            up_hint = np.array([0.0, 1.0, 0.0])

        right = np.cross(forward, up_hint)
        right = right / (np.linalg.norm(right) + 1e-6)

        up = np.cross(right, forward)
        up = up / (np.linalg.norm(up) + 1e-6)

        hw = self.gate_width / 2
        hh = self.gate_height / 2

        corners = [
            center - hw * right + hh * up,   # top-left
            center + hw * right + hh * up,   # top-right
            center + hw * right - hh * up,   # bottom-right
            center - hw * right - hh * up,   # bottom-left
        ]

        return corners


def test_synthetic_camera():
    """Quick visual test of the synthetic camera."""
    cam = SyntheticCamera()

    # Drone at origin, looking along x-axis
    drone_pos = np.array([0.0, 0.0, 2.0])
    drone_quat = np.array([1.0, 0.0, 0.0, 0.0])  # identity

    # Gate 10m ahead
    gates = [
        np.array([0.0, 0.0, 2.0]) + np.array([10.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 2.0]) + np.array([20.0, 2.0, 1.0]),
    ]
    orientations = [
        np.array([1.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    ]

    # Identity quat: body x = world x (forward), body z = world z (up)
    # This is correct for camera looking along body x = world x
    drone_quat = np.array([1.0, 0.0, 0.0, 0.0])

    image = cam.render(drone_pos, drone_quat, gates, orientations, current_gate_idx=0)

    print(f"Rendered image shape: {image.shape}")
    print(f"Max pixel value: {image.max()}")
    print(f"Gate visible: {image.max() > 200}")

    # Save test image
    output_path = os.path.join(os.path.dirname(__file__), 'test_render.png')
    cv2.imwrite(output_path, image)
    print(f"Saved: {output_path}")

    return image


if __name__ == '__main__':
    test_synthetic_camera()
