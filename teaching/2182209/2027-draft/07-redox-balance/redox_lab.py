"""Class 7 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Redox reactions and electron balance. Every number on the Class 7 slides and in Lab 7
comes from this module.

Run `python redox_lab.py` for a printed summary, or `python redox_lab.py --json` to
write redox-results.json.

Half-reactions are written as reductions, ion + z e- -> metal. Molar masses (g/mol) from
the IUPAC 2021 standard atomic weights, as in Class 3. The order of how readily the metals
are oxidized follows their standard reduction potentials (Class 9), given here only as an
order. Model choices, stated: in the electron-supply model each Cu2+ takes two electrons
in one step, so an odd electron is left unused. The calculation needs only the standard
library; NumPy and SciPy are imported only to record their versions.
"""
import json
import math
import sys

HALF = {"Cu": ("Cu2+", 2), "Zn": ("Zn2+", 2), "Al": ("Al3+", 3), "Fe": ("Fe2+", 2), "Ag": ("Ag+", 1)}
MOLAR = {"Cu": 63.546, "Zn": 65.38, "Al": 26.982, "Fe": 55.845, "Ag": 107.87}
ORDER = ["Al", "Zn", "Fe", "H2", "Cu", "Ag"]    # most readily oxidized first
# oxidation numbers: (formula, charge, atom to find, count of it, [(partner, count, its oxidation number)])
ONS = [("Cu", 0, "Cu", 1, []), ("Cu2+", 2, "Cu", 1, []), ("CuO", 0, "Cu", 1, [("O", 1, -2)]),
       ("Cu2O", 0, "Cu", 2, [("O", 1, -2)]), ("SiO2", 0, "Si", 1, [("O", 2, -2)]),
       ("SiCl4", 0, "Si", 1, [("Cl", 4, -1)]), ("SO4 2-", -2, "S", 1, [("O", 4, -2)]),
       ("H2O2", 0, "O", 2, [("H", 2, 1)])]


def r6(x):
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def oxidation_number(charge, count, partners):
    """Sum of oxidation numbers equals the charge of the species."""
    return (charge - sum(n * on for _, n, on in partners)) / count


def combine(metal, ion_of):
    """Overall reaction: `metal` is oxidized, the ion of `ion_of` is reduced.

    Multiply each half-reaction so the electrons lost equal the electrons gained.
    """
    z_ox, z_red = HALF[metal][1], HALF[ion_of][1]
    e = z_ox * z_red // math.gcd(z_ox, z_red)
    a, b = e // z_ox, e // z_red                     # a metal + b ion -> a metal ion + b metal
    left = b * z_red                                 # charge on the left (ions only)
    right = a * z_ox
    spont = ORDER.index(metal) < ORDER.index(ion_of)
    return {"metal": metal, "ion": HALF[ion_of][0], "ox_ion": HALF[metal][0], "product": ion_of,
            "a": a, "b": b, "e": e, "charge_left": left, "charge_right": right, "goes": spont}


def supply(n_ions, n_e, z=2):
    """Whole ions and electrons: each ion takes z electrons at once."""
    made = min(n_ions, n_e // z)
    return {"e": n_e, "made": made, "ions_left": n_ions - made, "e_left": n_e - z * made}


def displacement(m_zn, c_cu, v_ml):
    """Zn(s) + Cu2+(aq) -> Zn2+(aq) + Cu(s), 1:1."""
    n_zn, n_cu = m_zn / MOLAR["Zn"], c_cu * v_ml / 1000
    n = min(n_zn, n_cu)
    return {"m_zn": m_zn, "n_zn": n_zn, "n_cu2": n_cu, "limiting": "Cu2+" if n_cu < n_zn else "Zn",
            "n_rxn": n, "m_cu": n * MOLAR["Cu"], "m_zn_used": n * MOLAR["Zn"], "m_zn_left": m_zn - n * MOLAR["Zn"],
            "cu2_left": n_cu - n, "e_mol": 2 * n}


def lab_results():
    return {"zncu": combine("Zn", "Cu"), "alcu": combine("Al", "Cu"),
            "sup4": supply(3, 4), "sup_all": 3 * 2, "supply": [supply(3, k) for k in range(9)],
            "disp": displacement(1.00, 0.100, 100.0), "on_si": oxidation_number(0, 1, [("O", 2, -2)])}


def classroom_results():
    R = {"meta": {"numpy": __import__("numpy").__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "ons": [{"f": f, "atom": a, "on": oxidation_number(c, n, p)} for f, c, a, n, p in ONS],
        "pairs": [combine(m, i) for m in ("Zn", "Al", "Fe", "Cu") for i in ("Cu", "Ag", "Zn") if m != i],
        "supply": [supply(3, k) for k in range(9)],
        "disp": [{k: r6(v) if isinstance(v, float) else v for k, v in displacement(m / 4, 0.100, 100.0).items()} for m in range(1, 9)],
        "order": ORDER, "molar": MOLAR,
        "si_ox_e": 4,                     # Si 0 -> +4: 4 electrons per Si in Si + O2 -> SiO2
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("redox-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote redox-results.json"); sys.exit()
    L = R["lecture"]
    for o in L["ons"]:
        print("%-7s %s: %s" % (o["f"], o["atom"], "%+d" % o["on"] if o["on"] else "0"))
    for p in L["pairs"]:
        print("%d %s + %d %s -> %d %s + %d %s  e=%d  charge %d = %d  goes: %s" % (p["a"], p["metal"], p["b"], p["ion"], p["a"], p["ox_ion"], p["b"], p["product"], p["e"], p["charge_left"], p["charge_right"], p["goes"]))
    for s in L["supply"]:
        print(s)
    d = R["lab"]["disp"]
    print("Zn %.4f mol, Cu2+ %.4f mol, limiting %s, Cu %.4f g, Zn left %.4f g" % (d["n_zn"], d["n_cu2"], d["limiting"], d["m_cu"], d["m_zn_left"]))
