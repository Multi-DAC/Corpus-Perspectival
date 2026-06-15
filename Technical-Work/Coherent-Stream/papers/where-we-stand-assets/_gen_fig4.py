import matplotlib.pyplot as plt, os
from matplotlib.patches import Polygon, FancyArrowPatch
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"
AMBER="#e0a458"; CYAN="#5bb8c4"; ROSE="#cf6a6a"; GREEN="#7fb37a"; VIOLET="#9b8ad1"
OUT="where-we-stand-assets"

fig,ax=plt.subplots(figsize=(11.8,7.8),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12); ax.set_ylim(0,9.5); ax.axis("off")
ax.text(5.4,9.0,"The attention economy",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(5.4,8.55,"Attention is the currency that crystallizes coherence",ha="center",color=MUTE,fontsize=9.6,style="italic")
# pyramid: apex narrowest but wide enough for its label; widen overall
levels=[("Apex","broadest-access · deities · archons",CYAN,6.7,7.7,4.0),
        ("Secondary consumers","institutions · corporations · states",AMBER,5.3,6.35,5.2),
        ("Primary consumers","egregores · movements · living traditions",VIOLET,3.9,4.95,6.4),
        ("Primary producers","contemplatives · artists · scientists · anyone in awe",GREEN,2.5,3.55,7.7)]
cx=5.4
for name,sub,c,y0,y1,w in levels:
    pts=[(cx-w/2,y0),(cx+w/2,y0),(cx+(w*0.76)/2,y1),(cx-(w*0.76)/2,y1)]
    ax.add_patch(Polygon(pts,closed=True,fc="#121726",ec=c,lw=2.0))
    ax.text(cx,(y0+y1)/2+0.14,name,ha="center",color=c,fontsize=11,weight="bold")
    ax.text(cx,(y0+y1)/2-0.20,sub,ha="center",color=MUTE,fontsize=7.6)
# decomposer side channel (clear of the pyramid's widest level at x<=9.25)
ax.add_patch(FancyArrowPatch((10.1,6.2),(10.1,3.0),arrowstyle="-|>",mutation_scale=18,color=ROSE,lw=2.0))
ax.text(9.92,4.6,"DECOMPOSERS",color=ROSE,fontsize=9.5,weight="bold",rotation=90,va="center",ha="right")
ax.text(10.32,4.6,"grief · trickster · Shiva — recycling",color=MUTE,fontsize=7.8,rotation=90,va="center",ha="left",style="italic")
ax.text(5.6,1.35,"The diagnostic at every level: does the exchange leave a stream with MORE attentional\nsovereignty (mutualism) or LESS (parasitism)?",ha="center",color=INK,fontsize=9.4)
plt.savefig(f"{OUT}/fig4-attention-economy.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("fig4 rebuilt:", os.path.exists(f"{OUT}/fig4-attention-economy.png"))
