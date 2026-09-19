tcl
# synth_ccsa.tcl -- synthesize and implement the CCSA at a given width.
# Usage: vivado -mode batch -source synth_ccsa.tcl -tclargs <W>

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set top    ccsa_adder
set rptdir [file normalize "./supp/F_fpga_reports/raw"]
file mkdir $rptdir

read_verilog -sv supp/B_rtl/ccsa_adder.sv
synth_design -top $top -part $part -generic W=$W
opt_design
place_design
route_design

report_timing_summary -file $rptdir/ccsa_W${W}_timing.rpt
report_utilization    -file $rptdir/ccsa_W${W}_util.rpt
report_power          -file $rptdir/ccsa_W${W}_power.rpt
write_checkpoint      -force $rptdir/ccsa_W${W}.dcp
