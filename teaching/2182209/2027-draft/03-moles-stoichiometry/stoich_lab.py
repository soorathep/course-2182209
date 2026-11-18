"""Class 3 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Moles, units and stoichiometry: from a mass of Si to atoms, and from a balanced
equation to the SiO2 grown on a wafer. Every number on the Class 3 slides and in
Lab 3 comes from this module.

Run `python stoich_lab.py` for a printed summary, or `python stoich_lab.py --json`
to write stoich-results.json.

Data: Avogadro constant (exact, SI 2019); atomic masses from Class 1 (NIST isotopes)
and the rounded values supplied in the exercises; Si lattice constant 0.5431 nm and
densities of crystalline Si (2.329 g/cm3) and thermal SiO2 (2.20 g/cm3) from the CRC
Handbook. NumPy only, so it also runs in the browser.
"""
import json
import sys

import numpy as np

NA = 6.02214076e23                       # 1/mol, exact
M_PRECISE = {"Si": 28.0855, "O": 15.9994, "Cu": 63.546, "N": 14.007, "H": 1.008, "S": 32.06, "Cl": 35.45, "F": 18.998, "C": 12.011}
M_GIVEN = {"Si": 28.1, "O": 16.0}         # the rounded values supplied in the exercises
RHO_SI, RHO_OX = 2.329, 2.20              # g/cm3: crystalline Si, thermal (amorphous) SiO2
A_SI_NM = 0.5431                          # Si lattice constant, nm; 8 atoms per diamond-cubic cell (Class 2)


def r6(x):
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def molar_mass(formula, table=None):
    """Molar mass in g/mol of a formula given as {"Si": 1, "O": 2}."""
    t = table or M_PRECISE
    return sum(t[el] * n for el, n in formula.items())


SIO2 = {"Si": 1, "O": 2}


def mass_to_atoms(m_g, M):
    n = m_g / M
    return {"m_g": m_g, "M": M, "n_mol": n, "N": n * NA}


def oxidation(m_si_g, table=M_GIVEN):
    """Si + O2 -> SiO2, complete conversion of m_si_g of Si with excess O2 (mole ratio 1:1:1)."""
    n = m_si_g / table["Si"]
    M_ox = molar_mass(SIO2, table)
    return {"m_Si": m_si_g, "n_Si": n, "M_SiO2": M_ox, "m_SiO2": n * M_ox, "m_O2": n * 2 * table["O"],
            "balance": m_si_g + n * 2 * table["O"] - n * M_ox}


def si_density_from_cell():
    """Density of Si from its unit cell: 8 atoms in a cube of edge a."""
    a_cm = A_SI_NM * 1e-7
    n_per_cm3 = 8 / a_cm ** 3
    return {"a_cm": a_cm, "atoms_per_cm3": n_per_cm3, "rho": n_per_cm3 * M_PRECISE["Si"] / NA}


def si_consumed_ratio():
    """Thickness of Si consumed per thickness of SiO2 grown: (rho_ox/M_ox) / (rho_Si/M_Si)."""
    m_ox = molar_mass(SIO2)
    return (RHO_OX / m_ox) / (RHO_SI / M_PRECISE["Si"])


def oxide_layer(t_ox_nm, area_cm2=1.0):
    """Grow t_ox_nm of SiO2 on area_cm2 of a Si wafer."""
    k = si_consumed_ratio()
    V_ox = t_ox_nm * 1e-7 * area_cm2
    m_ox = V_ox * RHO_OX
    n = m_ox / molar_mass(SIO2)
    m_si = n * M_PRECISE["Si"]
    return {"t_ox_nm": t_ox_nm, "t_si_nm": k * t_ox_nm, "m_SiO2_g": m_ox, "m_Si_g": m_si, "m_O_g": m_ox - m_si,
            "gain_g": m_ox - m_si, "n_mol": n}


def lab_results():
    ox = oxidation(0.562)
    return {
        "M_SiO2": molar_mass(SIO2, M_GIVEN), "ox562": ox,
        "atoms_0p02": ox["n_Si"] * NA,
        "si_density": si_density_from_cell(),
        "ratio": si_consumed_ratio(),
        "layer100": oxide_layer(100.0),
        "sweep": [oxide_layer(float(t)) for t in range(0, 501, 10)],
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "NA": NA, "M": M_PRECISE, "M_given": M_GIVEN, "rho_si": RHO_SI, "rho_ox": RHO_OX,
        "molar": [{"formula": f, "M": molar_mass(c)} for f, c in (("Si", {"Si": 1}), ("SiO2", SIO2), ("CuSO4", {"Cu": 1, "S": 1, "O": 4}), ("NH3", {"N": 1, "H": 3}))],
        "atoms_1g": {el: mass_to_atoms(1.0, M_PRECISE[el]) for el in ("Si", "Cu")},
        "ox281": oxidation(0.281), "ox562": oxidation(0.562),
        "si_density": si_density_from_cell(), "ratio": si_consumed_ratio(),
        "layer100": oxide_layer(100.0),
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("stoich-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote stoich-results.json"); sys.exit()
    L = R["lecture"]
    for q in L["molar"]:
        print(f"M({q['formula']}) = {r6(q['M'])} g/mol")
    print("1 g Si:", L["atoms_1g"]["Si"])
    print("562 mg Si:", {k: r6(v) for k, v in L["ox562"].items()})
    print("Si density from the unit cell:", {k: r6(v) for k, v in L["si_density"].items()})
    print("Si consumed per SiO2 grown:", r6(L["ratio"]))
    print("100 nm oxide on 1 cm2:", {k: r6(v) for k, v in L["layer100"].items()})
