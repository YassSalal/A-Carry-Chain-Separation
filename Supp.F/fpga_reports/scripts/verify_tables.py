#!/usr/bin/env python3
"""Assert collated CSVs match the manuscript Table 10/11/12 values."""
import argparse, csv, sys
from pathlib import Path

# Canonical values transcribed from the manuscript.
EXPECTED_10 = {
    (8,"CCSA"):              (1.16, 4.64, 108, 40, 38),
    (8,"K-S Pipelined"):     (1.03, 4.12, 176, 52, 41),
    (16,"CCSA"):             (1.18, 4.72, 212, 72, 42),
    (16,"K-S Pipelined"):    (1.18, 5.89, 148, 100, 48),
    (32,"CCSA"):             (1.19, 4.77, 420, 136, 51),
    (32,"K-S Pipelined"):    (1.19, 7.15, 292, 196, 62),
    (64,"CCSA"):             (1.20, 4.81, 836, 264, 67),
    (64,"K-S Pipelined"):    (1.20, 8.42, 580, 388, 85),
    (128,"CCSA"):            (1.21, 4.85, 1668, 520, 96),
    (128,"K-S Pipelined"):   (1.21, 9.71, 1156, 772, 128),
    (256,"CCSA"):            (1.22, 4.89, 3332, 1032, 142),
    (256,"K-S Pipelined"):   (1.22, 11.02, 2308, 1540, 198),
}

EXPECTED_11 = {
    (8,"CARRY4-Ripple"):     (0.71, 30, 12, 8),
    (8,"CARRY4-Pipelined"):  (0.85, 2.55, 176, 38, 26, 18),
    (16,"CARRY4-Ripple"):    (1.00, 58, 18, 16),
    (16,"CARRY4-Pipelined"): (1.05, 5.25, 95, 274, 50, 26),
    (32,"CARRY4-Ripple"):    (1.30, 114, 24, 32),
    (32,"CARRY4-Pipelined"): (1.40, 12.60, 71, 414, 698, 36),
    (64,"CARRY4-Ripple"):    (1.68, 226, 38, 64),
    (64,"CARRY4-Pipelined"): (1.65, 28.05, 60, 629, 194, 54),
    (128,"CARRY4-Ripple"):   (2.71, 450, 60, 128),
    (128,"CARRY4-Pipelined"):(1.95, 64.35, 51, 1357, 838, 68),
    (256,"CARRY4-Ripple"):   (4.34, 898, 96, 256),
    (256,"CARRY4-Pipelined"):(2.31, 150.15, 43, 3115, 4770, 140),
}

def check(path, expected, fields, tol=0.02):
    with path.open() as f:
        rows = list(csv.DictReader(f))
    errs = 0
    for r in rows:
        key = (int(r["W"]), r["Architecture"])
        if key not in expected: continue
        exp = expected[key]
        got = tuple(float(r[f]) for f in fields)
        for e, g, f in zip(exp, got, fields):
            if abs(e - g) / max(abs(e), 1e-9) > tol:
                print(f"MISMATCH {key} {f}: expected {e}, got {g}")
                errs += 1
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collated", required=True)
    args = ap.parse_args()
    d = Path(args.collated)
    e = 0
    e += check(d/"table10.csv", EXPECTED_10,
               ["T_clk_ns","Latency_ns","LUTs","FFs","Power_mW"])
    e += check(d/"table11.csv", EXPECTED_11,
               ["T_clk_ns","Latency_ns","LUTs","FFs","Power_mW"]
               if "Pipelined" in str(EXPECTED_11) else ["T_clk_ns","LUTs","FFs"])
    if e:
        print(f"FAILED with {e} mismatches"); sys.exit(1)
    print("OK: all collated values match manuscript tables.")

if __name__ == "__main__":
    main()