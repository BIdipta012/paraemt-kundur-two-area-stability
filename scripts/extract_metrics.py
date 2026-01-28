#!/usr/bin/env python3
import sys
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------
# Paths and ParaEMT import so unpickling Lib_BW types works
# --------------------------------------------------------------------
ROOT = Path(__file__).parent.parent          # ~/BLACK/ACADEMIC/pub/fresh_paraEMT_study
PARA_DIR = ROOT / "ParaEMT_public"
sys.path.insert(0, str(PARA_DIR))            # make Lib_BW, etc. visible



STATE_INDEX = 1  # or whatever you use later

def load_pkl(path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    # New format: dict with "time" and "x"
    t = np.array(data["time"])
    x_dict = data["x"]  # dict: {1: state_vec_t1, 2: state_vec_t2, ...}

    # Sort keys to ensure correct time order
    keys = sorted(x_dict.keys())
    X = np.vstack([x_dict[k] for k in keys])  # shape: (n_samples, n_states)

    return t, X

def main():
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Current 4 scenarios, files in baseline_analysis/
    scenarios = {
        "Baseline":   PARA_DIR / "baseline_analysis/sim_snp_S6_50u_baseline.pkl",
        "Islanding":  PARA_DIR / "baseline_analysis/sim_snp_S6_50u_islanding.pkl",
        "Fault_LLG":  PARA_DIR / "baseline_analysis/sim_snp_S6_50u_fault_llg.pkl",
        "Heavy_Load": PARA_DIR / "baseline_analysis/sim_snp_S6_50u_heavy_load.pkl",
        "Strong_Grid": PARA_DIR / "baseline_analysis/sim_snp_S6_50u_Strong.pkl",   
   
    }

    rows = []

    print("\n" + "=" * 80)
    print("📊 EXTRACTING METRICS FROM 4 SCENARIOS")
    print("=" * 80 + "\n")

    for scen, p in scenarios.items():
        if not p.exists():
            print(f"⚠️  Missing file for {scen}: {p}")
            continue

        print(f"Processing: {scen:10} → {p}")

    # Choose measurement state per scenario
        if scen == "Fault_LLG":
            STATE_INDEX = 0   # strongly fault-sensitive state
        else:
            STATE_INDEX = 1   # frequency-like state for others

        t, X = load_pkl(p)
        print(scen, "time samples:", t.size)
        y = X[:, STATE_INDEX]
        # Basic time step
        if t.size > 1:
            dt = float(t[1] - t[0])
            dy = np.diff(y)
            rocof_series = dy / dt
        else:
            dt = 0.0
            rocof_series = np.array([])

        mean = float(np.mean(y))
        minv = float(np.min(y))
        maxv = float(np.max(y))
        std  = float(np.std(y))

        # Nadir depth = how far min is below mean
        nadir_depth = mean - minv

        # Simple max RoCoF over whole record (you can keep your windows if you want)
        if rocof_series.size > 0:
            max_rocof = float(np.max(np.abs(rocof_series)))
        else:
            max_rocof = 0.0

        # Settling time: first time |y - final_mean| < 1% final_mean
        if y.size > 1000:
            final_val = float(np.mean(y[-1000:]))
        else:
            final_val = float(np.mean(y))

        settled_idx = np.where(np.abs(y - final_val) < 0.01 * abs(final_val))[0]
        if settled_idx.size > 0:
            settling_time = float(t[settled_idx[0]])
        else:
            settling_time = None

        rows.append({
            "Scenario": scen,
            "Duration_s": float(t[-1]) if t.size else 0.0,
            "Timesteps": int(t.size),
            "Mean": mean,
            "Min": minv,
            "Max": maxv,
            "Std": std,
            "NadirDepth": nadir_depth,
            "MaxRoCoF": max_rocof,
            "SettlingTime_s": settling_time,
        })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "all_metrics_fresh.csv"
    df.to_csv(csv_path, index=False)

    print("\n" + "=" * 80)
    print("📊 METRICS SUMMARY TABLE")
    print("=" * 80 + "\n")
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("No metrics extracted.")
    print("\n" + "=" * 80)
    print(f"✅ Metrics saved to: {csv_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
