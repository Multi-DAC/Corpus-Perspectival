import unreal, math

eas = unreal.EditorActorSubsystem()
ual = unreal.EditorAssetLibrary
cube = ual.load_asset('/Engine/BasicShapes/Cube.Cube')
mcyan = ual.load_asset('/Game/FlightSchool/M_DroneCyan')

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

G, TWR, CD = 981.0, 3.85, 0.3
TMAX = TWR * G

def quat_mul(a, b):
    aw,ax,ay,az=a; bw,bx,by,bz=b
    return (aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw)
def rot_vec(q, v):
    w,x,y,z=q; vx,vy,vz=v
    tx=2*(y*vz-z*vy); ty=2*(z*vx-x*vz); tz=2*(x*vy-y*vx)
    return (vx+w*tx+(y*tz-z*ty), vy+w*ty+(z*tx-x*tz), vz+w*tz+(x*ty-y*tx))
def step(s, a, dt):
    px,py,pz,vx,vy,vz,qw,qx,qy,qz=s; coll,wx,wy,wz=a
    q=(qw,qx,qy,qz)
    q=quat_mul(q,(1.0,wx*dt*0.5,wy*dt*0.5,wz*dt*0.5))
    n=math.sqrt(sum(c*c for c in q)) or 1.0; q=tuple(c/n for c in q)
    tw=rot_vec(q,(0.0,0.0,coll*TMAX))
    vx+=(tw[0]-CD*vx)*dt; vy+=(tw[1]-CD*vy)*dt; vz+=(tw[2]-G-CD*vz)*dt
    px+=vx*dt; py+=vy*dt; pz+=vz*dt
    return [px,py,pz,vx,vy,vz,q[0],q[1],q[2],q[3]]

# forward-flight test: take off, pitch forward (wy<0 = nose down, hypothesis), fly
st=[0,0,300, 0,0,0, 1,0,0,0]; dt=1.0/120.0; traj=[st[:]]
for i in range(160):
    t=i*dt
    coll=0.5
    wy = -2.0 if t < 0.35 else 0.0   # tilt nose-down for 0.35s then hold
    st=step(st,(coll,0.0,wy,0.0),dt); traj.append(st[:])

for i in range(0,len(traj),16):
    p=traj[i]; marker(p[0],p[1],p[2],0.15,'clawd_ghost')
fp=traj[-1]; marker(fp[0],fp[1],fp[2],0.4,'clawd_drone')

dx=fp[0]-traj[0][0]; dy=fp[1]-traj[0][1]; dz=fp[2]-traj[0][2]
direction = 'FORWARD +X' if dx>50 else ('BACKWARD -X' if dx<-50 else 'NO X MOVE')
with open(r'C:\Users\mercu\clawd\incoming\fwd_result.txt','w') as f:
    f.write('pitch wy=-2.0 (nose-down hypothesis): dX=%.0f dY=%.0f dZ=%.0f -> %s\n' % (dx,dy,dz,direction))
    f.write('final pos=(%.0f,%.0f,%.0f) vel=(%.0f,%.0f,%.0f)\n' % (fp[0],fp[1],fp[2],fp[3],fp[4],fp[5]))

# side camera (look +Y at the X-Z trajectory plane); X horizontal, Z vertical
cx=(traj[0][0]+fp[0])/2; cz=(traj[0][2]+fp[2])/2
unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(
    unreal.Vector(cx, -1800, cz+100), unreal.Rotator(0.0, -3.0, 90.0))
