# Common constraints for all baseline runs.
# 1 ns over-constrained clock; Vivado reports true Fmax from post-route.
create_clock -period 1.000 -name clk [get_ports clk]

set_input_delay  -clock clk 0.200 [all_inputs]
set_output_delay -clock clk 0.200 [all_outputs]
set_load 0.100 [all_outputs]
