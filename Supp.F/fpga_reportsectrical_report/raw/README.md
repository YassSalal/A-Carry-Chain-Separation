# =====================================================================
# synth_kogge_stone.tcl
#
# Synthesize, place, and route the Kogge-Stone baseline in two forms:
#   - K-S Pipelined    : one prefix-tree level per clock cycle
#   - K-S Combinational: full prefix tree in one cycle
# Writes reports into supp/F_fpga_reports/raw/ with the "kogge_stone_"
# prefix, matching collate.py.
#
# Usage:
#   vivado -mode batch -source synth_kogge_stone.tcl -tclargs <W>
# =====================================================================

set W [lindex $argv 0]
if {$W eq ""} { set W 64 }

set part   xc7a100tcsg324-1
set rptdir [file normalize "./supp/F_fpga_reports/raw"]
file mkdir $rptdir

# ---- Pipelined Kogge-Stone --------------------------------------------
set top ks_adder_pipelined
read_verilog -sv supp/B_rtl/kogge_stone_adder.sv

synth_design -top $top -part $part -generic W=$W -generic PIPELINED=1
opt_design
place_design
route_design

report_timing_summary -file $rptdir/kogge_stone_pipelined_W${W}_timing.rpt
report_utilization    -file $rptdir/kogge_stone_pipelined_W${W}_util.rpt
report_power          -file $rptdir/kogge_stone_pipelined_W${W}_power.rpt
write_checkpoint -force $rptdir/kogge_stone_pipelined_W${W}.dcp

# ---- Combinational Kogge-Stone ----------------------------------------
set top ks_adder_flat
synth_design -top $top -part $part -generic W=$W -generic PIPELINED=0
opt_design
place_design
route_design

report_timing_summary -file $rptdir/kogge_stone_flat_W${W}_timing.rpt
report_utilization    -file $rptdir/kogge_stone_flat_W${W}_util.rpt
report_power          -file $rptdir/kogge_stone_flat_W${W}_power.rpt
write_checkpoint -force $rptdir/kogge_stone_flat_W${W}.dcp
