// Kogge-Stone pipelined adder.
// One prefix-tree level per clock cycle. Initiation interval II = 1.
// N_cyc = ceil(log2(W)) + 1 (final sum stage is the +1).
// All pipeline registers share the same enable.

module kogge_stone_pipelined #(
    parameter int W = 64
) (
    input  logic         clk,
    input  logic         rst_n,
    input  logic         valid_in,
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic         valid_out,
    output logic [W-1:0] S,
    output logic         Cout
);

    localparam int LEVELS = $clog2(W);
    localparam int STAGES = LEVELS + 1;   // +1 for the sum stage

    logic [W-1:0] p [0:LEVELS];
    logic [W-1:0] g [0:LEVELS];
    logic [W-1:0] p_r [0:LEVELS];
    logic [W-1:0] g_r [0:LEVELS];
    logic         cin_r [0:STAGES];
    logic         vld_r [0:STAGES];

    // Stage 0: input registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            p_r[0] <= '0;
            g_r[0] <= '0;
            cin_r[0] <= 1'b0;
            vld_r[0] <= 1'b0;
        end else begin
            p_r[0] <= A ^ B;
            g_r[0] <= A & B;
            cin_r[0] <= Cin;
            vld_r[0] <= valid_in;
        end
    end

    assign p[0] = p_r[0];
    assign g[0] = g_r[0];

    // Prefix levels
    genvar s, i;
    generate
        for (s = 0; s < LEVELS; s++) begin : g_level
            logic [W-1:0] g_next, p_next;
            for (i = 0; i < W; i++) begin : g_bit
                if (i >= (1 << s)) begin : g_active
                    assign g_next[i] = g[s][i] | (p[s][i] & g[s][i - (1 << s)]);
                    assign p_next[i] = p[s][i] & p[s][i - (1 << s)];
                end else begin : g_pass
                    assign g_next[i] = g[s][i];
                    assign p_next[i] = p[s][i];
                end
            end

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    p_r[s+1] <= '0;
                    g_r[s+1] <= '0;
                    cin_r[s+1] <= 1'b0;
                    vld_r[s+1] <= 1'b0;
                end else begin
                    p_r[s+1] <= p_next;
                    g_r[s+1] <= g_next;
                    cin_r[s+1] <= cin_r[s];
                    vld_r[s+1] <= vld_r[s];
                end
            end
        end
    endgenerate

    assign p[LEVELS] = p_r[LEVELS];
    assign g[LEVELS] = g_r[LEVELS];

    // Final sum stage
    logic [W-1:0] S_next;
    logic         Cout_next;

    generate
        for (i = 0; i < W; i++) begin : g_sum
            assign S_next[i] = p[0][i] ^ (g[LEVELS][i-1 < 0 ? 0 : i-1] |
                                          (p[LEVELS][i] & cin_r[LEVELS]));
        end
    endgenerate
    assign Cout_next = g[LEVELS][W-1] | (p[LEVELS][W-1] & cin_r[LEVELS]);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            S <= '0;
            Cout <= 1'b0;
            valid_out <= 1'b0;
        end else begin
            S <= S_next;
            Cout <= Cout_next;
            valid_out <= vld_r[LEVELS];
        end
    end

endmodule
