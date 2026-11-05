"""Register-level model of the CCSA (Variant B) with persistent state, using the
normative equations of Section 7.3.1. Tests single and back-to-back additions."""
import numpy as np, sys
def bits(x,W): return np.array([(x>>i)&1 for i in range(W)]+[0],dtype=np.uint8)  # positions 0..W
class CCSA:
    def __init__(s,W):
        s.W=W; z=np.zeros(W+1,np.uint8)
        s.U=z.copy(); s.L=z.copy(); s.M=z.copy(); s.E=z.copy()   # persistent registers
    def add(s,a,b):
        W=s.W; A=bits(a,W); B=bits(b,W)
        # Step 1
        s.U=A^B; s.L=A&B
        U1,L1=s.U,s.L
        sh=lambda v: np.concatenate(([0],v[:-1])).astype(np.uint8)   # v[l-1], v[-1]=0
        # Step 2
        R=U1&(1-sh(U1))&(1-sh(L1)); Lam=(1-U1)&sh(U1)
        B2=np.zeros(W+1,np.uint8); prev=0
        for l in range(W+1):
            prev=R[l] | (prev & (1-Lam[l])); B2[l]=prev
        s.E=B2&U1
        U2=U1&(1-s.E); L2=L1|s.E; s.M=s.E.copy()
        # Step 3
        U3=((1-U2)&sh(U2)) | ((1-sh(s.M))&sh(L2)&(1-sh(U2))&(1-U2)); L3=L2&s.M
        # Step 4
        U4=U3|L3
        return int(sum(int(v)<<i for i,v in enumerate(U4))), s.E.copy()
if __name__=='__main__':
    rng=np.random.default_rng(0xCC5A)
    # exhaustive single additions W=6 and W=8
    for W in (6,8):
        c=CCSA(W); bad=0
        for a in range(1<<W):
            for b in range(1<<W):
                if c.add(a,b)[0]!=a+b: bad+=1
        print(f'W={W}: exhaustive single additions, errors={bad}')
    # exhaustive consecutive pairs W=4 (all 2^16 x 2^16 too many) -> W=4 all pairs of pairs
    W=4; c=CCSA(W); bad=0; n=0
    ops=[(a,b) for a in range(16) for b in range(16)]
    for p in ops:
        for q in ops:
            c.add(*p); r=c.add(*q)[0]; n+=1
            if r!=q[0]+q[1]: bad+=1
    print(f'W=4: all {n} ordered pairs of consecutive additions, errors={bad}')
    # long random sequences at W=64 and 256 (same hardware instance, back-to-back)
    for W,N in ((64,20000),(256,5000)):
        c=CCSA(W); bad=0
        for _ in range(N):
            a=int(rng.integers(0,1<<62))<<(W-62) | int(rng.integers(0,1<<62)) if W>62 else int(rng.integers(0,1<<W))
            b=int(rng.integers(0,1<<62))<<(W-62) | int(rng.integers(0,1<<62)) if W>62 else int(rng.integers(0,1<<W))
            a&=(1<<W)-1; b&=(1<<W)-1
            if c.add(a,b)[0]!=a+b: bad+=1
        print(f'W={W}: {N} back-to-back random additions, errors={bad}')
