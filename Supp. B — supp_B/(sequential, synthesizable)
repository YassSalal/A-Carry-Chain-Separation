//============================================================================
// ccsA_variant_B — Carry-Chain-Separation Adder, Variant B
// Supplementary Material B — synthesizable Verilog-2001
//
// Marker-aware implementation. The marker register M is load-bearing for
// the stage-relative invariant V^(2)(U,L,M) and for the Step-3 carry-chain
// collapse. It must not be optimized away, retimed, or replaced by a
// combinational alias of E.
//============================================================================
module ccsA_variant_B #(
    parameter W = 64
) (
    input  wire              clk,
    input  wire              rst_n,
    input  wire              start,
    input  wire [W-1:0]      A,
    input  wire [W-1:0]      B,
    output reg  [W-1:0]      S,
    output wire              done
);

    // -----------------------------------------------------------------------
    // B.3 Phase control
    // -----------------------------------------------------------------------
    reg [2:0] step;              // 0 = idle, 1..4 = phi1..phi4
    wire phi1 = (step == 3'd1);
    wire phi2 = (step == 3'd2);
    wire phi3 = (step == 3'd3);
    wire phi4 = (step == 3'd4);
    assign done = (step == 3'd4);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            step <= 3'd0;
        else if (step == 3'd0)
            step <= start ? 3'd1 : 3'd0;
        else if (step == 3'd4)
            step <= 3'd0;         // return to idle after the result is latched
        else
            step <= step + 3'd1;
    end

    // -----------------------------------------------------------------------
    // B.4 State registers
    //
    // U, L are written every phase. M is written only at phi2 and retained
    // through phi3 and phi4 (no write in those phases). The preserve
    // attributes are essential: removing M changes the semantics of Step 3.
    // -----------------------------------------------------------------------
    (* preserve = "true" *) reg [W-1:0] U;
    (* preserve = "true" *) reg [W-1:0] L;
    (* preserve = "true" *) reg [W-1:0] M;   // marker: written only at phi2

    // -----------------------------------------------------------------------
    // B.5 Step 1 — Vertical half-addition (phi1)
    //
    // U1[l] = A[l] ^ B[l],  L1[l] = A[l] & B[l]
    // -----------------------------------------------------------------------
    wire [W-1:0] U1_c = A ^ B;
    wire [W-1:0] L1_c = A & B;

    // -----------------------------------------------------------------------
    // B.6 Step 2 — Boundary-controlled switching (phi2)
    //
    // R[l]    = U[l] & ~U[l-1] & ~L[l-1]
    // Lam[l]  = ~U[l] & U[l-1]
    // B2[l]   = R[l] | (B2[l-1] & ~Lam[l]),   B2[-1] = 0
    // E[l]    = B2[l] & U[l]
    // U2[l]   = U[l] & ~E[l]
    // L2[l]   = L[l] | E[l]
    // M[l]    = E[l]
    //
    // During phi2, the register bank U, L holds U1, L1.
    // -----------------------------------------------------------------------
    wire [W-1:0] R, Lam, B2, E;
    wire [W-1:0] U2_c, L2_c;

    genvar g;
    generate
        for (g = 0; g < W; g = g + 1) begin : g_step2
            wire u1_l  = U[g];
            wire u1_lm = (g == 0) ? 1'b0 : U[g-1];
            wire l1_lm = (g == 0) ? 1'b0 : L[g-1];
            wire b2_lm = (g == 0) ? 1'b0 : B2[g-1];

            // Right-boundary detector
            assign R[g]   = u1_l & ~u1_lm & ~l1_lm;

            // Left-boundary detector
            assign Lam[g] = ~u1_l & u1_lm;

            // Bus 2 recurrence (LSB -> MSB)
            assign B2[g]  = R[g] | (b2_lm & ~Lam[g]);
        end
    endgenerate

    assign E    = B2 & U;
    assign U2_c = U & ~E;
    assign L2_c = L | E;

    // -----------------------------------------------------------------------
    // B.7 Step 3 — Carry-chain collapse, Variant B (phi3)
    //
    // U3[l] = (~U2[l] & U2[l-1])
    //       | (~M[l-1] & L2[l-1] & ~U2[l-1] & ~U2[l])
    // L3[l] = L2[l] & M[l]
    //
    // Factored form used in RTL:
    //   U3[l] = ~U2[l] & ( U2[l-1] | (~M[l-1] & L2[l-1] & ~U2[l-1]) )
    //
    // During phi3, the register bank U, L holds U2, L2 and M holds the
    // registered marker from phi2.
    // -----------------------------------------------------------------------
    wire [W-1:0] U3_c, L3_c;
    generate
        for (g = 0; g < W; g = g + 1) begin : g_step3
            wire u2_l  = U[g];
            wire u2_lm = (g == 0) ? 1'b0 : U[g-1];
            wire l2_lm = (g == 0) ? 1'b0 : L[g-1];
            wire m_lm  = (g == 0) ? 1'b0 : M[g-1];

            assign U3_c[g] = ~u2_l & ( u2_lm | (~m_lm & l2_lm & ~u2_lm) );
            assign L3_c[g] = L[g] & M[g];
        end
    endgenerate

    // -----------------------------------------------------------------------
    // B.8 Step 4 — Collision-free merge (phi4)
    //
    // U4[l] = U3[l] | L3[l],  L4[l] = 0
    //
    // During phi4, U, L hold U3, L3.
    // -----------------------------------------------------------------------
    wire [W-1:0] U4_c = U | L;
    // L4 is identically zero; no register is needed for it.

    // -----------------------------------------------------------------------
    // B.9 Register update
    //
    // U and L are loaded at every phase. M is loaded only at phi2 and
    // retains its value through phi3 and phi4.
    // -----------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            U <= {W{1'b0}};
            L <= {W{1'b0}};
            M <= {W{1'b0}};
            S <= {W{1'b0}};
        end else begin
            if (phi1) begin
                U <= U1_c;
                L <= L1_c;
            end
            if (phi2) begin
                U <= U2_c;
                L <= L2_c;
                M <= E;              // marker captured here; never derived later
            end
            if (phi3) begin
                U <= U3_c;
                L <= L3_c;
                // M is deliberately NOT assigned here; it retains E from phi2.
            end
            if (phi4) begin
                U <= U4_c;
                L <= {W{1'b0}};
                S <= U4_c;           // registered output
            end
        end
    end

endmodule
