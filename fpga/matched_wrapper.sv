// Matched-protocol harness (Section 8.2.2) for the repository adders.
// Every design sits between the same input and output registers. Each adapter exposes
// start/done: combinational adders complete in the issuing cycle (done = start), the
// pipelined adders after their latency, and the CCSA when its FSM asserts done.
//   DEPENDENT = 1 : each new operand pair uses the previous sum (dependent chain)
//   DEPENDENT = 0 : independent operands, issued as fast as the design accepts them
// Simulate with tb_matched.sv before synthesis; this file has not been simulated here.
module matched_wrapper #(parameter int W = 64, parameter bit DEPENDENT = 1) (
  input  logic         clk, rst,
  input  logic [W-1:0] x_in,
  input  logic         x_valid,
  output logic [W:0]   s_out,
  output logic         s_valid,
  output logic [31:0]  op_count);
  logic [W-1:0] a_q, b_q; logic start_q, busy, have; logic [W:0] sum; logic done; logic accepts_every_cycle;
  adder_dut #(.W(W)) dut (.clk(clk), .rst(rst), .start(start_q), .a(a_q), .b(b_q), .s(sum), .done(done),
                          .accepts_every_cycle(accepts_every_cycle));
  wire free  = !busy || done;                                   // no operation in flight after this edge
  wire issue = x_valid && (DEPENDENT ? (free && !(start_q && !done)) : (accepts_every_cycle || free));
  always_ff @(posedge clk) begin
    if (rst) begin a_q <= '0; b_q <= '0; start_q <= 1'b0; busy <= 1'b0; have <= 1'b0; end
    else begin
      if (done) begin busy <= 1'b0; have <= 1'b1; end
      if (start_q && !done && !accepts_every_cycle) busy <= 1'b1;
      start_q <= issue;
      if (issue) begin
        a_q <= (DEPENDENT && (have || done)) ? sum[W-1:0] : x_in;   // feed back the previous result
        b_q <= x_in;
      end
    end
  end
  always_ff @(posedge clk) begin                                // output register boundary
    if (rst) begin s_out <= '0; s_valid <= 1'b0; op_count <= '0; end
    else begin s_out <= sum; s_valid <= done; if (done) op_count <= op_count + 1; end
  end
endmodule
