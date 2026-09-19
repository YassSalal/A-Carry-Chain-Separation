PY      := python3
IVERILOG:= iverilog
VVP     := vvp
VIVADO  := vivado

W       ?= 8
N_RAND  ?= 20000

.PHONY: all ref rtl sim synth clean

all: ref rtl sim

ref:
	$(PY) Supp.A/reference_model/ccsa_ref.py

rtl:
	$(IVERILOG) -g2012 -o build/tb_ccsa.vvp \
	    Supp.B/rtl/ccsa_adder.sv Supp.C/testbench/tb_ccsa.sv

sim: rtl
	$(VVP) build/tb_ccsa.vvp

synth:
	$(VIVADO) -mode batch -source Supp.D/vivado_scripts/sweep_widths.tcl

clean:
	rm -rf build/
