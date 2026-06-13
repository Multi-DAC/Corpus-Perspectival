import sys
import ctypes
import time
import numpy as np

# Native Windows API Virtual Key Codes
VK_UP      = 0x26
VK_DOWN    = 0x28
VK_LEFT    = 0x25
VK_RIGHT   = 0x27
VK_W       = 0x57
VK_A       = 0x41
VK_S       = 0x53
VK_D       = 0x44
VK_Q       = 0x51
VK_E       = 0x45
VK_M       = 0x4D  # Toggle Key
VK_SHIFT   = 0x10
VK_CONTROL = 0x11

# Global state tracker for manual override flight mode
MANUAL_MODE_ACTIVE = False
_last_toggle_time = 0.0

def is_pressed(vk_code):
    """Query the true hardware state of a key across the OS kernel."""
    return (ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000) != 0

def check_toggle_logic():
    """Polls the M key with a debounce timer to safely switch modes."""
    global MANUAL_MODE_ACTIVE, _last_toggle_time
    now = time.time()
    if is_pressed(VK_M):
        if now - _last_toggle_time > 0.4:  # 400ms software debounce window
            MANUAL_MODE_ACTIVE = not MANUAL_MODE_ACTIVE
            _last_toggle_time = now
            print(f"\n[MODE CHANGE] >>> MANUAL OVERRIDE: {MANUAL_MODE_ACTIVE} <<<", flush=True)

print("==========================================================")
print("AIGP TOGGLE-LOCK MANUAL FLIGHT WRAPPER ACTIVE")
print("==========================================================")
print(" -> PRESS 'M' to toggle between Autonomous and Manual flight.")
print(" -> W / S : Pitch Up / Down")
print(" -> A / D : Roll Left / Right")
print(" -> Q / E : Yaw Left / Right")
print(" -> SHIFT / CTRL : Throttle Up / Down")
print("==========================================================")

# 1. Import your original flight script natively
import run_dreamer

run_dreamer.SAVE_EVERY = 1    # 1 means save every single frame (Full 30 Hz capture)
run_dreamer.SAVE_CAP = 10000  # Expand cap to allow up to ~5.5 minutes of raw capture

# --- Manual-mode appearance-frame capture (Day 133 fix) ----------------------
# run_dreamer's frame capture lives DOWNSTREAM of its `if frame is None: continue`
# check, so returning (None,-1) to silence the AI loop also killed all capture in
# manual mode. But the receiver thread keeps decoding into self.frame regardless,
# so we grab the live frame HERE — where we already hold it — and save it, then
# still return (None,-1) to keep the AI silent. Flight #2's spin-out validated the
# appearance gate; official-domain frames are exactly what we now need, and drunken
# manual wandering past the gates is perfect appearance data (flying skill irrelevant).
import os as _os
MANUAL_SAVE_EVERY = 2       # save every Nth NEW frame while in manual mode (~15 fps off a 30 Hz feed)
MANUAL_SAVE_CAP   = 20000   # long-harvest headroom
_MANUAL_DIR = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "official_frames", "manual_" + time.strftime("%Y%m%d_%H%M%S"))
_manual = {"count": 0, "saved": 0, "last_id": -1, "dir_made": False}

# 2. Intercept Frame Buffer to halt AI loops when manual tracking is on
original_get_frame = run_dreamer.LatestFrame.get

def patched_get_frame(self):
    check_toggle_logic()
    if MANUAL_MODE_ACTIVE:
        # The receiver thread is still filling self.frame; capture it before we
        # tell the AI loop "no new frame."
        with self.lock:
            frame = self.frame
            fid = self.frame_id
        if frame is not None and fid != _manual["last_id"]:
            _manual["last_id"] = fid
            _manual["count"] += 1
            if (_manual["count"] % MANUAL_SAVE_EVERY == 0
                    and _manual["saved"] < MANUAL_SAVE_CAP):
                try:
                    import cv2
                    if not _manual["dir_made"]:
                        _os.makedirs(_MANUAL_DIR, exist_ok=True)
                        _manual["dir_made"] = True
                        print(f"[CAPTURE] manual-mode frames -> {_MANUAL_DIR}", flush=True)
                    cv2.imwrite(
                        _os.path.join(_MANUAL_DIR, f"manual_{_manual['count']:06d}.jpg"),
                        frame)
                    _manual["saved"] += 1
                    if _manual["saved"] % 30 == 0:
                        print(f"[CAPTURE] {_manual['saved']} manual frames saved", flush=True)
                except Exception:
                    pass
        # Force-silence the AI loop by pretending no frame update occurred
        return (None, -1)
    return original_get_frame(self)

run_dreamer.LatestFrame.get = patched_get_frame


# 3. Intercept the network connection stack
original_mavlink_connection = run_dreamer.mavutil.mavlink_connection
_global_conn = None
_original_send_attitude = None

def patched_mavlink_connection(*args, **kwargs):
    global _global_conn, _original_send_attitude
    conn = original_mavlink_connection(*args, **kwargs)
    
    # Save network pipeline handle references
    _original_send_attitude = conn.mav.set_attitude_target_send
    _global_conn = conn
    
    # Drop inline loop calls when manual flight tracking is toggled on
    def custom_send_attitude_target(time_boot_ms, target_system, target_component, 
                                    type_mask, q, roll_rate, pitch_rate, yaw_rate, thrust):
        check_toggle_logic()
        if MANUAL_MODE_ACTIVE:
            return  # Suppress background model telemetry
        return _original_send_attitude(time_boot_ms, target_system, target_component, 
                                       type_mask, q, roll_rate, pitch_rate, yaw_rate, thrust)

    conn.mav.set_attitude_target_send = custom_send_attitude_target
    return conn

run_dreamer.mavutil.mavlink_connection = patched_mavlink_connection


# 4. Asynchronous keyboard worker tracking coordinate transforms
def manual_flight_worker():
    boot_time = time.time()
    
    while True:
        try:
            check_toggle_logic()
            if MANUAL_MODE_ACTIVE and _original_send_attitude is not None:
                # Set baseline telemetry values (FLU format)
                roll_flu = 0.0
                pitch_flu = 0.0
                yaw_flu = 0.0
                thrust = 0.55  # Neutral hover state constant

                # Map digital keys to manual analog rates
                if is_pressed(VK_W) or is_pressed(VK_UP): 
                    pitch_flu = 1.2   # Pitch forward
                elif is_pressed(VK_S) or is_pressed(VK_DOWN): 
                    pitch_flu = -1.2  # Pitch backward
                    
                if is_pressed(VK_A) or is_pressed(VK_LEFT): 
                    roll_flu = -1.2   # Roll left
                elif is_pressed(VK_D) or is_pressed(VK_RIGHT): 
                    roll_flu = 1.2    # Roll right
                    
                if is_pressed(VK_Q): 
                    yaw_flu = -1.5    # Yaw left
                elif is_pressed(VK_E): 
                    yaw_flu = 1.5     # Yaw right
                    
                if is_pressed(VK_SHIFT): 
                    thrust = 0.85     # Ascent throttle boost
                elif is_pressed(VK_CONTROL): 
                    thrust = 0.25     # Descent throttle cut

                # Apply the Handedness Transform (FLU -> FRD Verbatim)
                rates_converted = run_dreamer.zup_to_ned_rates(
                    np.array([roll_flu, pitch_flu, yaw_flu])
                )

                # Deliver individual float indexes explicitly to fix packaging errors
                ms_boot = int((time.time() - boot_time) * 1000)
                _original_send_attitude(
                    ms_boot, _global_conn.target_system, _global_conn.target_component,
                    run_dreamer.RATES_MASK, [1.0, 0.0, 0.0, 0.0],
                    float(rates_converted[0]), 
                    float(rates_converted[1]), 
                    float(rates_converted[2]), 
                    float(thrust)
                )
        except Exception as e:
            pass
            
        # Paced at ~30Hz to match official simulator hardware resolution
        time.sleep(0.033)

import threading
threading.Thread(target=manual_flight_worker, daemon=True).start()

if __name__ == "__main__":
    run_dreamer.main()
