# Usage: vivado -mode batch -source scripts/synth_impl.tcl -tclargs <W> <design>
set W      [lindex $argv 0]
set design [lindex $argv 1]

set part xc7a100tcsg324-1
set top  top

set rtl_dir ./baselines/${design}/rtl
if {![file isdirectory $rtl_dir]} {
    set rtl_dir ./ccs/rtl
}

read_verilog [glob ${rtl_dir}/*.sv]
read_xdc ./constraints/timing.xdc

synth_design -top $top -part $part -retiming off
opt_design
place_design
route_design

set tag "v2.1.0-baselines"
set commit [exec git rev-parse HEAD]

report_timing_summary -file ./logs/${design}_W${W}_timing.rpt
report_utilization    -file ./logs/${design}_W${W}_util.rpt
report_power          -file ./logs/${design}_W${W}_power.rpt

set fp [open ./logs/${design}_W${W}.log w]
puts $fp "tag=${tag}"
puts $fp "commit=${commit}"
puts $fp "vivado=[version -short]"
puts $fp "device=${part}"
puts $fp "design=${design}"
puts $fp "W=${W}"
puts $fp "command=vivado -mode batch -source scripts/synth_impl.tcl -tclargs ${W} ${design}"
close $fp

puts "DONE ${design} W=${W}"
