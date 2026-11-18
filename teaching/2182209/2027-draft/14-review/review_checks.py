"""Class 14 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Review in three stations. Every number on the Class 14 slides and in Lab 14 comes from this
module. The formulas are the same as in the Class 6, 9, 10, 11 and 13 modules; they are
repeated here so that this file runs on its own.

Run `python review_checks.py` for a printed summary, or `python review_checks.py --json` to
write review-results.json.

Station 1, materials and doping (Classes 1, 2, 6): Si at 300 K, n_i 1.45e10 cm-3,
mobilities 1350 and 480 cm2/(V s), 1e16 cm-3 of P.
Station 2, Cu deposition (Classes 9, 10, 13): 0.100 A, 600 s, 90% efficiency, 10.0 cm2;
E0(Cu2+/Cu) 0.34 V; acid bath at pH 1.
Station 3, storage choice (Classes 10, 11): a 3 W, 5 s pulse and a 0.10 W, 1 h load.
Teaching devices, stated: an EDLC of 4.4 F charged to 2.7 V (usable energy taken as all of
1/2 C V^2), maximum power 5 W; a Li-ion cell of 100 mAh at 3.7 V, maximum power at 2C.
"""
import json
import math
import sys

import numpy as np
from scipy import constants as sc

Q_E, F = sc.e, sc.physical_constants["Faraday constant"][0]
RT = sc.R * 298.15
K = math.log(10) * RT / F

# Station 1
NI, MU_N, MU_P = 1.45e10, 1350.0, 480.0
ATOMS_SI = 8 / (0.5431e-7) ** 3


def carriers_n(N):
    n = N / 2 + math.sqrt(N * N / 4 + NI * NI)
    p = NI * NI / n
    return {"n": n, "p": p, "rho": 1 / (Q_E * (n * MU_N + p * MU_P))}


# Station 2
M_CU, RHO_CU = 63.546, 8.96


def plate(I, t, eff, area):
    m = eff * I * t / F / 2 * M_CU
    return {"Q": I * t, "m_mg": m * 1e3, "h_um": m / RHO_CU / area * 1e4}


# Station 3
EDLC = {"C": 4.4, "V": 2.7, "Pmax": 5.0}
EDLC["E_J"] = 0.5 * EDLC["C"] * EDLC["V"] ** 2
BAT = {"Ah": 0.100, "V": 3.7}
BAT["E_J"] = BAT["Ah"] * BAT["V"] * 3600
BAT["Pmax"] = 2 * BAT["Ah"] * BAT["V"]            # 2C


def choose(P, t):
    """Which devices can deliver power P (W) for t (s)."""
    need = P * t
    ok = {}
    for name, d in (("EDLC", EDLC), ("battery", BAT)):
        ok[name] = {"energy_ok": d["E_J"] >= need, "power_ok": d["Pmax"] >= P}
        ok[name]["ok"] = ok[name]["energy_ok"] and ok[name]["power_ok"]
    return {"P": P, "t": t, "E_J": need, "fits": ok}


def lab_results():
    c = carriers_n(1e16)
    intr = 1 / (Q_E * NI * (MU_N + MU_P))
    return {"s1": {"cu2_electrons": 29 - 2, "p": c["p"], "rho": c["rho"], "rho_i": intr, "ratio": intr / c["rho"], "frac": 1e16 / ATOMS_SI},
            "s2": {**plate(0.100, 600, 0.90, 10.0), "E_001": 0.34 + K / 2 * math.log10(0.010), "bath_sp": "Cu2+"},
            "s3": {"pulse": choose(3.0, 5.0), "long": choose(0.10, 3600.0), "edlc": EDLC, "bat": BAT,
                   "table_P": [0.1, 0.5, 1.0, 2.0, 3.0, 5.0], "table_t": [1, 5, 60, 600, 3600]}}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    L = lab_results()
    grid = {f"{P:g}|{t:g}": choose(P, t) for P in L["s3"]["table_P"] for t in L["s3"]["table_t"]}
    R["lecture"] = {"grid": grid, "K": K, "F": F, "atoms_si": ATOMS_SI, "ni": NI}
    R["lab"] = L
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("review-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote review-results.json"); sys.exit()
    s1, s2, s3 = R["lab"]["s1"], R["lab"]["s2"], R["lab"]["s3"]
    print("S1: Cu2+ e- %d; p %.2e; rho %.4f; rho_i %.3e; ratio %.2e; fraction %.1e" % (s1["cu2_electrons"], s1["p"], s1["rho"], s1["rho_i"], s1["ratio"], s1["frac"]))
    print("S2: Q %.1f C; m %.2f mg; h %.3f um; E(0.010 M) %.4f V; bath %s" % (s2["Q"], s2["m_mg"], s2["h_um"], s2["E_001"], s2["bath_sp"]))
    print("S3: EDLC %.1f J, %.1f W; battery %.0f J, %.2f W" % (s3["edlc"]["E_J"], s3["edlc"]["Pmax"], s3["bat"]["E_J"], s3["bat"]["Pmax"]))
    for k in ("pulse", "long"):
        c = s3[k]; print(k, "%.0f J" % c["E_J"], {n: v["ok"] for n, v in c["fits"].items()})
