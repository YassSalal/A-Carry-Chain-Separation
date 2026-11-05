"""Switch-level DC model of Bus 2 across consecutive additions.
Nodes per k-segment: n0 (repeater output) ... nk. Slice i: VSW at node i+1 (on if R),
HSW between nodes i and i+1 (on if not Lambda), receiver reads node i+1.
Drivers are resistors to VDD/GND; isolated islands keep the charge left by the previous
addition (discharge time 23.6 ns >> T_clk) and share it among their nodes.
Variants: A = manuscript as written (no reset, full-swing repeater)
          B = Step-1 reset to LOW, full-swing repeater
          C = Step-1 reset + rise-only repeater (pull-down stage enabled only during reset)"""
import numpy as np
VDD=0.70; VT=0.35; RV=280.0; RH=220.0; RREP=312.5; RPD=10e6; K=16
def markers(a,b,W):
    A=np.array([(a>>i)&1 for i in range(W)],np.uint8); B=np.array([(b>>i)&1 for i in range(W)],np.uint8)
    U=A^B; L=A&B; Up=np.concatenate(([0],U[:-1])); Lp=np.concatenate(([0],L[:-1]))
    R=U&(1-Up)&(1-Lp); Lam=(1-U)&Up
    B2=np.zeros(W,np.uint8); p=0
    for l in range(W): p=R[l]|(p&(1-Lam[l])); B2[l]=p
    return U,R,Lam,B2&U
def solve_segment(Rs,Lams,prev_v,rep_in_high,variant):
    k=len(Rs); n=k+1
    G=np.zeros((n,n)); I=np.zeros(n); driven=np.zeros(n,bool)
    # union-find of conducting HSWs
    par=list(range(n))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for i in range(k):
        if not Lams[i]:
            g=1/RH; G[i,i]+=g; G[i+1,i+1]+=g; G[i,i+1]-=g; G[i+1,i]-=g; par[f(i)]=f(i+1)
    for j in range(n): G[j,j]+=1/RPD
    for i in range(k):
        if Rs[i]: G[i+1,i+1]+=1/RV; I[i+1]+=VDD/RV; driven[i+1]=True
    if variant in 'AB':
        G[0,0]+=1/RREP; I[0]+=(VDD/RREP if rep_in_high else 0); driven[0]=True
    elif rep_in_high:
        G[0,0]+=1/RREP; I[0]+=VDD/RREP; driven[0]=True
    comps={}
    for j in range(n): comps.setdefault(f(j),[]).append(j)
    v=np.zeros(n)
    for c in comps.values():
        if any(driven[j] for j in c):
            sub=np.ix_(c,c); v[c]=np.linalg.solve(G[sub],I[c])
        else:
            v[c]=np.mean(prev_v[c])          # charge sharing of stale charge
    return v
def run(seq,W,variant):
    nseg=(W+K-1)//K; prev=[np.zeros(K+1) for _ in range(nseg)]
    fails=0; worst=9.0; first_fail=None
    for t,(a,b) in enumerate(seq):
        U,R,Lam,Ealg=markers(a,b,W)
        if variant in 'BC': prev=[np.zeros(K+1) for _ in range(nseg)]
        rep_high=False; newprev=[]
        Ephys=np.zeros(W,np.uint8)
        for s in range(nseg):
            lo=s*K; hi=min(W,lo+K); kk=hi-lo
            v=solve_segment(R[lo:hi],Lam[lo:hi],prev[s][:kk+1],rep_high,variant)
            Ephys[lo:hi]=(v[1:kk+1]>VT).astype(np.uint8)&U[lo:hi]
            for i in range(kk):
                if U[lo+i]:
                    m=(v[i+1]-VT) if Ealg[lo+i] else (VT-v[i+1]); worst=min(worst,m)
            rep_high=v[kk]>VT; pv=np.zeros(K+1); pv[:kk+1]=v; newprev.append(pv)
        prev=newprev
        if (Ephys!=Ealg).any():
            fails+=1
            if first_fail is None: first_fail=t
    return fails,worst,first_fail
if __name__=='__main__':
    rng=np.random.default_rng(7)
    W=64; full=(1<<W)-1
    def rnd(): return int(rng.integers(0,1<<63))*2+int(rng.integers(0,2))
    seqs={'random back-to-back (2000 additions)':[(rnd()&full,rnd()&full) for _ in range(2000)]}
    # worst-case 1: bus fully HIGH, then carry chains that must read LOW in isolated islands
    allhigh=(full,0)
    grp=0;  # per 4-bit group: pos0 a=b=1 (carry), pos1-2 a=1 b=0 (carry chain), pos3 zero
    a2=sum(((0b0111)<<(4*g)) for g in range(W//4)); b2=sum(((0b0001)<<(4*g)) for g in range(W//4))
    seqs['all-HIGH, then isolated carry chains']=[allhigh,(a2,b2)]*50
    # worst-case 2: carry-free chain starting at first slice after each repeater, previous segment LOW
    a3=sum(1<<(16*s) for s in range(W//16)); seqs['chain start at repeater output, LOW upstream']=[(a3,0)]*10
    # worst-case 3: alternating selection patterns
    seqs['alternating 0101/1010 patterns']=[(int('01'*32,2),0),(int('10'*32,2),0)]*50
    for name,seq in seqs.items():
        for var in 'ABC':
            f,w,ff=run(seq,W,var)
            print(f'{name:48s} variant {var}: wrong E in {f:4d}/{len(seq)} additions, worst margin {w*1000:7.1f} mV')
