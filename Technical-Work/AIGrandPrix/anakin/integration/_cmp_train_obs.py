import os,sys,numpy as np,cv2
H=os.path.dirname(os.path.abspath(__file__)); A=os.path.dirname(H)
sys.path.insert(0,os.path.join(A,"sim")); sys.path.insert(0,H)
from maneuver_env import AnakinManeuverEnv
def unpack(x):
    if isinstance(x,tuple): x=x[0]
    return x["image"] if isinstance(x,dict) else x
def sv(o,name):
    a=np.asarray(unpack(o))
    if a.dtype!=np.uint8:
        a=(a*255).clip(0,255).astype(np.uint8) if a.max()<=1.01 else a.astype(np.uint8)
    cv2.imwrite(os.path.join(H,name),cv2.cvtColor(a,cv2.COLOR_RGB2BGR)); return a
env=AnakinManeuverEnv(max_steps=200,dt=0.02,device="cuda",seed=1001)
o=env.reset()
a=sv(o,"_cmp_train_s000.png")
print("train obs shape",a.shape,"dtype",a.dtype,"min/max",a.min(),a.max())
act=np.zeros(env.action_space.shape,dtype=np.float32)
for i in range(30): o=env.step(act)
sv(o,"_cmp_train_s030.png")
print("saved _cmp_train_s000.png + _cmp_train_s030.png")
