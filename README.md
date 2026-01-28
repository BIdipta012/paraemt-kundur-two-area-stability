# EMT-Based Frequency Stability Assessment of a Modified Kundur Two-Area System Using ParaEMT

This repository contains code associated with the work:

> EMT-Based Frequency Stability Assessment of a Modified Kundur Two-Area System Using the Open-Source ParaEMT Simulator (submitted to TENCON 2026).

We use the open-source ParaEMT simulator to study five operating scenarios on the modified Kundur two-area system (ParaEMT system 6): 

**Baseline**, 
**Strong Grid**, 
**Islanding**, 
**Heavy Load**, 
and 
**line-to-line-to-ground (Fault LLG)**. 
From a monitored rotor-speed state, we compute frequency-like stability metrics including nadir depth, maximum rate of change of frequency (RoCoF), and settling time, 
which are useful for microgrid protection and control design.

## Dependencies

- Python 3.12 (or similar 3.x version)
- ParaEMT (NREL open-source EMT simulator)
- NumPy
- Pandas
- Numba
- (Optional) Matplotlib for plotting

You can install Python packages with:

```bash
pip install -r requirements.txt
