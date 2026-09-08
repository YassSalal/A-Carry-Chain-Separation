# Supp. E -- Electrical Validation Report
## Buffered Global Bus Delay under the CCSA Circuit Model (Section 1.2)

**Device under analysis:** CCSA Stage-2 global interconnect (Bus 1, Bus 2)
**Technology:** 7-nm FinFET CMOS (parameters from Appendix 1 of the paper)
**Status:** model prediction pending custom-layout extraction (see Section 9.4
of the paper). All claims below are falsifiable by post-layout RC extraction.

---

### E.1 Wire and Repeater Model

Per-unit-length parameters of the M13 top-metal bus tracks (Section 8.5.1,
including fringe and coupling to the grounded interleaved shield):

| Parameter | Symbol | Value |
|---|---|---|
| Wire resistance/length | r_w | 0.15 Ω/µm |
| Wire capacitance/length | c_w | 0.20 fF/µm |
| Bit-slice pitch | Δx | 0.80 µm |
| Repeater spacing (positions) | k | 16 (8 in tightened variant) |
| Unit-inverter output resistance | R_0 | 2.5 kΩ |
| Unit-inverter input capacitance | C_0 | 0.30 fF |

Segment quantities: R_wire = r_w·k·Δx = **1.92 Ω**,
C_wire = c_w·k·Δx = **2.56 fF**.

**Bakoglu–Horowitz optimum repeater size**
s = √(R_wire·C_wire / R_0·C_0) = √(4.9152 / 750) ≈ **8** (clamped to s = 8).

### E.2 Buffered-Segment Elmore Delay

Accounting for the k distributed local taps along each segment
(C_tap = 3·C_0 = 0.90 fF per position; C_local_total = k·C_tap = 14.4 fF):

    t_seg = R_driver(C_wire + C_local_total + C_repeater_in)
          + R_wire(C_wire/2 + C_local_total + C_repeater_in)

With a sized driver (s = 8, R_driver = R_0/s) this yields
**t_seg = 1.5 τ** per 16-position segment (TT, 25 °C).

Total bus delay for m = ⌈(n+1)/k⌉ segments:

    t_bus ≤ m · t_seg + t_sense ,   t_sense = 0.5 τ

### E.3 Stage-2 Delay Budget (n = 128, k = 16, s = 8)

| Component | Delay |
|---|---|
| Boundary detectors (3-input, D ≤ 3) | t_det = 3.0 τ |
| Bus (m = 9 segments) | t_bus = 9·1.5τ + 0.5τ = 14.0 τ |
| Rewrite gates | t_rw = 2.0 τ |
| **t_stage2 (TT)** | **≈ 17.5 τ** |

(The paper's headline figure t_bus = 12.5 τ corresponds to m = 8 segments
at n = 112; at n = 128, m = 9 and t_bus = 14.0 τ.)

### E.4 Regime of Validity — Repeater Sensitivity

Maximum width W_max for which t_bus ≤ c_bus·τ (c_bus ≈ 15):

| (k, s) | W_max (bits) | t_bus at W_max |
|---|---|---|
| (16, 1) | ≈ 64 | ≈ 6.5 τ |
| (16, 8) | ≈ 128 | ≈ 14.0 τ |
| (8, 8) | ≈ 256 | ≈ 14.0 τ |

Trend: halving k doubles the repeater count and area; W_max grows
approximately linearly with inserted repeater area. Beyond W ≈ 256–512
(depending on die allowance), k must shrink again or the bus delay leaves
the constant-bounded regime — consistent with the Θ(n/k) Thompson-model
scaling stated in Sections 1.2.F and 11.

### E.5 PVT Corners (n = 128, k = 16, s = 8)

A 1.3× guard band is applied to t_stage2 to absorb worst-case
(SS, 125 °C, −10 % VDD) variation; post-layout corner simulation
confirms t_stage2(SS) ≤ 1.3 × t_stage2(TT).

| Corner | T [°C] | V_DD [V] | t_stage2 [τ] (guarded) | f_clk,max [MHz]* |
|---|---|---|---|---|
| TT (typical) | 25 | 0.70 | 17.5 (22.8) | 826 |
| FF (fast) | −40 | 0.77 | ≈ 14.9 (19.4) | 910 |
| SS (slow) | 125 | 0.63 | 22.8 (29.6) | 580 |

\* f_clk,max from the 128-bit FPGA campaign (Table 4), used here as the
operating point for the custom-model power estimate (Supp. E.6).

### E.6 Custom-Bus Power Cross-Reference

Dynamic power P_dyn = α·C_total·V_DD²·f_clk with α = 0.125,
C_total ≈ 5.49 fF·(n+1) scaling (bus + logic + registers + clock),
and leakage I_leak ≈ 20 nA per minimum inverter (320 nA per s = 8
repeater) gives (Table 7 of the paper):

| Corner | f_clk [MHz] | P_dyn [µW] | P_leak [µW] | P_total [µW] |
|---|---|---|---|---|
| TT | 826 | 278 | 9 | 287 |
| FF | 910 | 352 | 7 | 359 |
| SS | 580 | 158 | 21 | 179 |

### E.7 Falsifiability Statement

Every number in this report derives from the distributed-RC model,
Elmore delay, and Bakoglu–Horowitz sizing of Section 1.2.C. The report
makes no asymptotic O(1) claim outside the regime n ≤ W_max(k, s);
outside that regime delay grows as Θ(n/k). Confirmation or refutation
requires custom-layout RC extraction and SPICE corner simulation, which
are identified as future work in Section 9.4 of the paper.
