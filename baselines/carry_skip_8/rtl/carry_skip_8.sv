// Carry-skip adder with fixed 8-bit blocks.
// Each block computes its own ripple carry, a block-propagate P_block,
// and a bypass mux that routes the block carry-in to carry-out when
// P_block = 1. Combinational: no clock.

module carry_skip_8 #(
    parameter int W = 64
) (
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic [W-1:0] S,
    output logic         Cout
);

    localparam int BITS = 8;
    localparam int NBLK = (W + BITS - 1) / BITS;

    logic [W:0] C;
    logic [NBLK-1:0] Pblk;

    assign C[0] = Cin;

    genvar b, j;
    generate
        for (b = 0; b < NBLK; b++) begin : g_block
            logic [BITS:0] c_int;
            logic [BITS-1:0] p, g;
            logic [BITS-1:0] p_used;

            assign c_int[0] = C[b*BITS];

            for (j = 0; j < BITS; j++) begin : g_bit
                if ((b*BITS + j) < W) begin : g_valid
                    assign p[j] = A[b*BITS+j] ^ B[b*BITS+j];
                    assign g[j] = A[b*BITS+j] & B[b*BITS+j];
                    assign p_used[j] = p[j];
                    assign c_int[j+1] = g[j] | (p[j] & c_int[j]);
                    assign S[b*BITS+j] = p[j] ^ c_int[j];
                end else begin : g_pad
                    assign p[j] = 1'b0;
                    assign g[j] = 1'b0;
                    assign p_used[j] = 1'b1;   // neutral for block propagate
                    assign c_int[j+1] = c_int[j];
                end
            end

            assign Pblk[b] = &p_used;
            // Bypass mux: if block propagates, carry-out = carry-in
            assign C[(b+1)*BITS > W ? W : (b+1)*BITS] =
                   Pblk[b] ? C[b*BITS] : c_int[BITS];
        end
    endgenerate

    assign Cout = C[W];

endmodule
