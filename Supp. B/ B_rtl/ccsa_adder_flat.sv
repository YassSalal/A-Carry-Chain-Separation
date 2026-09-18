// =====================================================================
// ccsa_adder_flat.sv
//
// Combinational (single-cycle) CCSA, Variant B.
// Implements the same four steps of Algorithm 1 as ccsa_adder.sv, but
// with no pipeline registers. Latency is the post-route critical path.
//
// Output S is W+1 bits.
// =====================================================================
`timescale 1ns/1ps

module ccsa_adder_flat #(
    parameter integer W = 8
)(
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output wire [W:0]   S
);

    // ---- Step 1: vertical half-addition --------------------------------
    wire [W:0] U1, L1;
    genvar l;
    generate
        for (l = 0; l < W; l = l + 1) begin : g_step1
            assign U1[l] = A[l] ^ B[l];
            assign L1[l] = A[l] & B[l];
        end
        assign U1[W] = 1'b0;
        assign L1[W] = 1'b0;
    endgenerate

    // ---- Shifted neighbours --------------------------------------------
    wire [W:0] U1_prev = {U1[W-1:0], 1'b0};
    wire [W:0] L1_prev = {L1[W-1:0], 1'b0};

    // ---- Step 2: boundary detection and dual-bus switching -------------
    wire [W:0] R_w   = U1 & ~U1_prev & ~L1_prev;
    wire [W:0] Lam_w = ~U1 & U1_prev;

    wire [W:0] B2_w;
    assign B2_w[0] = R_w[0];
    generate
        for (l = 1; l <= W; l = l + 1) begin : g_bus2
            assign B2_w[l] = R_w[l] | (B2_w[l-1] & ~Lam_w[l]);
        end
    endgenerate

    wire [W:0] E  = B2_w & U1;
    wire [W:0] U2 = U1 & ~E;
    wire [W:0] L2 = L1 |  E;
    wire [W:0] M  = E;

    // ---- Step 3: carry-chain collapse (shifted neighbours) -------------
    wire [W:0] U2_prev = {U2[W-1:0], 1'b0};
    wire [W:0] L2_prev = {L2[W-1:0], 1'b0};
    wire [W:0] M_prev  = {M [W-1:0], 1'b0};

    wire [W:0] U3 = (~U2 & U2_prev) |
                    (~M_prev & L2_prev & ~U2_prev & ~U2);
    wire [W:0] L3 = L2 & M;

    // ---- Step 4: collision-free merge ----------------------------------
    assign S = U3 | L3;

endmodule