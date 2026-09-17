python
#!/usr/bin/env python3
"""
Parse Vivado timing/utilization/power reports into a single CSV.
Produces results_summary.csv with one row per (architecture, width).
"""
import csv
import re
import sys
from pathlib import Path

REPORT_DIR = Path("./reports")
OUT_CSV    = Path("./results_summary.csv")

ARCH_PATTERNS = {
    "CCSA":               r"ccsa_(\d+)",
    "ManchesterRipple":   r"manchester_ripple_(\d+)",
    "ManchesterStatic":   r"manchester_static_(\d+)",
    "CarrySkip":          r"carry_skip_(\d+)",
    "KS_Pipelined":       r"ks_pipelined_(\d+)",
    "KS_Combinational":   r"ks_comb_(\d+)",
    "CARRY4_Ripple":      r"carry4_ripple_(\d+)",
    "CARRY4_Pipelined":   r"carry4_pipelined_(\d+)",
}

def parse_timing(path):
    txt = path.read_text(errors="ignore")
    m = re.search(r"Slack\s*\(MET\)\s*:\s*([-\d.]+)ns", txt)
    if m:
        return None  # met
    m = re.search(r"Slack\s*\(VIOLATED\)\s*:\s*([-\d.]+)ns", txt)
    if m:
        return None
    m = re.search(r"Data Path Delay:\s*([\d.]+)ns", txt)
    return float(m.group(1)) if m else None

def parse_util(path):
    txt = path.read_text(errors="ignore")
    luts = ffs = None
    m = re.search(r"Slice LUTs\s*\|\s*(\d+)", txt)
    if m: luts = int(m.group(1))
    m = re.search(r"Slice Registers\s*\|\s*(\d+)", txt)
    if m: ffs = int(m.group(1))
    return luts, ffs

def parse_power(path):
    txt = path.read_text(errors="ignore")
    m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", txt)
    return float(m.group(1)) * 1000.0 if m else None  # mW

def identify(path):
    name = path.stem
    for arch, pat in ARCH_PATTERNS.items():
        m = re.match(pat, name)
        if m:
            return arch, int(m.group(1))
    return None, None

def main():
    rows = []
    for timing in sorted(REPORT_DIR.glob("*_timing.rpt")):
        arch, width = identify(timing)
        if arch is None:
            continue
        util  = REPORT_DIR / f"{timing.stem.replace('_timing','')}_util.rpt"
        power = REPORT_DIR / f"{timing.stem.replace('_timing','')}_power.rpt"
        delay = parse_timing(timing)
        luts, ffs = parse_util(util) if util.exists() else (None, None)
        pmw = parse_power(power) if power.exists() else None
        rows.append({
            "architecture": arch,
            "width_bits":   width,
            "critical_path_ns": delay,
            "LUTs":         luts,
            "FFs":          ffs,
            "power_mW":     pmw,
        })

    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {OUT_CSV} with {len(rows)} rows")

if __name__ == "__main__":
    sys.exit(main())
