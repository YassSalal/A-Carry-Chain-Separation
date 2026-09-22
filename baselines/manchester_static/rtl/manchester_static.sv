// Manchester-static adder: static CMOS control, no precharge, no segmentation.
// Same chain topology as Manchester-ripple, but gates expressed explicitly
// with NAND/NOR/AND/OR structure to reflect the static-control design.
// Combinational: no clock.

module manchester_static #(
    parameter int W = 64
) (
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic [W-1:0] S,
    output logic         Cout
);

    logic [W:0] C;
    logic [W-1:0] P, G, K;

    assign C[0] = Cin;

    genvar i;
    generate
        for (i = 0; i < W; i++) begin : g_static
            assign P[i] = A[i] ^ B[i];
            assign G[i] = A[i] & B[i];
            assign K[i] = ~(A[i] | B[i]);
            // Static carry: G + (P . C)
            assign C[i+1] = G[i] | (P[i] & C[i]);
            assign S[i]   = P[i] ^ C[i];
        end
    endgenerate

    assign Cout = C[W];

endmodule
