tcl
# =====================================================================
# Vivado 2023.2 synthesis + implementation for CCSA and baselines.
# Mirrors Section 9.1 of the manuscript.
# =====================================================================

set PART       xc7a100tcsg324-1
set TOP        ccsa
set WIDTHS     {8 16 32 64 128 256}
set OUTDIR     ./reports
file mkdir $OUTDIR

foreach w $WIDTHS {
    set proj "ccsa_${w}"
    create_project -force $proj ./$proj -part $PART

    # RTL sources
    add_files -norecurse ./rtl/ccsa_rtl.v
    add_files -norecurse ./rtl/ccsa_comb.v

    # Baselines
    add_files -norecurse ./baselines/manchester_ripple.v
    add_files -norecurse ./baselines/manchester_static.v
    add_files -norecurse ./baselines/carry_skip.v
    add_files -norecurse ./baselines/kogge_stone_pipelined.v
    add_files -norecurse ./baselines/kogge_stone_comb.v
    add_files -norecurse ./baselines/carry4_ripple.v
    add_files -norecurse ./baselines/carry4_pipelined.v

    set_property top $TOP [get_filesets sources_1]
    set_property generic "W=$w" [get_filesets sources_1]

    # Over-constrain to force aggressive routing (Section 9.1)
    create_clock -period 1.000 -name clk [get_ports clk]
    set_input_delay  0.200 -clock clk [all_inputs]
    set_output_delay 0.200 -clock clk [all_outputs]
    set_load 0.10 [all_outputs]

    # Synthesis
    synth_design -top $TOP -part $PART -flatten_hierarchy rebuilt \
        -retiming off -directive Default

    opt_design
    place_design
    route_design

    # Reports
    report_timing_summary -file $OUTDIR/${proj}_timing.rpt
    report_utilization    -file $OUTDIR/${proj}_util.rpt
    report_power          -file $OUTDIR/${proj}_power.rpt
    report_route_status   -file $OUTDIR/${proj}_route.rpt

    # Write post-route DCP for reproducibility
    write_checkpoint -force $OUTDIR/${proj}.dcp

    close_project
}
