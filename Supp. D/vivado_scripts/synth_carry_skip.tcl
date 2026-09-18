# =====================================================================
# synth_carry_skip.tcl
#
# Synthesize, place, and route the carry-skip baseline (8-bit blocks).
# Writes reports into supp/F_fpga_reports/raw/ with the "carry_skip_"
# prefix, matching collate.py.
#
# Usage:
#   vivado -mode batch -source synth_carry_skip.tcl -tclargs <W>
# =====================================================================

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set top    carry_skip_adder
set rptdir [file normalize "./supp/F_fpga_reports/raw"]
file mkdir $rptdir

read_verilog -sv supp/B_rtl/carry_skip_adder.sv

synth_design -top $top -part $part -generic W=$W -generic BLOCK=8
opt_design
place_design
route_design

report_timing_summary -file $rptdir/carry_skip_W${W}_timing.rpt
report_utilization    -file $rptdir/carry_skip_W${W}_util.rpt
report_power          -file $rptdir/carry_skip_W${W}_power.rpt
write_checkpoint -force $rptdir/carry_skip_W${W}.dcp
