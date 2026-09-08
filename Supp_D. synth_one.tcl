#-------------------------------------------------------------------------------
# synth_one.tcl -- Non-project Vivado synthesis/PnR script for one CCSA config
#
#   vivado -mode batch -source synth_one.tcl -tclargs <W> <outdir>
#
# Writes to <outdir>:
#   ccsa_seq_W<W>_util.rpt, _timing.rpt, _power.rpt, _route_status.rpt
# Reproduces the methodology of Section 9.1 (Artix-7, Vivado 2023.2,
# default strategies, retiming disabled, 1 ns over-constraint, 20% I/O
# delays, 0.10 pF output load).
#-------------------------------------------------------------------------------
set W      [lindex $argv 0]
set outdir [lindex $argv 1]
file mkdir $outdir

create_project -in_memory -part xc7a100tcsg324-1 -name ccsa_w${W}
read_verilog -sv [file normalize [file join [file dirname [info script]] .. Supp_B ccsa_rtl.v]]

# --- constraints (Section 9.1) ----------------------------------------------
set cstr [open [file join $outdir ccsa_w${W}.xdc] w]
puts $cstr "create_clock -name CLK -period 1.000 \[get_ports clk\]"
puts $cstr "set_input_delay  0.200 -clock CLK \[all_inputs\]"
puts $cstr "set_output_delay 0.200 -clock CLK \[all_outputs\]"
puts $cstr "set_load 0.10 \[all_outputs\]"
close $cstr
read_xdc [file join $outdir ccsa_w${W}.xdc]

# --- implementation ----------------------------------------------------------
synth_design -top ccsa_seq -generic W=${W} -part xc7a100tcsg324-1 \
             -retiming off -flatten_hierarchy none
opt_design
place_design
route_design

report_utilization      -file [file join $outdir ccsa_seq_W${W}_util.rpt]
report_timing_summary   -file [file join $outdir ccsa_seq_W${W}_timing.rpt]
report_power            -file [file join $outdir ccsa_seq_W${W}_power.rpt]
report_route_status     -file [file join $outdir ccsa_seq_W${W}_route_status.rpt]

puts "SYNTH_DONE W=${W} outdir=${outdir}"
