#!/usr/bin/env python3
"""Compare the bus-node voltages measured by make_cascade_deck.py decks (HSPICE .mt0 file)
with the algorithmic rewrite enable E = B2 AND U1, and report errors and worst margins.
Usage: python3 check_cascade.py bus64_TT.mt0 --width 64 --corner TT --pairs <same as deck>"""
import argparse,re
VDD={'TT':0.70,'FF':0.77,'SS':0.63,'SF':0.70,'FS':0.70}
ap=argparse.ArgumentParser(); ap.add_argument('mt0'); ap.add_argument('--width',type=int); ap.add_argument('--corner',default='TT'); ap.add_argument('--pairs',nargs='+')
a=ap.parse_args(); W=a.width; vt=VDD[a.corner]/2
txt=open(a.mt0).read().split(); vals={}
names=[t for t in txt if re.match(r'^(ve\d+_\d+|tbus\d+|treset\d+)$',t.lower())]
# HSPICE .mt0 lists names then values in the same order
nums=[t for t in txt if re.match(r'^-?\d',t)]
for n,v in zip(names,nums[-len(names):]): vals[n.lower()]=float(v) if v not in ('failed',) else None
for j,p in enumerate(a.pairs):
    x,y=(int(z,0) for z in p.split(','))
    A=[(x>>i)&1 for i in range(W)]; B=[(y>>i)&1 for i in range(W)]
    U=[s^t for s,t in zip(A,B)]; L=[s&t for s,t in zip(A,B)]
    R=[U[i]&(1-(U[i-1] if i else 0))&(1-(L[i-1] if i else 0)) for i in range(W)]
    Lam=[(1-U[i])&(U[i-1] if i else 0) for i in range(W)]
    b=0; err=0; worst=9
    for i in range(W):
        b=R[i]|(b&(1-Lam[i])); e=b&U[i]; v=vals.get(f've{i}_{j}')
        if U[i] and v is not None:
            m=(v-vt) if e else (vt-v); worst=min(worst,m); err+= m<0
    print(f'addition {j}: t_bus={vals.get(f"tbus{j}")} s, t_reset={vals.get(f"treset{j}")} s, wrong E={err}, worst margin={worst*1000:.0f} mV')
