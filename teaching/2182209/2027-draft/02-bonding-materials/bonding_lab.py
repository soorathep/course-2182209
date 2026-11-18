"""Class 2 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Bonding, structure and properties: why a chip needs a metal, a semiconductor and an
insulator. Every number on the Class 2 slides and in Lab 2 comes from this module.

Run `python bonding_lab.py` for a printed summary, or `python bonding_lab.py --json`
to write bonding-results.json, which the build embeds in the slides and the lab.

Data (representative values near room temperature, for teaching):
- Pauling electronegativities and the bond-type guide: OpenStax Chemistry 2e, Section 7.2.
- Electrical resistivities: metals from the CRC Handbook of Chemistry and Physics;
  intrinsic Si at 300 K from Sze and Ng, Physics of Semiconductor Devices; graphite and
  amorphous SiO2 are order-of-magnitude values, because they vary with direction,
  purity and how the material was made.
- Lattice constants and densities: CRC Handbook.
NumPy only, so it also runs in the browser.
"""
import json
import sys

import numpy as np

# Pauling electronegativities as printed in OpenStax Chemistry 2e, Figure 7.6 (one decimal),
# so that students can check every difference against the reading
EN = {"H": 2.1, "C": 2.5, "N": 3.0, "O": 3.5, "F": 4.0, "Li": 1.0, "Na": 0.9, "Al": 1.5,
      "Si": 1.8, "Cl": 3.0, "Cu": 1.9}
METALS = {"Li", "Na", "Al", "Cu"}

# resistivity in ohm m; "class" is the engineering role
RHO = [
    {"material": "Cu", "rho": 1.68e-8, "bonding": "metallic", "class": "conductor", "note": "wires and vias in chips"},
    {"material": "Al", "rho": 2.65e-8, "bonding": "metallic", "class": "conductor", "note": "chip wiring before Cu"},
    {"material": "W", "rho": 5.6e-8, "bonding": "metallic", "class": "conductor", "note": "contacts to the transistors"},
    {"material": "graphite", "rho": 1e-5, "bonding": "covalent layers", "class": "conductor", "note": "order of magnitude; depends on direction"},
    {"material": "Si (pure)", "rho": 2.3e3, "bonding": "covalent network", "class": "semiconductor", "note": "intrinsic, 300 K; doping lowers it (Class 6)"},
    {"material": "SiO2 (amorphous)", "rho": 1e16, "bonding": "covalent network", "class": "insulator", "note": "order of magnitude"},
]

CELLS = {  # atoms per cubic unit cell: corners, faces, edges, inside
    "Cu": {"lattice": "face-centered cubic", "a_nm": 0.3615, "corner": 8, "face": 6, "inside": 0},
    "W": {"lattice": "body-centered cubic", "a_nm": 0.3165, "corner": 8, "face": 0, "inside": 1},
    "Si": {"lattice": "diamond cubic", "a_nm": 0.5431, "corner": 8, "face": 6, "inside": 4},
}

DENSITY = {"quartz (crystalline SiO2)": 2.65, "fused silica (amorphous SiO2)": 2.20}


def r6(x):
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def bond_type(a, b):
    """Classify the bond between atoms a and b.

    Two metals: metallic. Otherwise by the electronegativity difference (OpenStax rule of
    thumb): below 0.4 nonpolar covalent, 0.4 to 1.8 polar covalent, above 1.8 ionic.
    """
    d = round(abs(EN[a] - EN[b]), 2)
    if a in METALS and b in METALS:
        kind = "metallic"
    elif d < 0.4:
        kind = "nonpolar covalent"
    elif d <= 1.8:
        kind = "polar covalent"
    else:
        kind = "ionic"
    return {"a": a, "b": b, "dEN": d, "kind": kind}


PAIRS = [("Cu", "Cu"), ("Si", "Si"), ("C", "C"), ("Si", "O"), ("Na", "Cl"), ("Li", "F")]


def orders(r_hi, r_lo):
    """Orders of magnitude between two resistivities: log10 of their ratio."""
    return float(np.log10(r_hi / r_lo))


def line_resistance(rho, L, w, t):
    """R = rho L / A for a rectangular wire (all in SI units)."""
    return rho * L / (w * t)


def layer_resistance(rho, t, area):
    """Resistance across an insulating layer of thickness t and area A."""
    return rho * t / area


def atoms_per_cell(name):
    c = CELLS[name]
    n = c["corner"] / 8 + c["face"] / 2 + c["inside"]
    return dict(c, name=name, atoms=n)


LINE = {"L": 1e-3, "w": 100e-9, "t": 200e-9}          # a 1 mm wire, 100 nm wide, 200 nm thick
LAYER = {"t": 100e-9, "area": 1e-12, "V": 1.0}         # 100 nm of SiO2 under a 1 um x 1 um pad, 1 V


def rho_of(name):
    return next(r["rho"] for r in RHO if r["material"] == name)


def line_table():
    out = []
    for name in ("Cu", "Al", "W"):
        R = line_resistance(rho_of(name), **LINE)
        out.append({"material": name, "rho": rho_of(name), "R": R, "vs_Cu": R / line_resistance(rho_of("Cu"), **LINE)})
    return out


def leakage():
    R = layer_resistance(rho_of("SiO2 (amorphous)"), LAYER["t"], LAYER["area"])
    return {"R": R, "I": LAYER["V"] / R, **LAYER}


def silica_density():
    q, f = DENSITY["quartz (crystalline SiO2)"], DENSITY["fused silica (amorphous SiO2)"]
    return {"quartz": q, "fused": f, "percent_lower": 100 * (q - f) / q}


def lab_results():
    lt = {r["material"]: r for r in line_table()}
    return {
        "pairs": {f"{a}-{b}": bond_type(a, b) for a, b in [("Si", "O"), ("Na", "Cl"), ("Cu", "Cu")]},
        "rho": RHO,
        "orders_SiO2_Cu": orders(rho_of("SiO2 (amorphous)"), rho_of("Cu")),
        "orders_Si_Cu": orders(rho_of("Si (pure)"), rho_of("Cu")),
        "line": LINE, "R_Cu": lt["Cu"]["R"], "R_Al": lt["Al"]["R"], "R_W": lt["W"]["R"],
        "R_Cu_half_width": line_resistance(rho_of("Cu"), LINE["L"], LINE["w"] / 2, LINE["t"]),
        "cells": {k: atoms_per_cell(k)["atoms"] for k in CELLS},
        "silica": silica_density(),
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "EN": EN, "metals": sorted(METALS),
        "pairs": [bond_type(a, b) for a, b in PAIRS],
        "rho": RHO,
        "orders_SiO2_Cu": orders(rho_of("SiO2 (amorphous)"), rho_of("Cu")),
        "line": LINE, "lines": line_table(),
        "leak": leakage(),
        "cells": [atoms_per_cell(k) for k in ("Cu", "W", "Si")],
        "silica": silica_density(),
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("bonding-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote bonding-results.json"); sys.exit()
    L = R["lecture"]
    for p in L["pairs"]:
        print(f"{p['a']}-{p['b']}: dEN {p['dEN']:.2f}, {p['kind']}")
    print("orders of magnitude, SiO2 vs Cu:", r6(L["orders_SiO2_Cu"]))
    for r in L["lines"]:
        print(f"1 mm line in {r['material']}: {r6(r['R'])} ohm ({r6(r['vs_Cu'])} x Cu)")
    print("SiO2 layer:", L["leak"])
    for c in L["cells"]:
        print(c["name"], c["lattice"], "atoms per cell", c["atoms"])
    print("silica density:", L["silica"])
