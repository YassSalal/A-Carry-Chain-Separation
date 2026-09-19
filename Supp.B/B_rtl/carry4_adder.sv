// carry4_adder.sv
// Wrapper around Xilinx CARRY4 primitives.
// Two modes selected by parameter PIPELINED.
//   PIPELINED = 0 -> combinational ripple (CARRY4-Ripple row in Table 11)
//   PIPELINED = 1 -> fully pipelined       (CARRY4-Pipelined row in Table 11)
//
// Vivado will map the CARRY4 instantiations to the dedicated carry primitive
// on Artix-7 (XC7A100T). This is what the manuscript refers to as the
// "vendor CARRY4 chain" / "hard-wired, non-gate carry path".

`timescale 1ns / 1ps

module carry4_adder #(
    parameter integer W          = 32,
    parameter integer PIPELINED  = 0
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire [W-1:0]        A,
    input  wire [W-1:0]        B,
    output wire [W:0]          S
);

    // -------- Step 1: propagate / generate --------
    wire [W-1:0] P = A ^ B;
    wire [W-1:0] G = A & B;

    // -------- Step 2: carry chain via CARRY4 primitives --------
    // Each CARRY4 handles 4 bits. Number of slices:
    localparam integer NSLICES = (W + 3) / 4;

    wire [W:0] C;         // C[0] = 0, C[i+1] = carry into bit i
    assign C[0] = 1'b0;

    genvar i;
    generate
        for (i = 0; i < NSLICES; i = i + 1) begin : g_carry
            wire [3:0] CO;
            wire [3:0] O;
            wire [3:0] p_slice;
            wire [3:0] g_slice;

            // Pad the last slice with zeros if W is not a multiple of 4
            assign p_slice = (4*i+3 < W) ? P[4*i +: 4] :
                             (4*i+2 < W) ? {1'b0, P[4*i +: 3]} :
                             (4*i+1 < W) ? {2'b00, P[4*i +: 2]} :
                             (4*i+0 < W) ? {3'b000, P[4*i]} : 4'b0000;
            assign g_slice = (4*i+3 < W) ? G[4*i +: 4] :
                             (4*i+2 < W) ? {1'b0, G[4*i +: 3]} :
                             (4*i+1 < W) ? {2'b00, G[4*i +: 2]} :
                             (4*i+0 < W) ? {3'b000, G[4*i]} : 4'b0000;

            CARRY4 u_carry4 (
                .CO  (CO),
                .O   (O),
                .CI  (C[4*i]),
                .CYINIT(1'b0),
                .DI  (g_slice),
                .S   (p_slice)
            );

            assign C[4*i + 1] = CO[0];
            assign C[4*i + 2] = CO[1];
            assign C[4*i + 3] = CO[2];
            if (4*i + 4 <= W)
                assign C[4*i + 4] = CO[3];
        end
    endgenerate

    // -------- Step 3: sum --------
    wire [W:0] S_comb;
    assign S_comb = {C[W], P} ^ {C[W:0]};  // S[i] = P[i] ^ C[i], S[W] = C[W]

    // -------- Step 4: optional pipelining --------
    // NOTE: for a true one-level-per-cycle pipeline you would register
    // after each CARRY4 slice boundary. The version below registers the
    // whole chain once; replace with a per-slice pipeline if your
    // synthesis script expects N_cyc = ceil(W/4) latency.
    generate
        if (PIPELINED) begin : g_pipe
            reg [W:0] S_q;
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) S_q <= {(W+1){1'b0}};
                else        S_q <= S_comb;
            end
            assign S = S_q;
        end else begin : g_comb
            assign S = S_comb;
        end
    endgenerate

endmodule
