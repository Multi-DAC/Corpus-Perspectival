"""
UDP vision-stream receiver for the DCL VQ1 sim (VADR-TS-002 Issue 00.02 §4.6).

Closes the #1 VQ1 bring-up blocker (VQ1_READINESS.md): competition_agent.py currently
feeds an np.zeros() placeholder; this reassembles the real chunked-JPEG UDP stream.

Spec §4.6 (verified against docs/VQ1_TECHNICAL_SPEC_VADR-TS-002_Issue00.02.pdf):
  Transport : UDP, port 5600 (default), Little-Endian, 30 Hz, 640x360 JPEG
  Each packet = fixed 24-byte Metadata Header + variable Binary Payload.
  Header fields (in order):
    frame_id      uint32 (4B)  unique sequence id for the image frame
    chunk_id      uint16 (2B)  index of this packet within the frame (0..total_chunks-1)
    total_chunks  uint16 (2B)  total packets to complete this frame
    jpeg_size     uint32 (4B)  total size of the reconstructed JPEG, bytes
    payload_size  uint32 (4B)  size of the JPEG slice in THIS packet, bytes
    sim_time_ns   uint64 (8B)  simulation epoch timestamp, nanoseconds

Design: real-time "latest complete frame wins" semantics. A background thread drains the
socket and reassembles; the control loop calls get_latest_frame() non-blocking. Incomplete
frames older than the newest frame_id are dropped (packet loss must not stall the stream).

Built sim-independent + unit-tested (see __main__): the reassembly logic — the load-bearing,
out-of-order/lossy part — is tested on synthetic chunked packets without the live sim.
JPEG decode (cv2) is a thin wrapper, exercised only if cv2 is importable.
"""

from __future__ import annotations
import socket
import struct
import threading
from dataclasses import dataclass, field

HEADER = struct.Struct("<IHHIIQ")  # 24 bytes; little-endian per spec §4.6
HEADER_SIZE = HEADER.size  # 24
DEFAULT_PORT = 5600
FRAME_SHAPE = (360, 640, 3)  # spec resolution (H, W, C)


@dataclass
class _FrameBuffer:
    total_chunks: int
    jpeg_size: int
    sim_time_ns: int
    chunks: dict[int, bytes] = field(default_factory=dict)

    def add(self, chunk_id: int, payload: bytes) -> None:
        self.chunks[chunk_id] = payload

    def complete(self) -> bool:
        return len(self.chunks) >= self.total_chunks

    def assemble(self) -> bytes:
        return b"".join(self.chunks[i] for i in range(self.total_chunks))


def parse_header(packet: bytes):
    """Return (frame_id, chunk_id, total_chunks, jpeg_size, payload_size, sim_time_ns)."""
    if len(packet) < HEADER_SIZE:
        raise ValueError(f"packet too short: {len(packet)} < {HEADER_SIZE}")
    return HEADER.unpack(packet[:HEADER_SIZE])


def chunk_frame(jpeg_bytes: bytes, frame_id: int, sim_time_ns: int = 0,
                payload_max: int = 1400) -> list[bytes]:
    """Encode a JPEG byte-string into spec-compliant UDP packets.

    Used by the synthetic generator / unit test AND as the canonical documentation of the
    wire format (a sender and receiver that agree on this function interoperate). payload_max
    ~1400 keeps packets under a typical MTU.
    """
    n = max(1, (len(jpeg_bytes) + payload_max - 1) // payload_max)
    packets = []
    for cid in range(n):
        sl = jpeg_bytes[cid * payload_max:(cid + 1) * payload_max]
        hdr = HEADER.pack(frame_id, cid, n, len(jpeg_bytes), len(sl), sim_time_ns)
        packets.append(hdr + sl)
    return packets


class UdpVisionReceiver:
    def __init__(self, port: int = DEFAULT_PORT, host: str = "0.0.0.0",
                 max_pending_frames: int = 4):
        self.port = port
        self.host = host
        self.max_pending_frames = max_pending_frames
        self._buffers: dict[int, _FrameBuffer] = {}
        self._latest_jpeg: bytes | None = None
        self._latest_frame_id: int = -1
        self._latest_sim_time_ns: int = 0
        self._lock = threading.Lock()
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self.frames_completed = 0
        self.packets_seen = 0

    # --- pure reassembly (unit-tested without a socket) ------------------------------
    def handle_packet(self, packet: bytes) -> bool:
        """Process one packet. Returns True if it completed a (new, newest) frame."""
        self.packets_seen += 1
        frame_id, chunk_id, total_chunks, jpeg_size, payload_size, sim_time_ns = parse_header(packet)
        payload = packet[HEADER_SIZE:HEADER_SIZE + payload_size]

        # Ignore chunks belonging to a frame older than what we've already delivered.
        if frame_id <= self._latest_frame_id:
            return False

        buf = self._buffers.get(frame_id)
        if buf is None:
            buf = _FrameBuffer(total_chunks=total_chunks, jpeg_size=jpeg_size, sim_time_ns=sim_time_ns)
            self._buffers[frame_id] = buf
            self._evict_stale(frame_id)
        buf.add(chunk_id, payload)

        if buf.complete():
            data = buf.assemble()
            # jpeg_size is a sanity check; tolerate mismatch by trusting assembled length
            with self._lock:
                self._latest_jpeg = data
                self._latest_frame_id = frame_id
                self._latest_sim_time_ns = buf.sim_time_ns
            self.frames_completed += 1
            # drop this and all older buffers
            for fid in [f for f in self._buffers if f <= frame_id]:
                del self._buffers[fid]
            return True
        return False

    def _evict_stale(self, newest_frame_id: int) -> None:
        """Bound memory: drop incomplete frames far older than the newest (packet loss)."""
        if len(self._buffers) <= self.max_pending_frames:
            return
        cutoff = newest_frame_id - self.max_pending_frames
        for fid in [f for f in self._buffers if f < cutoff]:
            del self._buffers[fid]

    # --- latest-frame accessors -------------------------------------------------------
    def get_latest_jpeg(self) -> tuple[bytes | None, int, int]:
        """Return (jpeg_bytes_or_None, frame_id, sim_time_ns) for the newest complete frame."""
        with self._lock:
            return self._latest_jpeg, self._latest_frame_id, self._latest_sim_time_ns

    def get_latest_frame(self):
        """Decode the latest complete frame to an (H,W,3) uint8 ndarray, or None.

        Requires cv2 (the AIGP vision pipeline's decoder). Returns None if no frame yet.
        """
        import numpy as np
        import cv2
        jpeg, _, _ = self.get_latest_jpeg()
        if jpeg is None:
            return None
        arr = np.frombuffer(jpeg, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # BGR (H,W,3)
        return img

    # --- socket loop ------------------------------------------------------------------
    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 22)
        self._sock.bind((self.host, self.port))
        self._sock.settimeout(0.5)
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="udp-vision-rx", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        assert self._sock is not None
        while self._running:
            try:
                data, _ = self._sock.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                self.handle_packet(data)
            except Exception:
                continue  # malformed packet — drop, keep streaming

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._sock is not None:
            self._sock.close()
            self._sock = None


# ---------------------------------------------------------------------------------------
# INTEGRATION NOTE (for the Clayton-aware afternoon step — NOT applied here):
#   competition_agent.py ~line 156 currently: camera = np.zeros((360, 640, 3), ...)
#   Replace with:
#       rx = UdpVisionReceiver(port=5600); rx.start()    # once, at agent init
#       ...
#       frame = rx.get_latest_frame()                    # in the loop; may be None pre-first-frame
#       if frame is None: frame = np.zeros((360,640,3), np.uint8)   # blind-flight fallback
#   Note: cv2 returns BGR; confirm gate_detector.py's expected channel order (BGR vs RGB).
# ---------------------------------------------------------------------------------------


if __name__ == "__main__":
    # Sim-independent unit test: synthetic frame -> chunk -> feed -> verify reassembly.
    import os, random

    def _test_roundtrip(jpeg_len, payload_max, frame_id=1, shuffle=False, drop=None):
        original = os.urandom(jpeg_len)
        pkts = chunk_frame(original, frame_id=frame_id, sim_time_ns=123456789, payload_max=payload_max)
        if drop is not None:
            pkts = [p for i, p in enumerate(pkts) if i != drop]
        if shuffle:
            random.shuffle(pkts)
        rx = UdpVisionReceiver()
        completed = any(rx.handle_packet(p) for p in pkts)
        jpeg, fid, ts = rx.get_latest_jpeg()
        return original, completed, jpeg, fid, ts

    print("=== UDP vision receiver — reassembly unit tests ===")
    # 1. exact size, in order
    orig, done, got, fid, ts = _test_roundtrip(4000, 1400)
    assert done and got == orig and fid == 1 and ts == 123456789, "in-order roundtrip failed"
    print(f"[1] in-order  : {len(orig)}B over {(len(orig)+1399)//1400} chunks -> reassembled OK, ts={ts}")

    # 2. out-of-order chunks
    orig, done, got, fid, ts = _test_roundtrip(10000, 1400, shuffle=True)
    assert done and got == orig, "out-of-order reassembly failed"
    print(f"[2] shuffled  : {len(orig)}B -> reassembled OK (order-independent)")

    # 3. exact multiple of payload_max (boundary)
    orig, done, got, fid, ts = _test_roundtrip(2800, 1400)
    assert done and got == orig, "boundary (exact-multiple) failed"
    print(f"[3] boundary  : {len(orig)}B == 2*1400 -> reassembled OK")

    # 4. single-packet frame
    orig, done, got, fid, ts = _test_roundtrip(500, 1400)
    assert done and got == orig, "single-packet failed"
    print(f"[4] single    : {len(orig)}B in 1 chunk -> OK")

    # 5. dropped packet -> frame must NOT complete (no false positive)
    orig, done, got, fid, ts = _test_roundtrip(10000, 1400, drop=2)
    assert not done, "dropped-packet frame wrongly reported complete!"
    print(f"[5] lossy     : dropped 1 of {(10000+1399)//1400} chunks -> correctly INCOMPLETE")

    # 6. latest-wins: older frame_id after a newer completed frame is ignored
    rx = UdpVisionReceiver()
    for p in chunk_frame(os.urandom(2000), frame_id=5, payload_max=1400):
        rx.handle_packet(p)
    newer = os.urandom(2000)
    for p in chunk_frame(newer, frame_id=9, payload_max=1400):
        rx.handle_packet(p)
    # now feed an OLD frame (id=3) fully — must be ignored
    for p in chunk_frame(os.urandom(2000), frame_id=3, payload_max=1400):
        rx.handle_packet(p)
    jpeg, fid, ts = rx.get_latest_jpeg()
    assert fid == 9 and jpeg == newer, f"latest-wins failed: fid={fid}"
    print(f"[6] latest-win: after frame 9, stale frame 3 ignored -> latest stays fid=9")

    # 7. header size invariant
    assert HEADER_SIZE == 24, f"header size {HEADER_SIZE} != 24 (spec violation)"
    print(f"[7] header    : struct '<IHHIIQ' = {HEADER_SIZE} bytes (matches spec §4.6)")

    print("\nALL REASSEMBLY TESTS PASSED (sim-independent).")
    try:
        import cv2, numpy as np  # noqa
        print("cv2 present -> get_latest_frame() decode path available.")
    except Exception as e:
        print(f"cv2 not importable here ({e.__class__.__name__}); decode path untested in this env "
              f"(reassembly is the load-bearing part and is verified). Confirm cv2 in the AIGP runtime.")
