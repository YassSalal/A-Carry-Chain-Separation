systemverilog
// =====================================================================
// CCSA Variant B - self-checking SystemVerilog testbench
// Contains corrected SVA assertions matching Section 6 of the manuscript.
// =====================================================================
`timescale 1ns/1ps

module tb_ccsa;

    localparam integer W = 8;

    logic              clk;
    logic              rst_n;
    logic              start;
    logic [W-1:0]      A, B;
    logic [W-1:0]      S;
    logic              done;

    // -----------------------------------------------------------------
    // DUT
    // -----------------------------------------------------------------
    ccsa #(.W(W)) dut (
        .clk(clk), .rst_n(rst_n), .start(start),
        .A(A), .B(B), .S(S), .done(done)
    );

    // -----------------------------------------------------------------
    // Clock
    // -----------------------------------------------------------------
    initial clk = 1'b0;
    always #0.5 clk = ~clk;   // 1 ns period

    // -----------------------------------------------------------------
    // Reference model
    // -----------------------------------------------------------------
    function automatic logic [W-1:0] ref_add(input logic [W-1:0] a,
                                             input logic [W-1:0] b);
        return a + b;
    endfunction

    // -----------------------------------------------------------------
    // Stage-relative invariant functions (mirror of Supp. A)
    // -----------------------------------------------------------------
    function automatic int unsigned V1(input logic [W-1:0] U,
                                       input logic [W-1:0] L);
        int unsigned acc = 0;
        for (int l = 0; l < W; l++) begin
            acc += U[l] << l;
            acc += L[l] << (l + 1);
        end
        return acc;
    endfunction

    function automatic int unsigned V2(input logic [W-1:0] U,
                                       input logic [W-1:0] L,
                                       input logic [W-1:0] M);
        int unsigned acc = 0;
        for (int l = 0; l < W; l++) begin
            acc += U[l] << l;
            acc += L[l] * M[l] << l;
            acc += L[l] * (1 - M[l]) << (l + 1);
        end
        return acc;
    endfunction

    function automatic int unsigned V3(input logic [W-1:0] U,
                                       logic [W-1:0] L);
        int unsigned acc = 0;
        for (int l = 0; l < W; l++) acc += (U[l] + L[l]) << l;
        return acc;
    endfunction

    // -----------------------------------------------------------------
    // SVA assertions
    // -----------------------------------------------------------------
    // a_step_value_preserve: stage-indexed invariant.
    // Step 1 (after first clock edge of a transaction):
    //   V1(dut.U, dut.L) == A + B
    // Step 2 (after second clock edge):
    //   V2(dut.U, dut.L, dut.M) == A + B
    // Step 3 (after third clock edge):
    //   V3(dut.U, dut.L) == A + B
    // Step 4 (after fourth clock edge):
    //   dut.U == A + B, dut.L == 0
    //
    // The testbench tracks step via dut.step.
    // -----------------------------------------------------------------
    logic [W-1:0] A_latched, B_latched;

    always @(posedge clk) begin
        if (start) begin
            A_latched <= A;
            B_latched <= B;
        end
    end

    property p_step1;
        @(posedge clk) (dut.step == 2'd1) |->
            V1(dut.U, dut.L) == (A_latched + B_latched);
    endproperty
    a_step1_value_preserve: assert property (p_step1)
        else $error("V1 invariant violated at step 1");

    property p_step2;
        @(posedge clk) (dut.step == 2'd2) |->
            V2(dut.U, dut.L, dut.M) == (A_latched + B_latched);
    endproperty
    a_step2_value_preserve: assert property (p_step2)
        else $error("V2 invariant violated at step 2");

    property p_step3;
        @(posedge clk) (dut.step == 2'd3) |->
            V3(dut.U, dut.L) == (A_latched + B_latched);
    endproperty
    a_step3_value_preserve: assert property (p_step3)
        else $error("V3 invariant violated at step 3");

    // a_boundary_exclusive
    property p_boundary_exclusive;
        @(posedge clk) (dut.step == 2'd2) |->
            ((dut.R_c & dut.Lam_c) == {W{1'b0}});
    endproperty
    a_boundary_exclusive: assert property (p_boundary_exclusive)
        else $error("R and Lambda asserted together");

    // a_chain_separation: E[l] high implies L1[l] low (NOT L2[l])
    property p_chain_separation;
        @(posedge clk) (dut.step == 2'd2) |->
            ((dut.E_c & dut.L1_c) == {W{1'b0}});
    endproperty
    a_chain_separation: assert property (p_chain_separation)
        else $error("chain-separation violated: E high with L1 high");

    // a_collision_free: at end of Step 3, U3 & L3 == 0
    property p_collision_free;
        @(posedge clk) (dut.step == 2'd3) |->
            ((dut.U3_c & dut.L3_c) == {W{1'b0}});
    endproperty
    a_collision_free: assert property (p_collision_free)
        else $error("collision-freeness violated at step 3");

    // a_final_canonical: after Step 4, L==0 and U==A+B
    property p_final_canonical;
        @(posedge clk) (dut.step == 2'd0 && done) |->
            (dut.L == {W{1'b0}}) &&
            (dut.S == (A_latched + B_latched));
    endproperty
    a_final_canonical: assert property (p_final_canonical)
        else $error("final canonical form violated");

    // -----------------------------------------------------------------
    // Stimulus
    // -----------------------------------------------------------------
    task automatic run_one(input logic [W-1:0] a, input logic [W-1:0] b);
        @(posedge clk);
        A = a; B = b; start = 1'b1;
        @(posedge clk);
        start = 1'b0;
        wait (done == 1'b1);
        @(posedge clk);
        if (S !== ((a + b) & ((1 << W) - 1)))
            $error("mismatch: A=%0d B=%0d S=%0d exp=%0d",
                   a, b, S, (a + b) & ((1 << W) - 1));
    endtask

    initial begin
        rst_n = 1'b0; start = 1'b0; A = '0; B = '0;
        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        @(posedge clk);

        // Exhaustive 8-bit
        for (int a = 0; a < (1 << W); a++)
            for (int b = 0; b < (1 << W); b++)
                run_one(a[W-1:0], b[W-1:0]);

        // Regression vectors
        run_one(8'd7,  8'd1);
        run_one(8'd255, 8'd255);

        $display("tb_ccsa: exhaustive 8-bit + regressions PASS");
        $finish;
    end

endmodule
