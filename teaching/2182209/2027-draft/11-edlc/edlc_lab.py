"""Class 11 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

The electric double layer and supercapacitors (EDLCs). Every number on the Class 11 slides
and in Lab 11 comes from this module.

Run `python edlc_lab.py` for a printed summary, or `python edlc_lab.py --json` to write
edlc-results.json.

Synthetic teaching data, labeled as such: two EDLCs, A (0.200 F) and B (0.100 F), each
charged at a constant 0.010 A, with a 1.0 ohm series resistance (ESR) that adds a 0.010 V
step when the current starts. The capacitance is found from the slope, C = I dt/dV, by a
least-squares line through the points (numpy.polyfit), so the ESR step does not enter it.
Order-of-magnitude values, stated: double-layer capacitance about 10 uF/cm2 of real surface;
activated carbon about 1000 m2/g. DRAM cell: about 20 fF at 1 V (typical order).
"""
import json
import sys

import numpy as np
from scipy import constants as sc

I = 0.010                     # A
ESR = 1.0                     # ohm
CAPS = {"A": 0.200, "B": 0.100}
T = np.arange(0, 21, 2.0)     # s
E_CHARGE = sc.e


def vt(C, t=T, I=I, esr=ESR):
    """Constant-current charge: V = I R + I t / C (synthetic data)."""
    return I * esr + I * t / C


def fit_C(t, v, I=I):
    """C = I / (dV/dt), slope from a least-squares line."""
    slope, icpt = np.polyfit(t, v, 1)
    return {"slope": float(slope), "intercept": float(icpt), "C": float(I / slope)}


def store(C, V=None, Q=None):
    """Q = C V and E = C V^2 / 2, from either V or Q."""
    if V is None:
        V = Q / C
    Q = C * V
    return {"C": C, "V": V, "Q": Q, "E_J": 0.5 * C * V * V}


def lab_results():
    vA, vB = vt(CAPS["A"]), vt(CAPS["B"])
    fA, fB = fit_C(T, vA), fit_C(T, vB)
    sA = store(fA["C"], V=1.0)
    return {"t": T.tolist(), "vA": [round(float(x), 4) for x in vA], "vB": [round(float(x), 4) for x in vB],
            "fitA": fA, "fitB": fB, "I": I, "esr_step": I * ESR,
            "t_to_1V": {"A": CAPS["A"] * 1.0 / I, "B": CAPS["B"] * 1.0 / I},
            "A_1V": sA, "A_double": store(2 * fA["C"], Q=sA["Q"])}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    c_area = 10e-6            # F/cm2
    area = 1000 * 1e4         # cm2/g, 1000 m2/g
    dram = store(20e-15, V=1.0)
    R["lecture"] = {
        "F_per_g": c_area * area, "c_area_uF": c_area * 1e6, "area_m2g": 1000,
        "dram": dram, "dram_electrons": dram["Q"] / E_CHARGE,
        "vlim": {"aqueous": 1.0, "organic": 2.7},
        "E_ratio_organic": (2.7 / 1.0) ** 2,
        "compare": [{"k": "Stores charge by", "edlc": "ions gathering at the surface", "bat": "redox reactions in the electrodes"},
                    {"k": "Voltage while discharging", "edlc": "falls in a straight line", "bat": "stays nearly flat"},
                    {"k": "Charge or discharge time", "edlc": "seconds", "bat": "tens of minutes to hours"},
                    {"k": "Cycle life", "edlc": "hundreds of thousands", "bat": "hundreds to thousands"},
                    {"k": "Energy per kg", "edlc": "low", "bat": "high"}],
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("edlc-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote edlc-results.json"); sys.exit()
    L = R["lab"]
    for k in ("A", "B"):
        f = L["fit" + k]; print("%s: slope %.4f V/s, intercept %.4f V, C = %.3f F" % (k, f["slope"], f["intercept"], f["C"]))
    print("time to 1.0 V:", L["t_to_1V"])
    print("A at 1.0 V:", L["A_1V"]); print("A doubled, same Q:", L["A_double"])
    Lc = R["lecture"]; print("carbon: %.0f F/g; DRAM: Q %.2e C = %.0f electrons" % (Lc["F_per_g"], Lc["dram"]["Q"], Lc["dram_electrons"]))
