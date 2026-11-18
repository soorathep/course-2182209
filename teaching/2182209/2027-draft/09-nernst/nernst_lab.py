"""Class 9 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Standard potentials, cell potential, Gibbs energy and the Nernst equation at 25 degC.
Every number on the Class 9 slides and in Lab 9 comes from this module.

Run `python nernst_lab.py` for a printed summary, or `python nernst_lab.py --json` to
write nernst-results.json.

Standard reduction potentials (V against the standard hydrogen electrode, 25 degC), rounded
to two decimals from OpenStax Chemistry 2e, Appendix L: Ag+/Ag 0.80, Cu2+/Cu 0.34,
H+/H2 0.00, Fe2+/Fe -0.44, Zn2+/Zn -0.76, Al3+/Al -1.66.
Constants: CODATA 2018 exact values of F and R, via scipy.constants. Activities are taken
equal to molar concentrations (an approximation that is fair for dilute solutions).
"""
import json
import math
import sys

import numpy as np
from scipy import constants as sc

F = sc.physical_constants["Faraday constant"][0]     # C/mol
RGAS = sc.R                                          # J/(mol K)
T = 298.15                                           # K
K = math.log(10) * RGAS * T / F                      # V, 0.05916 at 25 degC
E0 = {"Ag": (0.80, 1), "Cu": (0.34, 2), "H2": (0.00, 2), "Fe": (-0.44, 2), "Zn": (-0.76, 2), "Al": (-1.66, 3)}
ION = {"Ag": "Ag+", "Cu": "Cu2+", "H2": "H+", "Fe": "Fe2+", "Zn": "Zn2+", "Al": "Al3+"}


def r6(x):
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def e_half(metal, c):
    """Nernst for M^z+ + z e- -> M: E = E0 + (K/z) log10 c."""
    e0, z = E0[metal]
    return e0 + K / z * np.log10(c)


def cell(cathode, anode):
    """Standard cell: E0cell = E0(cathode) - E0(anode); dG0 = -n F E0cell for the balanced reaction."""
    zc, za = E0[cathode][1], E0[anode][1]
    n = zc * za // math.gcd(zc, za)
    e = E0[cathode][0] - E0[anode][0]
    return {"cathode": cathode, "anode": anode, "n": n, "E0": r6(e), "dG0_kJ": r6(-n * F * e / 1000), "goes": e > 0}


def daniell(c_zn, c_cu):
    """Zn | Zn2+ || Cu2+ | Cu: E = E0cell - (K/2) log10([Zn2+]/[Cu2+])."""
    e0 = E0["Cu"][0] - E0["Zn"][0]
    return e0 - K / 2 * np.log10(c_zn / c_cu)


def lab_results():
    zc = cell("Cu", "Zn")
    return {"K": K, "E_cu": {str(c): float(e_half("Cu", c)) for c in (1.0, 0.1, 0.01, 0.001)},
            "per_decade": K / 2, "per_two": K, "zncu": zc, "alcu": cell("Cu", "Al"),
            "dan": float(daniell(1.0, 0.010)), "F": F, "R": RGAS, "T": T}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    order = sorted(E0, key=lambda m: -E0[m][0])
    R["lecture"] = {
        "E0": [{"m": m, "ion": ION[m], "E0": E0[m][0], "z": E0[m][1]} for m in order],
        "cells": {f"{c}|{a}": cell(c, a) for c in E0 for a in E0 if c != a},
        "K": K, "F": F, "R": RGAS, "T": T,
        "cu_curve": [[r6(x), r6(e_half("Cu", 10 ** x))] for x in np.arange(-4, 0.001, 0.25)],
        "zn_curve": [[r6(x), r6(e_half("Zn", 10 ** x))] for x in np.arange(-4, 0.001, 0.25)],
        "E_cu": {str(c): float(e_half("Cu", c)) for c in (1.0, 0.1, 0.01, 0.001)},
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("nernst-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote nernst-results.json"); sys.exit()
    L = R["lab"]
    print("2.303 RT/F = %.5f V" % L["K"])
    for c, e in L["E_cu"].items():
        print("E(Cu2+/Cu) at %s M = %.4f V" % (c, e))
    print("per decade %.4f V, per two decades %.4f V" % (L["per_decade"], L["per_two"]))
    for k in ("zncu", "alcu"):
        c = L[k]; print("%s|%s: n=%d E0=%.3f V dG0=%.1f kJ/mol" % (c["cathode"], c["anode"], c["n"], c["E0"], c["dG0_kJ"]))
    print("Daniell [Zn2+]=1.0, [Cu2+]=0.010: E = %.4f V" % L["dan"])
