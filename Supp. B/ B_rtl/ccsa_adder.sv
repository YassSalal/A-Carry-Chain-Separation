// =====================================================================
// ccsa_adder.sv
//
// Carry-Chain-Separation Architecture (CCSA), Variant B.
// Sequential multi-cycle implementation of Algorithm 1 (Section 7.3.1).
//
//   - State arrays are W+1 positions wide (indices 0..W).
//   - Output S is W+1 bits (canonical sum, including carry-out).
//   - Step 3 uses the *shifted* neighbour l-1.
//   - Step 4 merges *registered* U3, L3 outputs (no recomputation).
//
// This file matches the normative equations of the manuscript exactly.
// See REPRODUCE.md for the equation-to-line mapping.
// =====================================================================
`timescale 1ns/1ps

module ccsa_adder #(
    parameter integer W = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                start,
    input  wire [W-1:0]        A,
    input  wire [W-1:0]        B,
    output reg  [W:0]          S,       // W+1-bit canonical sum
    output reg                 done
);

    // ---- Phase encoding ------------------------------------------------
    localparam [2:0] PH_IDLE  = 3'd0,
                     PH_STEP1 = 3'd1,
                     PH_STEP2 = 3'd2,
                     PH_STEP3 = 3'd3,
                     PH_STEP4 = 3'd4,
                     PH_DONE  = 3'd5;

    reg [2:0] phase;

    // ---- Registered state, indices 0..W --------------------------------
    reg [W:0] U1, L1;
    reg [W:0] U2, L2, M2;
    reg [W:0] U3, L3;

    // ---- Combinational next-state wires --------------------------------
    wire [W:0] U1_nxt, L1_nxt;
    wire [W:0] U2_nxt, L2_nxt, M2_nxt;
    wire [W:0] U3_nxt, L3_nxt;
    wire [W:0] U4_nxt;

    // ---- Shifted neighbours: prev[i] = arr[i-1], prev[0] = 0 -----------
    wire [W:0] U1_prev = {U1[W-1:0], 1'b0};
    wire [W:0] L1_prev = {L1[W-1:0], 1'b0};
    wire [W:0] U2_prev = {U2[W-1:0], 1'b0};
    wire [W:0] L2_prev = {L2[W-1:0], 1'b0};
    wire [W:0] M2_prev = {M2[W-1:0], 1'b0};

    // ---- Step 1: vertical half-addition --------------------------------
    genvar l;
    generate
        for (l = 0; l < W; l = l + 1) begin : g_step1
            assign U1_nxt[l] = A[l] ^ B[l];
            assign L1_nxt[l] = A[l] & B[l];
        end
        assign U1_nxt[W] = 1'b0;   // virtual boundary at index W
        assign L1_nxt[W] = 1'b0;
    endgenerate

    // ---- Step 2: boundary detection and dual-bus switching -------------
    wire [W:0] R_w, Lam_w, B2_w, E_w;

    assign R_w   = U1 & ~U1_prev & ~L1_prev;
    assign Lam_w = ~U1 & U1_prev;

    assign B2_w[0] = R_w[0];
    generate
        for (l = 1; l <= W; l = l + 1) begin : g_bus2
            assign B2_w[l] = R_w[l] | (B2_w[l-1] & ~Lam_w[l]);
        end
    endgenerate

    assign E_w    = B2_w & U1;
    assign U2_nxt = U1 & ~E_w;
    assign L2_nxt = L1 |  E_w;
    assign M2_nxt = E_w;

    // ---- Step 3: carry-chain collapse (shifted neighbours) -------------
    assign U3_nxt = (~U2 & U2_prev) |
                    (~M2_prev & L2_prev & ~U2_prev & ~U2);
    assign L3_nxt = L2 & M2;

    // ---- Step 4: collision-free merge of registered U3, L3 -------------
    assign U4_nxt = U3 | L3;

    // ---- Sequencer -----------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            phase <= PH_IDLE;
            U1 <= '0; L1 <= '0;
            U2 <= '0; L2 <= '0; M2 <= '0;
            U3 <= '0; L3 <= '0;
            S  <= '0;
            done <= 1'b0;
        end else begin
            case (phase)
                PH_IDLE: begin
                    done <= 1'b0;
                    if (start) phase <= PH_STEP1;
                end
                PH_STEP1: begin
                    U1 <= U1_nxt;  L1 <= L1_nxt;
                    phase <= PH_STEP2;
                end
                PH_STEP2: begin
                    U2 <= U2_nxt;  L2 <= L2_nxt;  M2 <= M2_nxt;
                    phase <= PH_STEP3;
                end
                PH_STEP3: begin
                    U3 <= U3_nxt;  L3 <= L3_nxt;
                    phase <= PH_STEP4;
                end
                PH_STEP4: begin
                    S <= U4_nxt;
                    phase <= PH_DONE;
                end
                PH_DONE: begin
                    done <= 1'b1;
                    phase <= PH_IDLE;
                end
                default: phase <= PH_IDLE;
            endcase
        end
    end

endmodule
