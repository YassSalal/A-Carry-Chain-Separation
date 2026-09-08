#-------------------------------------------------------------------------------
# run_synth_all.tcl -- Reproduce the full Table-4 campaign of Section 9.2.
#   vivado -mode batch -source run_synth_all.tcl
# Raw reports land in ../Supp_F/raw/  (populates Supp F of the package).
# Requires: Vivado 2023.2 (tested), Artix-7 part xc7a100tcsg324-1.
# Note: Kogge-Stone / Brent-Kung baseline RTL lives in the repository
#       (baselines/ directory) and is synthesized with identical scripts.
#-------------------------------------------------------------------------------
set script_dir [file dirname [file normalize [info script]]]
set raw_dir    [file normalize [file join $script_dir .. Supp_F raw]]
file mkdir $raw_dir

foreach W {8 16 32 64 128 256} {
    puts "=== CCSA W=$W ==="
    set outdir [file join $raw_dir ccsa_seq_W${W}]
    file mkdir $outdir
    catch {exec vivado -mode batch -source [file join $script_dir synth_one.tcl] \
         -tclargs $W $outdir > [file join $outdir synth.log] 2>@1} log_result
}

puts "ALL_WIDTHS_DONE. Reports in $raw_dir"
