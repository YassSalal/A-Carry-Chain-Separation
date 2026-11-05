module adder_dut #(parameter int W = 64) (input logic clk, rst, start, input logic [W-1:0] a, b,
  output logic [W:0] s, output logic done, output logic accepts_every_cycle);
  logic [W-1:0] sm; logic co;
  assign accepts_every_cycle = 1'b1;
  assign done = start;                       // combinational: result valid in the issuing cycle
  carry_skip_8 #(.W(W)) u (.A(a), .B(b), .Cin(1'b0), .S(sm), .Cout(co));
  assign s = {co, sm};
endmodule
