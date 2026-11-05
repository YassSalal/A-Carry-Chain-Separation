import numpy as np
def ccsa(a,b,W,cin):
    A=np.array([(a>>i)&1 for i in range(W)]+[0],np.int8); B=np.array([(b>>i)&1 for i in range(W)]+[0],np.int8)
    U1=A^B; L1=A&B
    def sh(v,b0=0): return np.concatenate(([b0],v[:-1]))
    R=U1&(1-sh(U1))&(1-sh(L1,cin)); Lam=(1-U1)&sh(U1)
    B2=np.zeros(W+1,np.int8); p=0
    for l in range(W+1): p=R[l]|(p&(1-Lam[l])); B2[l]=p
    E=B2&U1; U2=U1&(1-E); L2=L1|E; M=E
    U3=((1-U2)&sh(U2))|((1-sh(M))&sh(L2,cin)&(1-sh(U2))&(1-U2)); L3=L2&M
    return int(sum(int(v)<<i for i,v in enumerate(U3|L3)))
for W in (4,6,8):
    bad=sum(ccsa(a,b,W,c)!=a+b+c for a in range(1<<W) for b in range(1<<W) for c in (0,1))
    print(W,'carry-in via L1[-1] = cin: errors',bad)
