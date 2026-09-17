markdown
# Electrical Validation Report — CCSA Custom Bus (Falsifiable Model)

> **Status:** Model prediction, not silicon-validated.
> All values below are computed from the corrected segment model of
> Section 7.4 of the manuscript. This report supersedes any earlier
> version that used `t_seg = 1.5 τ` or `m = ⌈(n+1)/k⌉`.

## E.1 Parameter set (from Appendix B, Table 1.2)

| Symbol | Value | Source |
|---|---|---|
| τ | 12 ps | ASAP7 min-size 2-input NAND, V_DD=0.70 V, TT/25 °C |
| R_0 | 2.5 kΩ | 7-nm unit inverter |
| C_0 | 0.30 fF | 7-nm unit inverter |
| r_v | 0.15 Ω/μm | ASAP7 M13 |
| c_v | 0.20 fF/μm | ASAP7 M13 (incl. fringe to grounded shield) |
| Δx | 0.80 μm | Section 7.4.1 floorplan |
| k | 16 | Design choice |
| s | 8 | Design choice |
| R_HSW | 220 Ω | Section 1.3.C |
| R_VSW | 280 Ω | Section 1.3.C |
| C_tap | 0.5 fF | Section 1.3.C |
| C_keeper | 0.5 fF | Section 1.3.C |
| t_level_restore | 0.3 τ | Section 1.3.C |

## E.2 Corrected segment delay (with series switch resistance)

Per-segment wire quantities:

- R_wire = r_v · k · Δx = 0.15 · 16 · 0.80 = **1.92 Ω**
- C_wire = c_v · k · Δx = 0.20 · 16 · 0.80 = **2.56 fF**

Driver and switch series resistance:

- R_driver = R_0 / s = 2500 / 8 = 312.5 Ω
- R_series = R_driver + R_VSW + k·R_HSW
           = 312.5 + 280 + 16·220
           = **4112.5 Ω**

Capacitive load:

- C_load = C_wire + C_tap + C_keeper + C_rep
- C_rep = s·C_0 = 8·0.30 = 2.4 fF
- C_load = 2.56 + 0.5 + 0.5 + 2.4 = **5.96 fF**

Elmore terms:

- Term1 = R_series · C_load = 4112.5 · 5.96e-15 = 24.51 ps
- Term2 = R_wire · (C_wire/2 + C_tap + C_keeper + C_rep)
        = 1.92 · (1.28 + 0.5 + 0.5 + 2.4) fF
        = 1.92 · 4.68e-15 = 0.009 ps
- Term3 = t_level_restore = 0.3 · 12 = 3.6 ps

Total:

- **t_seg = 24.51 + 0.009 + 3.6 ≈ 28.12 ps ≈ 2.34 τ**

## E.3 Corrected segment count

For W bit positions with repeaters every k = 16 columns:

m(W) = ⌊(W − 1) / k⌋ + 1,  W ≥ 1,  m(0) = 0.

Bus delay:

t_bus(W)/τ = 2.34·m(W) + 0.5

Stage-2 delay:

t_step2(W)/τ = t_det/τ + t_bus(W)/τ + t_rw/τ
             = 3 + 2.34·m(W) + 0.5 + 2
             = 2.34·m(W) + 5.5

## E.4 Width sweep at T_clk = 1.22 ns (c_bus = 95.7)

| W | m(W) | t_bus/τ | t_step2/τ | Inside regime? |
|---|---|---|---|---|
| 8   | 1  | 2.84   | 7.84   | Yes |
| 16  | 1  | 2.84   | 7.84   | Yes |
| 32  | 2  | 5.18   | 10.18  | Yes |
| 64  | 4  | 9.86   | 14.86  | Yes |
| 128 | 8  | 19.22  | 24.22  | Yes |
| 256 | 16 | 37.94  | 42.94  | Yes |
| 512 | 32 | 75.38  | 80.38  | Yes |
| 608 | 38 | 89.42  | 94.42  | Yes |
| 624 | 39 | 91.76  | 96.76  | Yes |
| 640 | 40 | 94.10  | 99.10  | Yes |
| 641 | 41 | 96.44  | 101.44 | No  |

**W_max(16, 8, 1.22 ns) = 640 bits.**

## E.5 Width sweep at T_clk = 1.50 ns (c_bus = 119.0)

| W | m(W) | t_bus/τ | t_step2/τ | Inside regime? |
|---|---|---|---|---|
| 256 | 16 | 37.94  | 42.94  | Yes |
| 512 | 32 | 75.38  | 80.38  | Yes |
| 608 | 38 | 89.42  | 94.42  | Yes |
| 624 | 39 | 91.76  | 96.76  | Yes |
| 640 | 40 | 94.10  | 99.10  | Yes |
| 800 | 50 | 117.50 | 122.50 | Yes |
| 801 | 51 | 119.84 | 124.84 | No  |

**W_max(16, 8, 1.50 ns) = 800 bits.**

## E.6 Reproducibility

The script `supp_E/reproduce_tables.py` regenerates Tables 1.2 and 1.3 of
Appendix B from the equations above.

## E.7 Falsification condition

The model predicts that a custom-layout CCSA in the stated 7-nm
technology, with k = 16, s = 8, and T_clk = 1.22 ns, will meet timing at
W = 640 and will fail at W = 641 under the stated corner. Post-layout RC
extraction of the Bus 2 M13 track plus SPICE simulation at the boundary
would confirm or refute this prediction.markdown
# Electrical Validation Report — CCSA Custom Bus (Falsifiable Model)

> **Status:** Model prediction, not silicon-validated.
> All values below are computed from the corrected segment model of
> Section 7.4 of the manuscript. This report supersedes any earlier
> version that used `t_seg = 1.5 τ` or `m = ⌈(n+1)/k⌉`.

## E.1 Parameter set (from Appendix B, Table 1.2)

| Symbol | Value | Source |
|---|---|---|
| τ | 12 ps | ASAP7 min-size 2-input NAND, V_DD=0.70 V, TT/25 °C |
| R_0 | 2.5 kΩ | 7-nm unit inverter |
| C_0 | 0.30 fF | 7-nm unit inverter |
| r_v | 0.15 Ω/μm | ASAP7 M13 |
| c_v | 0.20 fF/μm | ASAP7 M13 (incl. fringe to grounded shield) |
| Δx | 0.80 μm | Section 7.4.1 floorplan |
| k | 16 | Design choice |
| s | 8 | Design choice |
| R_HSW | 220 Ω | Section 1.3.C |
| R_VSW | 280 Ω | Section 1.3.C |
| C_tap | 0.5 fF | Section 1.3.C |
| C_keeper | 0.5 fF | Section 1.3.C |
| t_level_restore | 0.3 τ | Section 1.3.C |

## E.2 Corrected segment delay (with series switch resistance)

Per-segment wire quantities:

- R_wire = r_v · k · Δx = 0.15 · 16 · 0.80 = **1.92 Ω**
- C_wire = c_v · k · Δx = 0.20 · 16 · 0.80 = **2.56 fF**

Driver and switch series resistance:

- R_driver = R_0 / s = 2500 / 8 = 312.5 Ω
- R_series = R_driver + R_VSW + k·R_HSW
           = 312.5 + 280 + 16·220
           = **4112.5 Ω**

Capacitive load:

- C_load = C_wire + C_tap + C_keeper + C_rep
- C_rep = s·C_0 = 8·0.30 = 2.4 fF
- C_load = 2.56 + 0.5 + 0.5 + 2.4 = **5.96 fF**

Elmore terms:

- Term1 = R_series · C_load = 4112.5 · 5.96e-15 = 24.51 ps
- Term2 = R_wire · (C_wire/2 + C_tap + C_keeper + C_rep)
        = 1.92 · (1.28 + 0.5 + 0.5 + 2.4) fF
        = 1.92 · 4.68e-15 = 0.009 ps
- Term3 = t_level_restore = 0.3 · 12 = 3.6 ps

Total:

- **t_seg = 24.51 + 0.009 + 3.6 ≈ 28.12 ps ≈ 2.34 τ**

## E.3 Corrected segment count

For W bit positions with repeaters every k = 16 columns:

m(W) = ⌊(W − 1) / k⌋ + 1,  W ≥ 1,  m(0) = 0.

Bus delay:

t_bus(W)/τ = 2.34·m(W) + 0.5

Stage-2 delay:

t_step2(W)/τ = t_det/τ + t_bus(W)/τ + t_rw/τ
             = 3 + 2.34·m(W) + 0.5 + 2
             = 2.34·m(W) + 5.5

## E.4 Width sweep at T_clk = 1.22 ns (c_bus = 95.7)

| W | m(W) | t_bus/τ | t_step2/τ | Inside regime? |
|---|---|---|---|---|
| 8   | 1  | 2.84   | 7.84   | Yes |
| 16  | 1  | 2.84   | 7.84   | Yes |
| 32  | 2  | 5.18   | 10.18  | Yes |
| 64  | 4  | 9.86   | 14.86  | Yes |
| 128 | 8  | 19.22  | 24.22  | Yes |
| 256 | 16 | 37.94  | 42.94  | Yes |
| 512 | 32 | 75.38  | 80.38  | Yes |
| 608 | 38 | 89.42  | 94.42  | Yes |
| 624 | 39 | 91.76  | 96.76  | Yes |
| 640 | 40 | 94.10  | 99.10  | Yes |
| 641 | 41 | 96.44  | 101.44 | No  |

**W_max(16, 8, 1.22 ns) = 640 bits.**

## E.5 Width sweep at T_clk = 1.50 ns (c_bus = 119.0)

| W | m(W) | t_bus/τ | t_step2/τ | Inside regime? |
|---|---|---|---|---|
| 256 | 16 | 37.94  | 42.94  | Yes |
| 512 | 32 | 75.38  | 80.38  | Yes |
| 608 | 38 | 89.42  | 94.42  | Yes |
| 624 | 39 | 91.76  | 96.76  | Yes |
| 640 | 40 | 94.10  | 99.10  | Yes |
| 800 | 50 | 117.50 | 122.50 | Yes |
| 801 | 51 | 119.84 | 124.84 | No  |

**W_max(16, 8, 1.50 ns) = 800 bits.**

## E.6 Reproducibility

The script `supp_E/reproduce_tables.py` regenerates Tables 1.2 and 1.3 of
Appendix B from the equations above.

## E.7 Falsification condition

The model predicts that a custom-layout CCSA in the stated 7-nm
technology, with k = 16, s = 8, and T_clk = 1.22 ns, will meet timing at
W = 640 and will fail at W = 641 under the stated corner. Post-layout RC
extraction of the Bus 2 M13 track plus SPICE simulation at the boundary
would confirm or refute this prediction.
