# --------------------------------------------
# EMT solver main function - multi-scenario
# --------------------------------------------

import os
import time
import numpy as np

from Lib_BW import *
from psutils import *
from preprocessscript import get_json_pkl

workingfolder = '.'
os.chdir(workingfolder)


def run_scenario(
    scenario_name,
    ts=50e-6,
    Tlen=10.0,
    systemN=6,
    netMod="lu",
    nparts=2,
):
    """
    Run one EMT simulation scenario on ParaEMT system 6.

    Scenarios:
      - Baseline
      - Strong_Grid
      - Heavy_Load
      - Islanding
      - Fault_LLG
    """

    SimMod = 0  # 0 - fresh run, 1 - from snapshot
    DSrate = 10
    N_row = 1
    N_col = 1

    # Output tags per scenario
    tag = scenario_name
    ts_us = int(ts * 1e6)
    output_snp_ful = f"sim_snp_S{systemN}_{ts_us}u_{tag}.pkl"
    output_snp_1pt = f"sim_snp_S{systemN}_{ts_us}u_1pt_{tag}.pkl"
    output_res = f"sim_res_S{systemN}_{ts_us}u_{tag}.pkl"

    # Initialize EMT
    t0 = time.time()
    if SimMod == 0:
        (pfd, ini, dyd, emt) = initialize_emt(
            workingfolder, systemN, N_row, N_col, ts, Tlen,
            mode=netMod, nparts=nparts
        )
    else:
        (pfd, ini, dyd, emt) = initialize_from_snp(
            output_snp_1pt, netMod, nparts
        )

    # --------- Common defaults for all scenarios ---------
    # Start with const-RLC, no PLL release
    emt.t_release_f = 0.0
    emt.loadmodel_option = 1  # 1 - const-RLC, 2 - const-Z

    # Disable gen trip by default
    emt.t_gentrip = 100.0
    emt.i_gentrip = 0
    emt.flag_gentrip = 1
    emt.flag_reinit = 1

    # Disable step change by default
    emt.t_sc = 100.0
    emt.i_gen_sc = 0
    emt.flag_exc_gov = 1
    emt.dsp = -0.02
    emt.flag_sc = 1

    # Reset any fault-related flags to a safe default
    if hasattr(emt, "flag_fault"):
        emt.flag_fault = 0

    # --------- Scenario-specific settings ---------

    if scenario_name == "Baseline":
        # Baseline: const-RLC, grid-connected, no major events
        # (defaults already reflect this)
        pass

    elif scenario_name == "Strong_Grid":
        # Strong Grid: const-RLC, stiff external grid, no islanding or fault
        # The strong-grid nature is encoded in system 6 data / ini; no extra changes here.
        pass

    elif scenario_name == "Heavy_Load":
        # HEAVY LOAD SCENARIO: increase loads, no gen trip, no fault
        emt.t_release_f = 0.0
        emt.loadmodel_option = 1  # const-RLC

        # disable gen trip
        emt.t_gentrip = 100.0
        emt.i_gentrip = 0
        emt.flag_gentrip = 1
        emt.flag_reinit = 1

        # scale all loads by 1.5x
        if hasattr(pfd, "load_MW") and hasattr(pfd, "load_Mvar"):
            pfd.load_MW *= 1.50
            pfd.load_Mvar *= 1.50

        # keep step-change disabled (t_sc far in the future)
        emt.t_sc = 100.0
        emt.i_gen_sc = 0
        emt.flag_exc_gov = 1
        emt.dsp = -0.02
        emt.flag_sc = 1

    elif scenario_name == "Islanding":
        # ISLANDING-LIKE SCENARIO: disable gen trip, change load model at 1.5 s
        emt.t_gentrip = 100.0
        emt.i_gentrip = 0
        emt.flag_gentrip = 1
        emt.flag_reinit = 1

        # Use const-Z load model and release PLL at 1.5 s
        t_release_f = 1.5
        loadmodel_option = 2
        emt.t_release_f = t_release_f
        emt.loadmodel_option = loadmodel_option  # const-Z after islanding

        # Keep step-change disabled so only islanding-like effect shows
        emt.t_sc = 100.0
        emt.i_gen_sc = 0
        emt.flag_exc_gov = 1
        emt.dsp = -0.02
        emt.flag_sc = 1

    elif scenario_name == "Fault_LLG"
        # FAULT_LLG SCENARIO: const-RLC load, apply LLG fault
        t_release_f = 0.0
        loadmodel_option = 1
        emt.t_release_f = t_release_f
        emt.loadmodel_option = loadmodel_option

        # disable gen trip so only the fault disturbs the system
        emt.t_gentrip = 100.0
        emt.i_gentrip = 0
        emt.flag_gentrip = 1
        emt.flag_reinit = 1

        # configure the fault
        emt.i_faultbus = 7      # fault bus index in the two-area system
        emt.Rfault = 0.01       # low fault resistance
        emt.fault_time = 2.0    # fault applied at 2.0 s
        if hasattr(emt, "flag_fault"):
            emt.flag_fault = 1

        # keep step-change disabled so fault is the main event
        emt.t_sc = 100.0
        emt.i_gen_sc = 0
        emt.flag_exc_gov = 1
        emt.dsp = -0.02
        emt.flag_sc = 1

    else:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    # --------- Time loop ---------

    tn = 0
    tsave = 0

    while tn * ts < Tlen:
        tn += 1

        # scenario events
        emt.StepChange(dyd, ini, tn)
        emt.GenTrip(pfd, dyd, ini, tn, netMod)
        # Fault injection is usually handled inside emt based on fault_time, i_faultbus, etc.

        # EMT steps
        emt.predictX(pfd, dyd, emt.ts)

        emt.Igs = emt.Igs * 0
        emt.updateIg(pfd, dyd, ini)

        emt.Igi = emt.Igi * 0
        emt.Iibr = emt.Iibr * 0
        emt.updateIibr(pfd, dyd, ini)

        if emt.loadmodel_option == 1:
            pass
        else:
            emt.Il = emt.Il * 0
            emt.updateIl(pfd, dyd, tn)

        emt.solveV(ini)
        emt.BusMea(pfd, dyd, tn)
        emt.updateX(pfd, dyd, ini, tn)
        emt.updateXibr(pfd, dyd, ini, ts)

        if emt.loadmodel_option == 1:
            pass
        else:
            emt.updateXl(pfd, dyd, tn)

        emt.x_pred = {0: emt.x_pred[1], 1: emt.x_pred[2], 2: emt.x_pv_1}

        if np.mod(tn, DSrate) == 0:
            tsave += 1
            emt.t.append(tn * ts)
            print(f"{scenario_name}: t = {emt.t[-1]:.4f}")

            emt.x[tsave] = emt.x_pv_1.copy()
            if len(pfd.ibr_bus) > 0:
                emt.x_ibr[tsave] = emt.x_ibr_pv_1.copy()
            if len(pfd.bus_num) > 0:
                emt.x_bus[tsave] = emt.x_bus_pv_1.copy()
            if len(pfd.load_bus) > 0:
                emt.x_load[tsave] = emt.x_load_pv_1.copy()
            emt.v[tsave] = emt.Vsol.copy()

    t1 = time.time()
    print(f"{scenario_name}: simulation completed in {t1 - t0:.1f} s")


def main():
    scenarios = ["Baseline", "Strong_Grid", "Heavy_Load", "Islanding", "Fault_LLG"]
    for sc in scenarios:
        print(f"\n=== Running scenario: {sc} ===")
        run_scenario(sc)


if __name__ == "__main__":
    main()
