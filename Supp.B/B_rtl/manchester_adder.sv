// =====================================================================
// manchester_adder.sv
//
// Manchester carry-chain baseline (Section 2.2 of the manuscript).
//
// Two coding styles are selected by MANCHESTER_STATIC:
//   0 = classical Manchester: carry modelled as a pass-transistor
//       chain, each stage selecting between local generate and the
//       incoming carry under control of the local propagate signal.
//   1 = static-CMOS control: the same recurrence written with an
//       explicit AND-OR gate per bit, so synthesis maps it to an
//       explicit gate chain rather than a pass-transistor network.
//
// Functionally both variants compute S = A + B with W+1 bits.
// This file is parameterised by W only; no registers, no clock.
// =====================================================================
`timescale 1ns/1ps

module manchester_adder #(
    parameter integer W = 8,
    parameter integer MANCHESTER_STATIC = 0
)(
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output wire [W:0]   S
);

    // Per-bit propagate and generate, indexed 1..W with a virtual
    // boundary at index 0 (p[0]=g[0]=c[0]=0).
    wire [W:0] p, g, c;
    assign p[0] = 1'b0;
    assign g[0] = 1'b0;
    assign c[0] = 1'b0;

    genvar i;
    generate
        for (i = 0; i < W; i = i + 1) begin : g_pg
            assign p[i+1] = A[i] ^ B[i];
            assign g[i+1] = A[i] & B[i];
        end
    endgenerate

    // ---- Carry chain ---------------------------------------------------
    generate
        if (MANCHESTER_STATIC == 0) begin : g_classical
            // Classical Manchester: pass-transistor chain.
            // Each stage either pulls the carry from g[i+1] or lets the
            // previous carry pass through under control of p[i+1].
            for (i = 0; i < W; i = i + 1) begin : g_chain
                assign c[i+1] = g[i+1] | (p[i+1] & c[i]);
            end
        end else begin : g_static
            // Static-CMOS control: explicit AND-OR gate per bit.
            for (i = 0; i < W; i = i + 1) begin : g_chain
                wire and_term;
                assign and_term = p[i+1] & c[i];
                assign c[i+1]   = g[i+1] | and_term;
            end
        end
    endgenerate

    // ---- Sum -----------------------------------------------------------
    generate
        for (i = 0; i < W; i = i + 1) begin : g_sum
            assign S[i] = p[i+1] ^ c[i];
        end
    endgenerate
    assign S[W] = c[W];

endmodule
