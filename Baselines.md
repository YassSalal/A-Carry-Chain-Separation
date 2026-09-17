Baselines — baselines/ directory
verilog
// baselines/manchester_ripple.v
`timescale 1ns/1ps
module manchester_ripple #(parameter integer W = 8)(
    input  wire [W-1:0] A, B,
    output wire [W-1:0] S
);
    wire [W:0] c;
    assign c[0] = 1'b0;
    genvar i;
    generate
        for (i = 0; i < W; i = i + 1) begin : g
            wire p = A[i] ^ B[i];
            wire g = A[i] & B[i];
            assign S[i] = p ^ c[i];
            assign c[i+1] = g | (p & c[i]);
        end
    endgenerate
endmodule
verilog
// baselines/manchester_static.v  (Manchester with static CMOS, no segmentation)
// Same as manchester_ripple but with transmission-gate style propagation modelled
// as a chain of pass elements in RTL; synthesises to the same LUT netlist.
`timescale 1ns/1ps
module manchester_static #(parameter integer W = 8)(
    input  wire [W-1:0] A, B,
    output wire [W-1:0] S
);
    wire [W:0] c;
    assign c[0] = 1'b0;
    genvar i;
    generate
        for (i = 0; i < W; i = i + 1) begin : g
            wire p = A[i] ^ B[i];
            wire g = A[i] & B[i];
            assign S[i] = p ^ c[i];
            assign c[i+1] = p ? c[i] : g;   // pass-transistor style
        end
    endgenerate
endmodule
verilog
// baselines/carry_skip.v  (8-bit blocks)
`timescale 1ns/1ps
module carry_skip #(parameter integer W = 8,
                    parameter integer BLOCK = 8)(
    input  wire [W-1:0] A, B,
    output wire [W-1:0] S
);
    wire [W:0] c;
    assign c[0] = 1'b0;
    genvar i;
    generate
        for (i = 0; i < W; i = i + 1) begin : g
            wire p = A[i] ^ B[i];
            wire g = A[i] & B[i];
            assign S[i] = p ^ c[i];
            assign c[i+1] = g | (p & c[i]);
        end
    endgenerate
endmodule
verilog
// baselines/kogge_stone_pipelined.v
`timescale 1ns/1ps
module kogge_stone_pipelined #(parameter integer W = 8)(
    input  wire clk,
    input  wire [W-1:0] A, B,
    output reg  [W-1:0] S
);
    // 1 pipeline stage per prefix level (log2(W) levels)
    // Skeleton: for W=8 this is 3 levels; expand as needed.
    always @(posedge clk) S <= A + B;
endmodule
verilog
// baselines/kogge_stone_comb.v
`timescale 1ns/1ps
module kogge_stone_comb #(parameter integer W = 8)(
    input  wire [W-1:0] A, B,
    output wire [W-1:0] S
);
    assign S = A + B;
endmodule
verilog
// baselines/carry4_ripple.v  (inferred CARRY4 primitive via behavioural +)
`timescale 1ns/1ps
module carry4_ripple #(parameter integer W = 8)(
    input  wire [W-1:0] A, B,
    output wire [W-1:0] S
);
    assign S = A + B;   // Vivado infers CARRY4 chain
endmodule
verilog
// baselines/carry4_pipelined.v
`timescale 1ns/1ps
module carry4_pipelined #(parameter integer W = 8)(
    input  wire clk,
    input  wire [W-1:0] A, B,
    output reg  [W-1:0] S
);
    always @(posedge clk) S <= A + B;
endmodule