# CCSA — Carry-Chain-Separation Architecture

Versioned supplementary material for the manuscript
"A Carry-Chain-Separation Architecture for Binary Addition".

## Contents

| Tag      | Path                              | Role                                        |
|----------|-----------------------------------|---------------------------------------------|
| Supp.A  | Supp.A/reference_model/ccsa_ref.py | Python reference model of Algorithm 1      |
| Supp.B  | Supp.B/rtl/ccsa_adder.sv           | Sequential RTL (W+1-bit output)             |
| Supp.B  | Supp.B/rtl/ccsa_adder_flat.sv      | Combinational RTL (single-cycle)            |
| Supp.C  | Supp.C/testbench/tb_ccsa.sv        | Self-checking SystemVerilog testbench       |
| Supp.D  | Supp.D/vivado_scripts/             | Vivado synthesis & sweep Tcl scripts        |
| Supp.E  | Supp.E/electrical_report/          | Electrical model report + Python evaluation |
| Supp.F  | Supp.F/fpga_reports/               | Raw Vivado reports + collation script       |

## Reproduce

    make all

See `REPRODUCE.md` for the equation-to-code mapping required by the
reviewer.

## Reproducibility

The exact artifacts backing the tables and figures in *Manuscript_18.09* are
released at the Git tag **`v2.0-ccsa`**.

Check out the tagged release:

    git clone https://github.com/YassSalal/A-Carry-Chain-Separation
    cd A-Carry-Chain-Separation
    git checkout v2.0-ccsa

Then follow `REPRODUCE.md`.

## Version

This repository supersedes an earlier revision in which the reference
model and RTL allocated only W state positions and used an incorrect
neighbour shift in Step 3. All results in the manuscript were
regenerated from the commit tagged `v2.0-ccsa`.
