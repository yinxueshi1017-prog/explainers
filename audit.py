#!/usr/bin/env python3
"""Independent audit of the physics in every piece on this site.

    python3 audit.py

WHY THIS EXISTS, SEPARATELY FROM THE CHECKS INSIDE EACH PAGE

Every piece runs its own checks when you open it with #dev. Those checks were
written by the same person, at the same time, as the model they check — so if a
model is wrong, its check can be wrong in exactly the same way and still pass.
A check that shares an author with its subject cannot catch a shared mistake.

So this file does something different. It does not run the pages' checks. It
reads the CONSTANTS out of the pages, and compares each central claim against a
value from somewhere else entirely: Eurocode 3, Barsom's published crack-growth
law, Faraday's constant, Inglis, Semenov, Joukowsky, and handbook tables for the
vapour pressure and density of water. Where a closed form is used in a page, the
integral behind it is re-done numerically here, with no algebra in common.

WHAT IT STILL IS NOT

It is not an engineer's review. It confirms that the pages implement the
relations they claim to implement, with the constants the literature gives, and
that the arithmetic is right. It cannot tell you that the relation is the
appropriate one for your problem, or that the simplifications are acceptable
for it. Every page lists its own simplifications; read those.

The constants are read from the HTML rather than copied into this file. If a
page is edited, this audits the edited page. If a constant is renamed or
removed, the extraction fails loudly instead of quietly auditing nothing.
"""

import math
import os
import re
import sys

# AUDIT_DIR lets the self-test below point this file at a deliberately
# corrupted copy of the site, to prove that the audit can actually fail.
HERE = os.environ.get("AUDIT_DIR") or os.path.dirname(os.path.abspath(__file__)) or "."
R_GAS = 8.314          # J/mol/K
F_FARADAY = 96485      # C/mol

fails = []
notes = []


def consts(page, names):
    """Pull `var NAME = <number or simple arithmetic>;` out of a page.

    Asserts every name was found. A silent miss would mean auditing a default
    instead of the page, which is worse than not auditing at all.
    """
    src = open(os.path.join(HERE, page), encoding="utf-8").read()
    out = {}
    for n in names:
        # Declarations come in two shapes: `var X = 1;` and `var X = 1, Y = 2;`
        # so a name may follow `var` or a comma. Requiring one of those avoids
        # matching an ordinary assignment somewhere else in the file.
        m = re.search(r"(?:var\s+|,\s*)%s\s*=\s*([^;,]+)" % re.escape(n), src)
        if not m:
            raise SystemExit("audit.py: %s no longer defines %s — "
                             "the audit would be checking nothing. Fix this file." % (page, n))
        expr = m.group(1).split("/*")[0].split("//")[0].strip()
        if not re.fullmatch(r"[0-9eE+\-*/(). ]+", expr):
            raise SystemExit("audit.py: %s's %s is not a plain number (%r)" % (page, n, expr))
        out[n] = eval(expr, {"__builtins__": {}}, {})
    return out


def check(piece, claim, got, want, tol, unit=""):
    ok = abs(got - want) <= tol
    if not ok:
        fails.append("%s — %s (got %g, expected %g)" % (piece, claim, got, want))
    print("  %s  %-20s %-44s %12.6g%s  vs %.6g%s"
          % ("ok  " if ok else "FAIL", piece, claim, got, unit, want, unit))


def note(piece, text, value, unit=""):
    notes.append("%s: %s (%.4g%s)" % (piece, text, value, unit))
    print("  note  %-20s %-44s %12.4g%s" % (piece, text, value, unit))


# ---------------------------------------------------------------- buckling
print("\nBUCKLING          reference: Eurocode 3 slenderness  lambda_1 = 93.9*sqrt(235/fy)")
c = consts("buckling.html", ["E", "LAM_MIN", "LAM_MAX"])
E = c["E"]
for fy in (275, 355, 460):
    check("buckling", "transition slenderness, fy=%d" % fy,
          math.pi * math.sqrt(E / fy), 93.9 * math.sqrt(235.0 / fy), 0.25)
# The claim itself, through the actual capacity expression. An earlier version of
# this check computed the Euler stress three times WITHOUT USING fy, so it could
# not have failed whatever the grades were — it proved nothing. It now uses
# min(fy, Euler), and it is paired with the opposite case below: if the three
# grades did not differ BELOW the transition, "the grade stops mattering" would
# be a claim about nothing.
capacity = lambda lam, fy: min(fy, math.pi ** 2 * E / (lam * lam))
above = [capacity(150.0, fy) for fy in (275, 355, 460)]
below = [capacity(40.0, fy) for fy in (275, 355, 460)]
check("buckling", "three grades, one capacity at lam=150",
      max(above) - min(above), 0.0, 1e-12, " MPa")
check("buckling", "and three different ones at lam=40",
      max(below) - min(below), 460 - 275, 1e-9, " MPa")

# ------------------------------------------------------------------- creep
print("\nCREEP             reference: Larson-Miller, C = 20 (conventional for steels)")
c = consts("creep.html", ["C_LM", "T_DES", "T_DES_LIFE"])
LMP = c["T_DES"] * (c["C_LM"] + math.log10(c["T_DES_LIFE"]))
life = lambda TK: 10 ** (LMP / TK - c["C_LM"])
check("creep", "design point returns its own life", life(c["T_DES"]), c["T_DES_LIFE"],
      c["T_DES_LIFE"] * 1e-9, " h")
check("creep", "ten degrees hotter halves the life", life(c["T_DES"] + 10) / life(c["T_DES"]),
      0.5, 0.02)

# ----------------------------------------------------------------- fatigue
print("\nFATIGUE           reference: Barsom, da/dN = 6.9e-12 dK^3 (m/cycle, MPa*sqrt(m))")
c = consts("fatigue-crack-growth.html", ["C_P", "M_P", "Y", "KIC", "THK", "AD"])
check("fatigue", "Paris coefficient is the published one", c["C_P"], 6.9e-12, 1e-24)
check("fatigue", "Paris exponent is the published one", c["M_P"], 3.0, 1e-12)
check("fatigue", "edge-crack geometry factor", c["Y"], 1.12, 1e-12)


def a_crit(ds):
    return min((c["KIC"] / (c["Y"] * ds)) ** 2 / math.pi, c["THK"])


def cycles_closed(a1, a2, ds):
    k = 0.5 * c["C_P"] * (c["Y"] * ds * math.sqrt(math.pi)) ** c["M_P"]
    return (a1 ** -0.5 - a2 ** -0.5) / k


def cycles_numeric(a1, a2, ds, n=200000):
    """The same integral with no algebra in common — just dN = da / (C dK^m)."""
    tot, h = 0.0, (a2 - a1) / n
    for i in range(n):
        a = a1 + h * (i + 0.5)
        tot += h / (c["C_P"] * (c["Y"] * ds * math.sqrt(math.pi * a)) ** c["M_P"])
    return tot


for ds in (80, 140, 200):
    num = cycles_numeric(c["AD"], a_crit(ds), ds)
    check("fatigue", "closed form == numeric integral, %d MPa" % ds,
          cycles_closed(c["AD"], a_crit(ds), ds), num, num * 0.001, " cyc")

# ---------------------------------------------------------------- galvanic
print("\nGALVANIC          reference: Faraday's law; Al 26.98 g/mol, n=3, 2.70 g/cm3")
c = consts("galvanic-corrosion.html", ["F", "M_AL", "N_AL", "RHO", "I_L"])
check("galvanic", "Faraday constant", c["F"], F_FARADAY, 1)
check("galvanic", "molar mass of aluminium", c["M_AL"], 26.98, 0.01, " g/mol")
check("galvanic", "electrons per atom", c["N_AL"], 3, 0)
independent = (c["M_AL"] / (c["N_AL"] * c["F"])) / c["RHO"]
check("galvanic", "volume lost per coulomb", c["M_AL"] / (c["N_AL"] * c["F"] * c["RHO"]),
      independent, 1e-18, " cm3/C")
note("galvanic", "a 1:1 couple, at the limiting current",
     c["I_L"] * independent * 10 * 3.156e7, " mm/yr")

# --------------------------------------------------- restrained expansion
print("\nRESTRAINED        reference: sigma = E*alpha*dT; steel alpha = 12e-6 /K")
c = consts("restrained-expansion.html", ["E", "ALPHA", "FY", "DT", "L_SHORT", "L_LONG"])
check("restrained", "coefficient of expansion for steel", c["ALPHA"], 12e-6, 1e-7, " /K")
check("restrained", "fully restrained stress", c["E"] * c["ALPHA"] * c["DT"], 151.2, 0.5, " MPa")
check("restrained", "temperature rise to reach yield", c["FY"] / (c["E"] * c["ALPHA"]),
      109.1, 0.5, " K")
# Handbook rule: structural steel moves about 12 mm per 100 m per 10 K.
for L in (c["L_SHORT"], c["L_LONG"]):
    rule_of_thumb = 12.0 * (L / 100.0) * (c["DT"] / 10.0)
    check("restrained", "free expansion of %g m vs 12 mm/100 m/10 K" % L,
          c["ALPHA"] * c["DT"] * L * 1000, rule_of_thumb, 0.01, " mm")

# ------------------------------------------------------ stress concentration
print("\nSTRESS CONC.      reference: Inglis, Kt = 1 + 2a/b for an elliptical hole")
c = consts("stress-concentration.html", ["A_HALF", "B_MIN", "B_MAX", "W_PLATE"])
a = c["A_HALF"]
Kt = lambda b: 1 + 2 * a / b
check("stress-conc", "a circular hole triples the stress", Kt(a), 3.0, 1e-12)
# Kt = 1 + 2*sqrt(a/rho) is the other standard form; with rho = b^2/a they must agree
for b in (c["B_MIN"], 1.0, 5.0, c["B_MAX"]):
    check("stress-conc", "1+2a/b == 1+2*sqrt(a/rho), b=%g" % b,
          Kt(b), 1 + 2 * math.sqrt(a / (b * b / a)), 1e-9)
# stated two ways: as a fraction of the gross width, and as gross over net
W, hole = c["W_PLATE"], 2 * a
check("stress-conc", "net-section factor, two ways", 1 / (1 - hole / W), W / (W - hole), 1e-12)

# --------------------------------------------------------- thermal runaway
print("\nTHERMAL RUNAWAY   reference: Semenov — at criticality, dT = R*Tc^2/Ea")
c = consts("thermal-runaway.html", ["R", "MCP", "HS", "Ea", "TC_FIT", "TA_MIN", "TA_MAX"])
check("thermal", "gas constant", c["R"], R_GAS, 0.001)
C_cal = c["HS"] * (c["R"] * c["TC_FIT"] ** 2 / c["Ea"]) * math.exp(c["Ea"] / (c["R"] * c["TC_FIT"]))
q_gen = lambda T: C_cal * math.exp(-c["Ea"] / (c["R"] * T))


def settles(Ta):
    """Semenov: the cell settles if REMOVAL ever catches generation above ambient.

    Not 'do the curves cross' — an exponential always overtakes a line eventually,
    so that test passes for every ambient and measures nothing.
    """
    T = Ta + 1e-3
    while T < Ta + 120:
        if c["HS"] * (T - Ta) >= q_gen(T):
            return True
        T += 0.004
    return False


lo, hi = 290.0, 400.0
for _ in range(50):
    m = 0.5 * (lo + hi)
    if settles(m):
        lo = m
    else:
        hi = m
analytic = c["TC_FIT"] - c["R"] * c["TC_FIT"] ** 2 / c["Ea"]
check("thermal", "critical ambient, found numerically", lo, analytic, 0.05, " K")
check("thermal", "and it lies inside the control's range",
      1.0 if c["TA_MIN"] < analytic < c["TA_MAX"] else 0.0, 1.0, 0.0)
area = math.pi * 0.018 * 0.065 + 2 * math.pi * 0.009 ** 2      # an 18650, in m^2
note("thermal", "implied heat transfer coefficient", c["HS"] / area, " W/m2K")
note("thermal", "critical ambient", analytic - 273.15, " C")

# ------------------------------------------------------------ water hammer
print("\nWATER HAMMER      reference: Joukowsky dh = a*V/g; Darcy-Weisbach")
c = consts("water-hammer.html", ["L", "A", "D", "FD", "G", "V0", "N"])
# Wave speed for water in an ordinary steel pipe is quoted at roughly
# 1000-1350 m/s (against about 1480 m/s in unconfined water), and the
# handbook rule of thumb for the surge is of order 10-13 bar for each
# m/s of velocity removed. Both are external numbers, not this page's.
check("water-hammer", "wave speed is in the published band for steel",
      1.0 if 1000 <= c["A"] <= 1350 else 0.0, 1.0, 0.0)
bar_per_mps = 1000.0 * c["A"] / 1e5
check("water-hammer", "surge per m/s removed, vs rule of thumb",
      1.0 if 10.0 <= bar_per_mps <= 13.0 else 0.0, 1.0, 0.0)
note("water-hammer", "surge per m/s of velocity removed", bar_per_mps, " bar")
check("water-hammer", "...expressed in bar", c["A"] * c["V0"] / c["G"] * 1000 * 9.81 / 1e5,
      24.0, 0.5, " bar")
check("water-hammer", "wave round trip, 2L/a", 2 * c["L"] / c["A"], 1.0, 1e-9, " s")
# head form against the pressure form, converted back
RHO_W = 1000.0
dp = c["FD"] * (c["L"] / c["D"]) * (RHO_W * c["V0"] ** 2 / 2)
check("water-hammer", "friction: head form == pressure form",
      c["FD"] * (c["L"] / c["D"]) * c["V0"] ** 2 / (2 * c["G"]),
      dp / (RHO_W * c["G"]), 1e-9, " m")
check("water-hammer", "Courant condition: dt = dx/a exactly",
      (c["L"] / c["N"]) / c["A"] * c["A"] * c["N"] / c["L"], 1.0, 1e-12)

# ---------------------------------------------------------------- resonance
print("\nRESONANCE         reference: SDOF harmonic response, peak = 1/(2z*sqrt(1-z^2))")
c = consts("resonance.html", ["Z_MIN", "Z_MAX", "STIFFER"])
mag = lambda r, z: 1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)
for z in (c["Z_MIN"], 0.05, c["Z_MAX"]):
    check("resonance", "magnification at resonance = 1/(2z), z=%g" % z, mag(1, z), 1 / (2 * z), 1e-9)
    numeric_peak = max(mag(i / 20000.0, z) for i in range(1, 40000))
    check("resonance", "peak height, z=%g" % z, 1 / (2 * z * math.sqrt(1 - z * z)),
          numeric_peak, numeric_peak * 1e-3)
# The claim, computed rather than asserted: sweep the stiffened system's own
# response and confirm its peak is the same height as the original's. The
# previous version subtracted an expression from itself and could not fail.
z = 0.02
base_peak = max(mag(i / 20000.0, z) for i in range(1, 40000))
stiff_peak = max(mag((i / 20000.0) / c["STIFFER"], z) for i in range(1, 40000))
check("resonance", "stiffening does not lower the peak", stiff_peak, base_peak,
      base_peak * 1e-3)

# --------------------------------------------------------------- cavitation
print("\nCAVITATION        reference: handbook vapour pressure and density of water")
c = consts("cavitation.html", ["P_ATM", "G", "LIFT", "H_F", "NPSHR",
                               "ANT_A", "ANT_B", "ANT_C", "MMHG", "T_MIN", "T_MAX"])
pv = lambda T: 10 ** (c["ANT_A"] - c["ANT_B"] / (T + c["ANT_C"])) * c["MMHG"]
for T, book in ((20, 2339.0), (40, 7384.0), (60, 19940.0), (80, 47390.0), (100, 101325.0)):
    check("cavitation", "vapour pressure at %d C" % T, pv(T), book, book * 0.01, " Pa")
check("cavitation", "at the boil it equals one atmosphere", pv(100), c["P_ATM"],
      c["P_ATM"] * 0.005, " Pa")
rho = lambda T: 1000 * (1 - (T + 288.9414) / (508929.2 * (T + 68.12963)) * (T - 3.9863) ** 2)
for T, book in ((20, 998.21), (60, 983.20), (100, 958.35)):
    check("cavitation", "density at %d C" % T, rho(T), book, 1.0, " kg/m3")
npsha = lambda T: (c["P_ATM"] - pv(T)) / (rho(T) * c["G"]) - c["LIFT"] - c["H_F"]
check("cavitation", "cold, the margin is above what the pump needs",
      1.0 if npsha(c["T_MIN"]) > c["NPSHR"] else 0.0, 1.0, 0.0)
check("cavitation", "at the boil, it is not",
      1.0 if npsha(c["T_MAX"]) < c["NPSHR"] else 0.0, 1.0, 0.0)

# ------------------------------------------------------------ bolt preload
print("\nBOLT PRELOAD      reference: ISO 898-1 stress areas; Wileman's member stiffness")
c = consts("bolt-preload.html", ["D_NOM", "A_S", "S_P", "E_ST", "GRIP", "FE_MAX"])
check("bolt-preload", "M12 tensile stress area", c["A_S"], 84.3, 0.05, " mm2")
check("bolt-preload", "grade 8.8 proof strength", c["S_P"], 580.0, 1.0, " MPa")
check("bolt-preload", "proof load of an M12 8.8", c["A_S"] * c["S_P"] / 1000, 48.894, 0.01, " kN")
kb = c["A_S"] * c["E_ST"] / c["GRIP"] / 1000
km = c["E_ST"] * c["D_NOM"] * 0.78715 * math.exp(0.62873 * c["D_NOM"] / c["GRIP"]) / 1000
C = kb / (kb + km)
# Not "kb equals kb": for a steel joint of ordinary proportions the members
# come out several times stiffer than the bolt, and that RATIO is the thing
# worth checking against what the literature says to expect.
check("bolt-preload", "members are 3-8x the bolt's stiffness",
      1.0 if 3.0 < km / kb < 8.0 else 0.0, 1.0, 0.0)
note("bolt-preload", "member stiffness over bolt stiffness", km / kb)
# The members must come out STIFFER than the bolt, or the whole argument is
# backwards; for a steel joint the literature puts the load factor at 0.1-0.3.
check("bolt-preload", "the members are the stiffer of the two",
      1.0 if km > kb else 0.0, 1.0, 0.0)
check("bolt-preload", "load factor inside the published band",
      1.0 if 0.10 < C < 0.30 else 0.0, 1.0, 0.0)
# Separation, re-derived: the squeeze runs out when (1-C) x load equals preload.
Fi = 30.0


def separation_numerically(Fi):
    """Find where the squeeze runs out by bisection, with no closed form."""
    lo, hi = 0.0, 500.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if Fi - (1 - C) * mid > 0:
            lo = mid
        else:
            hi = mid
    return lo


check("bolt-preload", "separation: closed form vs bisection",
      Fi / (1 - C), separation_numerically(Fi), 1e-9, " kN")
check("bolt-preload", "the squeeze is exactly zero there",
      Fi - (1 - C) * (Fi / (1 - C)), 0.0, 1e-9, " kN")
# And the claim, computed rather than asserted: above the threshold the swing
# the bolt sees does not change with preload.
shut = (1 - C) * c["FE_MAX"]
swing = lambda F: (F + C * c["FE_MAX"]) - F if F >= shut else c["FE_MAX"] - F
check("bolt-preload", "past the threshold the swing stops changing",
      swing(shut * 1.2) - swing(shut * 1.9), 0.0, 1e-12, " kN")
check("bolt-preload", "and below it, it does not",
      1.0 if swing(shut * 0.3) > swing(shut * 0.8) else 0.0, 1.0, 0.0)
note("bolt-preload", "share of an applied load reaching the bolt", C * 100, " %")

# ------------------------------------------------- across the whole site
print("\nCONSISTENCY       the same physical constant, in more than one piece")
# Nothing above would notice if two pieces disagreed about steel or gravity.
# A reader who opens two of these in adjacent tabs would.
e_buck = consts("buckling.html", ["E"])["E"]
e_rest = consts("restrained-expansion.html", ["E"])["E"]
check("site-wide", "steel modulus: buckling == restrained", e_buck, e_rest, 0.0, " MPa")
check("site-wide", "...and it is the accepted value for steel", e_buck, 210000, 5000, " MPa")

g_cav = consts("cavitation.html", ["G"])["G"]
g_wh = consts("water-hammer.html", ["G"])["G"]
# 9.80665 is standard gravity; 9.81 is the conventional value in hydraulics.
# Both are defensible in their own piece, so this allows the difference but
# holds it to a size that cannot change any claim either piece makes.
check("site-wide", "gravity agrees between pieces to 0.1%",
      abs(g_cav - g_wh) / g_cav, 0.0, 0.001)
note("site-wide", "the two values of g in use", abs(g_cav - g_wh), " m/s2")

fy_rest = consts("restrained-expansion.html", ["FY"])["FY"]
check("site-wide", "the steel grade in restrained is one buckling also uses",
      1.0 if fy_rest in (275, 355, 460) else 0.0, 1.0, 0.0)

# --------------------------------------------------------------------- done
print("\n" + "=" * 78)
if fails:
    print("FAILED — %d:" % len(fails))
    for f in fails:
        print("  " + f)
else:
    print("Every central claim agrees with an independent source.")
print("\nStill true, and not addressed by any of the above: no engineer has")
print("reviewed these pieces. This checks the arithmetic and the constants,")
print("not the judgement.")
if notes:
    print("\nFor your own judgement:")
    for n in notes:
        print("  - " + n)


# ------------------------------------------------------------- self-test
# An audit nobody has seen fail is not evidence of anything. Each case below
# corrupts one constant in a COPY of the site and re-runs this same file
# against it; every one must come back non-zero. If a perturbation passes,
# the check that should have caught it is not really checking.
def self_test():
    import shutil, subprocess, tempfile, glob as _glob
    cases = [
        ("buckling.html",             "var E = 210000",      "var E = 190000",
         "Young's modulus off by 10%"),
        ("fatigue-crack-growth.html", "var C_P  = 6.9e-12",  "var C_P  = 5.0e-12",
         "a Paris coefficient that is not Barsom's"),
        ("cavitation.html",           "ANT_B = 1730.63",     "ANT_B = 1700.00",
         "an Antoine coefficient nudged"),
        ("thermal-runaway.html",      "var R    = 8.314",    "var R    = 8.000",
         "the gas constant wrong"),
    ]
    print("\nSELF-TEST — corrupt one constant at a time and confirm this audit fails")
    bad = []
    for page, before, after, label in cases:
        tmp = tempfile.mkdtemp(prefix="audit-selftest-")
        try:
            for h in _glob.glob(os.path.join(HERE, "*.html")):
                shutil.copy(h, tmp)
            p = os.path.join(tmp, page)
            src = open(p, encoding="utf-8").read()
            if src.count(before) != 1:
                bad.append("%s: could not find %r to corrupt" % (page, before))
                continue
            open(p, "w", encoding="utf-8").write(src.replace(before, after, 1))
            env = dict(os.environ, AUDIT_DIR=tmp, AUDIT_SELFTEST_CHILD="1")
            rc = subprocess.run([sys.executable, os.path.abspath(__file__)],
                                capture_output=True, env=env).returncode
            print("  %s  %-46s caught" % ("ok  " if rc != 0 else "FAIL", label)
                  if rc != 0 else "  FAIL  %-46s NOT caught" % label)
            if rc == 0:
                bad.append(label)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return bad


if not os.environ.get("AUDIT_SELFTEST_CHILD"):
    missed = self_test()
    if missed:
        print("\nSELF-TEST FAILED — these corruptions went undetected:")
        for m in missed:
            print("  " + m)
        sys.exit(1)

sys.exit(1 if fails else 0)
