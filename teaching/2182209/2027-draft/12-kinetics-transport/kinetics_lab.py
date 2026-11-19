"""Class 12 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Electrode kinetics (Butler-Volmer) and mass transport (limiting current). Every number on
the Class 12 slides and in Lab 12 comes from this module.

Run `python kinetics_lab.py` for a printed summary, or `python kinetics_lab.py --json` to
write kinetics-results.json.

Model, stated: one-electron step (n = 1), symmetric (alpha = 0.5), 25 degC; cathodic current
negative. Kinetic current from Butler-Volmer, j_k = j0 [exp(alpha f eta) - exp(-alpha f eta)],
f = F/(RT). With a limiting current, the cathodic current is combined as
1/|j| = 1/|j_k| + 1/j_lim (kinetics and transport in series). Teaching parameters:
j0 = 1.00 mA/cm2; j_lim = 2 and 6 mA/cm2. Order-of-magnitude example for Cu plating:
D(Cu2+) = 7e-6 cm2/s, c = 0.10 M, diffusion layer 50 um, n = 2 (values of the usual order).
"""
import json
import math
import sys

import numpy as np
from scipy import constants as sc

F = sc.physical_constants["Faraday constant"][0]
RGAS, T = sc.R, 298.15
f = F / (RGAS * T)
ALPHA, J0 = 0.5, 1.00                      # -, mA/cm2


def j_bv(eta, j0=J0, a=ALPHA):
    """Butler-Volmer, mA/cm2; anodic positive."""
    return j0 * (np.exp(a * f * eta) - np.exp(-a * f * eta))


def j_cath(eta, j_lim, j0=J0):
    """Cathodic current with a transport limit, mA/cm2 (negative)."""
    jk = -j_bv(eta, j0)                    # positive magnitude for eta < 0
    return -1.0 / (1.0 / jk + 1.0 / j_lim)


def eta_for(j_target, j0):
    """Cathodic overpotential (V, negative) for a kinetic current magnitude j_target."""
    return -math.asinh(j_target / (2 * j0)) / (ALPHA * f)


def j_lim_est(n=2, D=7e-6, c_M=0.6, delta_cm=50e-4):
    """j_lim = n F D c / delta, mA/cm2 (c in mol/cm3)."""
    return n * F * D * (c_M * 1e-3) / delta_cm * 1e3


def lab_results():
    j05 = float(j_bv(-0.050))
    return {"j_m050": j05, "j_m100": float(j_bv(-0.100)), "ratio": float(j_bv(-0.100) / j_bv(-0.050)),
            "eta_slow": eta_for(abs(j05), 0.1),
            "jl2_m020": float(j_cath(-0.20, 2)), "jl2_m025": float(j_cath(-0.25, 2)),
            "jl6_m025": float(j_cath(-0.25, 6)),
            "gain_eta_pct": float((j_cath(-0.25, 2) / j_cath(-0.20, 2) - 1) * 100),
            "gain_jlim_pct": float((j_cath(-0.25, 6) / j_cath(-0.25, 2) - 1) * 100),
            "f": f, "alpha": ALPHA, "j0": J0}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    eta = np.round(np.arange(-0.25, 0.2501, 0.01), 3)
    R["lecture"] = {
        "f": f, "alpha": ALPHA, "tafel_mV": 1000 * math.log(10) / (ALPHA * f),
        "eta": eta.tolist(),
        "bv": {str(j0): [round(float(x), 5) for x in j_bv(eta, j0)] for j0 in (0.1, 1.0, 10.0)},
        "pol": {str(jl): [round(float(j_cath(e, jl)), 5) if e < 0 else None for e in eta] for jl in (2, 6)},
        "kin": [round(float(-j_bv(e)), 5) if e < 0 else None for e in eta],
        "jlim_cu": j_lim_est(),
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("kinetics-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote kinetics-results.json"); sys.exit()
    L = R["lab"]
    print("f = %.3f 1/V; Tafel slope %.1f mV/decade" % (L["f"], R["lecture"]["tafel_mV"]))
    print("j(-0.050) = %.3f, j(-0.100) = %.3f mA/cm2, ratio %.2f" % (L["j_m050"], L["j_m100"], L["ratio"]))
    print("eta for the same current at j0 = 0.1: %.4f V" % L["eta_slow"])
    print("j_lim 2: %.3f (-0.20 V), %.3f (-0.25 V), +%.1f%%" % (L["jl2_m020"], L["jl2_m025"], L["gain_eta_pct"]))
    print("j_lim 6 at -0.25 V: %.3f (+%.0f%%)" % (L["jl6_m025"], L["gain_jlim_pct"]))
    print("Cu plating j_lim estimate: %.1f mA/cm2" % R["lecture"]["jlim_cu"])
