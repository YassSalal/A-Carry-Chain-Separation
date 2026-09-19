# Sweep the widths reported in Table 10.
foreach W {8 16 32 64 128 256} {
    puts "== CCSA W=$W =="
    source supp/D_vivado_scripts/synth_ccsa.tcl
}