"""Exhaustive and directed verification of the CCSA normative equations (Section 7.3.1)
with carry-in injected as L1[-1] = c_in.

Bit-parallel implementation: each operand pair is one machine word per state row, bit l of the
word holding position l (0..W). For every vector it checks
  V1 = V2 = V3 = A + B + c_in,  U3 & L3 = 0,  L4 = 0,  U4 = A + B + c_in.
Usage:
  python3 verify_exhaustive.py exhaustive W CIN      (W <= 16)
  python3 verify_exhaustive.py directed             (W = 12, 16, 32, 64, 128, 256; python ints)
  python3 verify_exhaustive.py crosscheck REF_DIR   (agreement with Supp.A ccsa_ref.py, c_in = 0)
"""
import sys, time
import numpy as np

def step_all(A, B, cin, W, xp_int=False):
    """Works on numpy uint64 arrays or on Python ints (xp_int=True)."""
    MASK = (1 << (W + 1)) - 1
    if xp_int:
        mask = MASK; one = 1; zero = 0
    else:
        mask = np.uint64(MASK); one = np.uint64(1); zero = np.uint64(0)
    c = (one if cin else zero)
    # Step 1
    U1 = (A ^ B) & mask
    L1 = (A & B) & mask
    U1p = (U1 << one) & mask            # U1[l-1], U1[-1] = 0
    L1p = ((L1 << one) | c) & mask      # L1[l-1], L1[-1] = c_in
    # Step 2
    R = U1 & ~U1p & ~L1p & mask
    Lam = ~U1 & U1p & mask
    B2 = zero if xp_int else np.zeros_like(A)
    prev = zero if xp_int else np.zeros_like(A)
    for l in range(W + 1):
        bit = (one << (l if xp_int else np.uint64(l)))
        r = R & bit
        lam = Lam & bit
        p_shift = (prev << one) & bit             # B2[l-1] moved to position l
        cur = r | (p_shift & ~lam & bit)
        B2 = B2 | cur
        prev = cur
    E = B2 & U1
    U2 = U1 & ~E & mask
    L2 = (L1 | E) & mask
    M = E
    # Step 3 (shifted neighbours; L2[-1] = L1[-1] = c_in, U2[-1] = M[-1] = 0)
    U2p = (U2 << one) & mask
    L2p = ((L2 << one) | c) & mask
    Mp = (M << one) & mask
    U3 = ((~U2 & U2p) | (~Mp & L2p & ~U2p & ~U2)) & mask
    L3 = L2 & M
    # Step 4
    U4 = U3 | L3
    L4 = zero if xp_int else np.zeros_like(A)
    # values
    V1 = U1 + (L1 << one) + c
    V2 = U2 + (L2 & M) + ((L2 & ~M & mask) << one) + c
    V3 = U3 + L3
    return V1, V2, V3, U3 & L3, L4, U4

def exhaustive(W, cin, chunk_bits=22):
    assert W <= 16
    N = 1 << (2 * W)
    chunk = min(N, 1 << chunk_bits)
    t = time.time(); done = 0
    for start in range(0, N, chunk):
        idx = np.arange(start, start + chunk, dtype=np.uint64)
        A = idx >> np.uint64(W)
        B = idx & np.uint64((1 << W) - 1)
        V1, V2, V3, col, L4, U4 = step_all(A, B, cin, W)
        ref = A + B + np.uint64(cin)
        ok = (V1 == ref) & (V2 == ref) & (V3 == ref) & (col == 0) & (L4 == 0) & (U4 == ref)
        if not ok.all():
            k = int(np.argmin(ok)); print('FAIL', W, cin, int(A[k]), int(B[k])); sys.exit(1)
        done += chunk
    print(f'exhaustive W={W} c_in={cin}: {done} vectors, 0 errors, {time.time()-t:.0f} s', flush=True)

def directed_cases(W):
    ALL = (1 << W) - 1
    alt5 = int('01' * W, 2) & ALL      # ...0101
    altA = ALL ^ alt5                  # ...1010
    cases = {('all-zero', 0, 0), ('all-one', ALL, ALL), ('all-one + 0', ALL, 0), ('all-one + 1 (chain of length W)', ALL, 1),
             ('0101 + 1010', alt5, altA), ('0101 + 0101', alt5, alt5), ('1010 + 1010', altA, altA), ('0101 + 0', alt5, 0), ('1010 + 1', altA, 1)}
    lens = sorted({1, 2, 15, 16, 17, 31, 32, 33, W - 1})
    for k in range(W):
        # isolated generate (carry chain of length 1 into position k+1)
        cases.add(('isolated generate', 1 << k, 1 << k))
        for n in lens:
            if k + 1 + n > W: continue
            prop = ((1 << n) - 1) << (k + 1)
            cases.add((f'carry chain length {n}', (1 << k) | prop, 1 << k))       # generate at k, n propagates
            cases.add((f'carry-free run length {n}', prop, 0))                   # propagate run with no generate
    return sorted(cases)

def directed():
    total = 0
    for W in (12, 16, 32, 64, 128, 256):
        cs = directed_cases(W); n = 0
        for name, A, B in cs:
            for cin in (0, 1):
                V1, V2, V3, col, L4, U4 = step_all(A, B, cin, W, xp_int=True)
                ref = A + B + cin
                assert V1 == ref and V2 == ref and V3 == ref and col == 0 and L4 == 0 and U4 == ref, (W, name, A, B, cin)
                n += 1
        print(f'directed W={W}: {len(cs)} operand pairs x 2 carry-in values = {n} vectors, 0 errors')
        total += n
    print('directed total', total)

def crosscheck(ref_dir, n=20000, seed=0xCC5A):
    sys.path.insert(0, ref_dir)
    import random, ccsa_ref
    rng = random.Random(seed)
    for W in (8, 12, 16, 32, 64, 128, 256):
        for _ in range(n // 10 if W > 64 else n):
            A = rng.randrange(1 << W); B = rng.randrange(1 << W)
            S = ccsa_ref.ccsa(A, B, W)[0]
            U4 = step_all(A, B, 0, W, xp_int=True)[5]
            assert S == U4 == A + B
    print('crosscheck with ccsa_ref.py: agree')

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'exhaustive': exhaustive(int(sys.argv[2]), int(sys.argv[3]))
    elif m == 'directed': directed()
    elif m == 'crosscheck': crosscheck(sys.argv[2])
