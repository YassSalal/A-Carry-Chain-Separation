"""
Collate the raw Vivado .rpt files in supp/F_fpga_reports/raw/
into CSV files that reproduce Tables 10, 11, and 12 of the manuscript.
"""

import csv
import re
from pathlib import Path

RAW = Path(__file__).parent / "raw"

def parse_timing(rpt: Path):
    text = rpt.read_text(errors="ignore")
    m = re.search(r"Slack\s*\(MET\)\s*:\s*([-\d.]+)ns", text)
    period = None
    m2 = re.search(r"Clock Period\s*:\s*([\d.]+)ns", text)
    if m2:
        period = float(m2.group(1))
    return period

def parse_util(rpt: Path):
    text = rpt.read_text(errors="ignore")
    luts = re.search(r"Slice LUTs\s*\|\s*(\d+)", text)
    ffs  = re.search(r"Slice Registers\s*\|\s*(\d+)", text)
    return (int(luts.group(1)) if luts else None,
            int(ffs.group(1))  if ffs  else None)

def parse_power(rpt: Path):
    text = rpt.read_text(errors="ignore")
    m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", text)
    return float(m.group(1)) * 1000.0 if m else None  # mW

def main():
    rows = []
    for rpt in sorted(RAW.glob("*_timing.rpt")):
        stem = rpt.stem.replace("_timing", "")
        util = RAW / f"{stem}_util.rpt"
        powr = RAW / f"{stem}_power.rpt"
        period = parse_timing(rpt)
        luts, ffs = parse_util(util) if util.exists() else (None, None)
        power_mW = parse_power(powr) if powr.exists() else None
        rows.append([stem, period, luts, ffs, power_mW])

    out = RAW.parent / "collated.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["design", "T_clk_ns", "LUTs", "FFs", "power_mW"])
        w.writerows(rows)
    print(f"Wrote {out} with {len(rows)} rows.")

if __name__ == "__main__":
    main()
