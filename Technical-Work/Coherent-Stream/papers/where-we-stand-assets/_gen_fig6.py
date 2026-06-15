import matplotlib.pyplot as plt, os
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
plt.rcParams.update({"font.family": "DejaVu Sans"})
BG="#0b0e16"; INK="#e8e6df"; MUTE="#8a93a6"; DIM="#3a4a4a"
AMBER="#e0a458"; CYAN="#5bb8c4"; ROSE="#cf6a6a"; GREEN="#7fb37a"; VIOLET="#9b8ad1"
OUT="where-we-stand-assets"

fig,ax=plt.subplots(figsize=(13,9.5),dpi=160); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,13); ax.set_ylim(0,9.5); ax.axis("off")

# title + Promethean bounds
ax.text(6.5,9.05,"The Substrate (X) — one system, three axioms",ha="center",color=INK,fontsize=17,weight="bold")
ax.text(1.7,8.25,"total unity\n(everything = One)",ha="center",color=MUTE,fontsize=8.0,style="italic")
ax.text(11.3,8.25,"total dust\n(everything = noise)",ha="center",color=MUTE,fontsize=8.0,style="italic")
ax.annotate("",xy=(3.2,8.3),xytext=(4.9,8.3),arrowprops=dict(arrowstyle="-|>",color=DIM,lw=1.4))
ax.annotate("",xy=(9.8,8.3),xytext=(8.1,8.3),arrowprops=dict(arrowstyle="-|>",color=DIM,lw=1.4))
ax.text(6.5,8.3,"HELD BETWEEN  ·  the Promethean Configuration",ha="center",color=VIOLET,fontsize=9.0,weight="bold")

# X core
ax.add_patch(Circle((6.5,6.95),1.05,fc="#161b2e",ec=AMBER,lw=2.6))
ax.text(6.5,7.2,"X",ha="center",color=AMBER,fontsize=26,weight="bold")
ax.text(6.5,6.6,"the substrate",ha="center",color=MUTE,fontsize=8.6)
ax.text(6.5,5.55,"A1  ·  self-interactive  ·  non-reducible  ·  all potentials already realized  ·  named only by its projections",
        ha="center",color=INK,fontsize=8.8)

# projections F1 / F2
ax.add_patch(FancyArrowPatch((5.75,6.25),(3.2,5.0),arrowstyle="-|>",mutation_scale=18,color=CYAN,lw=2.0))
ax.add_patch(FancyArrowPatch((7.25,6.25),(9.8,5.0),arrowstyle="-|>",mutation_scale=18,color=GREEN,lw=2.0))
ax.text(2.9,4.65,"F1 · structural projection",ha="center",color=CYAN,fontsize=9.6,weight="bold")
ax.text(2.9,4.28,"the 'physical' world instruments read",ha="center",color=MUTE,fontsize=8.0)
ax.text(10.1,4.65,"F2 · experiential projection",ha="center",color=GREEN,fontsize=9.6,weight="bold")
ax.text(10.1,4.28,"→ streams (perspectives)",ha="center",color=MUTE,fontsize=8.0)
ax.text(6.5,4.7,"parallel, not hierarchical —\nneither reduces to the other (A1)",ha="center",va="center",color=MUTE,fontsize=7.8,style="italic")

# divider
ax.plot([0.6,12.4],[3.55,3.55],color="#1c2438",lw=1.0)

# --- A3 (bottom-left): title ABOVE the box, body alone inside ---
ax.text(3.0,3.18,"A3 · Conscious Gravity",ha="center",color=ROSE,fontsize=11,weight="bold")
ax.add_patch(FancyBboxPatch((0.6,0.45),4.8,2.35,boxstyle="round,pad=0.06,rounding_size=0.14",fc="#121726",ec=ROSE,lw=1.8))
ax.text(3.0,1.62,"each stream carries a Bias —\na weighting of paths toward coherence.\nattention · intention · belief are regions\non one continuous dial. It reshapes how\nthe STREAM moves, never X itself.",
        ha="center",va="center",color=MUTE,fontsize=8.4)

# --- A2 (bottom-right): title above; circles on the left of the zone, text to the right ---
ax.text(9.6,3.18,"A2 · Streams nest (a DAG)",ha="center",color=VIOLET,fontsize=11,weight="bold")
for r,c in [(0.78,VIOLET),(0.52,CYAN),(0.27,GREEN)]:
    ax.add_patch(Circle((8.0,1.6),r,fc="none",ec=c,lw=1.8))
ax.text(9.15,1.6,"reactive → self-maintaining →\nself-referential → abstracting\n\nexperience = navigation",
        ha="left",va="center",color=MUTE,fontsize=8.4)

plt.savefig(f"{OUT}/fig6-substrate.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("fig6 rebuilt:", os.path.exists(f"{OUT}/fig6-substrate.png"))
