# EMT-Based Frequency Stability Assessment of a Modified Kundur Two-Area System Using ParaEMT

This repository contains code and example data for the study:

> EMT-Based Frequency Stability Assessment of a Modified Kundur Two-Area System Using the Open-Source ParaEMT Simulator (submitted to TENCON 2026).

The project uses the open-source ParaEMT simulator to analyze frequency stability of the modified Kundur two-area benchmark (ParaEMT system 6) under five operating scenarios:

- Baseline  
- Strong Grid  
- Heavy Load  
- Islanding  
- Line-to-line-to-ground (Fault LLG) fault  

For each scenario, the code simulates the electromagnetic transient (EMT) response and computes frequency-like metrics from a monitored rotor-speed state, including nadir depth, maximum rate of change of frequency (RoCoF), and settling time. These metrics are intended to support microgrid protection and control design, especially in resource-constrained settings.

---

## Repository structure

- `main_step1_simulation.py`  
  Multi-scenario EMT driver script. Runs the five scenarios on ParaEMT system 6, using consistent simulation settings (50 μs time step, 10 s horizon) and scenario-specific configuration (Baseline, Strong Grid, Heavy Load, Islanding, Fault LLG).

- `Lib_BW.py`  
  Supporting library with EMT-related routines used by the main script.

- `scripts/`  
  - `extract_metrics.py`: post-processing script that reads scenario output files and computes the stability metrics for the monitored rotor-speed state, writing them to a CSV file. See `scripts/README.md` for more details.

- `results/`  
  - `all_metrics_fresh.csv`: example metrics table summarizing the seven scalar metrics (mean, min, max, standard deviation, nadir depth, maximum RoCoF, settling time) for each scenario.

- `README.md`  
  This file.

- `requirements.txt`  
  Python dependencies for running the scripts.

---

## Requirements

- Python 3.12 (or a compatible Python 3.x version)
- ParaEMT (NREL’s open-source EMT simulator, installed separately)
- Python packages:
  - `numpy`
  - `pandas`
  - `numba`
  - (optional) `matplotlib` for plotting

You can install the Python dependencies with:

```bash
pip install -r requirements.txt
