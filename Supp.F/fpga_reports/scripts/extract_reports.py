#!/usr/bin/env python3
"""
extract_reports.py — parse Vivado post-route reports into collated CSVs.
Reads:   raw/<arch>/<Wxxx>/*.rpt
Writes:  collated/table10.csv, table11.csv, table12.csv
"""
import argparse, csv, re, sys
from pathlib import Path

ARCHS = {
    "CCSA":                "CCSA",
    "Manchester-ripple":   "Manchester-ripple",
    "Manchester-static":   "Manchester-static",
    "Carry-skip-8bit":     "Carry-skip (8-bit)",
    "K-S-Pipelined":       "K-S Pipelined",
    "K-S-Combinational":   "K-S Combinational",
    "CARRY4-Ripple":       "CARRY4-Ripple",
    "CARRY4-Pipelined":    "CARRY4-Pipelined",
}

def parse_timing(rpt: Path):
    """Extract WNS and derived Fmax from timing_summary_routed.rpt."""
    text = rpt.read_text(errors="ignore")
    # WNS line format varies; grab the first 'WNS' data row
    m = re.search(r"\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+", text)
    wns = float(m.group(1)) if m else float("nan")
    # Fmax approximated from worst slack at the over-constrained 1 ns clock
    period = 1.000
    fmax = 1000.0 / (period - wns) if wns == wns and (period - wns) > 0 else float("nan")
    return wns, fmax

def parse_util(rpt: Path):
    """Extract LUTs and FFs from utilization_placed.rpt."""
    text = rpt.read_text(errors="ignore")
    luts = ffs = carry4 = 0
    m = re.search(r"Slice LUTs\s*\|\s*(\d+)", text)
    if m: luts = int(m.group(1))
    m = re.search(r"Slice Registers\s*\|\s*(\d+)", text)
    if m: ffs = int(m.group(1))
    m = re.search(r"CARRY4\s*\|\s*(\d+)", text)
    if m: carry4 = int(m.group(1))
    return luts, ffs, carry4

def parse_power(rpt: Path):
    """Extract total power (mW) from power_routed.rpt."""
    text = rpt.read_text(errors="ignore")
    m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", text)
    return float(m.group(1)) * 1000.0 if m else float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = Path(args.raw)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows10, rows11, rows12 = [], [], []
    for arch_dir, arch_label in ARCHS.items():
        for wdir in sorted((raw / arch_dir).glob("W*")):
            W = int(wdir.name[1:])
            wns, fmax = parse_timing(wdir / "timing_summary_routed.rpt")
            luts, ffs, carry4 = parse_util(wdir / "utilization_placed.rpt")
            power = parse_power(wdir / "power_routed.rpt")

            row = dict(W=W, Architecture=arch_label,
                       T_clk_ns=round(1.000 - wns, 3),
                       Latency_ns=round(4 * (1.000 - wns), 3),
                       LUTs=luts, FFs=ffs, Power_mW=round(power, 1))
            if arch_label.startswith("CARRY4"):
                rows11.append(row)
            else:
                rows10.append(row)
                rows12.append(dict(W=W, Arch=arch_label,
                                   ADP=round(luts * row["Latency_ns"], 0),
                                   EDP=round(power * row["Latency_ns"]**2, 3)))

    def dump(path, rows, fields):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows: w.writerow(r)

    dump(out / "table10.csv", rows10,
         ["W","Architecture","T_clk_ns","Latency_ns","LUTs","FFs","Power_mW"])
    dump(out / "table11.csv", rows11,
         ["W","Architecture","T_clk_ns","Latency_ns","LUTs","FFs","Power_mW"])
    dump(out / "table12.csv", rows12,
         ["W","Arch","ADP","EDP"])
    print(f"Wrote 3 CSVs to {out}")

if __name__ == "__main__":
    sys.exit(main())
