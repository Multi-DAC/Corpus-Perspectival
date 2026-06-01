import unreal, math

eas = unreal.EditorActorSubsystem()
ual = unreal.EditorAssetLibrary
cube = ual.load_asset('/Engine/BasicShapes/Cube.Cube')

# --- emissive cyan material for the drone + trajectory ghosts (visible in the void) ---
pkg = '/Game/FlightSchool'
cpath = pkg + '/M_DroneCyan'
if ual.does_asset_exist(cpath):
    mcyan = ual.load_asset(cpath)
else:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mcyan = at.create_asset('M_DroneCyan', pkg, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    nd = mel.create_material_expression(mcyan, unreal.MaterialExpressionConstant3Vector, -350, 0)
    nd.set_editor_property('constant', unreal.LinearColor(0.05, 3.0, 4.0, 1.0))
    mel.connect_material_property(nd, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mcyan)

# clear previous drone/ghost markers
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor) and (a.actor_has_tag('clawd_drone') or a.actor_has_tag('clawd_ghost')):
        eas.destroy_actor(a)

def marker(x, y, z, s, tag):
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
    a.static_mesh_component.set_static_mesh(cube)
    a.set_actor_scale3d(unreal.Vector(s, s, s))
    a.static_mesh_component.set_material(0, mcyan)
    a.tags = [tag]
    return a

# ===== CTBR dynamics (UE units: cm, s). Ports directly to C++ ADronePawn::Step =====
# UE is LEFT-HANDED, Z up, X forward, Y right. Body thrust is +Z (up).
G   = 981.0            # cm/s^2
TWR = 3.85             # our calibration
TMAX = TWR * G         # max thrust accel (cm/s^2); hover collective = 1/TWR = 0.26
CD  = 0.3              # linear drag (1/s)

def quat_mul(a, b):
    aw,ax,ay,az = a; bw,bx,by,bz = b
    return (aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw)

def rot_vec(q, v):   # rotate vector v by quaternion q (w,x,y,z)
    w,x,y,z = q; vx,vy,vz = v
    # t = 2*cross(q.xyz, v)
    tx = 2*(y*vz - z*vy); ty = 2*(z*vx - x*vz); tz = 2*(x*vy - y*vx)
    return (vx + w*tx + (y*tz - z*ty), vy + w*ty + (z*tx - x*tz), vz + w*tz + (x*ty - y*tx))

def step(state, action, dt):
    # state: pos(3), vel(3), quat(4 wxyz), -- action: collective[0..1], wx,wy,wz (rad/s body)
    px,py,pz, vx,vy,vz, qw,qx,qy,qz = state
    coll, wx, wy, wz = action
    q = (qw,qx,qy,qz)
    # integrate orientation by body rates (rate-controlled / ACRO)
    om = (wx*dt*0.5, wy*dt*0.5, wz*dt*0.5)
    dq = (1.0, om[0], om[1], om[2])
    q = quat_mul(q, dq)
    n = math.sqrt(sum(c*c for c in q)) or 1.0
    q = tuple(c/n for c in q)
    # thrust along body +Z, rotated to world
    tw = rot_vec(q, (0.0, 0.0, coll*TMAX))
    ax = tw[0] - CD*vx
    ay = tw[1] - CD*vy
    az = tw[2] - G - CD*vz
    vx += ax*dt; vy += ay*dt; vz += az*dt
    px += vx*dt; py += vy*dt; pz += vz*dt
    return [px,py,pz, vx,vy,vz, q[0],q[1],q[2],q[3]]

# ===== climb test: from rest at (0,0,200), level, collective 0.5 for 1.0s =====
st = [0,0,200, 0,0,0, 1,0,0,0]
dt = 1.0/120.0
traj = [st[:]]
for i in range(120):
    st = step(st, (0.5, 0.0, 0.0, 0.0), dt)
    traj.append(st[:])

# place ghosts every 20 steps, drone at final
for i in range(0, len(traj), 20):
    p = traj[i]
    marker(p[0], p[1], p[2], 0.15, 'clawd_ghost')
fp = traj[-1]
marker(fp[0], fp[1], fp[2], 0.4, 'clawd_drone')

# expected vs actual (validation)
exp_acc = 0.5*TMAX - G   # cm/s^2 upward
print('CLIMB TEST: z %.0f -> %.0f (climbed %.0f cm)  vz=%.0f cm/s  expected_acc=%.0f cm/s^2'
      % (traj[0][2], fp[2], fp[2]-traj[0][2], fp[5], exp_acc))

# camera to view the climb (side-on)
unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(
    unreal.Vector(-200, -900, 450), unreal.Rotator(0.0, -5.0, 75.0))
