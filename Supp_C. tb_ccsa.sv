//-----------------------------------------------------------------------------
// tb_ccsa.sv -- Self-checking SystemVerilog testbench for the CCSA
//               (Section 7.7 verification environment)
//
//   - Exhaustive mode for W <= 8 (+EXHAUSTIVE plusarg): all 2^(2W) pairs
//   - Random mode otherwise: NUM_VEC pseudo-random vectors plus corner
//     vectors (all-ones, all-ones+0, 0+all-ones)
//   - SVA checkers (Section 7.7):
//       a_step_value_preserve  (immediate, via TB reference function)
//       a_boundary_exclusive   (concurrent)
//       a_chain_separation     (concurrent)
//       a_collision_free       (concurrent)
//       a_final_canonical      (concurrent)
//
// Run (Xilinx XSim):
//   xvlog -sv ../Supp_B/ccsa_rtl.v tb_ccsa.sv
//   xelab tb_ccsa -generic "W=32" -snapshot tb_ccsa_w32
//   xsim tb_ccsa_w32 -runall
// Run (ModelSim/Questa):
//   vlog -sv ../Supp_B/ccsa_rtl.v tb_ccsa.sv
//   vsim -c -gW=32 tb_ccsa -do "run -all; quit -f"
//-----------------------------------------------------------------------------
`timescale 1ns/1ps

module tb_ccsa;
    parameter W       = 32;
    parameter NUM_VEC = 10000;
    parameter SEED    = 1;

    logic         clk = 1'b0, rst = 1'b1, start = 1'b0;
    logic [W-1:0] A = '0, B = '0;
    logic [W:0]   S;
    logic         done;
    logic [W-1:0] A_r = '0, B_r = '0;   // operands of the in-flight addition
    integer       errors = 0, vec = 0;

    ccsa_seq #(W) dut (
        .clk(clk), .rst(rst), .start(start), .A(A), .B(B),
        .done(done), .S(S)
    );

    always #5 clk = ~clk;   // 100 MHz nominal

    // TB-side semantic-value reference for a_step_value_preserve, mirroring
    // Theorem 7.2 (mixed weights at end of Step 2: M-flagged lower bits have
    // weight 2^k, unflagged original carries weight 2^(k+1)) and Theorem 7.3 /
    // Corollary 7.4 (end of Step 3: all surviving lower bits weight 2^k).
    // Sized for W up to 256.
    function automatic logic [2*W+1:0] semval_s2(
        input logic [W:0] u, input logic [W:0] l, input logic [W-1:0] m);
        logic [2*W+1:0] acc;
        integer k;
        begin
            acc = '0;
            for (k = 0; k < W; k = k + 1)
                acc = acc + (u[k] << k)
                        + (l[k] << (m[k] ? k : k+1));
            acc = acc + (u[W] << W);
            return acc;
        end
    endfunction

    function automatic logic [2*W+1:0] semval_s3(
        input logic [W:0] u, input logic [W:0] l);
        logic [2*W+1:0] acc;
        integer k;
        begin
            acc = '0;
            for (k = 0; k <= W; k = k + 1)
                acc = acc + ((u[k] | l[k]) << k);
            return acc;
        end
    endfunction

    function automatic logic [W-1:0] randv;
        integer j;
        begin
            for (j = 0; j < W; j = j + 1) randv[j] = $random;
        end
    endfunction

    //-- a_step_value_preserve (immediate checks at every phase boundary) ----
    always  @(posedge CLK) disable iff (!RST_N)
    (1, expected = A + B)
    |=>
    (step == 1) |-> (V1(U, L)     == expected)
    and
    (step == 2) |-> (V2(U, L, M)  == expected)   // corrected
    and
    (step == 3) |-> (V34(U, L)    == expected)
    and
    (step == 4) |-> (V34(U, L)    == expected);
endproperty

a_step_value_preserve : assert property (p_step_value_preserve)
    else $error("Stage-relative value invariant violated at step %0d", step);

    //-- Concurrent SVA checkers ---------------------------------------------
    a_boundary_exclusive: assert property (@(posedge clk) disable iff (rst)
        (dut.ph == 3) |-> ((dut.s2R & dut.s2Lambda) == 0))
        else $error("a_boundary_exclusive FAILED");

    a_chain_separation: assert property (@(posedge clk) disable iff (rst)
        (dut.ph == 3) |-> ((dut.Mq & dut.Lq) == 0))
        else $error("a_chain_separation FAILED");

    a_collision_free: assert property (@(posedge clk) disable iff (rst)
        (dut.ph == 4) |-> ((dut.Uq & dut.Lq) == 0))
        else $error("a_collision_free FAILED");

    a_final_canonical: assert property (@(posedge clk) disable iff (rst)
        done |-> (S == (W+1)'(A_r) + (W+1)'(B_r)))
        else $error("a_final_canonical FAILED");

    //-- Stimulus -------------------------------------------------------------
    task automatic run_one(input logic [W-1:0] a, input logic [W-1:0] b);
        begin
            wait (dut.ph == 0);            // IDLE
            @(negedge clk);
            A = a; B = b; A_r = a; B_r = b; start = 1'b1;
            @(negedge clk);
            start = 1'b0;
            wait (done == 1'b1);
            @(negedge clk);
            if (S !== ((W+1)'(a) + (W+1)'(b))) begin
                errors = errors + 1;
                $display("ERROR W=%0d vec=%0d A=%h B=%h S=%h expected=%h",
                         W, vec, a, b, S, ((W+1)'(a) + (W+1)'(b)));
            end
            vec = vec + 1;
        end
    endtask

    initial begin
        $display("CCSA TB start: W=%0d NUM_VEC=%0d SEED=%0d", W, NUM_VEC, SEED);
        repeat (4) @(negedge clk);
        rst <= 1'b0;

        if ($test$plusargs("EXHAUSTIVE") && (W <= 8)) begin
            for (integer a = 0; a < (1 << W); a++)
                for (integer b = 0; b < (1 << W); b++)
                    run_one(W'(a), W'(b));
        end else begin
            for (integer i = 0; i < NUM_VEC; i++)
                run_one(randv(), randv());
            run_one({W{1'b1}}, {W{1'b1}});
            run_one({W{1'b1}}, '0);
            run_one('0, {W{1'b1}});
            run_one({W{1'b1}}, {{(W-1){1'b0}}, 1'b1});
            run_one({{(W-1){1'b0}}, 1'b1}, {W{1'b1}});
        end

        $display("CCSA TB finished: W=%0d vectors=%0d errors=%0d", W, vec, errors);
        if (errors == 0) $display("TEST PASSED");
        else             $display("TEST FAILED");
        $finish;
    end
endmodule
