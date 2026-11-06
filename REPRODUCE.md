# Reference model: exhaustive (12- and 16-bit), directed corner cases, cross-check
   python3 Supp.A/A_reference_model/verify_exhaustive.py exhaustive 12 0
   python3 Supp.A/A_reference_model/verify_exhaustive.py exhaustive 12 1
   python3 Supp.A/A_reference_model/verify_exhaustive.py exhaustive 16 0   # ~20 min
   python3 Supp.A/A_reference_model/verify_exhaustive.py exhaustive 16 1   # ~20 min
   python3 Supp.A/A_reference_model/verify_exhaustive.py directed
   python3 Supp.A/A_reference_model/verify_exhaustive.py crosscheck Supp.A/A_reference_model

   # RTL (ModelSim/Questa), one run per width
   vlog -sv Supp.B/B_rtl/ccsa_adder.sv Supp.C/testbench/tb_ccsa_v2.sv +define+W_PARAM=64
   vsim -c tb_ccsa_v2 -do "run -all"
