// =====================================================================
// carry_skip_adder.sv
//
// Carry-skip (carry-bypass) adder baseline (Section 2.2).
//
// Fixed BLOCK-bit blocks. Each block computes:
//   pblk   = AND of per-bit propagate signals inside the block
//   lc     = intra-block ripple, seeded by the block carry-in bc[b]
//   bc[b+1]= (pblk & bc[b]) | lc[BLOCK]      (the skip mux)
//   c[bit] = (pblk & bc[b]) | lc[bit]        (carry into each bit)
//
// Functionally computes S = A + B with W+1 bits.
//
// NOTE: the reference design uses BLOCK=8 and widths that are
// multiples of 8 (8, 16, 32, 64, 128, 256). The block slicing below
// assumes W % BLOCK == 0, which holds for every width reported in the
// manuscript.
// =====================================================================
`timescale 1ns/1ps

module carry_skip_adder #(
    parameter integer W = 8,
    parameter integer BLOCK = 8
)(
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output wire [W:0]   S
);

    localparam integer NBLK = W / BLOCK;   // requires W % BLOCK == 0

    wire [W:0] p, g, c;
    wire [NBLK:0] bc;                       // bc[0]=0, bc[NBLK]=carry-out

    assign p[0]  = 1'b0;
    assign g[0]  = 1'b0;
    assign c[0]  = 1'b0;
    assign bc[0] = 1'b0;

    genvar i, b;
    generate
        for (i = 0; i < W; i = i + 1) begin : g_pg
            assign p[i+1] = A[i] ^ B[i];
            assign g[i+1] = A[i] & B[i];
        end
    endgenerate

    generate
        for (b = 0; b < NBLK; b = b + 1) begin : g_block
            // Block propagate: AND of p over the block.
            wire pblk;
            assign pblk = &p[(b+1)*BLOCK : b*BLOCK + 1];

            // Intra-block ripple carry, seeded by bc[b].
            wire [BLOCK:0] lc;
            assign lc[0] = bc[b];
            for (i = 0; i < BLOCK; i = i + 1) begin : g_rip
                assign lc[i+1] = g[b*BLOCK + i + 1] |
                                 (p[b*BLOCK + i + 1] & lc[i]);
            end

            // Skip mux: block carry-out.
            assign bc[b+1] = (pblk & bc[b]) | lc[BLOCK];

            // Carry into each bit within the block.
            for (i = 0; i < BLOCK; i = i + 1) begin : g_carry
                assign c[b*BLOCK + i] = (pblk & bc[b]) | lc[i];
            end
        end
    endgenerate

    generate
        for (i = 0; i < W; i = i + 1) begin : g_sum
            assign S[i] = p[i+1] ^ c[i];
        end
    endgenerate
    assign S[W] = bc[NBLK];

endmodule
