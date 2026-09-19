#!/usr/bin/env python3
"""
E6_tables_1_2_1_3.py — reproduces the electrical tables of the CCSA
manuscript (Appendix A Table 1.1, Appendix B Tables 1.2 and 1.3).

Usage
-----
    python E6_tables_1_2_1_3.py --out tables/ --verify
    python E6_tables_1_2_1_3.py --out tables/ --T-clk 1.00 1.22 1.50 2.00
    python E6_tables_1_2_1_3.py --out tables/ --verbose --verify

Exit status
-----------
    0   all requested tables written and (if --verify) all canonical
        values matched the manuscript
    1   one or more verifications failed
"""

from __future__ import annotations
import argparse
import csv
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path


# =============================================================================
# 1.  Parameters (Section 1.3.C, Section 7.5.1, Appendix B)
# =============================================================================
#
# Sources are documented in the "note" field of every entry.  The two
# quantities R_0 and C_0 are NOT printed in the manuscript; they are
# inferred here so that the published derived value
#
#     R_series = R_driver + R_VSW + k * R_HSW = 4.1 kΩ
#     t_seg    = 2.34 τ
#
# is reproduced exactly.  This is stated explicitly so the reader knows
# which numbers are primary and which are derived.
# =============================================================================

@dataclass
class Params:
    # --- unit ---------------------------------------------------------------
    tau_ps: float = 12.0                 # min 2-input NAND, ASAP7, 7 nm

    # --- design constants ---------------------------------------------------
    k: int = 16                          # repeater pitch (bits)
    s: int = 8                           # driver scale factor

    # --- transmission-gate on-resistances (ASAP7 7 nm, TT/25 °C, W = 1 µm) --
    R_HSW_ohm: float = 220.0
    R_VSW_ohm: float = 280.0

    # --- min-inverter primitives (inferred; see header note) ----------------
    R_0_ohm: float = 2400.0              # yields R_series = 4100 Ω
    C_0_fF:  float = 0.301               # yields t_seg  = 2.340 τ

    # --- local parasitics ---------------------------------------------------
    C_keeper_fF: float = 0.5
    C_tap_fF:    float = 0.5

    # --- M13 interconnect (Section 7.5.1) -----------------------------------
    r_v_ohm_per_um: float = 0.15
    c_v_fF_per_um:  float = 0.20
    delta_x_um:     float = 0.80         # bit-slice pitch

    # --- sense / level restore ---------------------------------------------
    t_sense_tau:         float = 0.5
    t_level_restore_tau: float = 0.3

    # --- non-bus timing budget (Section 1.3.F.1) ----------------------------
    t_det_tau:   float = 3.0             # 3-input boundary detector
    t_rw_tau:    float = 2.0             # rewrite gate
    t_setup_tau: float = 0.5             # DFF setup
    t_skew_tau:  float = 0.5             # bounded clock skew


# =============================================================================
# 2.  Derived quantities
# =============================================================================

@dataclass
class Derived:
    R_driver_ohm:   float
    R_series_ohm:   float
    C_rep_fF:       float
    C_wire_slice_fF: float
    C_wire_seg_fF:   float
    R_wire_slice_ohm: float
    R_wire_seg_ohm:   float
    t_seg_tau:       float
    t_seg_ps:        float
    t_bus_slope_tau: float     # ≈ 2.34
    t_bus_offset_tau: float    # ≈ 0.5
    t_step2_overhead_tau: float # ≈ 5.5


def derive(p: Params) -> Derived:
    """Evaluate the Elmore expression of Section 1.3.C once."""
    R_driver = p.R_0_ohm / p.s
    R_series = R_driver + p.R_VSW_ohm + p.k * p.R_HSW_ohm

    C_rep       = p.s * p.C_0_fF
    C_wire_slc  = p.c_v_fF_per_um * p.delta_x_um
    C_wire_seg  = C_wire_slc * p.k
    R_wire_slc  = p.r_v_ohm_per_um * p.delta_x_um
    R_wire_seg  = R_wire_slc * p.k

    # t_seg = R_series · C_sum + R_wire · C_half + t_level_restore
    # (ohm · fF = ps by construction: 1 Ω · 1 fF = 1 ps)
    C_sum  = C_wire_seg + p.C_tap_fF + p.C_keeper_fF + C_rep
    C_half = C_wire_seg / 2.0 + p.C_tap_fF + p.C_keeper_fF + C_rep

    t_seg_ps = (
        R_series * C_sum * 1e-3
        + R_wire_seg * C_half * 1e-3
        + p.t_level_restore_tau * p.tau_ps
    )
    t_seg_tau = t_seg_ps / p.tau_ps

    return Derived(
        R_driver_ohm       = R_driver,
        R_series_ohm       = R_series,
        C_rep_fF           = C_rep,
        C_wire_slice_fF    = C_wire_slc,
        C_wire_seg_fF      = C_wire_seg,
        R_wire_slice_ohm   = R_wire_slc,
        R_wire_seg_ohm     = R_wire_seg,
        t_seg_tau          = t_seg_tau,
        t_seg_ps           = t_seg_ps,
        t_bus_slope_tau    = t_seg_tau,
        t_bus_offset_tau   = p.t_sense_tau,
        t_step2_overhead_tau = p.t_det_tau + p.t_sense_tau + p.t_rw_tau,
    )


# =============================================================================
# 3.  Segment count and bus delay
# =============================================================================
#
# Corrected convention (Section 1.3.F.1):
#
#     m(W) = floor((W - 1) / k) + 1 ,   W ≥ 1 ;   m(0) = 0
#
# The simpler expression floor(W/k) + 1 overcounts by one when W is an
# exact multiple of k, which is why the manuscript uses the corrected
# form everywhere for timing, W_max, and bus-capacitance calculations.
# =============================================================================

def m_segments(W: int, k: int) -> int:
    if W <= 0:
        return 0
    return (W - 1) // k + 1


def t_bus_tau(W: int, p: Params, d: Derived) -> float:
    return d.t_bus_slope_tau * m_segments(W, p.k) + d.t_bus_offset_tau


def t_step2_tau(W: int, p: Params, d: Derived) -> float:
    return t_bus_tau(W, p, d) + d.t_step2_overhead_tau


def c_bus_tau(T_clk_ns: float, p: Params) -> float:
    """Available bus budget in units of τ (Section 1.3.F.1)."""
    T_ps = T_clk_ns * 1000.0
    overhead_ps = (
        p.t_det_tau + p.t_rw_tau + p.t_setup_tau + p.t_skew_tau
    ) * p.tau_ps
    return (T_ps - overhead_ps) / p.tau_ps


def W_max(T_clk_ns: float, p: Params, d: Derived, W_hi: int = 8192) -> int:
    """Largest W with t_bus(W) ≤ c_bus(T_clk) · τ."""
    budget = c_bus_tau(T_clk_ns, p)
    lo, hi = 0, W_hi
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if t_bus_tau(mid, p, d) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return lo


# =============================================================================
# 4.  Table 1.1 — Notation (Appendix A)
# =============================================================================

TABLE_1_1 = [
    ("W",               "Operand width in bits",                                "parameter",   "-"),
    ("l",               "Generic bit index, 0 ≤ l ≤ W-1",                       "index",       "-"),
    ("j",               "LSB index of a chain",                                 "index",       "Sec. 4, 6.2"),
    ("i",               "MSB index of a chain",                                 "index",       "Sec. 4, 6.2"),
    ("N_cyc",           "Number of algorithmic stages",                         "structural",  "4 (→3)"),
    ("T_clk",           "Clock period ≥ max{t_step} + t_setup + t_skew",        "tech-dep",    "-"),
    ("t_add",           "Total addition latency = N_cyc · T_clk",               "stage-limited","-"),
    ("t",               "Min-size 2-input NAND delay",                          "tech",        "≈12 ps"),
    ("k",               "Repeater pitch (bit positions)",                       "design",      "16"),
    ("s",               "Driver scale factor",                                  "design",      "8"),
    ("R_HSW",           "HSW transmission-gate on-resistance",                  "tech",        "≈220 Ω"),
    ("R_VSW",           "VSW transmission-gate on-resistance",                  "tech",        "≈280 Ω"),
    ("C_keeper",        "Keeper gate capacitance",                              "tech",        "≈0.5 fF"),
    ("t_level_restore", "Level-restore delay",                                  "tech",        "≈0.3 τ"),
]


# =============================================================================
# 5.  Writers
# =============================================================================

def write_table_1_1(out: Path) -> None:
    with (out / "table_1_1_notation.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Symbol", "Meaning", "Type", "Value / Units"])
        w.writerows(TABLE_1_1)


def write_table_1_2(out: Path, p: Params, d: Derived) -> None:
    rows = [
        ("Unit delay",                       "t",             p.tau_ps,                "ps",    "7-nm min NAND2, ASAP7"),
        ("Repeater pitch",                   "k",             p.k,                     "bits",  "design constant"),
        ("Driver scale factor",              "s",             p.s,                     "ratio", "design constant"),
        ("Min-inverter resistance",          "R_0",           p.R_0_ohm,               "Ω",     "inferred (see header note)"),
        ("Min-inverter capacitance",         "C_0",           p.C_0_fF,                "fF",    "inferred (see header note)"),
        ("Driver output resistance",         "R_driver",      d.R_driver_ohm,          "Ω",     "R_0 / s"),
        ("HSW on-resistance",                "R_HSW",         p.R_HSW_ohm,             "Ω",     "ASAP7 TT/25 °C, W = 1 µm"),
        ("VSW on-resistance",                "R_VSW",         p.R_VSW_ohm,             "Ω",     "ASAP7 TT/25 °C, W = 1 µm"),
        ("Series resistance per segment",    "R_series",      d.R_series_ohm,          "Ω",     "R_driver + R_VSW + k·R_HSW"),
        ("Wire resistance (per bit-slice)",  "R_wire_slice",  d.R_wire_slice_ohm,      "Ω",     "r_v · Δx"),
        ("Wire resistance (per segment)",    "R_wire_seg",    d.R_wire_seg_ohm,        "Ω",     "r_v · k · Δx"),
        ("Wire capacitance (per bit-slice)", "C_wire_slice",  d.C_wire_slice_fF,       "fF",    "c_v · Δx"),
        ("Wire capacitance (per segment)",   "C_wire_seg",    d.C_wire_seg_fF,         "fF",    "c_v · k · Δx"),
        ("Keeper gate capacitance",          "C_keeper",      p.C_keeper_fF,           "fF",    "design estimate"),
        ("Local tap capacitance",            "C_tap",         p.C_tap_fF,              "fF",    "design estimate"),
        ("Repeater input capacitance",       "C_rep",         d.C_rep_fF,              "fF",    "s · C_0"),
        ("Level-restore delay",              "t_L",           p.t_level_restore_tau,   "τ",     "design estimate"),
        ("Bus sense-receiver delay",         "t_sense",       p.t_sense_tau,           "τ",     "Section 1.3.C"),
        ("Segment Elmore delay",             "t_seg",         d.t_seg_tau,             "τ",     "Section 1.3.C"),
        ("Segment Elmore delay",             "t_seg",         d.t_seg_ps,              "ps",    "= t_seg_tau · τ"),
        ("Boundary detector delay",          "t_det",         p.t_det_tau,             "τ",     "3-input comb. net"),
        ("Rewrite gate delay",               "t_rw",          p.t_rw_tau,              "τ",     "Section 7.6"),
        ("DFF setup time",                   "t_setup",       p.t_setup_tau,           "τ",     "Section 1.3.A"),
        ("Clock skew",                       "t_skew",        p.t_skew_tau,            "τ",     "bounded skew"),
        ("Interconnect r_v",                 "r_v",           p.r_v_ohm_per_um,        "Ω/µm",  "M13 top copper"),
        ("Interconnect c_v",                 "c_v",           p.c_v_fF_per_um,         "fF/µm", "M13 top copper"),
        ("Bit-slice pitch",                  "Δx",            p.delta_x_um,            "µm",    "Section 7.5.1"),
    ]
    with (out / "table_1_2_parameters.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Quantity", "Symbol", "Value", "Units", "Source / Note"])
        for r in rows:
            w.writerow(r)


def write_table_1_3(out: Path, p: Params, d: Derived, T_clk_ns: float) -> None:
    cbus = c_bus_tau(T_clk_ns, p)
    Wmax = W_max(T_clk_ns, p, d)
    fname = f"table_1_3_T{int(round(T_clk_ns * 1000))}ps.csv"
    with (out / fname).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"# Target clock T_clk = {T_clk_ns:.2f} ns  "
                    f"(c_bus = {cbus:.1f} τ;  W_max = {Wmax})"])
        w.writerow(["W", "m(W)", "t_bus/τ", "t_step2/τ", "Within modeled regime?"])
        widths = [8, 16, 32, 64, 128, 256, 512, 608, 624, 640, Wmax, Wmax + 1]
        seen = set()
        for W in widths:
            if W in seen or W < 1:
                continue
            seen.add(W)
            m  = m_segments(W, p.k)
            tb = t_bus_tau(W, p, d)
            ts = t_step2_tau(W, p, d)
            ok = "Yes" if tb <= cbus else "No"
            w.writerow([W, m, f"{tb:.2f}", f"{ts:.2f}", ok])


# =============================================================================
# 6.  Self-verification against the manuscript
# =============================================================================

def verify(p: Params, d: Derived) -> int:
    errs = 0

    def chk(label: str, got: float, exp: float, tol: float = 0.02) -> None:
        nonlocal errs
        ok = abs(got - exp) / max(abs(exp), 1e-9) <= tol
        mark = "OK " if ok else "BAD"
        print(f"  [{mark}] {label:<38} got={got:>10.4f}   exp={exp:>10.4f}")
        if not ok:
            errs += 1

    print("Verifying against canonical manuscript values:")

    # Section 1.3.C and 1.3.F
    chk("R_series  [Ω]",               d.R_series_ohm,     4100.0, 0.01)
    chk("R_wire    per segment [Ω]",   d.R_wire_seg_ohm,   1.92,   0.05)
    chk("C_wire    per segment [fF]",  d.C_wire_seg_fF,    2.56,   0.05)
    chk("t_seg     [τ]",               d.t_seg_tau,        2.34,   0.02)

    # Section 1.3.F.2 / F.3
    chk("c_bus @ T_clk = 1.00 ns",     c_bus_tau(1.00, p), 77.3,   0.01)
    chk("c_bus @ T_clk = 1.22 ns",     c_bus_tau(1.22, p), 95.7,   0.01)
    chk("c_bus @ T_clk = 1.50 ns",     c_bus_tau(1.50, p), 119.0,  0.01)
    chk("c_bus @ T_clk = 2.00 ns",     c_bus_tau(2.00, p), 160.7,  0.01)

    chk("W_max   @ T_clk = 1.00 ns",   float(W_max(1.00, p, d)),  512.0,  0.001)
    chk("W_max   @ T_clk = 1.22 ns",   float(W_max(1.22, p, d)),  640.0,  0.001)
    chk("W_max   @ T_clk = 1.50 ns",   float(W_max(1.50, p, d)),  800.0,  0.001)
    chk("W_max   @ T_clk = 2.00 ns",   float(W_max(2.00, p, d)),  1088.0, 0.001)

    print("\nSpot checks on Table 1.3 rows:")
    for W, m_exp, tb_exp in [
        (8, 1, 2.84), (16, 1, 2.84), (32, 2, 5.18), (64, 4, 9.86),
        (128, 8, 19.22), (256, 16, 37.94), (512, 32, 75.38),
        (640, 40, 94.10), (641, 41, 96.44),
    ]:
        chk(f"m({W:>3})",             float(m_segments(W, p.k)), float(m_exp),  1e-6)
        chk(f"t_bus({W:>3}) / τ",     t_bus_tau(W, p, d),        tb_exp,         0.01)

    return errs


# =============================================================================
# 7.  CLI
# =============================================================================

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="tables",
                    help="output directory (default: tables)")
    ap.add_argument("--T-clk", nargs="+", type=float,
                    default=[1.00, 1.22, 1.50, 2.00],
                    help="target clock periods in ns (default: 1.00 1.22 1.50 2.00)")
    ap.add_argument("--verify", action="store_true",
                    help="assert every canonical value against the manuscript")
    ap.add_argument("--verbose", action="store_true",
                    help="print the full parameter/derived dictionaries")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    p = Params()
    d = derive(p)

    print(f"τ = {p.tau_ps} ps   k = {p.k}   s = {p.s}")
    print(f"R_driver = {d.R_driver_ohm:.1f} Ω   R_series = {d.R_series_ohm:.1f} Ω")
    print(f"C_rep = {d.C_rep_fF:.3f} fF   C_wire_seg = {d.C_wire_seg_fF:.3f} fF")
    print(f"t_seg = {d.t_seg_ps:.3f} ps = {d.t_seg_tau:.4f} τ")
    print(f"t_bus(W)/τ   = {d.t_bus_slope_tau:.4f} · m(W) + {d.t_bus_offset_tau:.3f}")
    print(f"t_step2(W)/τ = {d.t_bus_slope_tau:.4f} · m(W) + {d.t_step2_overhead_tau:.3f}")
    print()

    if args.verbose:
        print("Params:")
        for k_, v_ in asdict(p).items():
            print(f"  {k_:<24} = {v_}")
        print("Derived:")
        for k_, v_ in asdict(d).items():
            print(f"  {k_:<24} = {v_}")
        print()

    print(f"Table 1.1  ->  {out}/table_1_1_notation.csv")
    write_table_1_1(out)

    print(f"Table 1.2  ->  {out}/table_1_2_parameters.csv")
    write_table_1_2(out, p, d)

    for T in args.T_clk:
        cbus = c_bus_tau(T, p)
        Wmax = W_max(T, p, d)
        fname = f"table_1_3_T{int(round(T * 1000))}ps.csv"
        print(f"Table 1.3  T_clk = {T:.2f} ns  (c_bus = {cbus:.1f} τ, "
              f"W_max = {Wmax:>5d})  ->  {out}/{fname}")
        write_table_1_3(out, p, d, T)

    # Provenance file
    (out / "PROVENANCE.txt").write_text(
        "Generated by E6_tables_1_2_1_3.py\n"
        f"tau   = {p.tau_ps} ps\n"
        f"k     = {p.k}\n"
        f"s     = {p.s}\n"
        f"R_0   = {p.R_0_ohm} ohm    (inferred; yields R_series = 4.1 kΩ)\n"
        f"C_0   = {p.C_0_fF} fF      (inferred; yields t_seg = 2.34 τ)\n"
        f"t_seg = {d.t_seg_tau:.4f} tau = {d.t_seg_ps:.3f} ps\n"
        "All values computed from the Elmore expression of Section 1.3.C.\n"
        "Model prediction only — not FPGA-validated, not post-layout extracted.\n"
    )

    if args.verify:
        print()
        errs = verify(p, d)
        print()
        if errs:
            print(f"FAILED: {errs} mismatches")
            return 1
        print("ALL CANONICAL VALUES MATCH THE MANUSCRIPT.")

    return 0


if __name__ == "__main__":
    sys.exit(main())