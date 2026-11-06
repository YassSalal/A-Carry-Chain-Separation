// =====================================================================
// tb_ccsa_v2.sv  —  self-checking testbench for ccsa_adder.sv (Supp. B)
//
// Replaces Supp.C/testbench/tb_ccsa.sv, which (i) never drives `start`,
// (ii) samples S after a fixed four cycles instead of waiting for `done`,
// (iii) draws operands with $random (32 bits, sign-extended for W > 32,
//      unseeded) and (iv) leaves the invariant checks commented out.
//
// This testbench:
//   * drives the start/done handshake of the released controller and
//     checks that `done` rises exactly six cycles after `start`
//     (four datapath cycles + IDLE + DONE, Section 7.2);
//   * draws every operand word independently and uniformly with
//     $urandom from a fixed seed (SEED = 32'hCC5A), so all W bits are random;
//   * runs directed corner cases (all-zero, all-one, alternating 0101/1010,
//     isolated generates, carry chains and carry-free runs of length
//     1, 2, 15, 16, 17, 31, 32, 33 and W-1 at every start position,
//     i.e. including chains that begin, end or cross a k = 16 repeater
//     boundary);
//   * optionally runs an exhaustive campaign for W <= 12 (+define+EXHAUSTIVE);
//   * checks after every addition, through hierarchical references,
//       V1 = V2 = V3 = A + B,  U3 & L3 = 0,  S = A + B.
//
// The released RTL has no carry-in port (L1_prev[0] is tied to 0), so
// carry-in is verified on the reference model only (verify_exhaustive.py).
//
// Run (examples):
//   vsim  -c -GW=64  tb_ccsa_v2 -do "run -all"            (ModelSim/Questa)
//   iverilog -g2012 -DW_PARAM=12 -DEXHAUSTIVE -o tb tb_ccsa_v2.sv ccsa_adder.sv && vvp tb
// =====================================================================
`timescale 1ns/1ps
`ifndef W_PARAM
 `define W_PARAM 64
`endif
module tb_ccsa_v2;
    parameter integer W        = `W_PARAM;
    parameter integer N_RANDOM = 20000;
    parameter [31:0]  SEED     = 32'hCC5A;

    logic clk = 0, rst_n = 0, start = 0;
    logic [W-1:0] A = '0, B = '0;
    wire  [W:0]   S;
    wire          done;

    ccsa_adder #(.W(W)) dut (.clk(clk), .rst_n(rst_n), .start(start),
                             .A(A), .B(B), .S(S), .done(done));
    always #5 clk = ~clk;

    integer n_checked = 0, n_errors = 0;

    // --- value functions of Section 6.1 on the DUT's registered state ---
    function automatic [W+1:0] v1(input [W:0] U, input [W:0] L);
        v1 = {1'b0, U} + ({1'b0, L} << 1);
    endfunction
    function automatic [W+1:0] v2(input [W:0] U, input [W:0] L, input [W:0] M);
        v2 = {1'b0, U} + {1'b0, (L & M)} + ({1'b0, (L & ~M)} << 1);
    endfunction

    // --- one addition through the handshake, with all checks ---
    task automatic add_check(input [W-1:0] a, input [W-1:0] b);
        logic [W+1:0] ref_sum;
        integer cyc;
        ref_sum = a + b;
        @(negedge clk); A = a; B = b; start = 1;
        @(negedge clk); start = 0;
        cyc = 1;
        while (!done) begin
            @(negedge clk); cyc++;
            if (cyc > 10) begin $error("done never rose"); $fatal; end
        end
        // registered state of the finished addition
        if (v1(dut.U1, dut.L1)            !== ref_sum) begin n_errors++; $error("V1 A=%h B=%h", a, b); end
        if (v2(dut.U2, dut.L2, dut.M2)    !== ref_sum) begin n_errors++; $error("V2 A=%h B=%h", a, b); end
        if ({1'b0, dut.U3} + {1'b0, dut.L3} !== ref_sum) begin n_errors++; $error("V3 A=%h B=%h", a, b); end
        if ((dut.U3 & dut.L3) !== '0)                begin n_errors++; $error("collision A=%h B=%h", a, b); end
        if ({1'b0, S} !== ref_sum)                   begin n_errors++; $error("S A=%h B=%h got=%h", a, b, S); end
        if (cyc != 6)                                begin n_errors++; $error("done after %0d cycles, expected 6", cyc); end
        n_checked++;
    endtask

    function automatic [W-1:0] urand_w();
        logic [W-1:0] r;
        for (int i = 0; i < W; i += 32) r[i +: 32] = $urandom;   // independent 32-bit words
        return r;
    endfunction

    task automatic directed();
        logic [W-1:0] ALL, alt5, altA, prop;
        int lens[9] = '{1, 2, 15, 16, 17, 31, 32, 33, W-1};
        ALL = '1;
        for (int i = 0; i < W; i++) alt5[i] = ~i[0];
        altA = ~alt5;
        add_check('0, '0);       add_check(ALL, ALL);   add_check(ALL, '0);   add_check(ALL, 1);
        add_check(alt5, altA);   add_check(alt5, alt5); add_check(altA, altA);
        add_check(alt5, '0);     add_check(altA, 1);
        for (int k = 0; k < W; k++) begin
            add_check(W'(1) << k, W'(1) << k);                          // isolated generate
            foreach (lens[j]) if (lens[j] > 0 && k + 1 + lens[j] <= W) begin
                prop = ((W'(1) << lens[j]) - 1) << (k + 1);
                add_check((W'(1) << k) | prop, W'(1) << k);             // carry chain of length lens[j]
                add_check(prop, '0);                                    // carry-free run of length lens[j]
            end
        end
    endtask

    initial begin
        void'($urandom(SEED));
        repeat (3) @(negedge clk); rst_n = 1;
        directed();
        $display("directed: %0d additions", n_checked);
`ifdef EXHAUSTIVE
        if (W <= 12) begin
            for (longint a = 0; a < (1 << W); a++)
                for (longint b = 0; b < (1 << W); b++) add_check(W'(a), W'(b));
            $display("exhaustive W=%0d done", W);
        end
`endif
        for (int i = 0; i < N_RANDOM; i++) add_check(urand_w(), urand_w());
        $display("tb_ccsa_v2: W=%0d checked=%0d errors=%0d seed=%h  %s",
                 W, n_checked, n_errors, SEED, (n_errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
