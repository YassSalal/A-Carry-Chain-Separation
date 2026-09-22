// Kogge-Stone parallel-prefix adder, fully combinational.
// Single-cycle prefix tree of depth ceil(log2(W)).

module kogge_stone_comb #(
    parameter int W = 64
) (
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic [W-1:0] S,
    output logic         Cout
);

    logic [W-1:0] p [0:$clog2(W)];
    logic [W-1:0] g [0:$clog2(W)];

    assign p[0] = A ^ B;
    assign g[0] = A & B;

    genvar s, i;
    generate
        for (s = 0; s < $clog2(W); s++) begin : g_level
            for (i = 0; i < W; i++) begin : g_bit
                if (i >= (1 << s)) begin : g_active
                    assign g[s+1][i] = g[s][i] | (p[s][i] & g[s][i - (1 << s)]);
                    assign p[s+1][i] = p[s][i] & p[s][i - (1 << s)];
                end else begin : g_pass
                    assign g[s+1][i] = g[s][i];
                    assign p[s+1][i] = p[s][i];
                end
            end
        end
    endgenerate

    // Carry into bit i = g_final[i-1], with C[0] = Cin
    logic [W:0] C;
    assign C[0] = Cin;

    generate
        for (i = 0; i < W; i++) begin : g_sum
            assign C[i+1] = g[$clog2(W)][i] | (p[$clog2(W)][i] & Cin);
            assign S[i]   = p[0][i] ^ C[i];
        end
    endgenerate

    assign Cout = C[W];

endmodule
