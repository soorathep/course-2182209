"""Class 4 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Solutions, concentration and electrolytes: the CuSO4 bath used to plate copper wiring.
Every number on the Class 4 slides and in Lab 4 comes from this module.

Run `python solutions_lab.py` for a printed summary, or `python solutions_lab.py --json`
to write solutions-results.json.

Data: atomic masses as in Class 3; the dilution cases are the exercise data of the 2026
pack (synthetic, no solute lost). Ultrapure water at 25 C: 18.18 Mohm cm (theoretical,
from the self-ionization of water). NumPy only, so it also runs in the browser.
"""
import json
import sys

import numpy as np

M_AT = {"Cu": 63.546, "S": 32.06, "O": 15.9994, "H": 1.008, "Cl": 35.45, "Na": 22.990, "C": 12.011}


def r6(x):
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def molar_mass(formula):
    return sum(M_AT[el] * n for el, n in formula.items())


M_CUSO4 = molar_mass({"Cu": 1, "S": 1, "O": 4})
M_H2O = molar_mass({"H": 2, "O": 1})
M_HYDRATE = M_CUSO4 + 5 * M_H2O          # CuSO4.5H2O, the blue crystals that are weighed

CASES = [("A", 0.100, 20.0), ("B", 0.0500, 40.0), ("C", 0.0200, 100.0)]   # C in mol/L, V in mL


def amount(C, V_mL):
    """n = C V, with V converted to L."""
    return C * V_mL / 1000


def dilution_volume(C_stock, C_target, V_target_mL):
    """Volume of stock for C1 V1 = C2 V2."""
    return C_target * V_target_mL / C_stock


def hydrate_mass(C, V_mL):
    """Mass of CuSO4.5H2O to make V_mL of C mol/L CuSO4."""
    return amount(C, V_mL) * M_HYDRATE


def ions(C_salt, cation=("Cu2+", 2, 1), anion=("SO4 2-", -2, 1)):
    """Ion concentrations from a salt that dissociates completely, with a charge check."""
    (cn, cq, cnu), (an, aq, anu) = cation, anion
    c_cat, c_an = cnu * C_salt, anu * C_salt
    return {"cation": cn, "anion": an, "c_cat": c_cat, "c_an": c_an, "c_total": c_cat + c_an,
            "charge": cq * c_cat + aq * c_an}


def mgL_to_molL(mg_per_L, M):
    return mg_per_L * 1e-3 / M


def lab_results():
    return {
        "cases": [{"case": k, "C": C, "V_mL": V, "n": amount(C, V)} for k, C, V in CASES],
        "V_stock": dilution_volume(0.100, 0.0250, 80.0),
        "M_hydrate": M_HYDRATE,
        "m_250mL_0p1": hydrate_mass(0.100, 250.0),
        "m_500mL_0p2": hydrate_mass(0.200, 500.0),
        "ions_0p1": ions(0.100),
        "cl_50": mgL_to_molL(50.0, M_AT["Cl"]),
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "M_CuSO4": M_CUSO4, "M_H2O": M_H2O, "M_hydrate": M_HYDRATE,
        "cases": [{"case": k, "C": C, "V_mL": V, "n": amount(C, V)} for k, C, V in CASES],
        "V_stock": dilution_volume(0.100, 0.0250, 80.0),
        "m_1L_0p25": hydrate_mass(0.250, 1000.0),
        "ions": [ions(0.100), ions(0.100, ("Na+", 1, 1), ("Cl-", -1, 1)), ions(0.100, ("Na+", 1, 2), ("SO4 2-", -2, 1))],
        "cl_50": mgL_to_molL(50.0, M_AT["Cl"]),
        "upw_Mohm_cm": 18.18,
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("solutions-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote solutions-results.json"); sys.exit()
    L = R["lecture"]
    print("M(CuSO4) =", r6(L["M_CuSO4"]), " M(CuSO4.5H2O) =", r6(L["M_hydrate"]))
    for c in L["cases"]:
        print(c["case"], "n =", r6(c["n"]), "mol")
    print("stock for 80.0 mL of 0.0250 M:", r6(L["V_stock"]), "mL")
    print("hydrate for 1.00 L of 0.250 M:", r6(L["m_1L_0p25"]), "g")
    for q in L["ions"]:
        print(q)
    print("50 mg/L chloride:", r6(L["cl_50"]), "mol/L")
