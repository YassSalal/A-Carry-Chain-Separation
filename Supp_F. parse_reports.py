#!/usr/bin/env python3
"""parse_reports.py -- Collate raw Vivado reports (Supp_F/raw) into
results_summary.csv with the columns used in Tables 4-6 of the paper.

Usage:  python3 parse_reports.py [raw_dir] > results_summary.csv
"""
import re, sys, pathlib, csv

def grab(pat, text, cast=float, default=None):
    m = re.search(pat, text)
    return cast(m.group(1)) if m else default

def parse_timing(p):
    t = p.read_text(errors="replace")
    wns = grab(r"WNS\(ns\)\s+([-\d.]+)", t)
    fmax = grab(r"([ \d.]+)\s*\|.*Max.*", t)          # row: Freq (MHz)
    if fmax is None:
        fmax = grab(r"([ \d.]+)\s*\|.*\|.*clk", t)
    return wns

def parse_util(p):
    t = p.read_text(errors="replace")
    luts = grab(r"Slice LUTs\*?\s+\|\s+(\d+)", t, int)
    ffs  = grab(r"Slice Registers\s+\|\s+(\d+)", t, int)
    return luts, ffs

def parse_power(p):
    t = p.read_text(errors="replace")
    tot = grab(r"Total On-Chip Power \(W\)\s+\|\s+([\d.]+)", t)
    return float(tot) * 1000 if tot else None   # mW

def main():
    raw = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "raw")
    w = csv.writer(sys.stdout)
    w.writerow(["design", "W", "LUTs", "FFs", "WNS_ns", "power_mW"])
    for d in sorted(raw.glob("*_W*")):
        m = re.match(r"(.+)_W(\d+)$", d.name)
        if not m:
            continue
        luts = ffs = wns = pwr = None
        for f in d.glob("*_util.rpt"):
            luts, ffs = parse_util(f)
        for f in d.glob("*_timing.rpt"):
            wns = parse_timing(f)
        for f in d.glob("*_power.rpt"):
            pwr = parse_power(f)
        w.writerow([m.group(1), m.group(2), luts, ffs, wns,
                    f"{pwr:.2f}" if pwr else ""])

if __name__ == "__main__":
    main()
