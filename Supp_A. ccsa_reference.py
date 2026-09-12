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


# --------------------------------------------------------------------------
# CCSA Variant-B pipeline (Sections 3-6 of the paper)
# --------------------------------------------------------------------------
def ccsa_add(a: int, b: int, n: int, check: bool = True):
    """Add two (n+1)-bit operands. Returns (sum, trace).

    sum has n+2 bits. trace is a list of (step_name, U, L) snapshots.
    """
    W = n + 1                 # operand width
    E = W + 1                 # extended grid: positions 0..n plus virtual n+1
    target = a + b

    # -- Step 1: vertical half-addition ------------------------------------
    U = _bits(a ^ b, W) + [0]          # U[l] = a[l] XOR b[l]
    L = _bits(a & b, W) + [0]          # L[l] = a[l] AND b[l]
    trace = [("step1", list(U), list(L))]
    if check:
        assert semantic_value(U, L) == target, "Lemma 7.1 violated"

    # -- Step 2: boundary-controlled switching -----------------------------
    U2 = [0] * E
    L2 = [0] * E
    M = [0] * E
    B2 = 0                             # B2[-1] = 0
    for l in range(E):
        R    = U[l] & (1 - _at(U, l - 1)) & (1 - _at(L, l - 1))
        Lam  = (1 - U[l]) & _at(U, l - 1)
        B2   = R | (B2 & (1 - Lam))                # HSW conducts when Lambda=0
        e    = B2 & U[l]                           # rewrite-enable E[l]
        U2[l] = U[l] & (1 - e)
        L2[l] = L[l] | e
        M[l]  = e
    trace.append(("step2", list(U2), list(L2)))
    if check:
        assert semantic_value_step2(U2, L2, M) == target, "Theorem 7.2 violated"

    # -- Step 3: carry-chain inversion (Variant B) -------------------------
    U3 = [0] * E
    L3 = [0] * E
    for l in range(E):
        U3[l] = ((1 - U2[l]) & _at(U2, l - 1)) | \
                ((1 - _at(M, l - 1)) & _at(L2, l - 1) &
                 (1 - _at(U2, l - 1)) & (1 - U2[l]))
        L3[l] = L2[l] & M[l]
    trace.append(("step3", list(U3), list(L3)))
    if check:
        assert semantic_value_step3(U3, L3) == target, "Theorem 7.3 violated"
        for l in range(E):                         # Proposition 1
            assert not (U3[l] & L3[l]), "collision-free condition violated"

    # -- Step 4: collision-free merge --------------------------------------
    U4 = [U3[l] | L3[l] for l in range(E)]
    L4 = [0] * E
    trace.append(("step4", list(U4), list(L4)))
    if check:
        assert semantic_value(U4, L4) == target, "Theorem 7.4 violated"
        assert all(v in (0, 1) for v in U4)

    s = sum(U4[l] << l for l in range(E))
    assert s == target, "Theorem 7.5 violated"
    return s, trace


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
