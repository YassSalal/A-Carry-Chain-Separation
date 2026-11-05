module adder_dut #(parameter int W = 64) (input logic clk, rst, start, input logic [W-1:0] a, b,
  output logic [W:0] s, output logic done, output logic accepts_every_cycle);
  assign accepts_every_cycle = 1'b0;
  ccsa_adder #(.W(W)) u (.clk(clk), .rst_n(!rst), .start(start), .A(a), .B(b), .S(s), .done(done));
endmodule
