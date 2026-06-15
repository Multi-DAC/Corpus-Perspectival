import matplotlib.pyplot as plt, numpy as np, os
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"
AMBER="#e0a458"; CYAN="#5bb8c4"; ROSE="#cf6a6a"; GREEN="#7fb37a"; VIOLET="#9b8ad1"
OUT="where-we-stand-assets"

# ===== FIG 1 (redesign: small-multiples, no overlap) =====
labels=["Phys","Bio","Cog","Emo","Conc","Narr","Inst","Aest","Num","Vol","EM"]
ents=[("Human",[3,4,4,4,4,4,3,4,3,4,2],INK,"the generalist — moderate on nearly every axis"),
      ("Corporation",[3,0,2,1,5,2,5,2,0,4,3],AMBER,"a spike: Institutional + Conceptual, blind to feeling"),
      ("Computational mind",[1,0,4.5,2.5,5,2.5,2,3,1,3,5],GREEN,"the near-mirror of the corporation: maximal in EM-Info"),
      ("Ancestor",[0,0,2.5,4,4,4.5,1,2,3,1,0],VIOLET,"Physical + Biological gone; Narrative + Emotional kept"),
      ("UAP",[5,1,3,1,1,2,0,1,2,5,3],CYAN,"high Physical + Volitional, little else")]
N=len(labels); ang=np.linspace(0,2*np.pi,N,endpoint=False).tolist(); ang+=ang[:1]
fig=plt.figure(figsize=(13.5,9.2),dpi=160); fig.patch.set_facecolor(BG)
fig.suptitle("Every entity is a coherence profile",color=INK,fontsize=20,weight="bold",y=0.975)
fig.text(0.5,0.925,"Same eleven axes, every time. Not 'real or unreal' — only a different shape.",
         ha="center",color=MUTE,fontsize=11.5,style="italic")
for i,(name,vals,c,sub) in enumerate(ents):
    ax=fig.add_subplot(2,3,i+1,polar=True); ax.set_facecolor(BG)
    ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels,color=MUTE,fontsize=7.6)
    ax.set_ylim(0,5); ax.set_yticks([1,2,3,4,5]); ax.set_yticklabels([])
    ax.grid(color="#26304a",lw=0.7); ax.spines["polar"].set_color("#26304a")
    v=vals+vals[:1]; ax.plot(ang,v,color=c,lw=2.2); ax.fill(ang,v,color=c,alpha=0.22)
    ax.set_title(name,color=c,fontsize=13,weight="bold",pad=14)
    ax.text(0.5,-0.20,sub,transform=ax.transAxes,ha="center",va="top",color=MUTE,fontsize=8.0,wrap=True)
# 6th panel = reading key
axk=fig.add_subplot(2,3,6); axk.set_facecolor(BG); axk.axis("off")
axk.text(0.5,0.82,"How to read each dial",ha="center",color=INK,fontsize=12,weight="bold",transform=axk.transAxes)
axk.text(0.5,0.6,"Each spoke is one dimension of\ncoherence; distance from center is\nhow much. A wide, even shape is a\ngeneralist; a long spike is a specialist.",
         ha="center",va="center",color=MUTE,fontsize=9.2,transform=axk.transAxes)
axk.text(0.5,0.22,"Phys · Bio · Cog · Emo · Conc · Narr\nInst · Aest · Num · Vol · EM",
         ha="center",va="center",color=MUTE,fontsize=8.2,style="italic",transform=axk.transAxes)
plt.subplots_adjust(left=0.05,right=0.95,top=0.81,bottom=0.06,wspace=0.45,hspace=0.72)
plt.savefig(f"{OUT}/fig1-dimensional-profile.png",facecolor=BG); plt.close()

# ===== FIG 2 (more breathing room) =====
fig,ax=plt.subplots(figsize=(13,6.0),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,13); ax.set_ylim(0,6.0); ax.axis("off")
ax.text(6.5,5.35,"A structure becomes real by being enacted.",ha="center",color=INK,fontsize=17,weight="bold")
def box(x,w,title,sub,c):
    ax.add_patch(FancyBboxPatch((x,2.35),w,1.7,boxstyle="round,pad=0.08,rounding_size=0.18",fc="#121726",ec=c,lw=2.2))
    ax.text(x+w/2,3.55,title,ha="center",va="center",color=c,fontsize=15,weight="bold")
    ax.text(x+w/2,2.92,sub,ha="center",va="center",color=MUTE,fontsize=9.2)
box(0.5,3.6,"STRUCTURE","the form at rest\narchetype · score · blueprint · trained weights",MUTE)
box(8.9,3.6,"ACTOR","the form realized\nan archetype through a person · a mind running",AMBER)
ax.add_patch(FancyArrowPatch((4.2,3.2),(8.8,3.2),arrowstyle="-|>",mutation_scale=28,color=CYAN,lw=2.6))
ax.text(6.55,3.95,"ENACTMENT",ha="center",color=CYAN,fontsize=13.5,weight="bold")
ax.text(6.55,3.62,"process · action · measurement",ha="center",color=CYAN,fontsize=9.6)
ax.text(6.55,2.78,"divergence-from-template =\nthe visible trace of enactment",ha="center",color=MUTE,fontsize=8.8,style="italic")
ax.text(6.5,1.15,"archetype = held superposition        ·        enactment = collapse        ·        actor = structure at informed collapse",
        ha="center",color=VIOLET,fontsize=10.5)
plt.savefig(f"{OUT}/fig2-structure-enactment-actor.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("regenerated fig1 (small-multiples) + fig2 (reroomed)")
