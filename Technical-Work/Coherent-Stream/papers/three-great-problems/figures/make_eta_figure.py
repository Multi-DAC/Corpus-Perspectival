"""Generate the eta double-dissociation figure for the paper (content-capacity residue).

Panel (a): eta-proxy (1 - purity of subsystem) vs entanglement entropy -> tight monotone.
Panel (b): eta-proxy vs magic (stabilizer Renyi entropy) -> flat at zero (independent).
Establishes: the 'content-capacity residue' is an ENTANGLEMENT-monotone, independent of magic.
"""
import itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
P = {"I": I2, "X": X, "Y": Y, "Z": Z}
s = 1 / np.sqrt(2)
k0 = np.array([1, 0], complex); k1 = np.array([0, 1], complex)


def kron(ms):
    o = ms[0]
    for m in ms[1:]:
        o = np.kron(o, m)
    return o


def magic(psi, n=2):
    d = 2 ** n; tot = 0.0
    for L in itertools.product("IXYZ", repeat=n):
        e = np.real(np.vdot(psi, kron([P[x] for x in L]) @ psi))
        tot += (e * e / d) ** 2
    return max(0.0, -np.log2(d * tot))


def rhoS(psi):
    M = psi.reshape(2, 2); return M @ M.conj().T


def eta_proxy(psi):
    r = rhoS(psi); return float(1 - np.real(np.trace(r @ r)))


def vn(psi):
    ev = np.linalg.eigvalsh(rhoS(psi)); ev = ev[ev > 1e-12]
    return float(-np.sum(ev * np.log2(ev)))


# Panel (a): entanglement family  cos t |00> + sin t |11>
ts = np.linspace(0, np.pi / 2, 40)
ent, eta_a = [], []
for t in ts:
    psi = np.cos(t) * kron([k0, k0]) + np.sin(t) * kron([k1, k1])
    ent.append(vn(psi)); eta_a.append(eta_proxy(psi))

# Panel (b): magic family at zero entanglement  |psi(a)>|0>
als = np.linspace(0, np.pi / 4, 40)
mag, eta_b = [], []
for a in als:
    q = np.cos(a) * k0 + np.exp(1j * np.pi / 4) * np.sin(a) * k1
    q = q / np.linalg.norm(q)
    psi = kron([q, k0])
    mag.append(magic(psi)); eta_b.append(eta_proxy(psi))

# reference points (the double dissociation)
bell = (kron([k0, k0]) + kron([k1, k1])) * s
T = (k0 + np.exp(1j * np.pi / 4) * k1) * s
prodT = kron([T, k0])

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.7))
ax[0].plot(ent, eta_a, "-", color="#1b6", lw=2)
ax[0].scatter([vn(bell)], [eta_proxy(bell)], color="#c33", zorder=5, s=55,
              label="Bell |Φ+⟩  (magic=0)")
ax[0].set_xlabel("entanglement entropy  $S(\\rho_S)$ [bits]")
ax[0].set_ylabel("content-capacity residue  $\\eta = 1-\\mathrm{Tr}\\,\\rho_S^2$")
ax[0].set_title("(a)  residue tracks entanglement", fontsize=11)
ax[0].legend(fontsize=8, loc="lower right"); ax[0].grid(alpha=0.25)

ax[1].plot(mag, eta_b, "-", color="#36b", lw=2)
ax[1].scatter([magic(prodT)], [eta_proxy(prodT)], color="#c33", zorder=5, s=55,
              label="|T⟩|0⟩  (η=0)")
ax[1].set_xlabel("magic  $M_2$ (stabilizer Rényi entropy) [bits]")
ax[1].set_ylabel("content-capacity residue  $\\eta$")
ax[1].set_ylim(-0.05, 0.55)
ax[1].set_title("(b)  residue is independent of magic", fontsize=11)
ax[1].legend(fontsize=8, loc="upper right"); ax[1].grid(alpha=0.25)

fig.tight_layout()
fig.savefig("eta_dissociation.pdf", bbox_inches="tight")
fig.savefig("eta_dissociation.png", dpi=150, bbox_inches="tight")
print("saved eta_dissociation.pdf/.png")
print(f"  check: Bell eta={eta_proxy(bell):.3f} magic={magic(bell):.3f} | "
      f"|T>|0> eta={eta_proxy(prodT):.3f} magic={magic(prodT):.3f}")
