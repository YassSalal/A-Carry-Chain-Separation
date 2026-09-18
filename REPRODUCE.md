# Equation-to-code mapping (manuscript Section 7.3.1)

All line numbers refer to the files in this repository at tag
`v2.0-ccsa`.

## Step 1 — Vertical half-addition

  U1[l] = A[l] XOR B[l]      -> supp/B_rtl/ccsa_adder.sv, g_step1.U1_nxt
  L1[l] = A[l] AND B[l]      -> supp/B_rtl/ccsa_adder.sv, g_step1.L1_nxt
  Python                     -> supp/A_reference_model/ccsa_ref.py, Step 1 block

## Step 2 — Boundary-controlled switching

  R[l]    = U1[l] & ~U1[l-1] & ~L1[l-1]   -> ccsa_adder.sv, assign R_w
  Lambda[l] = ~U1[l] & U1[l-1]            -> ccsa_adder.sv, assign Lam_w
  B2[l]   = R[l] | (B2[l-1] & ~Lambda[l]) -> ccsa_adder.sv, g_bus2
  E[l]    = B2[l] & U1[l]                 -> ccsa_adder.sv, assign E_w
  U2[l]   = U1[l] & ~E[l]                 -> ccsa_adder.sv, assign U2_nxt
  L2[l]   = L1[l] | E[l]                  -> ccsa_adder.sv, assign L2_nxt
  M[l]    = E[l]                          -> ccsa_adder.sv, assign M2_nxt
  Python                                  -> ccsa_ref.py, Step 2 block

## Step 3 — Carry-chain collapse (Variant B)

  U3[l] = (~U2[l] & U2[l-1]) |
          (~M[l-1] & L2[l-1] & ~U2[l-1] & ~U2[l])
        -> ccsa_adder.sv, assign U3_nxt (uses U2_prev, L2_prev, M2_prev)
        -> ccsa_ref.py, Step 3 block (uses g(U2,l-1), g(L2,l-1), g(M,l-1))
  L3[l] = L2[l] & M[l]
        -> ccsa_adder.sv, assign L3_nxt
        -> ccsa_ref.py, Step 3 block

## Step 4 — Collision-free merge

  U4[l] = U3[l] | L3[l]      -> ccsa_adder.sv, assign U4_nxt (from
                                *registered* U3, L3, not recomputed)
  L4[l] = 0                  -> ccsa_adder.sv, implicit (L4 not stored)

## Stage-relative invariants (Section 6.1)

  V1 -> ccsa_ref.py, V1()
  V2 -> ccsa_ref.py, V2()
  V3 -> ccsa_ref.py, V3()
  SVA-style checks -> tb_ccsa.sv, V1_calc / V2_calc / V3_calc

## W+1-bit output

  RTL output port:   output reg [W:0] S   (ccsa_adder.sv)
  Python return:     S (integer, W+1 bits)
  Testbench compare: expected = {1'b0,a} + {1'b0,b}  (tb_ccsa.sv)