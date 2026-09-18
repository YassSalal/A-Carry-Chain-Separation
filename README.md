# CCSA — Carry-Chain-Separation Architecture

Versioned supplementary material for the manuscript
"A Carry-Chain-Separation Architecture for Binary Addition".

## Contents

| Tag      | Path                              | Role                                        |
|----------|-----------------------------------|---------------------------------------------|
| Supp. A  | supp/A_reference_model/ccsa_ref.py | Python reference model of Algorithm 1      |
| Supp. B  | supp/B_rtl/ccsa_adder.sv           | Sequential RTL (W+1-bit output)             |
| Supp. B  | supp/B_rtl/ccsa_adder_flat.sv      | Combinational RTL (single-cycle)            |
| Supp. C  | supp/C_testbench/tb_ccsa.sv        | Self-checking SystemVerilog testbench       |
| Supp. D  | supp/D_vivado_scripts/             | Vivado synthesis & sweep Tcl scripts        |
| Supp. E  | supp/E_electrical_report/          | Electrical model report + Python evaluation |
| Supp. F  | supp/F_fpga_reports/               | Raw Vivado reports + collation script       |

## Reproduce

    make all

See `REPRODUCE.md` for the equation-to-code mapping required by the
reviewer.

## Version

This repository supersedes an earlier revision in which the reference
model and RTL allocated only W state positions and used an incorrect
neighbour shift in Step 3. All results in the manuscript were
regenerated from the commit tagged `v2.0-ccsa`.