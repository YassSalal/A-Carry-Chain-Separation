"""
Reproduce Appendix B, Tables 1.2 and 1.3 of the manuscript.
"""

TAU_PS = 12.0

def t_seg_tau(k=16, s=8):
    # Corrected Elmore value reported in Section 7.4, including
    # k * R_HSW series resistance.
    return 2.34

def t_bus_tau(W, k=16):
    return 2.34 * (W // k) + 0.5

def t_step2_tau(W, k=16):
    return 2.34 * (W // k) + 5.5

def c_bus(T_clk_ns, tau_ps=TAU_PS):
    return (T_clk_ns * 1000.0 - 6 * tau_ps) / tau_ps

def W_max(T_clk_ns, k=16):
    budget = c_bus(T_clk_ns)
    W = 0
    while t_bus_tau(W + 1, k) <= budget:
        W += 1
    return W, budget

def print_block(T_clk_ns, widths, label):
    Wmax, budget = W_max(T_clk_ns)
    print(f"\nBlock {label}: T_clk = {T_clk_ns} ns, c_bus = {budget:.1f}, W_max = {Wmax}")
    print(f"{'W':>5} {'m(W)':>6} {'t_bus/tau':>10} {'t_step2/tau':>12} within?")
    for W in widths:
        m = W // 16
        tb = t_bus_tau(W)
        ts = t_step2_tau(W)
        print(f"{W:>5} {m:>6} {tb:>10.2f} {ts:>12.2f} {'yes' if tb <= budget else 'NO'}")

if __name__ == "__main__":
    print_block(1.22, [8,16,32,64,128,256,512,608,624,640,641], "A")
    print_block(1.50, [256,512,608,624,640,800,801], "B")