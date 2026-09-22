// CARRY4-Ripple adder.
// Uses Xilinx CARRY4 primitives explicitly. Combinational.
// W must be a multiple of 4.

module carry4_ripple #(
    parameter int W = 64
) (
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic [W-1:0] S,
    output logic         Cout
);

    localparam int N = W / 4;

    logic [W:0] C;
    assign C[0] = Cin;

    genvar b, j;
    generate
        for (b = 0; b < N; b++) begin : g_slice
            logic [3:0] co;
            logic [3:0] o;

            CARRY4 u_carry4 (
                .CO     (co),
                .O      (o),
                .CI     (C[4*b]),
                .CYINIT (1'b0),
                .DI     ({A[4*b+3] & B[4*b+3],
                          A[4*b+2] & B[4*b+2],
                          A[4*b+1] & B[4*b+1],
                          A[4*b+0] & B[4*b+0]}),
                .S      ({A[4*b+3] ^ B[4*b+3],
                          A[4*b+2] ^ B[4*b+2],
                          A[4*b+1] ^ B[4*b+1],
                          A[4*b+0] ^ B[4*b+0]})
            );

            assign C[4*b+4] = co[3];
            assign S[4*b+3:4*b] = o;
        end
    endgenerate

    assign Cout = C[W];

endmodule
