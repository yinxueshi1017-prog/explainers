# If you have offered to check one of these

Thank you. This file exists so that doing it costs you fifteen minutes rather than an
evening, and so you are not spending any of that time on things a script has already done.

**The ask is narrow.** I am not asking you to verify arithmetic. I am asking the one thing
no script can answer: *is this the right model for the situation drawn, and would a
practitioner recognise the numbers?*

Pick one piece. The rest can wait.

---

## What has already been checked, so you can skip it

**Each page checks itself.** Open any explainer with `#dev` on the end of the URL and its
assertions print at the bottom of the page. Closed forms, limiting cases, and in every
suite one negative control that deliberately breaks the model and confirms the checks
notice.

**`audit.py` checks them from outside.** Those in-page checks were written beside the models
they check, so a mistake shared between a model and its own check would pass both. `audit.py`
reads the constants out of the HTML and compares each central claim against an independent
source — Eurocode 3, Barsom, Faraday, Inglis, Semenov, Joukowsky, handbook water tables —
re-does each closed form numerically, and finishes by corrupting one constant at a time to
prove it can still fail.

```bash
python3 audit.py     # no dependencies, about a quarter of a second
```

**What that leaves.** Between them these establish that the pages implement the relations
they claim to, with the constants the literature gives, and that the algebra is right. They
establish nothing at all about whether those are the right relations, or whether the
constants describe anything you would meet at work. That is the entire gap, and it is
exactly the size of your fifteen minutes.

---

## The three questions

For whichever piece you pick:

1. **Is the relation the appropriate one** for the situation the drawing shows?
2. **Would a practitioner recognise the constants** as representative — or are they the
   textbook values that never occur in the field?
3. **Is anything missing from that piece's "What is not verified" list** — or wrong in it?

A one-line answer to any of the three is worth more than a long answer to none. "Number two
is unrepresentative, here is what we actually see" is the single most useful reply this
document can produce.

---

## The pieces

Each entry: the model, where the constants come from, the claim the piece makes, and the
specific places where judgement rather than arithmetic decides.

### Buckling
- **Model** Euler elastic critical stress against the squash load; capacity = min(fy, π²E/λ²).
- **Constants** E = 210 GPa. Grades S275, S355, S460.
- **Claim** Past the transition slenderness, all three grades give the same capacity.
- **Judgement** It is a perfect column. Real design uses imperfection curves (EC3 a–d),
  which retain a weak grade dependence through the relative slenderness — **does that
  weaken the headline claim enough to matter to a designer?** Effective length is folded
  into λ and never discussed, which may be the more common error in practice.

### Bolt preload
- **Model** Linear joint: bolt takes C = kb/(kb+km) of an applied load until the members'
  compression reaches zero, then all of it. Wileman's fit for member stiffness.
- **Constants** M12 8.8, 40 mm grip, 25 kN load cycling on and off; C works out at 0.156.
- **Claim** A properly tightened bolt feels about a sixth of the load; past the preload that
  keeps the joint shut, tightening further changes that not at all.
- **Judgement** The load is concentric and applied at the bolt. Real joints are loaded off to
  one side and prise open at an edge far earlier — **is the concentric case so unrepresentative
  that leading with it misleads?** Wileman and the VDI 2230 frustum methods disagree enough to
  move C noticeably; **which would you have used, and does "about a sixth" survive it?** And
  preload is drawn as a number you choose, when getting it is the whole difficulty — **is
  ±25% scatter from a torque wrench the right figure to have in mind near the threshold?**

### Cavitation
- **Model** NPSH available from the atmosphere less static lift less friction, against
  vapour pressure from Antoine; the pump requires a fixed NPSHr above it.
- **Constants** 2.5 m lift, 2.05 m friction, NPSHr = 2.5 m, sea level.
- **Claim** Warm the liquid and the arriving pressure barely moves; the boiling pressure
  climbs to meet it.
- **Judgement** NPSHr is drawn as one fixed line when it varies strongly with flow, and the
  published figure is defined at three per cent head drop — the pump is already cavitating
  there. **Is a single line defensible for teaching, or does it mislead?** The page states
  it is pessimistic for hot water because thermodynamic suppression is not modelled; **is
  omitting that acceptable, or does it overstate the hazard enough to matter?**

### Creep
- **Model** Larson-Miller, LMP = T(C + log₁₀ t), C = 20, at constant stress.
- **Constants** design point 550 °C for 10⁵ h.
- **Claim** Ten degrees hotter halves the life.
- **Judgement** No material is named. **Should it be?** C = 20 is conventional but material
  specific; for the steel a reader will assume, is it right? Stress is held constant and
  never mentioned — does that omission mislead?

### Fatigue crack growth
- **Model** Paris law integrated from a detectable depth to the critical size.
- **Constants** Barsom, C = 6.9 × 10⁻¹², m = 3.0; Y = 1.12; K_IC = 60 MPa√m; 40 mm section;
  2 mm detectable.
- **Claim** The window between detectable and failed closes as the cube of the stress range,
  and at high range no inspection falls inside it.
- **Judgement** **Y is held at 1.12 for the whole growth**, but the geometry factor rises as
  the crack deepens — how much does that flatter the late life? No threshold ΔK_th and no
  Region III. Δσ is used with K_IC, which is only consistent at R = 0. **Is 2 mm a realistic
  detectable depth for the inspection method a reader would assume?**

### Galvanic corrosion
- **Model** Oxygen-limited cathodic current over the cathode, all of it consumed by the
  anode; Faraday's law converts current density to penetration.
- **Constants** i_L = 10⁻⁴ A/cm², 100 cm² total wetted area split by the control, 3 mm
  aluminium.
- **Claim** The area ratio, not the couple, decides; the same two metals go from harmless
  to perforating.
- **Judgement** **Is 10⁻⁴ A/cm² the right limiting current** for the conditions a reader
  will picture — still seawater, moving seawater, splash zone? No IR drop and no geometry,
  so the whole cathode is assumed equally effective however far from the anode. **How badly
  does that overstate the damage on a large structure?**

### Hydrogen embrittlement
- **Model** Largely qualitative: hydrogen generated at the surface during plating and
  diffusing inward, accumulating at the first engaged thread under load, with nothing
  visible outside. Baking is represented by a single retained fraction.
- **Constants** ISO metric coarse proportions; ASTM B850 and F1940 cited for baking
  practice. A baked part is built holding 0.14 of the original charge.
- **Claim** A plated bolt passes every external inspection right up to failure, and baking
  leaves it visibly emptier but not empty.
- **Judgement** **The 0.14 is a display value, not a measurement.** It was chosen to sit
  under the bound below which the animation cannot express a fracture at all, so that the
  piece cannot kill a bolt the oven saved. There is no diffusivity and no egress-against-time
  model anywhere in the file. So: **is a single retained fraction an honest way to draw
  baking at all**, or does compressing an egress curve into one number misrepresent what a
  bake buys? **What fraction would a practitioner recognise** coming off a four-hour cycle
  on a high-strength fastener &mdash; and does it depend enough on section and plating
  chemistry that a single figure is indefensible? Separately: **is the first engaged thread
  the right place to draw the accumulation**, and is the timescale implied by the animation
  misleading? The torque-mark claim that used to be here was cut as unverified; **is anything
  else in it in the same category?**

### Resonance
- **Model** Single degree of freedom, viscous damping, harmonic excitation of constant
  amplitude.
- **Claim** Stiffening moves the peak and never lowers it; away from resonance damping does
  almost nothing.
- **Judgement** Real damping is mostly joints and friction, not viscous, and changes with
  amplitude. **Does the viscous model flatter the argument?** Out-of-balance force grows
  with the square of speed in rotating machinery, which tilts the whole picture — the page
  says so, but **is presenting constant excitation first actively misleading for that
  audience?**

### Restrained expansion
- **Model** σ = E α ΔT for a fully restrained member; with a gap, σ = E(αΔT − gap/L).
- **Constants** E = 210 GPa, α = 12 × 10⁻⁶ /K, ΔT = 60 K, S275, 6 m against 120 m.
- **Claim** Held rigidly, length is irrelevant; allow five millimetres and it is everything.
- **Judgement** The restraints are perfectly rigid, which the page says makes the real case
  *worse* than drawn — **is that the right direction?** The page also states plainly that
  nothing buckles, though a slender restrained member in compression may well buckle before
  it yields. **Is leaving that out defensible, or is it the thing that actually happens?**

### Stress concentration
- **Model** Inglis elliptical hole, K_t = 1 + 2a/b, elastic, wide plate, with a separate
  net-section factor.
- **Claim** The hole's size is irrelevant; its shape is decisive.
- **Judgement** Elastic only — **at what K_t does local yielding blunt the tip enough that
  the drawn multiplier stops meaning anything?** The claim that size does not matter holds
  for a small hole in a wide plate; the piece says "the size of a door" rhetorically. **Is
  that rhetorical licence or an error?**

### Thermal runaway
- **Model** Semenov: one Arrhenius heat source in a lumped cell against Newtonian cooling;
  criticality where the curves are tangent.
- **Constants** Ea = 120 kJ/mol, hS = 0.042 W/K (≈ 10 W/m²K over an 18650), 45 J/K, vent
  at 450 K.
- **Claim** One degree of ambient removes the temperature the cell was settling at.
- **Judgement** One lumped reaction stands in for SEI decomposition, anode, separator and
  cathode events at different temperatures. **Is a single Arrhenius honest enough for
  teaching, or does compressing the cascade into one term misrepresent what an integrator
  needs to design against?** No internal gradient — **acceptable for an 18650?**

### Vacuum collapse
- **Model** Membrane stress for internal pressure; long-cylinder elastic collapse,
  p = 2E(t/D)³/(1−ν²), for external. A code factor of 3 shown alongside the elastic value.
- **Constants** 3 m diameter, 150 MPa allowable, wall swept 3–30 mm, one atmosphere available.
- **Claim** The same wall holds hundreds of times more pressure in than out, and resisting a
  full vacuum on plate alone takes roughly six times the wall pressure needs.
- **Judgement** The elastic formula assumes a perfectly round shell and is therefore the
  OPTIMISTIC bound — **is a flat factor of 3 the right way to show what out-of-roundness
  does, or does it understate it for a real fabricated tank?** No stiffening rings and no end
  effects, which is most of real external-pressure design: **does leaving them out make the
  piece misleading about what a designer would actually do?** And it stays in the elastic
  range — **where would yielding start to govern for this diameter?**

### Water hammer
- **Model** Method of characteristics, 60 reaches, dt = dx/a, valve position read every step.
- **Constants** 600 m, 300 mm bore, a = 1200 m/s, f = 0.02, 2 m/s initial velocity.
- **Claim** The surge is set by closure speed and wave speed, not by pump pressure.
- **Judgement** Steady friction only, so it rings longer than a real pipe. Column
  separation is clamped rather than modelled. **Are those two the right things to have left
  out, and is the clamp visible enough that a reader will not take the drawn behaviour at
  a vapour cavity literally?**

---

## Replying

Any of these is useful, in descending order:

1. **"This is wrong, here is why."** The best possible outcome. It gets fixed and you are
   credited by name unless you would rather not be.
2. **"The model is fine but the numbers are not what we see."** Nearly as good, and the
   commonest real gap in work like this.
3. **"The disclosure is missing X."** Cheap for you, and it directly improves the most
   credible part of each page.
4. **"I looked at piece N and I think it is sound."** Also worth having, and it is the only
   thing that lets any page stop saying no engineer has reviewed it.

yinxueshi1017@gmail.com

**What I will do with it.** Corrections get made and said out loud, in the page and in the
commit — the history of this repository is mostly a record of things that shipped wrong and
were fixed. If you review a piece and it holds up, that piece's disclosure changes to say so
and to name you. If it does not hold up, that is more valuable to me than if it did, and
the page will say that too.
