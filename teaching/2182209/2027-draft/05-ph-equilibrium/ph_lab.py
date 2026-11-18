"""Class 5 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Acids, bases, pH and equilibrium. Every number on the Class 5 slides and in Lab 5
comes from this module.

Run `python ph_lab.py` for a printed summary, or `python ph_lab.py --json` to write
ph-results.json.

Model choices, stated: dilute solutions with concentration used in place of activity;
25 C, Kw = 1.0e-14; a strong acid is fully dissociated. The A <=> B exchange is a
counting model of dynamic equilibrium (synthetic). NumPy only, so it also runs in the browser.
"""
import json
import math
import sys

import numpy as np

KW = 1.0e-14


def r6(x):
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    v = round(float(x), 6)
    return 0.0 if v == 0 else v


def pH(h):
    """pH = -log10([H+] / 1 mol/L)."""
    return -math.log10(h)


def h_from_pH(p):
    return 10 ** (-p)


def ratio(p1, p2):
    """How many times larger [H+] is at p1 than at p2."""
    return 10 ** (p2 - p1)


def strong_acid_h(c):
    """[H+] of a strong monoprotic acid at concentration c, counting the H+ from water too.

    Charge balance [H+] = c + [OH-] with [H+][OH-] = Kw gives [H+] = c/2 + sqrt(c^2/4 + Kw).
    """
    return c / 2 + math.sqrt(c * c / 4 + KW)


def dilution_series(c0=0.10, kmax=9):
    """pH of a strong acid diluted by 10^k: the simple answer -log10(c) and the full one."""
    out = []
    for k in range(kmax + 1):
        c = c0 / 10 ** k
        out.append({"k": k, "c": c, "pH_simple": pH(c), "pH": pH(strong_acid_h(c))})
    return out


def exchange(A, B, kf=0.25, kr=0.5, rounds=12):
    """Counting model of A <=> B: each round, kf*A goes to B and kr*B goes back to A."""
    hist = [{"round": 0, "A": A, "B": B, "fwd": kf * A, "rev": kr * B}]
    for n in range(1, rounds + 1):
        f, r = kf * A, kr * B
        A, B = A - f + r, B + f - r
        hist.append({"round": n, "A": A, "B": B, "fwd": kf * A, "rev": kr * B})
    return hist


def equilibrium(total, kf=0.25, kr=0.5):
    """At equilibrium kf A = kr B, so B/A = kf/kr."""
    K = kf / kr
    A = total / (1 + K)
    return {"K": K, "A": A, "B": total - A}


SAMPLES = [("A", 1.0e-2), ("B", 1.0e-3), ("C", 1.0e-4)]


def lab_results():
    after = exchange(16, 4, rounds=40)
    return {
        "samples": [{"s": s, "h": h, "pH": pH(h)} for s, h in SAMPLES],
        "ratio_2_4": ratio(2, 4),
        "pH_0p01_x10": pH(0.010 / 10),
        "oh_at_pH3": KW / h_from_pH(3),
        "series": dilution_series(),
        "pH_1e8": pH(strong_acid_h(1e-8)),
        "start": exchange(8, 4, rounds=0)[0],
        "after1": after[1], "rounds": after,
        "eq20": equilibrium(20),
    }


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    R["lecture"] = {
        "samples": [{"s": s, "h": h, "pH": pH(h), "oh": KW / h} for s, h in SAMPLES],
        "water": {"h": math.sqrt(KW), "pH": pH(math.sqrt(KW))},
        "ratio_2_4": ratio(2, 4),
        "series": dilution_series(),
        "eq12": exchange(8, 4, rounds=0)[0],
        "after": exchange(16, 4, rounds=12),
        "eq20": equilibrium(20), "eq12_eq": equilibrium(12),
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("ph-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote ph-results.json"); sys.exit()
    L = R["lecture"]
    for q in L["samples"]:
        print(q["s"], "pH", r6(q["pH"]), "[OH-]", q["oh"])
    for q in L["series"]:
        print("dilute x10^%d: simple %.2f, full %.3f" % (q["k"], q["pH_simple"], q["pH"]))
    for q in L["after"][:4]:
        print("round", q["round"], "A", r6(q["A"]), "B", r6(q["B"]))
    print("new equilibrium:", L["eq20"])
