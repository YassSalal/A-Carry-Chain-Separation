# =====================================================================
# synth_manchester.tcl
#
# Synthesize, place, and route the Manchester (ripple) baseline.
# Writes timing/utilization/power reports into supp/F_fpga_reports/raw/
# with the "manchester_" prefix, matching collate.py.
#
# Usage:
#   vivado -mode batch -source synth_manchester.tcl -tclargs <W>
# =====================================================================

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set top    manchester_adder
set rptdir [file normalize "./supp/F_fpga_reports/raw"]
file mkdir $rptdir

# Manchester ripple and Manchester-static are selected by the
# MANCHESTER_STATIC generic inside manchester_adder.sv.
read_verilog -sv supp/B_rtl/manchester_adder.sv

synth_design -top $top -part $part -generic W=$W -generic MANCHESTER_STATIC=0
opt_design
place_design
route_design

report_timing_summary -file $rptdir/manchester_ripple_W${W}_timing.rpt
report_utilization    -file $rptdir/manchester_ripple_W${W}_util.rpt
report_power          -file $rptdir/manchester_ripple_W${W}_power.rpt
write_checkpoint -force $rptdir/manchester_ripple_W${W}.dcp

# Second pass: static-CMOS Manchester
synth_design -top $top -part $part -generic W=$W -generic MANCHESTER_STATIC=1
opt_design
place_design
route_design

report_timing_summary -file $rptdir/manchester_static_W${W}_timing.rpt
report_utilization    -file $rptdir/manchester_static_W${W}_util.rpt
report_power          -file $rptdir/manchester_static_W${W}_power.rpt
write_checkpoint -force $rptdir/manchester_static_W${W}.dcp