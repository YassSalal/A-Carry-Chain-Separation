python
#!/usr/bin/env python3
"""
Reproduce Appendix B Tables 1.2 and 1.3 from the corrected model.
"""
import math

# Parameters (Appendix B, Table 1.2)
TAU_PS = 12.0
R0_OHM = 2500.0
C0_FF  = 0.30
RV_OHM_PER_UM = 0.15
CV_FF_PER_UM  = 0.20
DX_UM  = 0.80
K      = 16
S      = 8
R_HSW  = 220.0
R_VSW  = 280.0
C_TAP  = 0.5
C_KEEP = 0.5
T_LEVEL_TAU = 0.3

def m(W):
    if W <= 0:
        return 0
    return (W - 1) // K + 1

def t_seg_tau():
    R_driver = R0_OHM / S
    R_wire   = RV_OHM_PER_UM * K * DX_UM
    C_wire   = CV_FF_PER_UM  * K * DX_UM
    C_rep    = S * C0_FF
    R_series = R_driver + R_VSW + K * R_HSW
    C_load   = C_wire + C_TAP + C_KEEP + C_rep
    term1 = R_series * C_load * 1e-3          # Ω·fF -> ps
    term2 = R_wire * (C_wire/2 + C_TAP + C_KEEP + C_rep) * 1e-3
    term3 = T_LEVEL_TAU * TAU_PS
    return (term1 + term2 + term3) / TAU_PS

def t_bus_tau(W):
    return 2.34 * m(W) + 0.5    Supp.E/reproduce_tables.py

def t_step2_tau(W):
    return 2.34 * m(W) + 5.5

def c_bus(T_clk_ns):
    return (T_clk_ns * 1000.0) / TAU_PS - 6.0

def w_max(T_clk_ns):
    budget = c_bus(T_clk_ns)
    W = 1
    while t_bus_tau(W) <= budget:
        W += 1
    return W - 1

if __name__ == "__main__":
    print(f"t_seg = {t_seg_tau():.3f} τ")
    for T in (1.00, 1.22, 1.50, 2.00):
        print(f"T_clk={T:.2f} ns  c_bus={c_bus(T):.2f}  W_max={w_max(T)}")

    print("\nWidth sweep at T_clk = 1.22 ns")
    print(f"{'W':>6} {'m':>4} {'t_bus/τ':>10} {'t_step2/τ':>12} {'inside':>8}")
    for W in (8, 16, 32, 64, 128, 256, 512, 608, 624, 640, 641):
        inside = t_bus_tau(W) <= c_bus(1.22)
        print(f"{W:>6} {m(W):>4} {t_bus_tau(W):>10.2f} {t_step2_tau(W):>12.2f} "
              f"{'Yes' if inside else 'No':>8}")
