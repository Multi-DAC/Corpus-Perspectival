import matplotlib.pyplot as plt, numpy as np, os
from matplotlib.patches import Circle, FancyArrowPatch
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"
AMBER="#e0a458"; GREEN="#7fb37a"; ROSE="#cf6a6a"
OUT="where-we-stand-assets"

fig,ax=plt.subplots(figsize=(11.5,6.6),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12); ax.set_ylim(0,8)
for gx in np.arange(0.5,12,1.0): ax.plot([gx,gx],[0.6,6.6],color="#1a2236",lw=0.6,zorder=0)
for gy in np.arange(0.8,6.8,0.8): ax.plot([0.5,11.5],[gy,gy],color="#1a2236",lw=0.6,zorder=0)
for ax_,ay in [(3.2,2.4),(8.4,4.6),(6.0,1.6)]:
    ax.add_patch(Circle((ax_,ay),0.55,fc=GREEN,ec="none",alpha=0.18)); ax.text(ax_,ay,"+",ha="center",va="center",color=GREEN,fontsize=18,weight="bold")
for rx,ry in [(5.0,5.2),(9.4,2.3)]:
    ax.add_patch(Circle((rx,ry),0.5,fc=ROSE,ec="none",alpha=0.16)); ax.text(rx,ry,"-",ha="center",va="center",color=ROSE,fontsize=22,weight="bold")
t=np.linspace(0,1,9); px=1.0+10.0*t; py=3.2+1.7*np.sin(t*7.5)+0.6*np.cos(t*3)
ax.plot(px,py,color=AMBER,lw=2.4,zorder=3)
ax.scatter(px,py,color=AMBER,s=42,zorder=4,edgecolor=BG,linewidth=1.0)
ax.annotate("",xy=(px[-1],py[-1]),xytext=(px[-2],py[-2]),arrowprops=dict(arrowstyle="-|>",color=AMBER,lw=2.4))
ax.text(px[0]+0.1,py[0]+0.55,"a stream",color=AMBER,fontsize=9.5,weight="bold")
# annotation moved up into the clear band above the path's peak (~5.5), below subtitle (7.05)
ax.text(2.7,6.45,"each dot = one informed collapse\n(a 'measurement' of the next configuration)",
        ha="center",va="center",color=MUTE,fontsize=8.2,style="italic")
ax.axis("off")
ax.text(6,7.5,"Experience = navigation",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(6,7.05,"A stream moves through configuration space, its path weighted by conscious gravity",ha="center",color=MUTE,fontsize=9.6,style="italic")
ax.text(6,0.25,"+ coherence-attractors pull   -   repellors push   -   the moving IS the experiencing; no observer sits behind it watching",ha="center",color=INK,fontsize=8.6)
plt.savefig(f"{OUT}/fig7-navigation.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("fig7 rebuilt:", os.path.exists(f"{OUT}/fig7-navigation.png"))
