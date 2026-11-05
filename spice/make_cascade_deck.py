#!/usr/bin/env python3
"""Self-contained HSPICE deck for the full-bus check (Reviewer 4 pt 2, Reviewer 5 pt 2).
Builds m cascaded k = 16 segments from the device sizes of Supp.E Listing 1, with the switch
controls exposed as ports (they are internal, undriven nets in Listing 1), a corrected keeper
(Listing 1 feeds the inverter output back to its own input through 1 GOhm, which opposes the
held level), and the rise-only repeater of Rule R1. Each operand pair is one addition:
cycle 1 = Step-1 reset (VSWs off, HSWs on, repeater pull-down enabled), cycle 2 = Step 2.

  python3 make_cascade_deck.py --width 64 --corner TT --nmodel nmos_rvt --pmodel pmos_rvt \
      --models asap7_TT.pm --pairs 0xFFFFFFFFFFFFFFFF,0x0 0x7777777777777777,0x1111111111111111 > bus64_TT.sp

--nmodel/--pmodel/--models: the device names and model file of your ASAP7 v1.7 installation.
FinFET (BSIM-CMG) devices are sized by fin count; the W values of Listing 1 are kept only as
comments. Check the pull-down (Listing 1 uses L = 1.0 um, outside a fixed-gate-length FinFET
PDK) and replace it by the weak device your PDK supports."""
import argparse
VDD={'TT':0.70,'FF':0.77,'SS':0.63,'SF':0.70,'FS':0.70}; TEMP={'TT':25,'FF':-40,'SS':125,'SF':25,'FS':25}
K=16; TCLK=1.22e-9; TR=20e-12
def markers(a,b,W):
    A=[(a>>i)&1 for i in range(W)]; B=[(b>>i)&1 for i in range(W)]
    U=[x^y for x,y in zip(A,B)]; L=[x&y for x,y in zip(A,B)]
    R=[U[i]&(1-(U[i-1] if i else 0))&(1-(L[i-1] if i else 0)) for i in range(W)]
    Lam=[(1-U[i])&(U[i-1] if i else 0) for i in range(W)]
    return R,Lam
def pwl(node,levels,vdd,inv=False):
    pts=[]; prev=None
    for t,v in levels:
        v=1-v if inv else v
        if prev is None: pts.append((0.0,v*vdd))
        elif v!=prev: pts+=[(t,prev*vdd),(t+TR,v*vdd)]
        prev=v
    return f"V{node} {node} 0 PWL(" + ' '.join(f'{t:.4e} {v:.3f}' for t,v in pts) + ")"
ap=argparse.ArgumentParser()
ap.add_argument('--width',type=int,default=64); ap.add_argument('--corner',default='TT')
ap.add_argument('--nmodel',default='nmos_rvt'); ap.add_argument('--pmodel',default='pmos_rvt')
ap.add_argument('--models',default='asap7_models.sp'); ap.add_argument('--pairs',nargs='+',required=True)
a=ap.parse_args(); W=a.width; m=(W+K-1)//K; vdd=VDD[a.corner]; N=a.nmodel; P=a.pmodel
pairs=[tuple(int(x,0) for x in p.split(',')) for p in a.pairs]
o=[f'* CCSA Bus-2 cascade W={W} (m={m}), corner {a.corner}, {len(pairs)} consecutive additions',
   f'.include "{a.models}"', f'.temp {TEMP[a.corner]}', '.option post=2 runlvl=6',
   f'Vdd vdd 0 {vdd}', 'Vss vss 0 0', f'Vbus1 bus1 0 {vdd}',
   '* --- devices: fin counts from Supp.E Listing 1 ---',
   '.subckt VSW bus1 bus2 R Rb vdd vss', f'MN bus2 R bus1 vss {N} nfin=4', f'MP bus2 Rb bus1 vdd {P} nfin=4', '.ends',
   '.subckt HSW up dn Hb H vdd vss', f'MN dn H up vss {N} nfin=4', f'MP dn Hb up vdd {P} nfin=4', '.ends',
   '.subckt RCV in out vdd vss', f'MN out in vss vss {N} nfin=2', f'MP out in vdd vdd {P} nfin=2', '.ends',
   '.subckt PD bus vdd vss', f'MN bus vdd vss vss {N} nfin=1 $ edit: weakest device of your PDK (target R_pd >= 10 MOhm)', '.ends',
   '* corrected keeper: two inverters, so the feedback reinforces the held level',
   '.subckt KEEP bus vdd vss', f'MN1 kb bus vss vss {N} nfin=1', f'MP1 kb bus vdd vdd {P} nfin=1',
   'Rk kb kbw 200k $ edit: weak feedback; replace by long-L or stacked devices in your PDK',
   f'MN2 bus kbw vss vss {N} nfin=1', f'MP2 bus kbw vdd vdd {P} nfin=1', '.ends',
   '* rise-only repeater (Rule R1): pull-down stage enabled only during the Step-1 reset',
   '.subckt REP_RO in out en vdd vss', f'MN6 n1 in vss vss {N} nfin=4', f'MP6 n1 in vdd vdd {P} nfin=4',
   f'MP7 out n1 vdd vdd {P} nfin=8', f'MN7 out n1 x vss {N} nfin=16', f'MN8 x en vss vss {N} nfin=16', '.ends',
   '.subckt SLICE bus1 up dn R Rb Hb H E vdd vss', 'XV bus1 dn R Rb vdd vss VSW', 'XH up dn Hb H vdd vss HSW',
   'XR dn E vdd vss RCV', 'XP dn vdd vss PD', '.ends']
ctrl_R={i:[] for i in range(W)}; ctrl_H={i:[] for i in range(W)}; en=[]
for j,(x,y) in enumerate(pairs):
    t1=j*4*TCLK; t2=t1+TCLK
    R,Lam=markers(x,y,W)
    for i in range(W):
        ctrl_R[i]+=[(t1,0),(t2,R[i])]
        ctrl_H[i]+=[(t1,1),(t2,1-Lam[i])]       # HSW on in reset; H = not Lambda in Step 2
    en+=[(t1,1),(t2,0)]
o.append(pwl('en',en,vdd))
for i in range(W):
    o+= [pwl(f'R{i}',ctrl_R[i],vdd), pwl(f'Rb{i}',ctrl_R[i],vdd,True), pwl(f'H{i}',ctrl_H[i],vdd), pwl(f'Hb{i}',ctrl_H[i],vdd,True)]
o.append('Vin nin 0 0 $ B2[-1] = 0 at the first repeater input')
prev='nin'
for s in range(m):
    o.append(f'Xrep{s} {prev} s{s}_0 en vdd vss REP_RO'); o.append(f'Xkp{s} {prev} vdd vss KEEP')
    for i in range(min(K,W-s*K)):
        l=s*K+i; o.append(f'Xbs{l} bus1 s{s}_{i} s{s}_{i+1} R{l} Rb{l} Hb{l} H{l} E{l} vdd vss SLICE')
    prev=f's{s}_{min(K,W-s*K)}'
o.append(f'.tran 1p {len(pairs)*4*TCLK:.4e}')
for j in range(len(pairs)):
    t1=j*4*TCLK; t2=t1+TCLK
    o.append(f'.meas tran treset{j} trig v(en) val={vdd/2} rise=1 td={t1:.4e} targ v({prev}) val={vdd/2} fall=1 td={t1:.4e}')
    o.append(f'.meas tran tbus{j} trig v(R0) val={vdd/2} rise=1 td={t2:.4e} targ v({prev}) val={vdd/2} rise=1 td={t2:.4e}')
    for l in range(W):
        o.append(f'.meas tran vE{l}_{j} find v(s{l//K}_{l%K+1}) at={t2+TCLK-50e-12:.4e}')
o.append('.end'); print('\n'.join(o))
