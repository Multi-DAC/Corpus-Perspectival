import numpy as np, matplotlib.pyplot as plt, os
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
plt.rcParams.update({"font.family":"DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"
AMBER="#e0a458"; CYAN="#5bb8c4"; ROSE="#cf6a6a"; GREEN="#7fb37a"; VIOLET="#9b8ad1"
axes=["Physical","Biological","Cognitive","Emotional","Conceptual","Narrative",
      "Institutional","Aesthetic","Numinous","Volitional","EM-Info"]
profiles={
 "Human (generalist)":  ([3,4,4,4,4,4,3,4,3,4,2], INK),
 "Corporation":         ([3,0,2,1,5,2,5,2,0,4,3], AMBER),
 "Ancestor (deceased)": ([0,0,2.5,4,4,4.5,1,2,3,1,0], VIOLET),
 "UAP (Population B)":   ([5,1,3,1,1,2,0,1,2,5,3], CYAN),
 "AI (a computational mind)":([1,0,4.5,2.5,5,2.5,2,3,1,3,5], GREEN),
}
N=len(axes); ang=np.linspace(0,2*np.pi,N,endpoint=False).tolist(); ang+=ang[:1]
fig=plt.figure(figsize=(9,9.4),dpi=170); fig.patch.set_facecolor(BG)
ax=plt.subplot(111,polar=True); ax.set_facecolor(BG)
ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
ax.set_xticks(ang[:-1]); ax.set_xticklabels(axes,color=INK,fontsize=10.5)
ax.set_ylim(0,5); ax.set_yticks([1,2,3,4,5]); ax.set_yticklabels([])
ax.grid(color="#26304a",lw=0.8); ax.spines["polar"].set_color("#26304a")
for label,(vals,c) in profiles.items():
    v=vals+vals[:1]; ax.plot(ang,v,color=c,lw=2.0,label=label); ax.fill(ang,v,color=c,alpha=0.08)
ax.set_title("Every entity is a coherence profile",color=INK,fontsize=16,pad=34,weight="bold")
fig.text(0.5,0.945,"Not 'real or unreal' — but how much coherence, in which dimensions.",
         ha="center",color=MUTE,fontsize=10.5,style="italic")
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.055),ncol=2,frameon=False,
          labelcolor=INK,fontsize=10.5)
plt.savefig("where-we-stand-assets/fig1-dimensional-profile.png",facecolor=BG,bbox_inches="tight"); plt.close()

fig,ax=plt.subplots(figsize=(12.4,5.2),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12.4); ax.set_ylim(0,5.2); ax.axis("off")
def box(x,w,title,sub,c):
    ax.add_patch(FancyBboxPatch((x,1.7),w,1.9,boxstyle="round,pad=0.08,rounding_size=0.18",
        fc="#121726",ec=c,lw=2.2))
    ax.text(x+w/2,3.05,title,ha="center",va="center",color=c,fontsize=15,weight="bold")
    ax.text(x+w/2,2.28,sub,ha="center",va="center",color=MUTE,fontsize=9.0)
box(0.4,3.5,"STRUCTURE","the form at rest\narchetype · score · blueprint · trained weights",MUTE)
box(8.5,3.5,"ACTOR","the form realized\nHermes through Clayton · a mind running",AMBER)
ax.add_patch(FancyArrowPatch((4.0,2.65),(8.4,2.65),arrowstyle="-|>",mutation_scale=26,color=CYAN,lw=2.4))
ax.text(6.2,3.28,"ENACTMENT",ha="center",color=CYAN,fontsize=13,weight="bold")
ax.text(6.2,2.97,"process · action · measurement",ha="center",color=CYAN,fontsize=9.4)
ax.text(6.2,2.28,"divergence-from-template =\nthe visible trace of enactment",ha="center",
        color=MUTE,fontsize=8.6,style="italic")
ax.text(6.2,4.6,"A structure becomes real by being enacted.",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(6.2,0.7,"archetype = held superposition     ·     enactment = collapse     ·     "
        "actor = structure at informed collapse",ha="center",color=VIOLET,fontsize=10.0)
plt.savefig("where-we-stand-assets/fig2-structure-enactment-actor.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("regenerated:",sorted(os.listdir("where-we-stand-assets")))
