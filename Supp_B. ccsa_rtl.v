//-----------------------------------------------------------------------------
// ccsa_rtl.v -- Carry-Chain-Separation Adder (CCSA), Variant B
//
// Contents:
//   ccsa_comb #(W) : single-cycle combinational implementation (Step 1-4
//                    unrolled; useful for formal equivalence checking).
//   ccsa_seq  #(W) : four-cycle sequential implementation with reused
//                    register banks U, L, M (the FPGA-validated design).
//
// All logic uses gates with fan-in <= 3. Global Bus 1 / Bus 2 behaviour is
// modelled by the boundary-controlled switching network of Section 8.4.
// In the FPGA fabric the transmission gates are realised as LUT muxes; in
// a custom ASIC they are CMOS pass gates (Section 1.2).
//-----------------------------------------------------------------------------
`timescale 1ns/1ps

module ccsa_comb #(parameter W = 32) (
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output wire [W:0]   S
);
    // -- Step 1: vertical half-addition (Section 8.4) -----------------------
    wire [W-1:0] U1 = A ^ B;
    wire [W-1:0] L1 = A & B;

    // Extended grids: index i corresponds to bit position l = i-1, so
    // i=0 is the virtual cell l=-1 and i=W+1 the virtual cell l=n+1,
    // both hardwired to zero (Section 8.2).
    wire [W+1:0] U1x = {1'b0, U1, 1'b0};
    wire [W+1:0] L1x = {1'b0, L1, 1'b0};

    // -- Step 2: boundary-controlled switching ------------------------------
    wire [W-1:0] R, Lambda, B2, E, U2, L2, M;
    genvar l;
    generate
        for (l = 0; l < W; l = l + 1) begin : STEP2
            assign R[l]     = U1x[l+1] & ~U1x[l] & ~L1x[l];   // right boundary
            assign Lambda[l]= ~U1x[l+1] & U1x[l];             // left boundary
            if (l == 0) begin
                assign B2[l] = R[l];                          // B2[-1] = 0
            end else begin
                assign B2[l] = R[l] | (B2[l-1] & ~Lambda[l]); // Bus 2 recurrence
            end
            assign E[l]  = B2[l] & U1x[l+1];                  // rewrite-enable
            assign U2[l] = U1x[l+1] & ~E[l];
            assign L2[l] = L1x[l+1] | E[l];
            assign M[l]  = E[l];
        end
    endgenerate

    wire [W+1:0] U2x = {1'b0, U2, 1'b0};
    wire [W+1:0] L2x = {1'b0, L2, 1'b0};
    wire [W+1:0] Mx  = {1'b0, M,  1'b0};

    // -- Step 3: carry-chain inversion (Variant B, Section 8.4) -------------
    wire [W:0]   U3;
    wire [W-1:0] L3;
    generate
        for (l = 0; l <= W; l = l + 1) begin : STEP3U
            assign U3[l] = (~U2x[l+1] & U2x[l]) |
                           (~Mx[l] & L2x[l] & ~U2x[l] & ~U2x[l+1]);
        end
        for (l = 0; l < W; l = l + 1) begin : STEP3L
            assign L3[l] = L2x[l+1] & Mx[l+1];
        end
    endgenerate

    // -- Step 4: collision-free merge (Proposition 1: OR == ADD) ------------
    generate
        for (l = 0; l < W; l = l + 1) begin : STEP4
            assign S[l] = U3[l] | L3[l];
        end
    endgenerate
    assign S[W] = U3[W];   // carry-out / left-boundary bit at position n+1
endmodule


//-----------------------------------------------------------------------------
// Sequential CCSA: one algorithmic step per clock cycle (Section 8.2).
// Phase enables are implicit in the FSM state (2-bit step counter).
//-----------------------------------------------------------------------------
module ccsa_seq #(parameter W = 32) (
    input  wire         clk,
    input  wire         rst,      // synchronous, active high
    input  wire         start,    // pulse high for one cycle in IDLE
    input  wire [W-1:0] A,
    input  wire [W-1:0] B,
    output reg          done,     // high for one cycle when S is valid
    output reg  [W:0]   S
);
    localparam PH_IDLE = 3'd0, PH1 = 3'd1, PH2 = 3'd2,
               PH3 = 3'd3, PH4 = 3'd4, PH_DONE = 3'd5;
    reg [2:0]   ph;
    reg [W:0]   Uq, Lq;      // register banks reused every cycle
    reg [W-1:0] Mq;

    // -- Step-2 combinational logic evaluated on the current (Uq, Lq) -------
    wire [W+1:0] Uqx = {1'b0, Uq[W-1:0], 1'b0};
    wire [W+1:0] Lqx = {1'b0, Lq[W-1:0], 1'b0};
    wire [W-1:0] s2R, s2Lambda, s2B2, s2E, s2U2, s2L2;
    genvar l;
    generate
        for (l = 0; l < W; l = l + 1) begin : S2
            assign s2R[l]      = Uqx[l+1] & ~Uqx[l] & ~Lqx[l];
            assign s2Lambda[l] = ~Uqx[l+1] & Uqx[l];
            if (l == 0) begin
                assign s2B2[l] = s2R[l];
            end else begin
                assign s2B2[l] = s2R[l] | (s2B2[l-1] & ~s2Lambda[l]);
            end
            assign s2E[l]  = s2B2[l] & Uqx[l+1];
            assign s2U2[l] = Uqx[l+1] & ~s2E[l];
            assign s2L2[l] = Lqx[l+1] | s2E[l];
        end
    endgenerate

    // -- Step-3 combinational logic evaluated on the current (Uq, Lq, Mq) ---
    wire [W+1:0] Mqx = {1'b0, Mq, 1'b0};
    wire [W:0]   s3U3;
    wire [W-1:0] s3L3;
    generate
        for (l = 0; l <= W; l = l + 1) begin : S3U
            assign s3U3[l] = (~Uqx[l+1] & Uqx[l]) |
                             (~Mqx[l] & Lqx[l] & ~Uqx[l] & ~Uqx[l+1]);
        end
        for (l = 0; l < W; l = l + 1) begin : S3L
            assign s3L3[l] = Lqx[l+1] & Mqx[l+1];
        end
    endgenerate

    // -- FSM -----------------------------------------------------------------
    always @(posedge clk) begin
        if (rst) begin
            ph <= PH_IDLE; done <= 1'b0; S <= {(W+1){1'b0}};
            Uq <= {(W+1){1'b0}}; Lq <= {(W+1){1'b0}}; Mq <= {W{1'b0}};
        end else begin
            case (ph)
                PH_IDLE: if (start) begin          // Step 1
                    Uq  <= {1'b0, A ^ B};
                    Lq  <= {1'b0, A & B};
                    Mq  <= {W{1'b0}};
                    done <= 1'b0;
                    ph  <= PH2;
                end
                PH2: begin                          // boundary switching
                    Uq <= {1'b0, s2U2};
                    Lq <= {1'b0, s2L2};
                    Mq <= s2E;
                    ph <= PH3;
                end
                PH3: begin                          // carry-chain inversion
                    Uq <= s3U3;
                    Lq <= {1'b0, s3L3};
                    ph <= PH4;
                end
                PH4: begin                          // collision-free merge
                    S    <= Uq | Lq;
                    done <= 1'b1;
                    ph   <= PH_DONE;
                end
                PH_DONE: begin
                    done <= 1'b0;
                    ph   <= PH_IDLE;
                end
                default: ph <= PH_IDLE;
            endcase
        end
    end
endmodule
