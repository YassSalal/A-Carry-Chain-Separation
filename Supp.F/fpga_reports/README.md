# FPGA Raw Reports — CCSA v2.0-ccsa

This directory contains the raw Vivado post-route reports backing Tables 10,
11, and 12 of the manuscript. It exists so that every number in those tables
can be independently inspected without owning a Vivado license and without
re-running synthesis.

## Layout

- `raw/<architecture>/<Wxxx>/` — one folder per (architecture, width) point.
- `collated/table10.csv` etc. — the exact CSVs used to fill the manuscript.
- `scripts/` — extraction, verification, and manifest tooling.

## What ships per (architecture, width)

Each `raw/<arch>/<Wxxx>/` folder contains:

| File | Purpose |
|---|---|
| `timing_summary_routed.rpt` | Post-route WNS/TNS, Fmax, critical path |
| `utilization_placed.rpt` | Slice LUTs, FFs, CARRY4, MUXF7/8, BRAM |
| `power_routed.rpt` | Total/dynamic/static power |
| `route_status.rpt` | Routed nets, wirelength, congestion |
| `drc_routed.rpt` | DRC cleanliness |
| `methodology_routed.rpt` | Methodology warnings |
| `clock_utilization_routed.rpt` | Clock resource usage |
| `runme.log` | Exact Vivado invocation |
| `constraints.xdc` | The XDC used for this run |
| `run.tcl` | The per-point Tcl driver |

## Reproduce from scratch (requires Vivado 2023.2 + license)

```bash
cd Supp.F/fpga_reports/scripts
vivado -mode batch -source generate_reports.tcl \
       -tclargs --root .. --rtl ../../../Supp.B/B_rtl