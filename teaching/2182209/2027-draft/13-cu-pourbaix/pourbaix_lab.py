"""Class 13 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

A limited-species Pourbaix (potential-pH) diagram for Cu in water at 25 degC. Every number
and every region on the Class 13 slides and in Lab 13 comes from this module.

Run `python pourbaix_lab.py` for a printed summary, or `python pourbaix_lab.py --json` to
write pourbaix-results.json.

Species, stated: Cu(s), Cu2+(aq), Cu2O(s), CuO(s) only. Cu(I) ions and the hydroxo and
cuprate ions of strongly alkaline water are left out, so the diagram is a teaching
simplification, wrong above about pH 12. Dissolved Cu is set at 1e-6 M, the usual corrosion
convention. Standard Gibbs energies of formation (kJ/mol), OpenStax Chemistry 2e Appendix G:
Cu2+(aq) 65.5, Cu2O(s) -146.0, CuO(s) -129.7, H2O(l) -237.1. Potentials against the SHE.

Method: for each species, the Gibbs energy per Cu atom of forming it from Cu(s), water and
H+, with electrons at potential E, is linear in pH and E. The stable species at a point is
the one with the lowest value. Each region is the box clipped by those linear inequalities.
"""
import json
import math
import sys

import numpy as np
from scipy import constants as sc

F = sc.physical_constants["Faraday constant"][0]
RT = sc.R * 298.15
LN10 = math.log(10)
GF = {"Cu2+": 65.5e3, "Cu2O": -146.0e3, "CuO": -129.7e3, "H2O": -237.1e3}     # J/mol
C_ION = 1e-6
BOX = (0.0, 14.0, -0.6, 1.2)                                                  # pH, E limits
SPECIES = ["Cu", "Cu2+", "Cu2O", "CuO"]


def coeffs(sp, c=C_ION):
    """G per Cu atom (J) = a + b pH + k E for forming sp from Cu(s)."""
    if sp == "Cu":
        return (0.0, 0.0, 0.0)
    if sp == "Cu2+":                               # Cu -> Cu2+ + 2e-
        return (GF["Cu2+"] + RT * math.log(c), 0.0, -2 * F)
    if sp == "Cu2O":                               # 2Cu + H2O -> Cu2O + 2H+ + 2e-, per Cu
        return ((GF["Cu2O"] - GF["H2O"]) / 2, -LN10 * RT, -F)
    if sp == "CuO":                                # Cu + H2O -> CuO + 2H+ + 2e-
        return (GF["CuO"] - GF["H2O"], -2 * LN10 * RT, -2 * F)


def g(sp, pH, E):
    a, b, k = coeffs(sp)
    return a + b * pH + k * E


def stable(pH, E):
    return min(SPECIES, key=lambda s: g(s, pH, E))


def clip(poly, a, b, k):
    """Keep the part of poly where a + b pH + k E <= 0 (Sutherland-Hodgman)."""
    out = []
    f = lambda p: a + b * p[0] + k * p[1]
    for i in range(len(poly)):
        P, Q = poly[i], poly[(i + 1) % len(poly)]
        fP, fQ = f(P), f(Q)
        if fP <= 0:
            out.append(P)
        if fP * fQ < 0:
            t = fP / (fP - fQ)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def regions():
    x0, x1, y0, y1 = BOX
    res = {}
    for s in SPECIES:
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for o in SPECIES:
            if o != s:
                a1, b1, k1 = coeffs(s); a2, b2, k2 = coeffs(o)
                poly = clip(poly, a1 - a2, b1 - b2, k1 - k2)
        res[s] = [[round(p[0], 4), round(p[1], 4)] for p in poly]
    return res


def lines():
    """Boundary equations, E = e0 + m pH (V), or a vertical pH line."""
    lc = math.log10(C_ION)
    return {
        "Cu2+/Cu": {"e0": GF["Cu2+"] / (2 * F) + 0.5 * LN10 * RT / F * lc, "m": 0.0},
        "Cu2O/Cu": {"e0": -(GF["H2O"] - GF["Cu2O"]) / (2 * F), "m": -LN10 * RT / F},
        "CuO/Cu2O": {"e0": -((GF["Cu2O"] + GF["H2O"]) - 2 * GF["CuO"]) / (2 * F), "m": -LN10 * RT / F},
        "Cu2+/Cu2O": {"e0": -(GF["Cu2O"] - (2 * GF["Cu2+"] + GF["H2O"])) / (2 * F) + LN10 * RT / F * lc, "m": LN10 * RT / F},
        "CuO/Cu2+": {"pH": ((GF["H2O"] + GF["Cu2+"] - GF["CuO"]) / (-LN10 * RT) - lc) / 2},
    }


POINTS = {"A": (4.0, -0.10), "B": (3.0, 0.50), "C": (9.0, 0.05), "D": (9.0, 0.40)}


def lab_results():
    L = lines()
    return {"points": {k: {"pH": p[0], "E": p[1], "sp": stable(*p)} for k, p in POINTS.items()},
            "pH9": {"Cu_to_Cu2O": L["Cu2O/Cu"]["e0"] + 9 * L["Cu2O/Cu"]["m"],
                    "Cu2O_to_CuO": L["CuO/Cu2O"]["e0"] + 9 * L["CuO/Cu2O"]["m"]},
            "scan9": [{"E": round(float(e), 2) + 0.0, "sp": stable(9.0, float(e))} for e in np.arange(-0.30, 0.601, 0.05)],
            "pH_CuO_Cu2": L["CuO/Cu2+"]["pH"], "E_Cu2_Cu": L["Cu2+/Cu"]["e0"]}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {"box": BOX, "c": C_ION, "regions": regions(), "lines": lines(), "slope": LN10 * RT / F,
                    "water": {"H2": {"e0": 0.0, "m": -LN10 * RT / F}, "O2": {"e0": 1.229, "m": -LN10 * RT / F}},
                    "fab": [{"k": "Acid Cu plating bath", "pH": 1.0, "E": 0.50}, {"k": "Neutral rinse water with air", "pH": 7.0, "E": 0.80},
                            {"k": "Alkaline slurry, mild oxidizer", "pH": 9.0, "E": 0.30}, {"k": "Under a cathodic potential", "pH": 7.0, "E": -0.40}]}
    for f_ in R["lecture"]["fab"]:
        f_["sp"] = stable(f_["pH"], f_["E"])
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("pourbaix-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote pourbaix-results.json"); sys.exit()
    for k, v in R["lecture"]["lines"].items():
        print("%-10s %s" % (k, {a: round(b, 4) for a, b in v.items()}))
    for k, p in R["lab"]["points"].items():
        print(k, p)
    print("pH 9 boundaries:", {k: round(v, 4) for k, v in R["lab"]["pH9"].items()})
    print("scan at pH 9:", [(s["E"], s["sp"]) for s in R["lab"]["scan9"]])
    for f_ in R["lecture"]["fab"]:
        print(f_)
    for s, poly in R["lecture"]["regions"].items():
        print(s, len(poly), "vertices")
