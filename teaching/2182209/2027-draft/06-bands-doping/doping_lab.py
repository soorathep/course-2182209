"""Class 6 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Energy bands and doping of Si. Every number on the Class 6 slides and in Lab 6 comes
from this module.

Run `python doping_lab.py` for a printed summary, or `python doping_lab.py --json` to
write doping-results.json.

Data for Si at 300 K, from Sze and Ng, Physics of Semiconductor Devices: intrinsic carrier
concentration n_i = 1.45e10 cm^-3 (the classic value; newer measurements give about
1.0e10), electron and hole mobilities 1350 and 480 cm^2/(V s), band gap 1.12 eV.
Band gaps of other materials: Ge 0.66, GaAs 1.42, diamond 5.5, SiO2 about 9 eV.
Model choices, stated: every dopant atom is ionized; mobilities do not change with
doping (real mobilities fall above about 1e17 cm^-3). NumPy only.
"""
import json
import sys

import numpy as np

Q = 1.602176634e-19        # C, elementary charge
NI = 1.45e10               # cm^-3
MU_N, MU_P = 1350.0, 480.0  # cm^2/(V s)
ATOMS_SI = 8 / (0.5431e-7) ** 3   # cm^-3, from the unit cell (Class 3)
GAPS = [("Cu", 0.0, "conductor"), ("Ge", 0.66, "semiconductor"), ("Si", 1.12, "semiconductor"),
        ("GaAs", 1.42, "semiconductor"), ("diamond", 5.5, "insulator"), ("SiO2", 9.0, "insulator")]
VALENCE = {"B": 3, "Si": 4, "P": 5, "As": 5, "Al": 3}


def r6(x):
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def dopant_role(el):
    """Replace one Si atom: one extra valence electron makes a donor, one fewer an acceptor."""
    d = VALENCE[el] - VALENCE["Si"]
    if d == 0:
        return {"el": el, "role": "no change", "type": "intrinsic", "majority": "none"}
    return {"el": el, "role": "donor" if d > 0 else "acceptor", "type": "n-type" if d > 0 else "p-type",
            "majority": "electron" if d > 0 else "hole", "extra": d}


def carriers(N, kind="n"):
    """Electron and hole concentrations (cm^-3) with N dopants per cm^-3, all ionized.

    Charge balance n + N_A = p + N_D and the mass-action law n p = n_i^2.
    """
    if N <= 0:
        n = p = NI
    else:
        maj = N / 2 + np.sqrt(N * N / 4 + NI * NI)
        mino = NI * NI / maj
        n, p = (maj, mino) if kind == "n" else (mino, maj)
    sigma = Q * (n * MU_N + p * MU_P)
    return {"N": N, "kind": kind, "n": float(n), "p": float(p), "np": float(n * p), "sigma": float(sigma), "rho": float(1 / sigma)}


def fraction(N):
    """Dopant atoms per Si atom."""
    return N / ATOMS_SI


def lab_results():
    c16 = carriers(1e16, "n")
    i = carriers(0)
    return {
        "roles": {el: dopant_role(el) for el in ("P", "B")},
        "atoms_si": ATOMS_SI, "frac_1e16": fraction(1e16),
        "n16": c16, "intrinsic": i, "ratio_rho": i["rho"] / c16["rho"],
        "ni": NI, "mu_n": MU_N, "mu_p": MU_P, "q": Q,
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "gaps": [{"m": m, "Eg": e, "cls": c} for m, e, c in GAPS],
        "ni": NI, "mu_n": MU_N, "mu_p": MU_P, "q": Q, "atoms_si": ATOMS_SI,
        "frac_ni": NI / ATOMS_SI,
        "roles": [dopant_role(el) for el in ("P", "As", "B", "Al")],
        "intrinsic": carriers(0),
        "table": [carriers(N, k) for k in ("n", "p") for N in (1e14, 1e16, 1e18)],
        "frac_1e16": fraction(1e16),
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("doping-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote doping-results.json"); sys.exit()
    L = R["lecture"]
    print("Si atoms per cm3:", "%.3e" % L["atoms_si"], " n_i / atoms:", "%.2e" % L["frac_ni"])
    for q in L["roles"]:
        print(q)
    i = L["intrinsic"]; print("intrinsic: rho = %.3e ohm cm" % i["rho"])
    for c in L["table"]:
        print("%s-type N=%.0e: n=%.3e p=%.3e rho=%.3e ohm cm" % (c["kind"], c["N"], c["n"], c["p"], c["rho"]))
    print("dopant fraction at 1e16:", "%.2e" % L["frac_1e16"])
