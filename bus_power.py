"""Activity-based energy per addition for the custom bus (variant C: Step-1 reset,
rise-only repeaters). Activities are counted on random operands with the switch-level
model; capacitances follow Table B.1 (C0 = 0.30 fF per unit inverter, 1 fin each)."""
import numpy as np
from bus_switch_sim import markers, solve_segment, K, VT
VDD=0.70; C0=0.30e-15; TCLK=1.22e-9
C_node=60.5e-15/16          # Bus-2 node: share of C_load (tap + wire + keeper + repeater input)
C_gate_tg=2*4*(C0/2)        # complementary TG, NFIN=4 per device: two control lines of 4 fins
C_rcv_out=2*C0              # receiver output + E-register input
C_rep_int=(C0+8*C0)+8*C0    # input stage output + output-stage self load (s = 8)
I_pd=VDD/10e6               # contention per HIGH node (pull-down)
T_high=3*TCLK               # node HIGH from Step 2 until the next Step-1 reset
I_leak_slice=1e-9           # off-state leakage bound per bit slice used in Section 7.4.4.G
def activity(W,N=3000,seed=3):
    rng=np.random.default_rng(seed); full=(1<<W)-1
    tot=dict(high=0,R=0,Lam=0,rep=0)
    nseg=(W+K-1)//K
    for _ in range(N):
        a=int.from_bytes(rng.bytes(W//8),'little')&full; b=int.from_bytes(rng.bytes(W//8),'little')&full
        U,R,Lam,E=markers(a,b,W); rep=False
        for s in range(nseg):
            lo=s*K; hi=min(W,lo+K); kk=hi-lo
            v=solve_segment(R[lo:hi],Lam[lo:hi],np.zeros(kk+1),rep,'C')
            tot['high']+=int((v[1:]>VT).sum()); tot['rep']+=int(rep); rep=v[kk]>VT
        tot['R']+=int(R.sum()); tot['Lam']+=int(Lam.sum())
    return {k:v/N for k,v in tot.items()}
for W in (64,256):
    a=activity(W)
    E={}
    E['Bus-2 node charging (reset + evaluate)']=a['high']*C_node*VDD**2
    E['Switch control lines (VSW and HSW gates)']=(a['R']+a['Lam'])*C_gate_tg*VDD**2
    E['Receivers']=a['high']*C_rcv_out*VDD**2*1.1
    E['Repeaters (internal)']=a['rep']*C_rep_int*VDD**2*1.1
    E['Pull-down contention']=a['high']*VDD*I_pd*T_high
    E['Leakage (4 cycles)']=W*I_leak_slice*VDD*4*TCLK
    tot=sum(E.values()); rate=1/(4*TCLK)
    print(f'\nW={W}: HIGH nodes/addition={a["high"]:.1f} ({a["high"]/W:.0%}), R={a["R"]:.1f}, Lambda={a["Lam"]:.1f}, repeaters toggled={a["rep"]:.2f}')
    for k,v in E.items(): print(f'  {k:42s} {v*1e15:8.2f} fJ  {v*rate*1e6:8.2f} uW')
    print(f'  {"Total per addition / average power":42s} {tot*1e15:8.2f} fJ  {tot*rate*1e6:8.2f} uW at {rate/1e6:.0f} Madd/s')
