"""Class 1 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Atoms, ions and the materials of a chip. Every number on the Class 1 slides and
in Lab 1 comes from this module.

Run `python atoms_lab.py` for a printed summary, or `python atoms_lab.py --json`
to write atoms-results.json, which the build embeds in the slides and the lab.

Data: element symbols and atomic numbers; isotope masses (u) and
representative isotopic abundances from NIST, "Atomic Weights and Isotopic
Compositions with Relative Atomic Masses" (https://www.nist.gov/pml/atomic-weights-and-isotopic-compositions-relative-atomic-masses).
Everything else is counting. NumPy only, so it also runs in the browser.
"""
import json
import sys

import numpy as np

# ---------------------------------------------------------------- elements
# symbol and name for Z = 1 to 30 (enough for every species in Classes 1 to 14)
ELEMENTS = [
    ("H", "hydrogen"), ("He", "helium"), ("Li", "lithium"), ("Be", "beryllium"), ("B", "boron"),
    ("C", "carbon"), ("N", "nitrogen"), ("O", "oxygen"), ("F", "fluorine"), ("Ne", "neon"),
    ("Na", "sodium"), ("Mg", "magnesium"), ("Al", "aluminum"), ("Si", "silicon"), ("P", "phosphorus"),
    ("S", "sulfur"), ("Cl", "chlorine"), ("Ar", "argon"), ("K", "potassium"), ("Ca", "calcium"),
    ("Sc", "scandium"), ("Ti", "titanium"), ("V", "vanadium"), ("Cr", "chromium"), ("Mn", "manganese"),
    ("Fe", "iron"), ("Co", "cobalt"), ("Ni", "nickel"), ("Cu", "copper"), ("Zn", "zinc"),
]
Z_OF = {sym: z + 1 for z, (sym, _) in enumerate(ELEMENTS)}

# isotopes: mass number A -> (isotope mass in u, abundance as a fraction of atoms)
ISOTOPES = {
    "Li": {6: (6.0151228874, 0.0759), 7: (7.0160034366, 0.9241)},
    "O": {16: (15.99491461957, 0.99757), 17: (16.99913175650, 0.00038), 18: (17.99915961286, 0.00205)},
    "Si": {28: (27.97692653465, 0.92223), 29: (28.97649466490, 0.04685), 30: (29.973770136, 0.03092)},
    "Cu": {63: (62.92959772, 0.6915), 65: (64.92778970, 0.3085)},
}


def r6(x):
    """Round to 6 decimals for printing (lists too), as the slides show it."""
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


# ---------------------------------------------------------------- counting
def particles(symbol, charge=0, A=None):
    """Protons, electrons and (if A is given) neutrons of an atom or a monatomic ion.

    Z identifies the element; net charge (in units of e) = protons - electrons.
    """
    Z = Z_OF[symbol]
    out = {"symbol": symbol, "name": ELEMENTS[Z - 1][1], "Z": Z, "charge": charge,
           "protons": Z, "electrons": Z - charge}
    if A is not None:
        out["A"] = A
        out["neutrons"] = A - Z
    return out


def build_atom(p, n, e):
    """What the atom builder on slide 10 shows for p protons, n neutrons and e electrons."""
    if p < 1 or p > len(ELEMENTS):
        return {"p": p, "n": n, "e": e, "symbol": None}
    sym, name = ELEMENTS[p - 1]
    q = p - e
    return {"p": p, "n": n, "e": e, "symbol": sym, "name": name, "A": p + n, "charge": q,
            "kind": "neutral atom" if q == 0 else ("cation" if q > 0 else "anion")}


def label(symbol, charge):
    """Text label such as Cu2+, O2- or Na+."""
    if charge == 0:
        return symbol
    mag = "" if abs(charge) == 1 else str(abs(charge))
    return f"{symbol}{mag}{'+' if charge > 0 else '-'}"


ION_TABLE = [("Li", 0), ("Li", 1), ("Na", 1), ("Cu", 0), ("Cu", 1), ("Cu", 2), ("Si", 0), ("O", -2), ("F", -1)]


def ion_table():
    return [dict(particles(s, q), label=label(s, q)) for s, q in ION_TABLE]


# ---------------------------------------------------------------- isotopes
def isotopes(symbol):
    Z = Z_OF[symbol]
    return [{"A": A, "label": f"{symbol}-{A}", "protons": Z, "neutrons": A - Z, "mass_u": m, "abundance": f}
            for A, (m, f) in sorted(ISOTOPES[symbol].items())]


def average_mass(symbol, abundances=None):
    """Abundance-weighted mean isotope mass (u), the atomic weight used in later classes.

    `abundances` (optional) replaces the natural fractions, in the order of mass number;
    they are normalized so that they sum to 1.
    """
    iso = sorted(ISOTOPES[symbol].items())
    m = np.array([v[0] for _, v in iso])
    f = np.array([v[1] for _, v in iso]) if abundances is None else np.array(abundances, dtype=float)
    f = f / f.sum()
    return float(m @ f)


def cu_sweep():
    """Average atomic mass of Cu as the Cu-65 fraction goes from 0 to 1 in steps of 0.01."""
    return [{"f65": round(k / 100, 2), "M": average_mass("Cu", [1 - k / 100, k / 100])} for k in range(101)]


# ---------------------------------------------------------------- compounds
# formula units: list of (symbol, count); ionic compounds also list the known anion and its charge
COMPOUNDS = {
    "SiO2": {"atoms": [("Si", 1), ("O", 2)], "bonding": "covalent network", "role": "insulator between devices and wires"},
    "CuO": {"atoms": [("Cu", 1), ("O", 1)], "anion": ("O", -2, 1), "cation": ("Cu", 1)},
    "Cu2O": {"atoms": [("Cu", 2), ("O", 1)], "anion": ("O", -2, 1), "cation": ("Cu", 2)},
    "CuSO4": {"atoms": [("Cu", 1), ("S", 1), ("O", 4)], "anion": ("SO4", -2, 1), "cation": ("Cu", 1)},
    "LiPF6": {"atoms": [("Li", 1), ("P", 1), ("F", 6)], "anion": ("PF6", -1, 1), "cation": ("Li", 1)},
    "NaCl": {"atoms": [("Na", 1), ("Cl", 1)], "anion": ("Cl", -1, 1), "cation": ("Na", 1)},
}


def formula_count(name):
    """Atoms, protons and electrons in one neutral formula unit."""
    c = COMPOUNDS[name]
    atoms = sum(k for _, k in c["atoms"])
    protons = sum(Z_OF[s] * k for s, k in c["atoms"])
    return {"formula": name, "atoms": atoms, "elements": len(c["atoms"]), "protons": protons, "electrons": protons}


def cation_charge(name):
    """Charge of each metal ion from charge balance: n_cat * q_cat + n_an * q_an = 0."""
    c = COMPOUNDS[name]
    an, q_an, n_an = c["anion"]
    sym, n_cat = c["cation"]
    q = -n_an * q_an / n_cat
    assert q == int(q)
    return {"formula": name, "anion": an, "anion_charge": q_an, "metal": sym, "n_metal": n_cat,
            "metal_charge": int(q), "metal_ion": label(sym, int(q)), "metal_electrons": Z_OF[sym] - int(q)}


# ---------------------------------------------------------------- the chip
CHIP = [
    {"layer": "A", "material": "Si", "kind": "element", "role": "semiconductor: the transistors are built in it", "class": "semiconductor"},
    {"layer": "B", "material": "SiO2", "kind": "compound", "role": "insulator: keeps wires and devices apart", "class": "insulator"},
    {"layer": "C", "material": "Cu", "kind": "element", "role": "conductor: the wires (interconnects) that carry current", "class": "conductor"},
]


# ---------------------------------------------------------------- results
def lab_results():
    cu, cu2 = particles("Cu", 0), particles("Cu", 2)
    return {
        "counts": {k: particles(s, q) for k, (s, q) in {"Cu2+": ("Cu", 2), "Na+": ("Na", 1), "Li+": ("Li", 1),
                                                         "O2-": ("O", -2), "Si": ("Si", 0)}.items()},
        "cu_diff": cu["electrons"] - cu2["electrons"],
        "neutrons": {"Cu-65": particles("Cu", 0, 65)["neutrons"], "Si-28": particles("Si", 0, 28)["neutrons"]},
        "cu_iso": isotopes("Cu"),
        "M_Cu": average_mass("Cu"),
        "M_Cu_f65_035": average_mass("Cu", [0.65, 0.35]),
        "sweep": cu_sweep(),
        "Cu2O": cation_charge("Cu2O"), "CuO": cation_charge("CuO"),
        "SiO2": formula_count("SiO2"),
        "chip": CHIP,
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "elements": [{"Z": z + 1, "symbol": s, "name": n} for z, (s, n) in enumerate(ELEMENTS)],
        "ions": ion_table(),
        "li_demo": [build_atom(3, 4, 3), build_atom(3, 4, 2)],
        "isotopes": {s: isotopes(s) for s in ("Li", "O", "Si", "Cu")},
        "M": {s: average_mass(s) for s in ("Li", "O", "Si", "Cu")},
        "compounds": [formula_count(n) for n in ("SiO2", "CuSO4")],
        "charges": [cation_charge(n) for n in ("CuO", "Cu2O", "CuSO4", "LiPF6", "NaCl")],
        "chip": CHIP,
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("atoms-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote atoms-results.json"); sys.exit()
    L = R["lecture"]
    for q in L["ions"]:
        print(f"{q['label']:5s} protons {q['protons']:2d} electrons {q['electrons']:2d}")
    for s, m in L["M"].items():
        print(f"average atomic mass {s}: {r6(m)} u")
    for c in L["charges"]:
        print(f"{c['formula']}: {c['metal_ion']} ({c['metal_electrons']} electrons)")
    print("SiO2:", L["compounds"][0])
    print("Cu with 35% Cu-65:", r6(R["lab"]["M_Cu_f65_035"]), "u")
