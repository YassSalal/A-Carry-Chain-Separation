// Manchester-ripple adder (classical, no segmentation, no static control).
// Gate-level LUT implementation. Carry ripples through all W positions.
// Combinational: no clock, no registers.

module manchester_ripple #(
    parameter int W = 64
) (
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic [W-1:0] S,
    output logic         Cout
);

    logic [W:0] C;
    logic [W-1:0] P, G;

    assign C[0] = Cin;

    genvar i;
    generate
        for (i = 0; i < W; i++) begin : g_manch
            assign P[i] = A[i] ^ B[i];
            assign G[i] = A[i] & B[i];
            // Manchester mux: carry propagates through P switch
            assign C[i+1] = G[i] | (P[i] & C[i]);
            assign S[i]   = P[i] ^ C[i];
        end
    endgenerate

    assign Cout = C[W];

endmodule
