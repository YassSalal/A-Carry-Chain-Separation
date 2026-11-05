module adder_dut #(parameter int W = 64) (input logic clk, rst, start, input logic [W-1:0] a, b,
  output logic [W:0] s, output logic done, output logic accepts_every_cycle);
  logic [W-1:0] sm; logic co;
  assign accepts_every_cycle = 1'b1;
  carry4_pipelined #(.W(W)) u (.clk(clk), .rst_n(!rst), .valid_in(start), .A(a), .B(b), .Cin(1'b0),
                 .valid_out(done), .S(sm), .Cout(co));
  assign s = {co, sm};
endmodule
