"""Plot the single-segment transient waveform for the CCSA manuscript (new Fig. 3).

Export from your simulator a CSV with columns:
    time_s, v_vsw_ctrl, v_inject, v_far_end
(VSW control gate, Bus-2 node at the injection slice, Bus-2 node at the far end
of the k = 16 segment), for the TT corner and optionally SS/FF.

Usage:
    python plot_segment_waveform.py tt.csv [ss.csv ff.csv] -o fig_segment_waveform.png

The script marks the 50% crossings and prints t_seg so the figure and Table 10
are produced from the same data. It plots only what is in the CSV files.
"""
import argparse
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VDD = {"tt": 0.70, "ff": 0.77, "ss": 0.63}
COL = {"inject": "#2a78d6", "far": "#eb6834", "ctrl": "#a8a79f"}


def load(path):
    t, c, a, b = [], [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            t.append(float(row["time_s"]) * 1e12)
            c.append(float(row["v_vsw_ctrl"]))
            a.append(float(row["v_inject"]))
            b.append(float(row["v_far_end"]))
    return t, c, a, b


def crossing(t, v, level):
    for i in range(1, len(v)):
        if v[i - 1] < level <= v[i]:
            return t[i - 1] + (level - v[i - 1]) * (t[i] - t[i - 1]) / (v[i] - v[i - 1])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("-o", "--out", default="fig_segment_waveform.png")
    args = ap.parse_args()
    fig, axs = plt.subplots(1, len(args.csv), figsize=(3.4 * len(args.csv), 2.4), squeeze=False)
    for ax, path in zip(axs[0], args.csv):
        corner = next((k for k in VDD if k in path.lower()), "tt")
        vdd = VDD[corner]
        t, c, a, b = load(path)
        ax.plot(t, c, color=COL["ctrl"], lw=1, label="VSW control")
        ax.plot(t, a, color=COL["inject"], lw=2, label="Bus 2, injection slice")
        ax.plot(t, b, color=COL["far"], lw=2, ls=(0, (4, 2)), label="Bus 2, far end (slice 16)")
        ax.axhline(vdd / 2, color="#77776f", lw=0.8, ls=":")
        ta, tb = crossing(t, a, vdd / 2), crossing(t, b, vdd / 2)
        if ta is not None and tb is not None:
            ax.annotate("", xy=(tb, vdd / 2), xytext=(ta, vdd / 2),
                        arrowprops=dict(arrowstyle="<->", color="#2b2b29", lw=0.8))
            ax.text((ta + tb) / 2, vdd / 2 + 0.03, f"t_seg = {tb - ta:.1f} ps", ha="center", fontsize=7)
            print(f"{path}: t_seg = {tb - ta:.2f} ps")
        ax.set_title(corner.upper(), fontsize=8, loc="left")
        ax.set_xlabel("Time (ps)")
        ax.set_ylabel("Voltage (V)")
        ax.spines[["top", "right"]].set_visible(False)
    axs[0][0].legend(fontsize=6.5, frameon=False, loc="lower right")
    fig.savefig(args.out, dpi=600, bbox_inches="tight")


if __name__ == "__main__":
    main()
