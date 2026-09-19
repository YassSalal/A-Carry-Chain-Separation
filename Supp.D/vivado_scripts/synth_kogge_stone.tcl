# =====================================================================
# synth_kogge_stone.tcl
#
# Synthesize, place, and route the Kogge-Stone baseline in two forms:
#   ks_adder_pipelined : one prefix-tree level per clock cycle
#   ks_adder_flat      : full prefix tree in one cycle
# Writes reports into Supp.F/fpga_reports/raw/ with the
# "kogge_stone_pipelined_" and "kogge_stone_flat_" prefixes.
#
# Usage:
#   vivado -mode batch -source synth_kogge_stone.tcl -tclargs <W>
# =====================================================================

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set rptdir [file normalize "./Supp.F/fpga_reports/raw"]
file mkdir $rptdir

read_verilog -sv Supp.B/B_rtl/kogge_stone_adder.sv

# ---- Pipelined Kogge-Stone ------------------------------------------
set top ks_adder_pipelined
synth_design -top $top -part $part -generic W=$W
opt_design
place_design
route_design

report_timing_summary -file $rptdir/kogge_stone_pipelined_W${W}_timing.rpt
report_utilization    -file $rptdir/kogge_stone_pipelined_W${W}_util.rpt
report_power          -file $rptdir/kogge_stone_pipelined_W${W}_power.rpt
write_checkpoint -force $rptdir/kogge_stone_pipelined_W${W}.dcp

# ---- Combinational Kogge-Stone --------------------------------------
set top ks_adder_flat
synth_design -top $top -part $part -generic W=$W
opt_design
place_design
route_design

report_timing_summary -file $rptdir/kogge_stone_flat_W${W}_timing.rpt
report_utilization    -file $rptdir/kogge_stone_flat_W${W}_util.rpt
report_power          -file $rptdir/kogge_stone_flat_W${W}_power.rpt
write_checkpoint -force $rptdir/kogge_stone_flat_W${W}.dcp
