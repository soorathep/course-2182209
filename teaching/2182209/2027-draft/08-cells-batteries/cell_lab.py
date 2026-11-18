"""Class 8 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Electrochemical cells and batteries: where electrons and ions go. Every number and every
path on the Class 8 slides and in Lab 8 comes from this module.

Run `python cell_lab.py` for a printed summary, or `python cell_lab.py --json` to write
cell-results.json.

Three cells, each with a negative and a positive electrode:
  Daniell cell   Zn | Zn2+ || Cu2+ | Cu
  Li-ion         graphite (LiC6) | Li+ electrolyte | LiCoO2
  zinc-air       Zn | KOH(aq) | O2 (air)
Rules used, stated: oxidation happens at the anode and reduction at the cathode in every
cell; electrons in the outer circuit flow from anode to cathode; in the electrolyte,
cations move toward the cathode and anions toward the anode. In discharge the cell drives
the current; in charge a power supply drives it the other way. Li-ion reactions are written
for full delithiation of CoO2 for simplicity (real cells cycle about half of the Li).
Molar masses (g/mol): IUPAC 2021 standard atomic weights. Standard library only; NumPy and
SciPy are imported only to record their versions.
"""
import json
import math
import sys

M = {"Zn": 65.38, "O": 15.999, "Cu": 63.546}
M["O2"], M["ZnO"] = 2 * M["O"], M["Zn"] + M["O"]

CELLS = {
    "daniell": {"name": "Daniell cell", "neg": "Zn", "pos": "Cu", "electrolyte": "salt bridge (KNO3)",
                "neg_rx": ("Zn → Zn2+ + 2e−", 2), "pos_rx": ("Cu2+ + 2e− → Cu", 2),
                "cation": "K+", "anion": "NO3−", "rechargeable": False},
    "liion": {"name": "Li-ion", "neg": "graphite", "pos": "LiCoO2", "electrolyte": "Li+ in an organic solvent",
              "neg_rx": ("LiC6 → C6 + Li+ + e−", 1), "pos_rx": ("CoO2 + Li+ + e− → LiCoO2", 1),
              "cation": "Li+", "anion": "PF6−", "rechargeable": True},
    "znair": {"name": "zinc-air", "neg": "Zn", "pos": "air electrode", "electrolyte": "KOH(aq)",
              "neg_rx": ("Zn + 2OH− → ZnO + H2O + 2e−", 2), "pos_rx": ("O2 + 2H2O + 4e− → 4OH−", 4),
              "cation": "K+", "anion": "OH−", "rechargeable": False},
}


def path(cell, mode="discharge"):
    """Which electrode is the anode, and where electrons and ions go."""
    c = CELLS[cell]
    if mode == "discharge":
        anode, cathode, sign = c["neg"], c["pos"], "negative"
    else:                                    # charge: a power supply reverses both reactions
        anode, cathode, sign = c["pos"], c["neg"], "positive"
    return {"cell": cell, "mode": mode, "anode": anode, "cathode": cathode, "anode_sign": sign,
            "e_from": anode, "e_to": cathode, "cation_to": cathode, "anion_to": anode,
            "supply": mode == "charge"}


def combine_znair():
    """Electrons lost by Zn equal electrons gained by O2."""
    z_ox, z_red = CELLS["znair"]["neg_rx"][1], CELLS["znair"]["pos_rx"][1]
    e = z_ox * z_red // math.gcd(z_ox, z_red)
    return {"zn": e // z_ox, "o2": e // z_red, "e": e}


def znair_mass(m_zn):
    """2 Zn + O2 -> 2 ZnO, from a mass of Zn."""
    n = m_zn / M["Zn"]
    return {"m_zn": m_zn, "n_zn": n, "m_o2": n / 2 * M["O2"], "m_zno": n * M["ZnO"], "e_mol": 2 * n}


def bridge(e_mol):
    """Daniell cell: charge each half-cell would build up without ions moving."""
    return {"e_mol": e_mol, "zn2_added": e_mol / 2, "cu2_removed": e_mol / 2,
            "anion_to_zn": e_mol, "cation_to_cu": e_mol}


def co_oxidation():
    """Oxidation number of Co: Li +1, O -2, sum 0."""
    return {"CoO2": 0 - 2 * -2, "LiCoO2": 0 - 1 - 2 * -2}


def lab_results():
    return {"daniell": path("daniell"), "li_dis": path("liion", "discharge"), "li_chg": path("liion", "charge"),
            "co": co_oxidation(), "znair": combine_znair(), "zn1": znair_mass(1.00)}


def classroom_results():
    R = {"meta": {"numpy": __import__("numpy").__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "cells": CELLS,
        "paths": {f"{c}_{m}": path(c, m) for c in CELLS for m in ("discharge", "charge") if m == "discharge" or CELLS[c]["rechargeable"]},
        "bridge": bridge(0.0200), "co": co_oxidation(), "znair": combine_znair(),
        "zn_table": [znair_mass(m / 2) for m in range(1, 11)], "molar": M,
        "e_daniell_preview": 1.10,          # V, computed in Class 9
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("cell-results.json", "w") as fh:
            json.dump(R, fh, indent=1, ensure_ascii=False)
        print("wrote cell-results.json"); sys.exit()
    for k, p in R["lecture"]["paths"].items():
        print("%-16s anode %-9s (%s)  e- %s -> %s  cations -> %s" % (k, p["anode"], p["anode_sign"], p["e_from"], p["e_to"], p["cation_to"]))
    print("bridge:", R["lecture"]["bridge"])
    print("Co:", R["lecture"]["co"], " zinc-air:", R["lecture"]["znair"])
    z = R["lab"]["zn1"]; print("1.00 g Zn: O2 %.4f g, ZnO %.4f g, e- %.5f mol" % (z["m_o2"], z["m_zno"], z["e_mol"]))
