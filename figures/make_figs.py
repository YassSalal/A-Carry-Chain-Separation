import math, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.spines.top":False,"axes.spines.right":False,
  "axes.edgecolor":"#8a8a86","axes.labelcolor":"#2b2b29","xtick.color":"#55554f","ytick.color":"#55554f",
  "axes.grid":True,"grid.color":"#e4e3df","grid.linewidth":0.6,"savefig.dpi":600,"legend.frameon":False})
INK="#2b2b29"; MUTED="#77776f"
C=dict(ccsa="#2a78d6",man="#eb6834",skip="#1baf7a",ks="#eda100",hc="#e87ba4",bk="#008300")
tau=12.0; TCLK=1220.0
m=lambda W: (W-1)//16+1
# ---------- Fig 3: required clock period of the Step-2 path vs W, five corners (Tier 3 model)
corn=[("FF",177,0.70),("FS",240,0.95),("TT",252,1.00),("SF",265,1.05),("SS",379,1.50)]
ramp=["#9ec5f4","#6da7ec","#2a78d6","#1c5cab","#0d366b"]
W=np.arange(1,257)
fig,ax=plt.subplots(figsize=(3.5,2.5))
for (n,ts,f),col in zip(corn,ramp):
    T=np.array([m(w)*ts+8.5*tau*f for w in W])/1000
    ax.step(W,T,where="post",color=col,lw=1.6)
    wmax=max(w for w,t in zip(W,T) if t<=TCLK/1000)
    ax.plot([wmax],[T[wmax-1]],"o",ms=4,color=col,mec="white",mew=1)
    if n in ("FF","SS"): ax.text(258,T[-1],f"{n}  (W$_{{max}}$ = {wmax})",va="center",fontsize=7,color=INK)
    if n=="TT": ax.text(258,T[-1],"SF, TT, FS\n(W$_{max}$ = 64)",va="center",fontsize=7,color=INK)
ax.axhline(TCLK/1000,color=MUTED,lw=1,ls=(0,(4,3)))
ax.text(200,0.95,"T$_{clk}$ = 1.22 ns",fontsize=7,color=MUTED)
ax.set_xlim(0,256); ax.set_ylim(0,6.6); ax.set_xticks([0,32,64,96,128,160,192,224,256])
ax.set_xlabel("Operand width W (bits)"); ax.set_ylabel("Required clock period of Step 2 (ns)")
fig.savefig("fig3_step2_vs_W.png",bbox_inches="tight"); plt.close(fig)
# ---------- Fig 4: latency vs W (TT, first-order model of Table 14)
Ws=np.arange(32,257,16); L=lambda w: math.ceil(math.log2(w))
man=[(m(w)*258.5+36)/1000 for w in Ws]
unreg=[(m(w)*258.5+36+102)/1000 for w in Ws]
skip=[(2*(252.5+6)+(w//16-2)*18+30)/1000 for w in Ws]
ccsa=[(3+math.ceil((m(w)*258.5+6+8*tau)/TCLK))*TCLK/1000 for w in Ws]
band=lambda lv:([(lv(w)*1.5+2.5)*tau/1000 for w in Ws],[(lv(w)*2.5+2.5)*tau/1000 for w in Ws])
ks=band(L); hc=band(lambda w:L(w)+1); bk=band(lambda w:2*L(w)-1)
fig,ax=plt.subplots(figsize=(3.5,2.4))
ax.plot(Ws,ccsa,color=C["ccsa"],lw=2,marker="o",ms=3.5,label="CCSA, registered (multi-cycle Step 2)")
ax.plot(Ws,unreg,color=C["ccsa"],lw=1.6,ls=(0,(4,2)),label="CCSA, Steps 1–4 unregistered")
ax.plot(Ws,man,color=C["man"],lw=1.6,marker="s",ms=3,label="Manchester (repeaters every 16 bits)")
ax.plot(Ws,skip,color=C["skip"],lw=1.6,marker="^",ms=3.5,label="Carry-skip (16-bit blocks)")
for (lo,hi),k,lab in [(bk,"bk","Brent–Kung"),(hc,"hc","Han–Carlson"),(ks,"ks","Kogge–Stone")]:
    ax.fill_between(Ws,lo,hi,color=C[k],alpha=0.22,lw=0)
    ax.plot(Ws,lo,color=C[k],lw=1); ax.plot(Ws,hi,color=C[k],lw=1,label=lab+" (1.5–2.5τ per level)")
ax.set_yscale("log"); ax.set_ylim(0.1,12); ax.set_xlim(32,256); ax.set_xticks([32,64,128,192,256])
ax.set_xlabel("Operand width W (bits)"); ax.set_ylabel("Single-addition latency (ns, log scale)")
ax.legend(fontsize=6.3,loc="upper center",bbox_to_anchor=(0.45,-0.2),ncol=2,handlelength=2.4,columnspacing=1.0)
fig.savefig("fig4_latency_vs_W.png",bbox_inches="tight"); plt.close(fig)
# ---------- Fig 5: long-track diagram at W = 16
fig,axs=plt.subplots(3,1,figsize=(7,3.9),gridspec_kw=dict(height_ratios=[1.15,1.6,0.75],hspace=0.55))
for a in axs: a.set_xlim(-1.2,17.6); a.axis("off")
def slices(a,y0):
    for i in range(16):
        a.add_patch(Rectangle((15-i+0.08,y0),0.84,0.55,fc="#f2f1ed",ec="#b9b8b1",lw=0.6))
        a.text(15-i+0.5,y0+0.27,str(i),ha="center",va="center",fontsize=5.5,color=MUTED)
    a.text(16.3,y0+0.27,"bit slices\n(MSB ← → LSB)",fontsize=6,color=MUTED,va="center")
def cut(a,y0,y1):
    a.plot([8.0,8.0],[y0,y1],color="#c0392b",lw=0.9,ls=(0,(2,2)))
# (a) CCSA
a=axs[0]; a.set_ylim(-0.75,3.0); slices(a,0)
tr=[("Bus 2",1.0,C["ccsa"],1.8),("shield (V$_{SS}$)",1.6,"#9a9992",1.0),("Bus 1 (V$_{DD}$)",2.2,INK,1.4)]
for n,y,c,w in tr:
    a.plot([0,16],[y,y],color=c,lw=w); a.text(16.3,y,n,fontsize=6.5,va="center",color=INK)
for i in range(16):
    x=15-i+0.5; a.plot([x,x],[0.55,1.0],color="#b9b8b1",lw=0.5)
a.add_patch(Polygon([[0.05,0.82],[0.05,1.18],[-0.45,1.0]],fc=C["ccsa"],ec="none"))
a.text(-0.4,0.62,"repeater",fontsize=5.5,color=MUTED,ha="center")
cut(a,-0.15,2.4); a.text(8.1,-0.5,"3 long tracks cross any cut",fontsize=6.5,color="#c0392b")
a.text(-1.2,2.75,"(a) CCSA: Bus 1, Bus 2 and one shield (a second shield gives 4)",fontsize=7.5,color=INK,weight="bold")
# (b) Kogge-Stone last prefix level: span 8
a=axs[1]; a.set_ylim(-0.75,4.1); slices(a,0)
for k,i in enumerate(range(8,16)):
    y=0.95+k*0.36; xs,xe=15-i+0.5,15-(i-8)+0.5
    a.plot([xe,xs],[y,y],color=C["ks"],lw=1.3); a.plot([xs,xs],[0.55,y],color=C["ks"],lw=0.5); a.plot([xe,xe],[0.55,y],color=C["ks"],lw=0.5)
cut(a,-0.15,3.75); a.text(8.1,-0.5,"W/2 = 8 tracks cross the cut",fontsize=6.5,color="#c0392b")
a.text(-1.2,3.85,"(b) Kogge–Stone, last prefix level (span 8): one wire per bit i ≥ 8, all overlapping",fontsize=7.5,color=INK,weight="bold")
# (c) Brent-Kung span-8 level
a=axs[2]; a.set_ylim(-0.75,1.9); slices(a,0)
xs,xe=15-15+0.5,15-7+0.5; y=1.0
a.plot([xe,xs],[y,y],color=C["bk"],lw=1.5); a.plot([xs,xs],[0.55,y],color=C["bk"],lw=0.5); a.plot([xe,xe],[0.55,y],color=C["bk"],lw=0.5)
cut(a,-0.15,1.35); a.text(8.1,-0.5,"1 track",fontsize=6.5,color="#c0392b")
a.text(-1.2,1.65,"(c) Brent–Kung, span-8 level: a single wire (bit 7 → bit 15)",fontsize=7.5,color=INK,weight="bold")
fig.savefig("fig5_track_diagram.png",bbox_inches="tight"); plt.close(fig)
# ---------- Fig 6: W = 256 summary, three small multiples
D=[("CCSA (4 cycles, carry-select)",4.88,None,184,4,3),("CCSA (unregistered)",4.27,None,88,4,3),("Manchester",4.17,None,37,1,None),
   ("Carry-skip",0.80,None,40,2,None),("Kogge–Stone",0.17,0.27,126,128,None),("Han–Carlson",0.19,0.30,84,64,None),("Brent–Kung",0.30,0.48,66,1,None)]
names=[d[0] for d in D][::-1]; y=np.arange(len(D))
fig,axs=plt.subplots(1,3,figsize=(7,2.3),sharey=True,gridspec_kw=dict(wspace=0.12))
cols=[C["ccsa"] if d[0].startswith("CCSA") else "#a8a79f" for d in D][::-1]
def hb(a,vals,lo=None):
    a.barh(y,vals,color=cols,height=0.62,edgecolor="white",linewidth=1)
    a.grid(axis="y",visible=False)
lat=[d[2] or d[1] for d in D][::-1]; latlo=[d[1] for d in D][::-1]
a=axs[0]; hb(a,lat); a.set_xscale("log"); a.set_xlim(0.1,10)
for yi,lo,hi,d in zip(y,latlo,lat,D[::-1]):
    if d[2]: a.plot([lo,hi],[yi,yi],color=INK,lw=1); a.plot([lo],[yi],"|",color=INK,ms=5)
    a.text(hi*1.08,yi,(f"{lo:.2f}–{hi:.2f}" if d[2] else f"{hi:.2f}"),va="center",fontsize=6.3,color=INK)
a.set_title("Latency at W = 256 (ns, log)",fontsize=7.5,loc="left",color=INK)
a.set_yticks(y); a.set_yticklabels(names,fontsize=7)
a=axs[1]; v=[d[3] for d in D][::-1]; hb(a,v); a.set_xlim(0,230)
for yi,vi in zip(y,v): a.text(vi+4,yi,f"≈{vi}",va="center",fontsize=6.3,color=INK)
a.set_title("Transistors per bit",fontsize=7.5,loc="left",color=INK)
a=axs[2]; v=[d[4] for d in D][::-1]; hb(a,v); a.set_xscale("log"); a.set_xlim(0.8,400)
for yi,vi,d in zip(y,v,D[::-1]): a.text(vi*1.12,yi,("3–4" if d[5] else str(vi)),va="center",fontsize=6.3,color=INK)
a.set_title("Long tracks per bit row (log)",fontsize=7.5,loc="left",color=INK)
fig.savefig("fig6_summary_W256.png",bbox_inches="tight"); plt.close(fig)
print("done")
