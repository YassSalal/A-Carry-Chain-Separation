#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supp.F/fpga_reports/collate.py

Collate raw Vivado 2023.2 reports (Artix-7 XC7A100T-1CSG324C) into the
CSVs backing Tables 10, 11 and 12 of the CCSA manuscript.

Directory layout expected:

    Supp.F/fpga_reports/raw/
        <arch>_w<W>_timing.rpt
        <arch>_w<W>_util.rpt
        <arch>_w<W>_power.rpt

where <arch> is one of:
    ccsa, manchester_ripple, manchester_static, carry_skip,
    ks_pipelined, ks_comb, carry4_ripple, carry4_pipelined

and <W> in {8, 16, 32, 64, 128, 256}.

Usage:
    python3 collate.py --raw Supp.F/fpga_reports/raw \
                       --out Supp.F/fpga_reports/tables

Author: CCSA reproducibility package
License: MIT
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Architectural metadata
# ---------------------------------------------------------------------------
# N_cyc: structural cycle count of the design (see Section 1.2).
#   - CCSA         : 4
#   - Manchester   : 1 (combinational)
#   - Carry-skip   : 1 (combinational)
#   - K-S comb     : 1 (combinational)
#   - K-S pipelined: 1 + ceil(log2(W))
#   - CARRY4 ripple: 1 (combinational)
#   - CARRY4 pipe  : ceil(W/4) (one CARRY4 slice per cycle) — matches
#                    manuscript values 3, 5, 9, 17, 33, 65 for W = 8..256
# is_pipelined: whether throughput = 1 / T_clk (True) or 1 / latency (False).

ARCH_META: Dict[str, Dict] = {
    "ccsa":              {"n_cyc": lambda W: 4,                     "pipelined": False, "clocked": True},
    "manchester_ripple": {"n_cyc": lambda W: 1,                     "pipelined": False, "clocked": False},
    "manchester_static": {"n_cyc": lambda W: 1,                     "pipelined": False, "clocked": False},
    "carry_skip":        {"n_cyc": lambda W: 1,                     "pipelined": False, "clocked": False},
    "ks_pipelined":      {"n_cyc": lambda W: 1 + (W - 1).bit_length(), "pipelined": True, "clocked": True},
    "ks_comb":           {"n_cyc": lambda W: 1,                     "pipelined": False, "clocked": False},
    "carry4_ripple":     {"n_cyc": lambda W: 1,                     "pipelined": False, "clocked": False},
    "carry4_pipelined":  {"n_cyc": lambda W: (W + 3) // 4,          "pipelined": True,  "clocked": True},
}

WIDTHS = [8, 16, 32, 64, 128, 256]


# ---------------------------------------------------------------------------
# 2. Corrected bus-delay model (Section 7.4 / Section 1.3.F.3)
# ---------------------------------------------------------------------------
def segment_count(W: int, k: int = 16) -> int:
    """Corrected segment-count convention from Section 1.3.F.1."""
    if W <= 0:
        return 0
    return (W - 1) // k + 1


def bus_delay_tau(W: int, k: int = 16, t_seg_tau: float = 2.34,
                  t_sense_tau: float = 0.5) -> float:
    """
    Return t_bus(W) / tau under the corrected segment model.

    From Section 7.4:
        t_bus(W)/tau = 2.34 * m(W) + 0.5
    with m(W) = floor((W-1)/k) + 1.
    """
    m = segment_count(W, k)
    return t_seg_tau * m + t_sense_tau          # <- no stray text here


def w_max_for_budget(c_bus_tau: float, k: int = 16,
                     t_seg_tau: float = 2.34, t_sense_tau: float = 0.5) -> int:
    """Largest W with bus_delay_tau(W) <= c_bus_tau."""
    W = 1
    while bus_delay_tau(W + 1, k, t_seg_tau, t_sense_tau) <= c_bus_tau:
        W += 1
    return W


# ---------------------------------------------------------------------------
# 3. Vivado report parsers
# ---------------------------------------------------------------------------
@dataclass
class Row:
    arch: str
    W: int
    n_cyc: int
    t_clk_ns: Optional[float] = None          # post-route T_clk
    latency_ns: Optional[float] = None
    throughput_mops: Optional[float] = None
    luts: Optional[int] = None
    ffs: Optional[int] = None
    carry4: Optional[int] = None
    muxf7: Optional[int] = None
    muxf8: Optional[int] = None
    lutram: Optional[int] = None
    equiv_luts: Optional[int] = None
    power_mw: Optional[float] = None
    adp: Optional[float] = None
    edp: Optional[float] = None
    notes: List[str] = field(default_factory=list)


_NUM_RE = re.compile(r"([-\d.]+)")


def _first_number(line: str) -> Optional[float]:
    m = _NUM_RE.search(line)
    return float(m.group(1)) if m else None


def parse_timing(path: Path, W: int, n_cyc: int) -> Dict[str, float]:
    """
    Extract post-route WNS and T_clk from a Vivado 'report_timing_summary'
    .rpt file.

    We look for the line:
        WNS(ns)      TNS(ns)  TNS Failing Endpoints  ...
        -------      -------  ---------------------
        <WNS>        <TNS>    ...
    and, if a clock period is also reported, for:
        Clock Summary / <name> / <period>

    For combinational designs (no clock), WNS is negative and
    T_clk = |WNS| (the critical-path delay).
    """
    out: Dict[str, float] = {}
    text = path.read_text(errors="replace")

    # --- Try the "WNS" summary block ---
    wns_match = re.search(
        r"WNS\(ns\).*?\n\s*-+\s*\n\s*([-\d.]+)", text, re.DOTALL
    )
    if wns_match:
        out["wns_ns"] = float(wns_match.group(1))

    # --- Try to find an explicit clock period ---
    clk_match = re.search(
        r"^\s*\S+\s+\{\S+\}\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+",
        text, re.MULTILINE
    )
    if clk_match:
        out["clk_ns"] = float(clk_match.group(1))

    return out


def parse_utilization(path: Path) -> Dict[str, int]:
    """
    Extract LUT / FF / CARRY4 / MUXF7 / MUXF8 / LUTRAM counts from a
    Vivado 'report_utilization' .rpt file.
    """
    out: Dict[str, int] = {}
    text = path.read_text(errors="replace")

    patterns = {
        "luts":    r"\|\s*Slice LUTs\s*\|\s*(\d+)",
        "ffs":     r"\|\s*Slice Registers\s*\|\s*(\d+)",
        "carry4":  r"\|\s*CARRY4\s*\|\s*(\d+)",
        "muxf7":   r"\|\s*MUXF7\s*\|\s*(\d+)",
        "muxf8":   r"\|\s*MUXF8\s*\|\s*(\d+)",
        "lutram":  r"\|\s*LUT as Memory\s*\|\s*(\d+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            out[key] = int(m.group(1))
    return out


def parse_power(path: Path) -> Dict[str, float]:
    """
    Extract total on-chip power (mW) from a Vivado 'report_power' .rpt file.
    Looks for the 'Total On-Chip Power (W)' summary line.
    """
    out: Dict[str, float] = {}
    text = path.read_text(errors="replace")
    m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", text)
    if m:
        out["power_w"] = float(m.group(1))
    return out


# ---------------------------------------------------------------------------
# 4. Row builder
# ---------------------------------------------------------------------------
def build_row(raw_dir: Path, arch: str, W: int) -> Row:
    meta = ARCH_META[arch]
    n_cyc = meta["n_cyc"](W)
    row = Row(arch=arch, W=W, n_cyc=n_cyc)

    timing = raw_dir / f"{arch}_w{W}_timing.rpt"
    util   = raw_dir / f"{arch}_w{W}_util.rpt"
    power  = raw_dir / f"{arch}_w{W}_power.rpt"

    # --- Timing ---
    if timing.is_file():
        t = parse_timing(timing, W, n_cyc)
        if "clk_ns" in t:
            row.t_clk_ns = t["clk_ns"]
        elif "wns_ns" in t:
            # Combinational: T_clk := |WNS| (critical-path delay)
            row.t_clk_ns = abs(t["wns_ns"])
        else:
            row.notes.append("timing: no WNS/clk found")
    else:
        row.notes.append(f"missing {timing.name}")

    # --- Utilization ---
    if util.is_file():
        u = parse_utilization(util)
        row.luts   = u.get("luts")
        row.ffs    = u.get("ffs")
        row.carry4 = u.get("carry4")
        row.muxf7  = u.get("muxf7")
        row.muxf8  = u.get("muxf8")
        row.lutram = u.get("lutram")
        if row.luts is not None:
            row.equiv_luts = (
                (row.luts or 0)
                + 4 * (row.carry4 or 0)
                +     (row.muxf7  or 0)
                +     (row.muxf8  or 0)
                -     (row.lutram or 0)
            )
    else:
        row.notes.append(f"missing {util.name}")

    # --- Power ---
    if power.is_file():
        p = parse_power(power)
        if "power_w" in p:
            row.power_mw = p["power_w"] * 1000.0
    else:
        row.notes.append(f"missing {power.name}")

    # --- Derived quantities ---
    if row.t_clk_ns is not None:
        row.latency_ns = n_cyc * row.t_clk_ns
        if meta["pipelined"]:
            row.throughput_mops = 1000.0 / row.t_clk_ns
        elif meta["clocked"]:
            row.throughput_mops = 1000.0 / row.latency_ns
        else:
            row.throughput_mops = None       # combinational: n/a

    if row.equiv_luts is not None and row.latency_ns is not None:
        row.adp = row.equiv_luts * row.latency_ns          # LUT * ns
    if row.power_mw is not None and row.latency_ns is not None:
        row.edp = row.power_mw * (row.latency_ns ** 2)     # mW * ns^2 = pJ * ns

    return row


# ---------------------------------------------------------------------------
# 5. CSV writers
# ---------------------------------------------------------------------------
def _fmt(v, nd=2):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def write_table10(rows: List[Row], out_dir: Path) -> None:
    """Table 10: CCSA vs Manchester, carry-skip, Kogge-Stone."""
    wanted = ["ccsa", "manchester_ripple", "manchester_static",
              "carry_skip", "ks_pipelined", "ks_comb"]
    path = out_dir / "table10.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["W", "Architecture", "N_cyc", "T_clk_ns", "Latency_ns",
                    "Throughput_Mops", "LUTs", "FFs", "Power_mW"])
        for W in WIDTHS:
            for arch in wanted:
                r = next((x for x in rows if x.arch == arch and x.W == W), None)
                if r is None:
                    continue
                w.writerow([r.W, r.arch, r.n_cyc,
                            _fmt(r.t_clk_ns), _fmt(r.latency_ns),
                            _fmt(r.throughput_mops) if r.throughput_mops else "n/a",
                            r.luts or "", r.ffs or "", _fmt(r.power_mw)])
    print(f"  wrote {path}")


def write_table11(rows: List[Row], out_dir: Path) -> None:
    """Table 11: CCSA vs CARRY4-ripple and CARRY4-pipelined."""
    wanted = ["ccsa", "carry4_ripple", "carry4_pipelined"]
    path = out_dir / "table11.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["W", "Architecture", "N_cyc", "T_clk_ns", "Latency_ns",
                    "Throughput_Mops", "LUTs", "FFs", "Power_mW",
                    "Equiv_LUTs", "CARRY4", "MUXF7", "MUXF8", "LUTRAM"])
        for W in WIDTHS:
            for arch in wanted:
                r = next((x for x in rows if x.arch == arch and x.W == W), None)
                if r is None:
                    continue
                w.writerow([r.W, r.arch, r.n_cyc,
                            _fmt(r.t_clk_ns), _fmt(r.latency_ns),
                            _fmt(r.throughput_mops) if r.throughput_mops else "n/a",
                            r.luts or "", r.ffs or "", _fmt(r.power_mw),
                            r.equiv_luts or "", r.carry4 or "",
                            r.muxf7 or "", r.muxf8 or "", r.lutram or ""])
    print(f"  wrote {path}")


def write_table12(rows: List[Row], out_dir: Path) -> None:
    """Table 12: ADP and EDP, CCSA vs pipelined K-S."""
    path = out_dir / "table12.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Width_bits",
                    "CCSA_ADP_LUTns", "KS_ADP_LUTns",
                    "CCSA_EDP_pJns", "KS_EDP_pJns"])
        for W in WIDTHS:
            ccsa = next((x for x in rows if x.arch == "ccsa" and x.W == W), None)
            ks   = next((x for x in rows if x.arch == "ks_pipelined" and x.W == W), None)
            if ccsa is None or ks is None:
                continue
            w.writerow([W,
                        _fmt(ccsa.adp), _fmt(ks.adp),
                        _fmt(ccsa.edp), _fmt(ks.edp)])
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# 6. Main
# ---------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Collate CCSA Vivado reports into Tables 10-12.")
    ap.add_argument("--raw", required=True, type=Path,
                    help="Directory containing raw .rpt files.")
    ap.add_argument("--out", required=True, type=Path,
                    help="Directory to write table10.csv, table11.csv, table12.csv.")
    ap.add_argument("--k", type=int, default=16, help="Repeater pitch (default 16).")
    ap.add_argument("--clk-budget-ns", type=float, default=1.22,
                    help="Target clock period for W_max check (default 1.22 ns).")
    ap.add_argument("--tau-ps", type=float, default=12.0,
                    help="Elementary gate delay tau in ps (default 12.0).")
    args = ap.parse_args(argv)

    raw_dir: Path = args.raw
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.is_dir():
        print(f"ERROR: raw directory not found: {raw_dir}", file=sys.stderr)
        return 2

    # --- Bus-delay sanity check (Section 7.4) ---
    c_bus_tau = (args.clk_budget_ns * 1000.0 - 36.0 - 24.0 - 6.0 - 6.0) / args.tau_ps
    w_max = w_max_for_budget(c_bus_tau, k=args.k)
    print(f"[bus model]  c_bus = {c_bus_tau:.2f} tau,  W_max = {w_max}")
    print(f"[bus model]  check W=256 -> t_bus/tau = "
          f"{bus_delay_tau(256, k=args.k):.2f}")

    # --- Build rows ---
    rows: List[Row] = []
    for arch in ARCH_META:
        for W in WIDTHS:
            rows.append(build_row(raw_dir, arch, W))

    # --- Emit CSVs ---
    print("[tables]")
    write_table10(rows, out_dir)
    write_table11(rows, out_dir)
    write_table12(rows, out_dir)

    # --- Summary of missing artifacts ---
    missing = [(r.arch, r.W, r.notes) for r in rows if r.notes]
    if missing:
        print(f"[warn] {len(missing)} rows have incomplete source data:")
        for arch, W, notes in missing[:10]:
            print(f"   {arch} W={W}: {'; '.join(notes)}")
        if len(missing) > 10:
            print(f"   ... and {len(missing) - 10} more")
        return 1

    print("[ok] all rows populated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
