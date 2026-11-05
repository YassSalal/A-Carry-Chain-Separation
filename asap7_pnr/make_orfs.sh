#!/usr/bin/env bash
# ASAP7 place-and-route set-up for Reviewer 5 pt 3 with OpenROAD-flow-scripts (ORFS).
# Usage (from the CCSA repository root):  bash kit/asap7_pnr/make_orfs.sh <ORFS>/flow
# Creates flow/designs/asap7/ccsa_<design>_w<W>/ with config.mk and constraint.sdc for the CCSA,
# the static Manchester chain and the combinational Kogge-Stone adder, each between the same
# input/output registers (matched_wrapper, DEPENDENT=0). Then run, e.g.:
#   make -C <ORFS>/flow DESIGN_CONFIG=designs/asap7/ccsa_kogge_stone_comb_w64/config.mk
# and read area (um^2), utilization, wirelength and timing from logs/ and reports/.
# The CCSA is realized here entirely in standard cells: its Bus 2 becomes a gate-level OR chain,
# so this run measures the logic, registers and control of the CCSA; the transmission-gate bus,
# repeaters and shields must be added from the custom layout of Section 7.4.1.
set -euo pipefail
FLOW=$1; KIT=$(cd "$(dirname "$0")/.." && pwd); REPO=$(pwd)
for design in ccsa manchester_static kogge_stone_comb; do
  for W in 64 256; do
    d=$FLOW/designs/asap7/ccsa_${design}_w${W}; mkdir -p "$d"
    if [ "$design" = ccsa ]; then rtl="$REPO/Supp.B/B_rtl/ccsa_adder.sv"; else rtl="$(ls $REPO/baselines/$design/rtl/*.sv)"; fi
    cat > "$d/pnr_top.sv" <<SV
module pnr_top (input logic clk, rst, input logic [$((W-1)):0] x_in, input logic x_valid,
                output logic [$W:0] s_out, output logic s_valid, output logic [31:0] op_count);
  matched_wrapper #(.W($W), .DEPENDENT(0)) u (.*);
endmodule
SV
    cat > "$d/config.mk" <<MK
export DESIGN_NICKNAME = ccsa_${design}_w${W}
export DESIGN_NAME     = pnr_top
export PLATFORM        = asap7
export VERILOG_FILES   = $rtl $KIT/fpga/adapter_${design}.sv $KIT/fpga/matched_wrapper.sv $d/pnr_top.sv
export SDC_FILE        = $d/constraint.sdc
export CORE_UTILIZATION = 40
export PLACE_DENSITY   = 0.60
MK
    cat > "$d/constraint.sdc" <<SDC
# ASAP7 in ORFS uses picoseconds. Sweep the period down until worst slack is about zero.
set period 400
create_clock -name clk -period \$period [get_ports clk]
set_input_delay  [expr 0.3*\$period] -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay [expr 0.3*\$period] -clock clk [all_outputs]
SDC
  done
done
echo "ORFS designs written to $FLOW/designs/asap7/"
