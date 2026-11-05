[README_pnr.md](https://github.com/user-attachments/files/34408817/README_pnr.md)
# ASAP7 area and routing comparison (Reviewer 5 pt 3)
1. Install OpenROAD-flow-scripts (Docker image or build) with the ASAP7 platform.
2. bash kit/asap7_pnr/make_orfs.sh <ORFS>/flow ; run make for each generated config.
3. Report per design and width: standard-cell area (um^2), core area, total wirelength,
   routing congestion (GRT overflow), worst slack at the swept period, and power.
4. Add the transmission-gate bus of the CCSA from Section 7.4.1 (bit pitch 0.8 um, repeater
   footprint 0.5 x 1.0 um per k = 16 bits, Bus 1, Bus 2 and shield tracks) to its standard-cell
   area, and state that this part is a layout estimate. Replace the transistor-count column of
   Table 24 by these areas, or add them as two new columns.
SystemVerilog note: ORFS reads Verilog through Yosys; if a construct is rejected, convert the
RTL with sv2v first.
