[README1.md](https://github.com/user-attachments/files/32509896/README1.md)
# A-Carry-Chain-Separation

Reference model, RTL, testbenches, and verification logs for the
Carry-Chain-Separation Architecture (CCSA).

## Quick start

```bash
git clone https://github.com/YassSalal/A-Carry-Chain-Separation.git
cd A-Carry-Chain-Separation
git checkout v2.1.0-baselines

# Python reference model
python reference_model/ccsa_ref.py --exhaustive-8

# RTL simulation
vsim -c -do scripts/run_modelsim.do

# FPGA PPA
bash scripts/run_all_baselines.sh
