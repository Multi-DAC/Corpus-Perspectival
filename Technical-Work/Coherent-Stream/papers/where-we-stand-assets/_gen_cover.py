import matplotlib.pyplot as plt, numpy as np, os
from matplotlib.patches import Circle
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#ece9e1"; MUTE="#8a93a6"; FAINT="#243049"
AMBER="#e0a458"; CYAN="#5bb8c4"; GREEN="#7fb37a"; VIOLET="#9b8ad1"; ROSE="#cf6a6a"
OUT="where-we-stand-assets"

fig,ax=plt.subplots(figsize=(16,9),dpi=120); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,16); ax.set_ylim(0,9); ax.axis("off")
rng=np.random.default_rng(7)

# soft attractor-glow toward upper right (the coherence the streams navigate toward)
gx,gy=12.6,6.1
for r,a in [(3.6,0.05),(2.5,0.06),(1.5,0.08),(0.8,0.10)]:
    ax.add_patch(Circle((gx,gy),r,fc=AMBER,ec="none",alpha=a,zorder=1))

# a field of streams flowing left->right, gently converging toward the glow
x=np.linspace(-0.5,16.5,400)
for i in range(46):
    y0=rng.uniform(0.6,8.4)
    conv=(gy-y0)*np.clip((x-1)/14,0,1)*rng.uniform(0.45,0.95)   # drift toward attractor
    amp=rng.uniform(0.12,0.5); freq=rng.uniform(0.35,0.9); ph=rng.uniform(0,6.28)
    y=y0+conv+amp*np.sin(freq*x+ph)
    ax.plot(x,y,color=FAINT,lw=0.8,alpha=0.55,zorder=2)
# a few bright streams in the figure palette
for c,y0 in [(CYAN,2.0),(AMBER,7.6),(GREEN,4.2),(VIOLET,1.1),(ROSE,6.8),(CYAN,3.3)]:
    conv=(gy-y0)*np.clip((x-1)/14,0,1)*rng.uniform(0.55,0.9)
    amp=rng.uniform(0.18,0.42); freq=rng.uniform(0.4,0.8); ph=rng.uniform(0,6.28)
    y=y0+conv+amp*np.sin(freq*x+ph)
    ax.plot(x,y,color=c,lw=2.0,alpha=0.80,zorder=3)
    ax.scatter([x[-30]],[y[-30]],s=22,color=c,alpha=0.9,zorder=4)

# darken a band behind the title for legibility
ax.axhspan(3.5,6.2,xmin=0.0,xmax=0.74,facecolor=BG,alpha=0.55,zorder=5)

# title block (left-weighted)
ax.text(0.7,5.55,"WHERE WE STAND",color=INK,fontsize=58,weight="bold",zorder=6,
        family="DejaVu Sans")
ax.text(0.72,4.62,"On the Ecology of Beings, the Phenomenon,",color=MUTE,fontsize=20,zorder=6,style="italic")
ax.text(0.72,4.18,"and What We Think Is Actually Happening",color=MUTE,fontsize=20,zorder=6,style="italic")
ax.plot([0.75,6.2],[3.95,3.95],color=AMBER,lw=1.4,alpha=0.8,zorder=6)
ax.text(0.75,0.62,"Clayton Iggulden-Schnell  &  Clawd Iggulden-Schnell",color=INK,fontsize=15,zorder=6)
ax.text(0.75,0.28,"Multi-DAC  ·  June 2026  ·  a living draft, on the record",color=MUTE,fontsize=12.5,zorder=6)

plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
plt.savefig(f"{OUT}/cover-where-we-stand.png",facecolor=BG); plt.close()
print("cover written:", os.path.exists(f"{OUT}/cover-where-we-stand.png"))
