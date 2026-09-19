// =====================================================================
// kogge_stone_adder.sv
//
// Kogge-Stone parallel-prefix adder baseline (Section 9, Table 10).
//
// Two top modules are provided:
//   ks_adder_pipelined : one prefix-tree level per clock cycle.
//                        N_cyc = ceil(log2(W)) + 1.
//   ks_adder_flat      : full prefix tree combinational, N_cyc = 1.
//
// Both compute S = A + B with W+1 bits. The pipelined version captures
// inputs on `start`, streams through LEVELS pipeline registers, and
// raises `done` when the result is valid; `S` is the registered sum.
// =====================================================================
`timescale 1ns/1ps

// ---------------------------------------------------------------------
// Combinational Kogge-Stone
// ---------------------------------------------------------------------
module ks_adder_flat #(
    parameter integer W = 8
)(
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output wire [W:0]   S
);

    localparam integer LEVELS = (W <= 1) ? 0 : $clog2(W);

    wire [W-1:0] p [0:LEVELS];
    wire [W-1:0] g [0:LEVELS];

    genvar i, k;
    generate
        for (i = 0; i < W; i = i + 1) begin : g_level0
            assign p[0][i] = A[i] ^ B[i];
            assign g[0][i] = A[i] & B[i];
        end

        for (k = 1; k <= LEVELS; k = k + 1) begin : g_level
            localparam integer DIST = 1 << (k-1);
            for (i = 0; i < W; i = i + 1) begin : g_bit
                if (i >= DIST) begin : shifted
                    assign p[k][i] = p[k-1][i] & p[k-1][i - DIST];
                    assign g[k][i] = g[k-1][i] |
                                     (p[k-1][i] & g[k-1][i - DIST]);
                end else begin : unshifted
                    assign p[k][i] = p[k-1][i];
                    assign g[k][i] = g[k-1][i];
                end
            end
        end
    endgenerate

    assign S[0] = p[0][0];                       // c_0 = 0
    generate
        for (i = 1; i < W; i = i + 1) begin : g_sum
            assign S[i] = p[0][i] ^ g[LEVELS][i];
        end
    endgenerate
    assign S[W] = g[LEVELS][W-1];

endmodule


// ---------------------------------------------------------------------
// Pipelined Kogge-Stone
// ---------------------------------------------------------------------
module ks_adder_pipelined #(
    parameter integer W = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                start,
    input  wire [W-1:0]        A,
    input  wire [W-1:0]        B,
    output wire [W:0]          S,
    output wire                done
);

    localparam integer LEVELS = (W <= 1) ? 0 : $clog2(W);
    localparam integer N_CYC  = LEVELS + 1;

    reg [W-1:0] p_r [0:LEVELS];
    reg [W-1:0] g_r [0:LEVELS];
    reg [W-1:0] p0_r;

    reg [N_CYC-1:0] valid_pipe;

    wire [W-1:0] p_in = A ^ B;
    wire [W-1:0] g_in = A & B;

    integer i;
    genvar k;
    generate
        for (k = 1; k <= LEVELS; k = k + 1) begin : g_pipe
            localparam integer DIST = 1 << (k-1);
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    p_r[k] <= '0;
                    g_r[k] <= '0;
                end else begin
                    for (i = 0; i < W; i = i + 1) begin
                        if (i >= DIST) begin
                            p_r[k][i] <= p_r[k-1][i] & p_r[k-1][i - DIST];
                            g_r[k][i] <= g_r[k-1][i] |
                                         (p_r[k-1][i] & g_r[k-1][i - DIST]);
                        end else begin
                            p_r[k][i] <= p_r[k-1][i];
                            g_r[k][i] <= g_r[k-1][i];
                        end
                    end
                end
            end
        end
    endgenerate

    // Level 0: capture inputs on start.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            p_r[0] <= '0;
            g_r[0] <= '0;
            p0_r   <= '0;
        end else if (start) begin
            p_r[0] <= p_in;
            g_r[0] <= g_in;
            p0_r   <= p_in;
        end
    end

    // Valid pipeline.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) valid_pipe <= '0;
        else        valid_pipe <= {valid_pipe[N_CYC-2:0], start};
    end

    // Final sum: S[i] = p0[i] ^ c[i], with c[i] = g_r[LEVELS][i].
    wire [W:0] sum_comb;
    assign sum_comb[0] = p0_r[0];
    generate
        for (k = 1; k < W; k = k + 1) begin : g_sum
            assign sum_comb[k] = p0_r[k] ^ g_r[LEVELS][k];
        end
    endgenerate
    assign sum_comb[W] = g_r[LEVELS][W-1];

    assign S    = sum_comb;
    assign done = valid_pipe[N_CYC-1];

endmodule
