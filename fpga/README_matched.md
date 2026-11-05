# Matched FPGA campaign (Reviewer 7 pt 2, Reviewer 4 pt 6, Reviewer 7 pt 4)
1. Simulate first: adapt Supp.C/testbench to instantiate matched_wrapper with each adapter and
   check that s_out equals the running sum (DEPENDENT=1) or a+b (DEPENDENT=0).
2. For every design in {8,16,32,64,128,256} bits and DEPENDENT in {0,1}:
   vivado -mode batch -source kit/fpga/run_matched.tcl -tclargs <design> <W> <dep>
3. Commit results/matched/** (raw .rpt files) to Supp.F/fpga_reports/raw and regenerate manifest.json.
4. Per run: latency = cycles_per_op x period (cycles from the CCSA FSM / pipeline depth, 1 for
   combinational), throughput = 1/(II x period), area = LUT + FF, energy/op = P x II x period.
   Replace every cell marked with a dagger in Tables 16, 16b, 18a and 18b with these values,
   and delete the "interpolated" status entries.
Note: the CCSA FSM in Supp.B/B_rtl/ccsa_adder.sv takes 6 cycles from start to done
(IDLE, STEP1-4, DONE); either report N_cyc = 6 for this RTL or trim the FSM to 4 cycles.
