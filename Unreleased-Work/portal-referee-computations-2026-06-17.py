#!/usr/bin/env python
"""
Portal paper — referee-response computations (2026-06-17).
Three honest debts raised in technical review, made concrete:
  R13  EED charge-(non)conservation: wall locality + reversibility (the bound does not bind)
  R14  Natural coaxial helicity injection: does geomagnetic-bias-flux x telluric V offset resistive decay?
  R15  Ignition threshold: current-sheet drift for micro-turbulence onset vs. what a trigger delivers
All SI unless noted.
"""
import math

# ---- constants ----
hbar_c_eV_m = 197.327e6 * 1e-15      # eV*m
mu0   = 4*math.pi*1e-7
e     = 1.602176634e-19
amu   = 1.66053907e-27

print("="*70)
print("R13  EED charge-(non)conservation — locality + reversibility")
print("="*70)
m_scalar_eV = 2.3e-3                  # dark-energy-scale modulus, ~2.3 meV
L_wall = hbar_c_eV_m / m_scalar_eV    # Compton wall thickness = 1/m
print(f"  wall thickness 1/m            = {L_wall*1e6:8.1f} um  ({L_wall:.2e} m)")
print( "  In gauge-free EED  d_mu J^mu = -eps0 [] C  (C = div A + (1/c^2) d_t phi).")
print( "  EED EM source is J_eff = -a (d_mu sigma) F^{mu nu}: NONZERO ONLY where d sigma != 0,")
print( "  i.e. confined to the ~86 um wall shell.  Key physics:")
print( "   (i)  STATIC wall  -> static C-redistribution of Gauss's law, NOT ongoing charge creation;")
print( "        net charge in any volume conserved (a field reshuffle, like bound-charge polarization).")
print( "   (ii) RADIATIVE part (the SLW) carries OSCILLATORY C with zero cycle-average:")
print( "        the apparent dq/dt reverses each cycle -> no secular charge loss.")
print( "  The tight lab bounds (Borexino electron-decay tau_e > 6.6e28 yr) constrain IRREVERSIBLE")
print( "  charge disappearance.  The EED term here is reversible + non-secular for a stationary wall,")
print( "  so those bounds DO NOT BIND.  Residual constraint = any secular component -> vanishes")
print( "  for a standing wall.  Grade: resolved structurally; the remaining number is the secular")
print( "  drift, identically zero at zeroth order for a static defect.")

print()
print("="*70)
print("R14  Natural CHI budget — geomagnetic bias flux vs. resistive helicity decay")
print("="*70)
L   = 10.0          # Hessdalen-scale carrier (m)  [EMBLA: dm to ~30 m; take 10 m]
P   = 1.9e4         # absolute luminosity ~19 kW (Teodorani/EMBLA)
Bgeo= 5e-5          # geomagnetic field (T) ~0.5 G
# luminosity fixes B^2/sigma via R11:  P = B^2 L / (2 mu0^2 sigma)
B2_over_sigma = 2*mu0**2 * P / L
print(f"  from P = B^2 L/(2 mu0^2 sigma):  B^2/sigma = {B2_over_sigma:.2e}  (SI)")
# resistive helicity decay:  dH/dt|_decay = 2 B^2 L^2/(sigma mu0)  (force-free, alpha~1/L)
dHdt_decay = 2*B2_over_sigma*L**2/mu0
print(f"  resistive helicity decay  dH/dt|_decay = {dHdt_decay:.2f} Wb^2/s")
# injection:  dH/dt = 2 V psi,  psi ~ Bgeo * L^2 (geomagnetic flux through the object)
psi = Bgeo*L**2
print(f"  geomagnetic bias flux  psi = Bgeo L^2  = {psi:.2e} Wb")
V_min = dHdt_decay/(2*psi)
print(f"  -> sustaining voltage required:  V_min = dH/dt|_decay / (2 psi) = {V_min:.0f} V")
print( "  Atmospheric-electric (even fair-weather ~100 V/m x 10 m = 1 kV; storm-enhanced far more)")
print( "  and telluric surges clear ~100 V across a 10 m conductive structure by 1-3 orders.")
print( "  BUDGET CLOSES with large margin.  Bias flux is GEOMAGNETIC -> sharpens the prediction:")
print( "  carrier helicity sign should anchor to the geomagnetic orientation (handedness gets a")
print( "  geophysical reference), and the conductive geology must LINK Bgeo (signature-4 refinement).")

print()
print("="*70)
print("R15  Ignition threshold — drift for micro-turbulence onset vs. trigger delivery")
print("="*70)
Te_eV = 1.0                          # cool atmospheric plasma
mi    = 15*amu                       # N/O ion
cs    = math.sqrt(Te_eV*e/mi)        # ion-sound speed (Te>>Ti)
n     = 1e19                         # electron density (m^-3, weakly ionized glow)
J_th  = n*e*cs                       # ion-acoustic onset:  v_d = J/(ne) > c_s
print(f"  ion-sound speed c_s (Te=1 eV, N/O) = {cs:7.0f} m/s")
print(f"  micro-turbulence onset  J_th = n e c_s = {J_th:.2e} A/m^2")
B_car = 1e-3                         # carrier field ~10 G
delta = B_car/(mu0*J_th)            # current-sheet thickness to reach J_th
print(f"  -> needs current sheet of thickness  delta = B/(mu0 J_th) = {delta*100:.0f} cm  (at B~10 G)")
# what a trigger delivers (lightning channel)
I_lh, r_lh = 3e4, 1e-2
J_lh = I_lh/(math.pi*r_lh**2)
print(f"  lightning channel  J = {J_lh:.1e} A/m^2  -> exceeds threshold by x{J_lh/J_th:.0e}")
print( "  Lightning/sprite/piezo/telluric transients breach J_th by ~10^3-10^4: TRIGGER suffices.")
print( "  Picture: discharge momentarily drives J>>J_th -> micro-turbulence -> anomalous resistivity")
print( "  -> kV double layer + energetic particles -> self-sustained CHI; helicity conservation then")
print( "  carries the state long past the trigger (TRIGGER/SUSTAIN architecture).  The threshold IS")
print( "  the selection mechanism: rarity + place-fixity + intermittency follow from the conjunction")
print( "  (unscreening geology) AND (trigger breaches J_th) AND (conductive geometry links Bgeo).")
print( "  Prediction: occurrence correlates with trigger-event statistics (lightning/sprite/micro-seismic).")

print()
print("="*70)
print("R16  Dynamical Q-ball cavity sidebands (scaling; full breathing-mode solve pending)")
print("="*70)
h_eV_s = 4.135667696e-15
c      = 2.99792458e8
m_eV   = 2.3e-3
f_carrier = m_eV/h_eV_s              # Q-ball charge-rotation ~ field mass
lam    = c/f_carrier
L_match= c/(2*f_carrier)             # cavity FSR matched to carrier
L_cav  = 0.10                        # a 10 cm cavity
FSR    = c/(2*L_cav)
N_order= f_carrier/FSR
print( "  A Q-ball carries its charge on an internal phase rotation sigma_in e^{i w t}, so the wall")
print( "  field OSCILLATES.  Through e^{a sigma}F^2 it modulates the cavity index -> sideband comb at")
print( "  Omega +/- n w on the probe; cavity gain ~ Finesse x (a sigma_in).  Two frequencies:")
print(f"   carrier sideband  w ~ m :  f = m c^2/h = {f_carrier/1e9:6.0f} GHz   (lambda = {lam*1e3:.2f} mm, sub-THz)")
print(f"     FSR-matched by L = c/2f = {L_match*1e6:.0f} um, OR high-order N = f/FSR = {N_order:.0f} on a 10 cm cavity")
print( "   breathing sideband  w_b(rho) -> 0  as rho is bled UP to rho_crit (critical slowing-down at the")
print( "     delocalization bifurcation): a TUNABLE sideband sweeping toward DC maps the localization boundary.")
print( "  DISCIPLINE: the cavity maps the PHYSICAL localization failure (rho->rho_crit), NOT the observer-")
print( "  coupled limb -- an evacuated cavity has no observer-stream DOF.  It confirms a sharp delocalization")
print( "  boundary EXISTS (precondition for the fork-unification to be physical) and stops there.")
print( "  STATUS: carrier freq + cavity match fixed by the mass scale; the breathing-mode spectrum w_b(rho)")
print( "  and the Mathieu parametric-gain map require extending R12 (static) to the dynamical gauged Q-ball.")
print("="*70)
