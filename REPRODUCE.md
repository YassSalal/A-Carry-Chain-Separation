# Reproducibility Guide

## Repository structure

...
## Equation-to-code map

| Paper equation | File | Lines |
|---|---|---|
| Step 1 HA | `ccs/rtl/ccsa_adder.sv` | 42–46 |
| Step 2 R, Λ | `ccs/rtl/ccsa_adder.sv` | 52–56 |
| Step 2 B2, E | `ccs/rtl/ccsa_adder.sv` | 58–62 |
| Step 2 U2, L2, M | `ccs/rtl/ccsa_adder.sv` | 64–68 |
| Step 3 U3, L3 | `ccs/rtl/ccsa_adder.sv` | 74–78 |
| Step 4 U4 | `ccs/rtl/ccsa_adder.sv` | 84–86 |

## How to reproduce
Make all (Python model plus Icarus Verilog simulation).

## Verification campaigns

- Exhaustive 8-bit: `python reference_model/ccsa_ref.py --exhaustive-8`
- Random wide: `python reference_model/ccsa_ref.py --random-widths 16,32,64,128,256 --seed 0xCC5A`
- SVA: `vsim -c -do scripts/run_modelsim.do`
