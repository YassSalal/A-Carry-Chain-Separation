#!/usr/bin/env bash
set -e
mkdir -p logs

WIDTHS="8 16 32 64 128 256"
DESIGNS="manchester_ripple manchester_static carry_skip_8 \
         kogge_stone_pipelined kogge_stone_comb \
         carry4_ripple carry4_pipelined ccsa"

for W in $WIDTHS; do
  for D in $DESIGNS; do
    echo "=== Running $D W=$W ==="
    vivado -mode batch -source scripts/synth_impl.tcl -tclargs "$W" "$D"
  done
done
