// Self-checking testbench for all baselines.
// Exhaustive at small widths, random at large widths.
// Compile with:  -P W=<width>  -P DESIGN=<name>

`timescale 1ns/1ps

module tb_baselines;

    parameter int W = 16;

    logic clk;
    logic rst_n;
    logic valid_in;
    logic [W-1:0] A, B;
    logic Cin;
    logic [W-1:0] S_comb, S_pipe;
    logic Cout_comb, Cout_pipe;
    logic valid_out;

    // Device under test: combinational baselines
    manchester_ripple #(.W(W)) u_mr (
        .A(A), .B(B), .Cin(Cin), .S(S_comb), .Cout(Cout_comb)
    );

    // Pipelined DUT example
    kogge_stone_pipelined #(.W(W)) u_ks (
        .clk(clk), .rst_n(rst_n), .valid_in(valid_in),
        .A(A), .B(B), .Cin(Cin),
        .valid_out(valid_out), .S(S_pipe), .Cout(Cout_pipe)
    );

    // Clock
    initial clk = 0;
    always #0.5 clk = ~clk;

    // Reference check
    logic [W:0] expected;
    assign expected = {1'b0, A} + {1'b0, B} + Cin;

    int errors_comb = 0;
    int errors_pipe = 0;
    int n_tests = 0;

    task automatic check_comb();
        n_tests++;
        if ({Cout_comb, S_comb} !== expected) begin
            errors_comb++;
            if (errors_comb < 10)
                $display("COMB MISMATCH: A=%h B=%h Cin=%b got=%h exp=%h",
                         A, B, Cin, {Cout_comb, S_comb}, expected);
        end
    endtask

    initial begin
        rst_n = 0;
        valid_in = 0;
        A = '0; B = '0; Cin = 0;
        repeat (4) @(posedge clk);
        rst_n = 1;

        // Exhaustive small widths
        if (W <= 12) begin
            for (int a = 0; a < (1 << W); a++) begin
                for (int b = 0; b < (1 << W); b++) begin
                    A = a[W-1:0]; B = b[W-1:0]; Cin = 0;
                    #1 check_comb();
                end
            end
        end else begin
            // Random wide widths
            for (int i = 0; i < 10000; i++) begin
                A = $urandom; B = $urandom; Cin = $urandom & 1;
                #1 check_comb();
            end
        end

        // Pipelined check (subset)
        valid_in = 1;
        for (int i = 0; i < 200; i++) begin
            A = $urandom; B = $urandom; Cin = $urandom & 1;
            @(posedge clk);
        end
        valid_in = 0;
        repeat (16) @(posedge clk);

        $display("tb_baselines W=%0d tests=%0d comb_errors=%0d pipe_errors=%0d",
                 W, n_tests, errors_comb, errors_pipe);
        if (errors_comb == 0) $display("COMB: PASS");
        else                  $display("COMB: FAIL");
        $finish;
    end

endmodule
