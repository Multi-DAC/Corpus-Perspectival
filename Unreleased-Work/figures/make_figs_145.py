import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap

OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\figures"
os.makedirs(OUT, exist_ok=True)
WARM="#8c2f1d"; AMBER="#e0934b"; PARCH="#f6efe3"; INK="#3a2a1a"; BLUE="#1F3A5F"

# ============ FIGURE 1 — the room and its keyholes ============
fig,ax=plt.subplots(figsize=(10,8.4)); ax.set_xlim(-10,10); ax.set_ylim(-9,9); ax.axis("off")
ax.add_patch(Circle((0,0),2.7,facecolor=AMBER,edgecolor=WARM,linewidth=2.5,zorder=3))
ax.text(0,0.4,"ONE",ha="center",va="center",fontsize=20,fontweight="bold",color="white",zorder=4)
ax.text(0,-0.7,"topology",ha="center",va="center",fontsize=13,style="italic",color="white",zorder=4)
ax.text(0,-1.45,"(the room)",ha="center",va="center",fontsize=10,color="#fbeede",zorder=4)
spokes=[("Folklore","fairy · will-o'-wisp"),("Religion","angel · Marian light"),
        ("Occult","Enochian angel"),("Channeled","the hierarchy"),
        ("Crypto","orb · cryptid"),("Psychedelic","entity · machine-elf"),
        ("Clinical","NDE light · the hag"),("Philosophy","mundus imaginalis")]
R=6.6
for i,(ch,cost) in enumerate(spokes):
    a=np.pi/2 - i*2*np.pi/len(spokes)
    x,y=R*np.cos(a),R*np.sin(a)
    ax.plot([2.5*np.cos(a),x*0.82],[2.5*np.sin(a),y*0.82],color="#c9b79a",lw=1.6,zorder=1)
    ax.add_patch(Circle((x,y),0.42,facecolor="white",edgecolor=BLUE,linewidth=1.8,zorder=3))
    ha="center"
    ax.text(x,y+0.92,ch,ha=ha,va="center",fontsize=11.5,fontweight="bold",color=BLUE,zorder=4)
    ax.text(x,y-0.92,cost,ha=ha,va="center",fontsize=9.5,style="italic",color=INK,zorder=4)
ax.set_title("Figure 1.  The room and its keyholes",fontsize=15,fontweight="bold",color=WARM,pad=2)
fig.text(0.5,0.045,"One configuration-space topology, perceived through bottlenecks of differing geometry,\n"
         "returns in different costume to each channel. The structure is shared; the name is local.",
         ha="center",fontsize=10.5,color="#5a4632",style="italic")
plt.subplots_adjust(top=0.93,bottom=0.11)
plt.savefig(os.path.join(OUT,"one-room-fig1-keyholes.png"),dpi=200,facecolor="white"); plt.close()

# ============ FIGURE 4 — lineage vs independent channels ============
fig,ax=plt.subplots(figsize=(11.5,7.2)); ax.set_xlim(0,16); ax.set_ylim(0,10); ax.axis("off")
def box(x,y,w,h,txt,fc,ec,tc="white",fs=9.5,bold=True):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.06,rounding_size=0.12",
                 facecolor=fc,edgecolor=ec,linewidth=1.6,zorder=3))
    ax.text(x,y,txt,ha="center",va="center",fontsize=fs,color=tc,
            fontweight=("bold" if bold else "normal"),zorder=4)
def arr(x1,y1,x2,y2,color=BLUE,style="-|>"):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=15,
                 color=color,linewidth=1.8,zorder=2))
ax.text(8,9.4,"Figure 4.  Content-convergence is a lineage, not a consensus",
        ha="center",fontsize=15,fontweight="bold",color=WARM)
# the egregore chain
ax.text(8,8.4,"ONE EGREGORE, AGING  —  the channeled 'content' lineage (traceable)",
        ha="center",fontsize=11,fontweight="bold",color=BLUE)
chain=[("Blavatsky's\nMasters (1875)"),("Ascended\nMasters (1930s)"),
       ("Pleiadians /\nMeier (1975)"),("Council of\nNine (1970s)"),("Galactic Fed.\n(1990s+)")]
xs=np.linspace(2.1,13.9,5)
for k,(x,t) in enumerate(zip(xs,chain)):
    box(x,7.2,2.15,1.0,t,BLUE,"#0d1f33",fs=8.0)
    if k>0: arr(xs[k-1]+1.08,7.2,x-1.08,7.2)
# independent set
ax.text(8,5.3,"INDEPENDENT CHANNELS  —  structure-convergence, no shared lineage",
        ha="center",fontsize=11,fontweight="bold",color=WARM)
indep=["Sleep paralysis\n(Hufford)","NDE ↔ bardo","DMT entities\n(Strassman)",
       "Fae / djinn","Wild Hunt","Serpent of\nwisdom","Initiatory\ndeath (Eliade)","RSPK (Roll)"]
gx=np.tile(np.linspace(2.2,13.8,4),2); gy=np.repeat([4.1,2.7],4)
for x,y,t in zip(gx,gy,indep):
    box(x,y,2.35,0.95,t,PARCH,AMBER,tc=INK,fs=8.6,bold=False)
# Law of One bridging
box(8,1.0,7.4,0.95,"Law of One $\\cdot$ Seth $\\cdot$ A Course in Miracles\n— channeled, but converge on STRUCTURE",WARM,"#5a1a10",fs=8.4)
ax.add_patch(FancyArrowPatch((6.2,6.7),(7.0,1.5),arrowstyle="-|>",mutation_scale=14,
             color="#b07a4a",linewidth=1.6,linestyle="--",zorder=2,connectionstyle="arc3,rad=-0.2"))
ax.text(3.5,3.2,"breaks the\nlineage",ha="center",fontsize=8.5,style="italic",color="#8a5a2a")
fig.text(0.5,0.02,"The 'space-brother' sources converge on message-content because they are one narrative aging through vocabularies. "
         "The\nindependent channels converge on structure. Law of One, Seth, and A Course in Miracles join the structure set; the space-brother lineage does not.",
         ha="center",fontsize=9.3,color="#5a4632",style="italic")
plt.subplots_adjust(top=0.93,bottom=0.13)
plt.savefig(os.path.join(OUT,"one-room-fig4-lineage.png"),dpi=200,facecolor="white"); plt.close()

# ============ FIGURE 5 — the contamination gradient ============
fig,ax=plt.subplots(figsize=(11.5,3.9))
grad=np.linspace(0,1,256).reshape(1,-1)
cmap=LinearSegmentedColormap.from_list("g",["#3f7d4f","#c9b04a","#b0552a","#8c2f1d"])
ax.imshow(grad,aspect="auto",cmap=cmap,extent=[0,10,0,1])
ax.set_xlim(0,10); ax.set_ylim(-1.6,1.9); ax.axis("off")
ax.text(5,2.4,"Figure 5.  The contamination gradient",ha="center",fontsize=15,fontweight="bold",color=WARM)
zones=[(0.9,"CONTAMINATION-\nPROOF","Hufford sleep paralysis ·\nNDE↔bardo · Stevenson\nchildren · clinical DMT"),
       (3.4,"ROBUST /\nINDEPENDENT","orb-plasma · shapeshifter\n· death-navigation · serpent\n· missing-time"),
       (6.1,"PRIMING-\nDEPENDENT","OBE silver-cord\n· DMT entity identity"),
       (7.9,"CONSTRUCTED","Men in Black\n(Barker, 1956)"),
       (9.2,"DEFLATED","cattle mutilation\n(bloat / blowfly / FBI)")]
for x,lab,ex in zones:
    ax.plot([x,x],[0,1],color="white",lw=1.2,alpha=.5)
    ax.text(x,1.45,lab,ha="center",va="center",fontsize=9.5,fontweight="bold",color=INK)
    ax.text(x,-0.9,ex,ha="center",va="center",fontsize=8.3,color=INK)
ax.annotate("",xy=(9.7,0.5),xytext=(0.3,0.5),
            arrowprops=dict(arrowstyle="-|>",color="white",lw=2))
fig.text(0.5,0.02,"Channels deflate precisely where independence fails (P5): the framework predicts WHICH collapse "
         "(constructed, primed) and which survive (the contamination-proof backbone).",
         ha="center",fontsize=9.3,color="#5a4632",style="italic")
plt.subplots_adjust(top=0.8,bottom=0.16)
plt.savefig(os.path.join(OUT,"one-room-fig5-gradient.png"),dpi=200,facecolor="white"); plt.close()

print("wrote fig1, fig4, fig5 to", OUT)
