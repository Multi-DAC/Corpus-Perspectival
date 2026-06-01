import unreal, math, random

eas = unreal.EditorActorSubsystem()
cube = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube.Cube')

# --- clear previous gate bars (tagged 'clawd_gate') ---
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor) and a.actor_has_tag('clawd_gate'):
        eas.destroy_actor(a)

def rz(x, y, th):
    c, s = math.cos(th), math.sin(th)
    return (x * c - y * s, x * s + y * c)

def spawn_gate(cx, cy, cz, yaw_deg):
    """Square gate frame centered (cx,cy,cz), plane perpendicular to heading yaw."""
    th = math.radians(yaw_deg)
    H = 135.0  # half-side (cm) -> ~2.7m gate
    # local offsets (gate faces +X locally): (along-heading=0, width=Y, up=Z)
    bars = [
        ((0,  0,  H), (0.2, 2.9, 0.2)),  # top
        ((0,  0, -H), (0.2, 2.9, 0.2)),  # bottom
        ((0, -H,  0), (0.2, 0.2, 2.9)),  # left
        ((0,  H,  0), (0.2, 0.2, 2.9)),  # right
    ]
    for (lx, ly, lz), (sx, sy, sz) in bars:
        wx, wy = rz(lx, ly, th)
        a = eas.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(cx + wx, cy + wy, cz + lz),
            unreal.Rotator(0.0, 0.0, yaw_deg))
        a.static_mesh_component.set_static_mesh(cube)
        a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
        a.tags = ['clawd_gate']

# --- maneuver library (simplified port of our ManeuverLibrary) ---
# each: (forward_cm, turn_deg, dz_cm)
MANEUVERS = {
    'sprint':     (1800, 0,   0),
    'chicane':    (1200, 25,  0),
    'hairpin':    (900, 70,   0),
    'climb':      (1300, 10, 250),
    'dive':       (1300, 10,-250),
    'gentle_arc': (1400, 18,  0),
    'hard_turn':  (1000, 50,  0),
}
random.seed()  # fresh course each run

# walk a procedural course
x, y, z, heading = 0.0, 0.0, 200.0, 0.0
names = list(MANEUVERS.keys())
log = []
for i in range(7):
    m = random.choice(names)
    fwd, turn, dz = MANEUVERS[m]
    turn *= random.choice([-1, 1])  # left or right
    heading += turn
    th = math.radians(heading)
    x += fwd * math.cos(th)
    y += fwd * math.sin(th)
    z = max(150.0, z + dz)
    spawn_gate(x, y, z, heading)
    log.append('%s @(%.0f,%.0f,%.0f) hdg=%.0f' % (m, x, y, z, heading))

# camera: elevated, looking over the course centroid
import functools
gates = [(0,0,200)]  # start
cx, cy, cz = x/2, y/2, 400.0
cam = unreal.Vector(-800, cy - 2500, 1600)
d = unreal.Vector(cx - cam.x, cy - cam.y, cz - cam.z)
yaw = math.degrees(math.atan2(d.y, d.x))
pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))

print('COURSE: ' + ' | '.join(log))
