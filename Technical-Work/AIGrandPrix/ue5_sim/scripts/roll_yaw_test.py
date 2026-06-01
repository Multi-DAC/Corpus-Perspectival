import unreal, math

G, TWR, CD = 981.0, 3.85, 0.3
TMAX = TWR * G
def qm(a,b):
    aw,ax,ay,az=a; bw,bx,by,bz=b
    return (aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw)
def rv(q,v):
    w,x,y,z=q; vx,vy,vz=v
    tx=2*(y*vz-z*vy); ty=2*(z*vx-x*vz); tz=2*(x*vy-y*vx)
    return (vx+w*tx+(y*tz-z*ty), vy+w*ty+(z*tx-x*tz), vz+w*tz+(x*ty-y*tx))
def step(s,a,dt):
    px,py,pz,vx,vy,vz,qw,qx,qy,qz=s; coll,wx,wy,wz=a
    q=(qw,qx,qy,qz); q=qm(q,(1.0,wx*dt*0.5,wy*dt*0.5,wz*dt*0.5))
    n=math.sqrt(sum(c*c for c in q)) or 1.0; q=tuple(c/n for c in q)
    tw=rv(q,(0.0,0.0,coll*TMAX))
    vx+=(tw[0]-CD*vx)*dt; vy+=(tw[1]-CD*vy)*dt; vz+=(tw[2]-G-CD*vz)*dt
    px+=vx*dt; py+=vy*dt; pz+=vz*dt
    return [px,py,pz,vx,vy,vz,q[0],q[1],q[2],q[3]]
def run(action_fn, n=160, dt=1.0/120.0):
    s=[0,0,300,0,0,0,1,0,0,0]
    for i in range(n): s=step(s,action_fn(i*dt),dt)
    return s

# ROLL: collective 0.5, wx=+2.0 for 0.35s then hold
def roll_a(t): return (0.5, 2.0 if t<0.35 else 0.0, 0.0, 0.0)
rs = run(roll_a)
# YAW: hover collective, wz=+2.0 for 1.0s; measure heading change
def yaw_a(t): return (0.26, 0.0, 0.0, 2.0 if t<1.0 else 0.0)
ys = run(yaw_a, n=130)
qw,qx,qy,qz = ys[6],ys[7],ys[8],ys[9]
yaw_deg = math.degrees(math.atan2(2*(qw*qz+qx*qy), 1-2*(qy*qy+qz*qz)))

with open(r'C:\Users\mercu\clawd\incoming\rollyaw_result.txt','w') as f:
    f.write('ROLL wx=+2.0: dX=%.0f dY=%.0f dZ=%.0f -> %s\n' % (
        rs[0], rs[1], rs[2], '+Y (right)' if rs[1]>50 else ('-Y (left)' if rs[1]<-50 else 'no Y')))
    f.write('YAW  wz=+2.0: heading=%.0f deg -> %s\n' % (
        yaw_deg, 'CCW/+yaw' if yaw_deg>5 else ('CW/-yaw' if yaw_deg<-5 else 'no yaw')))
