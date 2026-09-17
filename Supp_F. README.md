markdown
# CCSA Supplementary Material — Repository Layout

- `supp_A/python_reference_model.py` — Python 3.11 reference model
- `supp_B/ccsa_rtl.v`               — synthesizable sequential RTL
- `supp_B/ccsa_comb.v`              — combinational RTL
- `supp_C/tb_ccsa.sv`               — self-checking SV testbench + SVA
- `supp_D/synth_ccsa.tcl`           — Vivado 2023.2 synthesis flow
- `supp_E/electrical_validation_report.md` — custom-bus delay model
- `supp_E/reproduce_tables.py`      — reproduces Appendix B Tables 1.2 & 1.3
- `supp_F/parse_reports.py`         — parses Vivado reports into CSV
- `baselines/`                      — Manchester (ripple, static),
                                      carry-skip, Kogge-Stone (pipelined,
                                      combinational), CARRY4 (ripple,
                                      pipelined)

## Reproduction

1. `python3 supp_A/python_reference_model.py`
2. `python3 supp_E/reproduce_tables.py`
3. `vivado -mode batch -source supp_D/synth_ccsa.tcl`
4. `python3 supp_F/parse_reports.py`

## Table numbering note

The manuscript’s evaluation tables are numbered **Table 10, Table 11, and
Table 12**. Earlier references to “Tables 4–6” were incorrect.
