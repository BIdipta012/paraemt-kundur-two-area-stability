# Scripts

This directory contains helper scripts for the ParaEMT Kundur two-area stability study.

## extract_metrics.py

`extract_metrics.py` loads the simulation results produced by `main_step1_simulation.py` for the scenarios:

- Baseline  
- Strong_Grid  
- Heavy_Load  
- Islanding  
- Fault_LLG  

For each scenario, it:

- Reads the saved `.pkl` file.  
- Extracts the monitored rotor-speed state (state index 1).  
- Computes the stability metrics (mean, min, max, standard deviation, nadir depth, maximum RoCoF, settling time).  
- Writes all metrics to `results/all_metrics_fresh.csv`.

Run it from the repository root with:

```bash
python scripts/extract_metrics.py

