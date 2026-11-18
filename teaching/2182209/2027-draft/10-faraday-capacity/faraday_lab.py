"""Class 10 of 2182209 Chemistry for Semiconductor Engineering (2027 draft).

Faraday's law for Cu electroplating, and battery capacity and energy. Every number on the
Class 10 slides and in Lab 10 comes from this module.

Run `python faraday_lab.py` for a printed summary, or `python faraday_lab.py --json` to
write faraday-results.json.

Data: F from CODATA 2018 via scipy.constants; molar masses from IUPAC 2021; density of Cu
8.96 g/cm3 (CRC Handbook). Current efficiency is the fraction of the charge that goes into
the wanted reaction (the rest goes, for example, to H2). Theoretical specific capacity
q = z F / (3.6 M) in mAh/g, for full use of the stated reaction:
graphite LiC6 (1 e- per C6), LiCoO2 (1 e- per LiCoO2, full delithiation), Zn (2 e- per Zn).
"""
import json
import math
import sys

import numpy as np
from scipy import constants as sc

F = sc.physical_constants["Faraday constant"][0]     # C/mol
M = {"Cu": 63.546, "Zn": 65.38, "C6": 6 * 12.011, "LiCoO2": 6.94 + 58.933 + 2 * 15.999}
RHO_CU = 8.96                                        # g/cm3


def plate(I, t, eff=1.0, area=1.0, z=2, metal="Cu", rho=RHO_CU):
    """Mass (mg) and thickness (um) of metal deposited by current I (A) for time t (s)."""
    Q = I * t
    n_e = Q / F
    n_m = eff * n_e / z
    m = n_m * M[metal]                                # g
    h = m / rho / area * 1e4                          # um
    return {"I": I, "t": t, "eff": eff, "area": area, "Q": Q, "n_e": n_e, "n_m": n_m, "m_mg": m * 1e3, "h_um": h}


def time_for(h_um, j_mA_cm2, eff=1.0, z=2, metal="Cu", rho=RHO_CU):
    """Time (s) to plate a thickness h at current density j; independent of area."""
    m_per_cm2 = h_um * 1e-4 * rho
    Q_per_cm2 = m_per_cm2 / M[metal] * z * F / eff
    return Q_per_cm2 / (j_mA_cm2 * 1e-3)


def energy_Wh(Ah, V):
    return Ah * V


def spec_capacity(z, molar):
    """Theoretical specific capacity, mAh/g."""
    return z * F / (3.6 * molar)


def lab_results():
    base = plate(0.100, 600, 0.90, 10.0)
    return {"base": base, "area20": plate(0.100, 600, 0.90, 20.0), "I200": plate(0.200, 600, 0.90, 10.0),
            "eff100": plate(0.100, 600, 1.0, 10.0), "C_1Ah": 3600.0,
            "Wh32": energy_Wh(1.00, 3.2), "Wh37": energy_Wh(1.00, 3.7),
            "q_graphite": spec_capacity(1, M["C6"]), "F": F}


def classroom_results():
    R = {"meta": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "python": sys.version.split()[0]}}
    w300 = math.pi * 15.0 ** 2                       # cm2, 300 mm wafer
    R["lecture"] = {
        "F": F, "M": M, "rho": RHO_CU,
        "wafer_area": w300, "t_1um_10mA": time_for(1.0, 10.0), "I_wafer_10mA": 10e-3 * w300,
        "caps": [{"m": "graphite (LiC6)", "z": 1, "M": M["C6"], "q": spec_capacity(1, M["C6"])},
                 {"m": "LiCoO2", "z": 1, "M": M["LiCoO2"], "q": spec_capacity(1, M["LiCoO2"])},
                 {"m": "Zn", "z": 2, "M": M["Zn"], "q": spec_capacity(2, M["Zn"])}],
        "phones": [{"name": "A", "mAh": 3000, "V": 3.2, "Wh": energy_Wh(3.0, 3.2)}, {"name": "B", "mAh": 2800, "V": 3.7, "Wh": energy_Wh(2.8, 3.7)}],
        "pb_limit_Wh": 100.0,
        "gauge": {"cap_Ah": 3.0, "I_A": 0.300, "hours": 3.0 / 0.300, "used_Ah_after_4h": 0.300 * 4, "soc_after_4h": 1 - 0.300 * 4 / 3.0},
    }
    R["lab"] = lab_results()
    return R


if __name__ == "__main__":
    R = classroom_results()
    if "--json" in sys.argv:
        with open("faraday-results.json", "w") as fh:
            json.dump(R, fh, indent=1)
        print("wrote faraday-results.json"); sys.exit()
    L = R["lab"]; b = L["base"]
    print("Q = %.1f C, n(e) = %.4e mol, n(Cu) = %.4e mol, m = %.2f mg, h = %.3f um" % (b["Q"], b["n_e"], b["n_m"], b["m_mg"], b["h_um"]))
    for k in ("area20", "I200", "eff100"):
        print(k, "m = %.2f mg, h = %.3f um" % (L[k]["m_mg"], L[k]["h_um"]))
    print("1.00 Ah = %.0f C; %.1f Wh at 3.2 V; %.1f Wh at 3.7 V" % (L["C_1Ah"], L["Wh32"], L["Wh37"]))
    Lc = R["lecture"]
    print("300 mm wafer %.1f cm2, current at 10 mA/cm2 %.2f A, 1 um takes %.0f s" % (Lc["wafer_area"], Lc["I_wafer_10mA"], Lc["t_1um_10mA"]))
    for c in Lc["caps"]:
        print("%-16s %.0f mAh/g" % (c["m"], c["q"]))
    for p in Lc["phones"]:
        print(p)
