import matplotlib.pyplot as plt, os
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"; AMBER="#e0a458"; CYAN="#5bb8c4"; VIOLET="#9b8ad1"
OUT="where-we-stand-assets"

fig,ax=plt.subplots(figsize=(13.4,6.0),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,13.4); ax.set_ylim(0,6.0); ax.axis("off")
ax.text(6.7,5.35,"A structure becomes real by being enacted.",ha="center",color=INK,fontsize=17,weight="bold")
def box(x,w,title,sub,c):
    ax.add_patch(FancyBboxPatch((x,2.35),w,1.7,boxstyle="round,pad=0.08,rounding_size=0.18",fc="#121726",ec=c,lw=2.2))
    ax.text(x+w/2,3.55,title,ha="center",va="center",color=c,fontsize=15,weight="bold")
    ax.text(x+w/2,2.90,sub,ha="center",va="center",color=MUTE,fontsize=8.2)
box(0.45,4.2,"STRUCTURE","the form at rest\narchetype · score · blueprint · trained weights",MUTE)
box(8.75,4.2,"ACTOR","the form realized\nan archetype through a person · a mind running",AMBER)
ax.add_patch(FancyArrowPatch((4.8,3.2),(8.65,3.2),arrowstyle="-|>",mutation_scale=28,color=CYAN,lw=2.6))
ax.text(6.72,3.95,"ENACTMENT",ha="center",color=CYAN,fontsize=13.5,weight="bold")
ax.text(6.72,3.62,"process · action · measurement",ha="center",color=CYAN,fontsize=9.2)
ax.text(6.72,2.80,"divergence-from-template =\nthe visible trace of enactment",ha="center",color=MUTE,fontsize=8.4,style="italic")
ax.text(6.7,1.15,"archetype = held superposition        ·        enactment = collapse        ·        actor = structure at informed collapse",
        ha="center",color=VIOLET,fontsize=10.2)
plt.savefig(f"{OUT}/fig2-structure-enactment-actor.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("fig2 rebuilt:", os.path.exists(f"{OUT}/fig2-structure-enactment-actor.png"))
