"""
CCSA Variant B - Python reference model.
Implements Algorithm 1 of the manuscript exactly, with the corrected
stage-relative invariants V1, V2, V3.

All indices use 0 as LSB; virtual boundary at -1 and W is 0.
"""

from typing import Tuple, List

# ---------------------------------------------------------------
# Virtual boundary conventions
# ---------------------------------------------------------------
def _get(vec: List[int], idx: int) -> int:
    """Read vec[idx] with virtual zero at idx<0 and idx>=len(vec)."""
    if idx < 0 or idx >= len(vec):
        return 0
    return vec[idx]


# ---------------------------------------------------------------
# Stage 1: vertical half-addition
# ---------------------------------------------------------------
def step1(A: List[int], B: List[int]) -> Tuple[List[int], List[int]]:
    W = len(A)
    U1 = [A[l] ^ B[l] for l in range(W)]
    L1 = [A[l] & B[l] for l in range(W)]
    return U1, L1


# ---------------------------------------------------------------
# Stage 2: boundary-controlled switching
# ---------------------------------------------------------------
def step2(U1: List[int], L1: List[int]):
    W = len(U1)
    R    = [0] * W
    Lam  = [0] * W
    B2   = [0] * W
    E    = [0] * W
    U2   = [0] * W
    L2   = [0] * W
    M    = [0] * W

    # 3-input boundary detectors
    for l in range(W):
        R[l]   = U1[l] & (1 - _get(U1, l - 1)) & (1 - _get(L1, l - 1))
        Lam[l] = (1 - U1[l]) & _get(U1, l - 1)

    # Bus 2 propagation, LSB -> MSB
    for l in range(W):
        prev = B2[l - 1] if l > 0 else 0
        B2[l] = R[l] | (prev & (1 - Lam[l]))

    # Local rewrite enable
    for l in range(W):
        E[l] = B2[l] & U1[l]

    # Post-switch grids and registered marker
    for l in range(W):
        U2[l] = U1[l] & (1 - E[l])
        L2[l] = L1[l] | E[l]
        M[l]  = E[l]

    return U2, L2, M, R, Lam, B2


# ---------------------------------------------------------------
# Stage 3: carry-chain collapse (Variant B)
# ---------------------------------------------------------------
def step3(U2: List[int], L2: List[int], M: List[int]):
    W = len(U2)
    U3 = [0] * W
    L3 = [0] * W
    for l in range(W):
        term1 = (1 - U2[l]) & _get(U2, l - 1)
        term2 = ((1 - _get(M, l - 1)) & _get(L2, l - 1)
                 & (1 - _get(U2, l - 1)) & (1 - U2[l]))
        U3[l] = term1 | term2
        L3[l] = L2[l] & M[l]
    return U3, L3


# ---------------------------------------------------------------
# Stage 4: collision-free merge
# ---------------------------------------------------------------
def step4(U3: List[int], L3: List[int]):
    W = len(U3)
    U4 = [U3[l] | L3[l] for l in range(W)]
    L4 = [0] * W
    return U4, L4


# ---------------------------------------------------------------
# Stage-relative semantic invariants
# ---------------------------------------------------------------
def V1(U: List[int], L: List[int]) -> int:
    return sum(U[l] << l for l in range(len(U))) + \
           sum(L[l] << (l + 1) for l in range(len(L)))


def V2(U: List[int], L: List[int], M: List[int]) -> int:
    return (sum(U[l] << l for l in range(len(U)))
            + sum(L[l] * M[l] << l for l in range(len(L)))
            + sum(L[l] * (1 - M[l]) << (l + 1) for l in range(len(L))))


def V3(U: List[int], L: List[int]) -> int:
    return sum((U[l] + L[l]) << l for l in range(len(U)))


# ---------------------------------------------------------------
# Full CCSA
# ---------------------------------------------------------------
def ccsa_add(A: int, B: int, W: int) -> int:
    a = [(A >> l) & 1 for l in range(W)]
    b = [(B >> l) & 1 for l in range(W)]

    U1, L1 = step1(a, b)
    assert V1(U1, L1) == A + B, "V1 invariant violated"

    U2, L2, M, *_ = step2(U1, L1)
    assert V2(U2, L2, M) == A + B, "V2 invariant violated"

    U3, L3 = step3(U2, L2, M)
    assert V3(U3, L3) == A + B, "V3 invariant violated"
    for l in range(W):
        assert (U3[l] & L3[l]) == 0, "collision-freeness violated"

    U4, L4 = step4(U3, L3)
    assert all(L4[l] == 0 for l in range(W)), "L4 not zeroed"
    assert V3(U4, L4) == A + B, "V4 invariant violated"

    return sum(U4[l] << l for l in range(W))


# ---------------------------------------------------------------
# Exhaustive 8-bit campaign
# ---------------------------------------------------------------
if __name__ == "__main__":
    W = 8
    for a in range(1 << W):
        for b in range(1 << W):
            s = ccsa_add(a, b, W)
            expected = (a + b) & ((1 << W) - 1)
            # Note: with virtual zero at W the final carry is lost, which
            # is the expected W-bit truncation. Widen by one bit if the
            # carry-out must be preserved.
            assert s == expected, f"FAIL A={a} B={b} got {s} exp {expected}"
    print("Exhaustive 8-bit: PASS (65,536 pairs)")

    # Regression vectors
    regressions = [(7, 1, 8), (255, 255, 8), (0, 0, 16),
                   (0xAAAA, 0x5555, 16), (12345, 67890, 32)]
    for a, b, w in regressions:
        s = ccsa_add(a, b, w)
        assert s == ((a + b) & ((1 << w) - 1)), f"regression fail {a}+{b}@{w}"
    print("Regression vectors: PASS")

    # Random vectors up to 256 bits
    import random
    random.seed(0xC0FFEE)
    for w in [16, 32, 64, 128, 256]:
        for _ in range(2000):
            a = random.getrandbits(w)
            b = random.getrandbits(w)
            s = ccsa_add(a, b, w)
            assert s == ((a + b) & ((1 << w) - 1)), f"random fail {w}"
    print("Random vectors to 256 bits: PASS")
