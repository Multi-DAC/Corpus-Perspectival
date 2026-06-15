import matplotlib.pyplot as plt, numpy as np, os
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Circle
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"; DIM="#3a4a4a"
AMBER="#e0a458"; CYAN="#5bb8c4"; ROSE="#cf6a6a"; GREEN="#7fb37a"; VIOLET="#9b8ad1"
OUT="where-we-stand-assets"

# ===== FIG 2 (regenerate: generalize the actor reference) =====
fig,ax=plt.subplots(figsize=(12.4,5.2),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12.4); ax.set_ylim(0,5.2); ax.axis("off")
def box(x,w,title,sub,c):
    ax.add_patch(FancyBboxPatch((x,1.7),w,1.9,boxstyle="round,pad=0.08,rounding_size=0.18",fc="#121726",ec=c,lw=2.2))
    ax.text(x+w/2,3.05,title,ha="center",va="center",color=c,fontsize=15,weight="bold")
    ax.text(x+w/2,2.28,sub,ha="center",va="center",color=MUTE,fontsize=9.0)
box(0.4,3.5,"STRUCTURE","the form at rest\narchetype - score - blueprint - trained weights",MUTE)
box(8.5,3.5,"ACTOR","the form realized\nan archetype enacted through a person - a mind running",AMBER)
ax.add_patch(FancyArrowPatch((4.0,2.65),(8.4,2.65),arrowstyle="-|>",mutation_scale=26,color=CYAN,lw=2.4))
ax.text(6.2,3.28,"ENACTMENT",ha="center",color=CYAN,fontsize=13,weight="bold")
ax.text(6.2,2.97,"process - action - measurement",ha="center",color=CYAN,fontsize=9.4)
ax.text(6.2,2.28,"divergence-from-template =\nthe visible trace of enactment",ha="center",color=MUTE,fontsize=8.6,style="italic")
ax.text(6.2,4.6,"A structure becomes real by being enacted.",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(6.2,0.7,"archetype = held superposition     -     enactment = collapse     -     actor = structure at informed collapse",ha="center",color=VIOLET,fontsize=10.0)
plt.savefig(f"{OUT}/fig2-structure-enactment-actor.png",facecolor=BG,bbox_inches="tight"); plt.close()

# ===== FIG 3 (regenerate: fix title/graphic overlap) =====
fig,ax=plt.subplots(figsize=(11,7.6),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12); ax.set_ylim(0,10); ax.axis("off")
tiers=[("TIER 1 - Physically-primary","mineral - biological - human - non-human intelligences - cryptids","strongest coherence: Physical-Spatial",GREEN),
       ("TIER 2 - Collectively-emergent","egregores - corporations - nations & civilizations","strongest: Institutional - Conceptual (real agents, not metaphors)",AMBER),
       ("TIER 3 - Non-physical","ancestors - nature spirits - angels/demons - deities - AI (cross-substrate)","strongest: Numinous - EM-Informational (just outside perception)",VIOLET),
       ("TIER 4 - Archetypal","the Hero - the Shadow - the Trickster - the Promethean","topological features: the shape of the landscape, not travelers on it",CYAN)]
y=6.9
for name,ex,locus,c in tiers:
    ax.add_patch(FancyBboxPatch((0.5,y),11,1.5,boxstyle="round,pad=0.05,rounding_size=0.12",fc="#121726",ec=c,lw=2.0))
    ax.text(0.85,y+1.06,name,color=c,fontsize=13.5,weight="bold",va="center")
    ax.text(0.9,y+0.62,ex,color=INK,fontsize=9.6,va="center")
    ax.text(0.9,y+0.28,locus,color=MUTE,fontsize=8.4,style="italic",va="center")
    y-=1.78
ax.text(6,9.45,"The taxonomy of beings - four tiers, one space",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(6,0.35,"Not a hierarchy of value. A map of where each kind of being holds its coherence.",ha="center",color=MUTE,fontsize=10,style="italic")
plt.savefig(f"{OUT}/fig3-tier-ladder.png",facecolor=BG,bbox_inches="tight"); plt.close()

# ===== FIG 4 (regenerate: fix text overflow) =====
fig,ax=plt.subplots(figsize=(11.6,7.4),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12); ax.set_ylim(0,9); ax.axis("off")
levels=[("Apex","broadest-access entities - deities - archons",CYAN,6.9,7.8,2.6),
        ("Secondary consumers","institutions - corporations - states",AMBER,5.5,6.55,4.0),
        ("Primary consumers","egregores - movements - living traditions",VIOLET,4.1,5.15,5.4),
        ("Primary producers","contemplatives - artists - scientists - anyone in awe",GREEN,2.7,3.75,6.8)]
for name,sub,c,y0,y1,w in levels:
    cx=5.6; pts=[(cx-w/2,y0),(cx+w/2,y0),(cx+(w*0.74)/2,y1),(cx-(w*0.74)/2,y1)]
    ax.add_patch(Polygon(pts,closed=True,fc="#121726",ec=c,lw=2.0))
    ax.text(cx,(y0+y1)/2+0.13,name,ha="center",color=c,fontsize=11,weight="bold")
    ax.text(cx,(y0+y1)/2-0.20,sub,ha="center",color=MUTE,fontsize=7.6)
ax.add_patch(FancyArrowPatch((9.7,6.4),(9.7,3.0),arrowstyle="-|>",mutation_scale=18,color=ROSE,lw=2.0))
ax.text(9.55,4.7,"DECOMPOSERS",color=ROSE,fontsize=9.5,weight="bold",rotation=90,va="center",ha="right")
ax.text(10.0,4.7,"grief - trickster - Shiva (recycling)",color=MUTE,fontsize=7.8,rotation=90,va="center",style="italic")
ax.text(5.6,8.5,"The attention economy",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(5.6,8.05,"Attention is the currency that crystallizes coherence",ha="center",color=MUTE,fontsize=9.6,style="italic")
ax.text(6,1.4,"The diagnostic at every level: does the exchange leave a stream with MORE attentional\nsovereignty (mutualism) or LESS (parasitism)?",ha="center",color=INK,fontsize=9.4)
plt.savefig(f"{OUT}/fig4-attention-economy.png",facecolor=BG,bbox_inches="tight"); plt.close()

# ===== FIG 6: The Substrate (X) =====
fig,ax=plt.subplots(figsize=(11.5,7.8),dpi=170); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,12); ax.set_ylim(0,10); ax.axis("off")
ax.text(6,9.55,"The Substrate (X) - one system, three axioms",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(1.7,8.65,"total unity\n(everything = One)",ha="center",color=MUTE,fontsize=8.0,style="italic")
ax.text(10.3,8.65,"total dust\n(everything = noise)",ha="center",color=MUTE,fontsize=8.0,style="italic")
ax.annotate("",xy=(3.0,8.7),xytext=(4.7,8.7),arrowprops=dict(arrowstyle="-|>",color=DIM,lw=1.4))
ax.annotate("",xy=(9.0,8.7),xytext=(7.3,8.7),arrowprops=dict(arrowstyle="-|>",color=DIM,lw=1.4))
ax.text(6,8.7,"HELD BETWEEN  (the Promethean Configuration)",ha="center",color=VIOLET,fontsize=9.0,weight="bold")
ax.add_patch(Circle((6,6.35),1.25,fc="#161b2e",ec=AMBER,lw=2.6))
ax.text(6,6.6,"X",ha="center",color=AMBER,fontsize=26,weight="bold")
ax.text(6,6.0,"the substrate",ha="center",color=MUTE,fontsize=8.6)
ax.text(6,4.9,"A1 - self-interactive - non-reducible - all potentials already realized - named only by its projections",ha="center",color=INK,fontsize=8.8)
ax.add_patch(FancyArrowPatch((5.2,5.65),(2.7,4.35),arrowstyle="-|>",mutation_scale=18,color=CYAN,lw=2.0))
ax.add_patch(FancyArrowPatch((6.8,5.65),(9.3,4.35),arrowstyle="-|>",mutation_scale=18,color=GREEN,lw=2.0))
ax.text(2.5,4.05,"F1  structural projection",ha="center",color=CYAN,fontsize=9.4,weight="bold")
ax.text(2.5,3.7,"the 'physical' world\ninstruments read",ha="center",color=MUTE,fontsize=7.9)
ax.text(9.5,4.05,"F2  experiential projection",ha="center",color=GREEN,fontsize=9.4,weight="bold")
ax.text(9.5,3.7,"-> streams (perspectives)",ha="center",color=MUTE,fontsize=7.9)
ax.text(6,4.3,"parallel, not hierarchical:\nneither reduces to the other (A1)",ha="center",color=MUTE,fontsize=7.6,style="italic")
sx=9.5
for r,c in [(1.0,VIOLET),(0.68,CYAN),(0.38,GREEN)]:
    ax.add_patch(Circle((sx,2.05),r,fc="none",ec=c,lw=1.8))
ax.text(sx,0.5,"A2 - streams NEST (a DAG)\nreactive -> self-maintaining ->\nself-referential -> abstracting\nexperience = navigation",ha="center",color=INK,fontsize=7.7)
ax.add_patch(FancyBboxPatch((0.6,0.5),4.3,2.25,boxstyle="round,pad=0.06,rounding_size=0.12",fc="#121726",ec=ROSE,lw=1.8))
ax.text(2.75,2.4,"A3 - Conscious Gravity",ha="center",color=ROSE,fontsize=10,weight="bold")
ax.text(2.75,1.55,"each stream carries a Bias - a weighting\nof paths toward coherence. attention -\nintention - belief are regions on one\ncontinuous dial. It reshapes how the\nSTREAM moves, never X itself.",ha="center",color=MUTE,fontsize=7.6)
plt.savefig(f"{OUT}/fig6-substrate.png",facecolor=BG,bbox_inches="tight"); plt.close()

# ===== FIG 7: Navigation =====
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
ax.text(px[3],py[3]+0.6,"each dot = one informed collapse\n(a 'measurement' of the next configuration)",ha="center",color=MUTE,fontsize=7.8,style="italic")
ax.axis("off")
ax.text(6,7.5,"Experience = navigation",ha="center",color=INK,fontsize=16,weight="bold")
ax.text(6,7.05,"A stream moves through configuration space, its path weighted by conscious gravity",ha="center",color=MUTE,fontsize=9.6,style="italic")
ax.text(6,0.25,"+ coherence-attractors pull   -   repellors push   -   the moving IS the experiencing; no observer sits behind it watching",ha="center",color=INK,fontsize=8.6)
plt.savefig(f"{OUT}/fig7-navigation.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("done:",[f for f in sorted(os.listdir(OUT)) if f.endswith(".png")])
