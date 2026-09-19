"""
CCSA Variant B reference model (Algorithm 1, Section 7.3.1).
W-bit operands A, B; W+1-bit result S = A + B.

This file is the single versioned reference implementation.
It matches the normative equations of Section 7.3.1 exactly:
  - arrays are indexed 0..W (W+1 positions),
  - the virtual boundary at index -1 and index W returns 0,
  - Step 3 uses the *shifted* neighbour U2[l-1], L2[l-1], M[l-1],
  - Step 4 merges the registered Step-3 outputs U3, L3,
  - the returned sum is the full W+1-bit integer.
"""

def ccsa(A: int, B: int, W: int):
    assert 0 <= A < (1 << W) and 0 <= B < (1 << W)

    # ------------------------------------------------------------------
    # Boundary-aware accessor: index -1 -> 0, index W -> arr[W] (which is
    # held at 0 by construction), any out-of-range -> 0.
    # ------------------------------------------------------------------
    def g(arr, idx):
        if 0 <= idx < len(arr):
            return arr[idx]
        return 0

    # ------------------------------------------------------------------
    # Step 1 - vertical half-addition
    # ------------------------------------------------------------------
    U1 = [0] * (W + 1)
    L1 = [0] * (W + 1)
    for l in range(W):
        al = (A >> l) & 1
        bl = (B >> l) & 1
        U1[l] = al ^ bl          # XOR
        L1[l] = al & bl          # AND
    # U1[W] = L1[W] = 0 by boundary convention.

    # ------------------------------------------------------------------
    # Step 2 - boundary-controlled switching
    # ------------------------------------------------------------------
    B2 = [0] * (W + 1)
    E  = [0] * (W + 1)
    U2 = [0] * (W + 1)
    L2 = [0] * (W + 1)
    M  = [0] * (W + 1)

    for l in range(W + 1):
        R_l   = U1[l] & (1 - g(U1, l - 1)) & (1 - g(L1, l - 1))
        Lam_l = (1 - U1[l]) & g(U1, l - 1)
        B2[l] = R_l | (g(B2, l - 1) & (1 - Lam_l))
        E[l]  = B2[l] & U1[l]
        U2[l] = U1[l] & (1 - E[l])
        L2[l] = L1[l] | E[l]
        M[l]  = E[l]

    # ------------------------------------------------------------------
    # Step 3 - carry-chain collapse (Variant B)
    # Uses the *shifted* neighbours l-1.
    # ------------------------------------------------------------------
    U3 = [0] * (W + 1)
    L3 = [0] * (W + 1)

    for l in range(W + 1):
        U2p = g(U2, l - 1)
        L2p = g(L2, l - 1)
        Mp  = g(M,  l - 1)
        U3[l] = ((1 - U2[l]) & U2p) | \
                ((1 - Mp) & L2p & (1 - U2p) & (1 - U2[l]))
        L3[l] = L2[l] & M[l]

    # ------------------------------------------------------------------
    # Step 4 - collision-free merge
    # ------------------------------------------------------------------
    U4 = [0] * (W + 1)
    L4 = [0] * (W + 1)

    for l in range(W + 1):
        U4[l] = U3[l] | L3[l]
        L4[l] = 0

    # ------------------------------------------------------------------
    # Reconstruct the W+1-bit canonical sum.
    # ------------------------------------------------------------------
    S = 0
    for l in range(W + 1):
        S |= (U4[l] & 1) << l

    return S, U1, L1, U2, L2, M, U3, L3, U4, L4


# ----------------------------------------------------------------------
# Stage-relative invariants (Section 6.1, Remark 6.1)
# ----------------------------------------------------------------------
def V1(U, L, W):
    return sum(U[l] << l for l in range(W + 1)) + \
           sum(L[l] << (l + 1) for l in range(W + 1))


def V2(U, L, M, W):
    s = 0
    for l in range(W + 1):
        s += (U[l] << l)
        s += (L[l] & M[l]) << l
        s += (L[l] & (1 - M[l])) << (l + 1)
    return s


def V3(U, L, W):
    return sum((U[l] | L[l]) << l for l in range(W + 1))


# ----------------------------------------------------------------------
# Self-checking campaigns
# ----------------------------------------------------------------------
def check(A, B, W):
    S, U1, L1, U2, L2, M, U3, L3, U4, L4 = ccsa(A, B, W)
    assert V1(U1, L1, W) == A + B, f"V1 failed A={A} B={B} W={W}"
    assert V2(U2, L2, M, W) == A + B, f"V2 failed A={A} B={B} W={W}"
    assert V3(U3, L3, W) == A + B, f"V3 failed A={A} B={B} W={W}"
    for l in range(W + 1):
        assert (U3[l] & L3[l]) == 0, f"collision at l={l}"
    assert L4 == [0] * (W + 1)
    assert S == A + B, f"sum failed A={A} B={B} W={W} S={S}"


def exhaustive(W):
    for A in range(1 << W):
        for B in range(1 << W):
            check(A, B, W)
    print(f"Exhaustive {W}-bit campaign passed ({1 << (2*W)} vectors).")


def random_vectors(W, n, seed=0xC0FFEE):
    import random
    rng = random.Random(seed)
    for _ in range(n):
        A = rng.randrange(1 << W)
        B = rng.randrange(1 << W)
        check(A, B, W)
    print(f"Random-vector campaign W={W}, n={n} passed.")


if __name__ == "__main__":
    # Regression vectors named in the review
    check(1, 255, 8)
    check(255, 255, 8)
    check(15, 1, 4)

    exhaustive(8)
    for W in (16, 32, 64, 128, 256):
        random_vectors(W, 20000)
