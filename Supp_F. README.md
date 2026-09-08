# Supp. F -- Raw FPGA Synthesis Reports

This directory holds the **unmodified, tool-generated** post-route reports
supporting Section 9 (Tables 4-6) and the custom-bus power model (Section 10.2.3).

## Layout

    Supp_F/raw/
      ccsa_seq_W8/    ccsa_seq_W8_util.rpt, _timing.rpt, _power.rpt,
                      _route_status.rpt, synth.log, ccsa_seq_W8.xdc
      ccsa_seq_W16/   ... (same naming)
      ...
      ccsa_seq_W256/
      kogge_stone_pipelined_W{8..256}/   (baseline, repository baselines/ RTL)
      kogge_stone_comb_W{8..256}/
      brent_kung_comb_W{8..256}/
      results_summary.csv              (collated by parse_reports.py)

## Regenerating

    vivado -mode batch -source ../Supp_D/run_synth_all.tcl

Each run uses Vivado 2023.2, part xc7a100tcsg324-1, default synthesis /
implementation strategies, retiming disabled, 1 ns clock over-constraint,
20 % input/output delays, 0.10 pF output load (Section 9.1). Reports are
committed **as generated**; only `results_summary.csv` is machine-derived
(via `parse_reports.py`).

## Contents of each report

| File | Key fields used in the paper |
|---|---|
| `*_util.rpt` | LUTs, FFs, routed wirelength |
| `*_timing.rpt` | WNS/TNS, post-route Fmax -> T_clk |
| `*_power.rpt` | Dynamic/leakage/total power (vectorless, 12.5 % toggle) |
| `*_route_status.rpt` | Fully routed confirmation (no congestion failures) |
| `synth.log` | Tool version, strategy flags, command echo |

## IMPORTANT limitation (repeated from Section 9.1)

The Artix-7 fabric implements the CCSA global buses through general-purpose
programmable interconnect, not dedicated metal tracks with
designer-controlled repeaters. These reports therefore validate logical
correctness, linear resource scaling, and latency *trends*; they do **not**
validate the absolute width-insensitive delay bound of the custom-bus
model (Supp. E).
