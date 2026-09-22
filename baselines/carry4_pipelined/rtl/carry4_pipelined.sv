// CARRY4-Pipelined adder.
// Each 4-bit CARRY4 slice separated by a pipeline register.
// Initiation interval II = 1. N_cyc = W/4 + 1 (input + output register).

module carry4_pipelined #(
    parameter int W = 64
) (
    input  logic         clk,
    input  logic         rst_n,
    input  logic         valid_in,
    input  logic [W-1:0] A,
    input  logic [W-1:0] B,
    input  logic         Cin,
    output logic         valid_out,
    output logic [W-1:0] S,
    output logic         Cout
);

    localparam int N = W / 4;
    localparam int STAGES = N + 1;

    logic [W:0] C_r [0:N];
    logic [W-1:0] S_r [0:N];
    logic vld_r [0:STAGES];

    // Input register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            C_r[0] <= '0;
            vld_r[0] <= 1'b0;
        end else begin
            C_r[0][0] <= Cin;
            vld_r[0] <= valid_in;
        end
    end

    genvar b;
    generate
        for (b = 0; b < N; b++) begin : g_stage
            logic [3:0] co;
            logic [3:0] o;
            logic [W:0] C_next;
            logic [W-1:0] S_next;

            CARRY4 u_carry4 (
                .CO     (co),
                .O      (o),
                .CI     (C_r[b][4*b]),
                .CYINIT (1'b0),
                .DI     ({A[4*b+3] & B[4*b+3],
                          A[4*b+2] & B[4*b+2],
                          A[4*b+1] & B[4*b+1],
                          A[4*b+0] & B[4*b+0]}),
                .S      ({A[4*b+3] ^ B[4*b+3],
                          A[4*b+2] ^ B[4*b+2],
                          A[4*b+1] ^ B[4*b+1],
                          A[4*b+0] ^ B[4*b+0]})
            );

            assign C_next = C_r[b];
            assign C_next[4*b+4] = co[3];
            assign S_next = S_r[b];
            assign S_next[4*b+3:4*b] = o;

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    C_r[b+1] <= '0;
                    S_r[b+1] <= '0;
                    vld_r[b+1] <= 1'b0;
                end else begin
                    C_r[b+1] <= C_next;
                    S_r[b+1] <= S_next;
                    vld_r[b+1] <= vld_r[b];
                end
            end
        end
    endgenerate

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            S <= '0;
            Cout <= 1'b0;
            valid_out <= 1'b0;
        end else begin
            S <= S_r[N];
            Cout <= C_r[N][W];
            valid_out <= vld_r[N];
        end
    end

endmodule
