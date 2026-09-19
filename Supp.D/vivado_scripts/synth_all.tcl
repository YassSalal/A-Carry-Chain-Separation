# synth_all.tcl  -- run once per (arch, width)
# usage: vivado -mode batch -source synth_all.tcl -tclargs <arch> <width>
set arch   [lindex $argv 0]
set width  [lindex $argv 1]

set rtl_map [dict create \
    ccsa               "Supp.B/rtl/ccsa_adder.sv" \
    manchester_ripple  "Supp.B/rtl/manchester_adder.sv" \
    manchester_static  "Supp.B/rtl/manchester_adder.sv" \
    carry_skip         "Supp.B/rtl/carry_skip_adder.sv" \
    ks_pipelined       "Supp.B/rtl/kogge_stone_adder.sv" \
    ks_comb            "Supp.B/rtl/kogge_stone_adder.sv" \
    carry4_ripple      "Supp.B/rtl/carry4_adder.sv" \
    carry4_pipelined   "Supp.B/rtl/carry4_adder.sv"]

set rtl [dict get $rtl_map $arch]

read_verilog $rtl
read_xdc constraints.xdc

synth_design -top ${arch}_top -part xc7a100tcsg324-1 -generic W=$width
opt_design
place_design
route_design

set out Supp.F/fpga_reports/raw/${arch}_w${width}
report_timing_summary -file ${out}_timing.rpt
report_utilization    -file ${out}_util.rpt
report_power          -file ${out}_power.rpt
write_checkpoint      -force ${out}.dcp
