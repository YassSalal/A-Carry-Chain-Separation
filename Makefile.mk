PY      := python3
IVERILOG:= iverilog
VVP     := vvp
VIVADO  := vivado

W       ?= 8
N_RAND  ?= 20000

.PHONY: all ref rtl sim synth clean

all: ref rtl sim

ref:
	$(PY) supp/A_reference_model/ccsa_ref.py

rtl:
	$(IVERILOG) -g2012 -o build/tb_ccsa.vvp \
	    supp/B_rtl/ccsa_adder.sv supp/C_testbench/tb_ccsa.sv

sim: rtl
	$(VVP) build/tb_ccsa.vvp

synth:
	$(VIVADO) -mode batch -source supp/D_vivado_scripts/sweep_widths.tcl

clean:
	rm -rf build/