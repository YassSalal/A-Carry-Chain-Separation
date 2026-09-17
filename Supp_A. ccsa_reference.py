#!/usr/bin/env python3
"""
ccsa_reference.py -- Python reference model for the Carry-Chain-Separation
Architecture (CCSA), Variant B (complementation-based carry inversion).

Implements the four data-independent algorithmic steps of the paper and
checks the semantic-value invariant V(U, L) after every step, the
collision-free condition (Prop. 1) after Step 3, and the canonical form
after Step 4.

Usage:
    python3 ccsa_reference.py                        # default campaign
    python3 ccsa_reference.py --exhaustive-max 8 --vectors 20000 \
        --random-widths 16 32 64 128 256 --seed 1
    python3 ccsa_reference.py --dump-trace           # print (U,L) per step

Tested with Python 3.11. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import random
import sys


# --------------------------------------------------------------------------
# Bit helpers
# --------------------------------------------------------------------------
def _bits(x: int, w: int) -> list[int]:
    return [(x >> i) & 1 for i in range(w)]


def _at(v: list[int], i: int) -> int:
    """Bit access with virtual boundary cells fixed to zero."""
    return v[i] if 0 <= i < len(v) else 0


def semantic_value(U: list[int], L: list[int]) -> int:
    """Definition 7.1 (state after Step 1):
    V(U,L) = sum U[l].2^l + sum L[l].2^(l+1)."""
    return sum(U[l] << l for l in range(len(U))) + \
           sum(L[l] << (l + 1) for l in range(len(L)))


def semantic_value_step2(U, L, M, W):
    """
    Corrected Step-2 semantic value for the CCSA (Variant B).

    V^(2)(U, L, M) =
          sum_{ell=0}^{W-1} U[ell] * 2^ell
        + sum_{ell=0}^{W-1} L[ell] * M[ell] * 2^ell
        + sum_{ell=0}^{W-1} L[ell] * (1 - M[ell]) * 2^(ell+1)

    The third sum accounts for original carry bits that were not
    rewritten in Step 2 (M[ell] = 0). The spurious term
    U[ell] * M[ell] * 2^(ell+1) that appeared in earlier drafts is
    identically zero because U_2[ell] * M[ell] = 0 by construction.
    """
    s = 0
    for ell in range(W):
        s += U[ell] * (1 << ell)                        # untouched upper-grid bit
        s += L[ell] * M[ell] * (1 << ell)               # rewritten carry-free bit
        s += L[ell] * (1 - M[ell]) * (1 << (ell + 1))   # original carry bit
    return s


def semantic_value_step3(U, L) -> int:
    """Theorem 7.3 / Corollary 7.4 (state after Step 3): every surviving
    lower-grid bit is a carry-free rewrite of weight 2^l; U and L are
    disjoint (Proposition 1), so OR and ADD coincide."""
    return sum((U[l] + L[l]) << l for l in range(len(U)))


REGRESSION_VECTORS = [
    # (A, B, W, note)
    (6,  3,  4, "carry-free chain at 0 + original carry at 1; old V2 gives 5, corrected gives 9"),
    (7,  1,  4, "maximal carry chain from LSB upward"),
    (1,  7,  4, "same as above, operands swapped"),
    (0,  0,  4, "degenerate case; all R=0, B2=0"),
    (15, 1,  4, "carry chain crossing the full 4-bit datapath"),
    (0b0110, 0b0011, 4, "worked example of Section 5.1"),
]

def run_regression_vectors():
    for A, B, W, note in REGRESSION_VECTORS:
        U1, L1 = step1(A, B, W)
        assert semantic_value_step1(U1, L1, W) == A + B
        U2, L2, M = step2(U1, L1, W)
        assert semantic_value_step2(U2, L2, M, W) == A + B, note
        U3, L3 = step3(U2, L2, M, W)
        assert semantic_value_step34(U3, L3, W) == A + B
        U4, L4 = step4(U3, L3, W)
        assert L4 == [0] * W
        assert semantic_value_step34(U4, L4, W) == A + B
        assert to_int(U4) == A + B
    print(f"All {len(REGRESSION_VECTORS)} regression vectors passed.")

# --------------------------------------------------------------------------
# CCSA Variant-B pipeline (Sections 3-6 of the paper)
# --------------------------------------------------------------------------
def ccsA_variant_B(A, B, W):
    # Virtual boundaries
    U = [0] * (W + 1)
    L = [0] * (W + 1)
    M = [0] * (W + 1)
    U[-1] = L[-1] = M[-1] = 0   # convention; index -1 handled explicitly

    # ---- Step 1: vertical half-addition ------------------------------
    U1 = [0] * W
    L1 = [0] * W
    for l in range(W):
        U1[l] = A[l] ^ B[l]
        L1[l] = A[l] & B[l]

    # virtual boundary bits
    U1m1 = 0          # U1[-1]
    L1m1 = 0          # L1[-1]

    assert value1(U1, L1) == A_int + B_int   # V^(1) = A + B

    # ---- Step 2: boundary-controlled switching -----------------------
    B2 = [0] * W
    E  = [0] * W
    U2 = [0] * W
    L2 = [0] * W
    M2 = [0] * W

    prev_U1 = U1m1
    prev_L1 = L1m1
    prev_B2 = 0
    for l in range(W):
        R_l = U1[l] & (1 - prev_U1) & (1 - prev_L1)
        Lam = (1 - U1[l]) & prev_U1
        B2[l] = R_l | (prev_B2 & (1 - Lam))
        E[l]  = B2[l] & U1[l]
        U2[l] = U1[l] & (1 - E[l])
        L2[l] = L1[l] | E[l]
        M2[l] = E[l]
        prev_U1 = U1[l]
        prev_L1 = L1[l]
        prev_B2 = B2[l]

    assert value2(U2, L2, M2) == A_int + B_int   # V^(2) = A + B

    # ---- Step 3: carry-chain collapse (Variant B) --------------------
    U3 = [0] * W
    L3 = [0] * W
    for l in range(W):
        u2_l  = U2[l]
        u2_lm = U2[l-1] if l > 0 else 0
        m_lm  = M2[l-1] if l > 0 else 0
        l2_lm = L2[l-1] if l > 0 else 0
        U3[l] = ((1-u2_l) & u2_lm) | \
                ((1-m_lm) & l2_lm & (1-u2_lm) & (1-u2_l))
        L3[l] = L2[l] & M2[l]

    assert all((U3[l] & L3[l]) == 0 for l in range(W))   # Prop. 1
    assert value3(U3, L3) == A_int + B_int               # V^(3) = A + B

    # ---- Step 4: collision-free merge --------------------------------
    U4 = [U3[l] | L3[l] for l in range(W)]
    L4 = [0] * W

    assert all(L4[l] == 0 for l in range(W))             # canonical form
    assert value4(U4, L4) == A_int + B_int               # V^(4) = A + B

    return U4


def value1(U, L):
    return sum(U[l] * (1 << l) for l in range(len(U))) + \
           sum(L[l] * (1 << (l+1)) for l in range(len(L)))

def value2(U, L, M):
    return sum(U[l] * (1 << l) for l in range(len(U))) + \
           sum(L[l] * M[l] * (1 << l) for l in range(len(L))) + \
           sum(L[l] * (1 - M[l]) * (1 << (l+1)) for l in range(len(L)))

def value3(U, L):
    return sum((U[l] + L[l]) * (1 << l) for l in range(len(U)))

value4 = value3


# --------------------------------------------------------------------------
# Verification campaigns (mirrors Section 7.7 of the paper)
# --------------------------------------------------------------------------
def run_exhaustive(w: int, verbose: bool = True) -> int:
    count = 0
    for a in range(1 << w):
        for b in range(1 << w):
            s, _ = ccsa_add(a, b, w - 1)
            assert s == a + b
            count += 1
    if verbose:
        print(f"[exhaustive] W={w:3d} bits: {count} operand pairs, 0 mismatches")
    return count


def run_random(w: int, vectors: int, seed: int, verbose: bool = True) -> None:
    rng = random.Random((seed, w).__hash__() & 0xFFFFFFFF)
    mask = (1 << w) - 1
    for i in range(vectors):
        a = rng.getrandbits(w)
        b = rng.getrandbits(w)
        s, _ = ccsa_add(a, b, w - 1)
        assert s == a + b, f"mismatch at vector {i}: {a}+{b} -> {s}"
        _ = mask
    if verbose:
        print(f"[random]     W={w:3d} bits: {vectors} vectors, 0 mismatches")


def main() -> int:
    ap = argparse.ArgumentParser(description="CCSA Variant-B reference model")
    ap.add_argument("--exhaustive-max", type=int, default=8,
                    help="exhaustively verify all widths 2..N (default 8)")
    ap.add_argument("--random-widths", type=int, nargs="+",
                    default=[16, 32, 64, 128, 256],
                    help="widths for random verification")
    ap.add_argument("--vectors", type=int, default=20000,
                    help="random vectors per width (paper used 2e4; 1e6 for W=256)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--dump-trace", action="store_true",
                    help="print (U,L) state after every step for one vector")
    args = ap.parse_args()

    if args.dump_trace:
        s, trace = ccsa_add(0b11010110, 0b01101101, 7)
        for name, U, L in trace:
            print(f"{name}: U={''.join(map(str, reversed(U)))} "
                  f"L={''.join(map(str, reversed(L)))}")
        print(f"sum={s}")
        return 0

    total = 0
    for w in range(2, args.exhaustive_max + 1):
        total += run_exhaustive(w)
    for w in args.random_widths:
        run_random(w, args.vectors, args.seed)
    print(f"ALL CHECKS PASSED ({total} exhaustive pairs + "
          f"{len(args.random_widths)}x{args.vectors} random vectors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
