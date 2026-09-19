# =====================================================================
# synth_manchester.tcl
#
# Synthesize, place, and route the Manchester baseline in two variants.
# Writes timing/utilization/power reports into Supp.F/fpga_reports/raw/
# with the "manchester_ripple_" and "manchester_static_" prefixes,
# matching collate.py.
#
# Usage:
#   vivado -mode batch -source synth_manchester.tcl -tclargs <W>
# =====================================================================

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set top    manchester_adder
set rptdir [file normalize "./Supp.F/fpga_reports/raw"]
file mkdir $rptdir

read_verilog -sv Supp.B/B_rtl/manchester_adder.sv

# ---- Classical Manchester (pass-transistor model) --------------------
synth_design -top $top -part $part -generic W=$W -generic MANCHESTER_STATIC=0
opt_design
place_design
route_design

report_timing_summary -file $rptdir/manchester_ripple_W${W}_timing.rpt
report_utilization    -file $rptdir/manchester_ripple_W${W}_util.rpt
report_power          -file $rptdir/manchester_ripple_W${W}_power.rpt
write_checkpoint -force $rptdir/manchester_ripple_W${W}.dcp

# ---- Static-CMOS Manchester -----------------------------------------
synth_design -top $top -part $part -generic W=$W -generic MANCHESTER_STATIC=1
opt_design
place_design
route_design

report_timing_summary -file $rptdir/manchester_static_W${W}_timing.rpt
report_utilization    -file $rptdir/manchester_static_W${W}_util.rpt
report_power          -file $rptdir/manchester_static_W${W}_power.rpt
write_checkpoint -force $rptdir/manchester_static_W${W}.dcp
