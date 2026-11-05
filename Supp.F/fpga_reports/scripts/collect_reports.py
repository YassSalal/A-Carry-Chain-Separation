#!/usr/bin/env python3
"""Collect Vivado post-route reports into Supp.F and collate them into the CSVs behind
Tables 16-18 (single source of truth for the manuscript numbers).

1. Copy each run folder written by kit/fpga/run_matched.tcl
   (results/matched/<design>_W<W>_dep<d>/ with timing_summary_routed.rpt,
   utilization_placed.rpt, power_routed.rpt, route_status.rpt, run_info.txt) into
   Supp.F/fpga_reports/raw/<design>/W<WWW>_dep<d>/:
       python3 collect_reports.py copy  results/matched  Supp.F/fpga_reports/raw
2. Collate:
       python3 collect_reports.py collate Supp.F/fpga_reports/raw Supp.F/fpga_reports/collated
   writes fpga_results.csv (one row per design, width and regime) and stops with an error
   if any report is missing or cannot be parsed.
3. Hash everything for the manifest:
       python3 Supp.F/fpga_reports/scripts/make_manifest.py Supp.F/fpga_reports
"""
import csv, re, shutil, sys
from pathlib import Path
CYCLES={'ccsa':6,'manchester_ripple':1,'manchester_static':1,'carry_skip_8':1,'kogge_stone_comb':1,
        'carry4_ripple':1,'kogge_stone_pipelined':None,'carry4_pipelined':None}   # None = pipeline depth, read from run_info
def die(msg): sys.exit('ERROR: '+msg)
def num(pat,text,where):
    m=re.search(pat,text,re.M)
    if not m: die(f'cannot parse {where} with /{pat}/')
    return float(m.group(1))
def parse_run(d: Path):
    info=dict(kv.split('=',1) for kv in (d/'run_info.txt').read_text().split())
    tim=(d/'timing_summary_routed.rpt').read_text(errors='ignore')
    utl=(d/'utilization_placed.rpt').read_text(errors='ignore')
    pwr=(d/'power_routed.rpt').read_text(errors='ignore')
    # Vivado "Design Timing Summary": header line with WNS(ns), dashes, then values
    wns=num(r'^\s*WNS\(ns\).*\n\s*-+.*\n\s*(-?\d+\.\d+)',tim,f'{d}/timing WNS')
    period=float(info['period_ns'])
    luts=num(r'^\|\s*Slice LUTs\*?\s*\|\s*(\d+)',utl,f'{d}/util LUTs')
    ffs =num(r'^\|\s*Slice Registers\s*\|\s*(\d+)',utl,f'{d}/util FFs')
    p_tot=num(r'^\|\s*Total On-Chip Power \(W\)\s*\|\s*(\d+\.\d+)',pwr,f'{d}/power total')*1000
    p_dyn=num(r'^\|\s*Dynamic \(W\)\s*\|\s*(\d+\.\d+)',pwr,f'{d}/power dynamic')*1000
    conf=re.search(r'^\|\s*Confidence Level\s*\|\s*(\w+)',pwr,re.M)
    design=info['design']; W=int(info['W']); dep=int(info['dependent'])
    cyc=CYCLES[design] if CYCLES[design] is not None else int(info.get('pipeline_depth','0')) or die(f'{d}: add pipeline_depth to run_info.txt')
    t_clk=period-wns                              # achieved post-route period
    lat=cyc*t_clk
    ii=cyc if (dep or design=='ccsa') else 1      # cycles between independent issues
    e_op=p_tot*ii*t_clk                           # pJ (mW x ns)
    return dict(design=design,W=W,dependent=dep,period_constraint_ns=period,WNS_ns=wns,T_clk_ns=round(t_clk,3),
                cycles=cyc,latency_ns=round(lat,3),II=ii,throughput_Mops=round(1000/(ii*t_clk),1),LUTs=int(luts),FFs=int(ffs),
                power_total_mW=round(p_tot,1),power_dynamic_mW=round(p_dyn,1),power_confidence=conf.group(1) if conf else '',
                E_op_pJ=round(e_op,1),EDP_pJns=round(e_op*lat,1),commit=info.get('commit',''),vivado=info.get('vivado',''),
                source=str(d))
def main():
    if len(sys.argv)!=4: die(__doc__)
    cmd,src,dst=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3])
    if cmd=='copy':
        for d in sorted(p for p in src.iterdir() if (p/'run_info.txt').exists()):
            info=dict(kv.split('=',1) for kv in (d/'run_info.txt').read_text().split())
            out=dst/info['design']/f"W{int(info['W']):03d}_dep{info['dependent']}"
            out.mkdir(parents=True,exist_ok=True)
            for f in d.iterdir(): shutil.copy2(f,out/f.name)
            print('copied',d,'->',out)
    elif cmd=='collate':
        rows=[parse_run(p.parent) for p in sorted(src.rglob('run_info.txt'))]
        if not rows: die(f'no run_info.txt under {src}')
        dst.mkdir(parents=True,exist_ok=True)
        with open(dst/'fpga_results.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        print(f'wrote {dst/"fpga_results.csv"} with {len(rows)} runs')
    else: die(__doc__)
if __name__=='__main__': main()
