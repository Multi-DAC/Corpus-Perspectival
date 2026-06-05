"""η vs magic vs entanglement — double-dissociation probe (LC34 verify-next #2).

η-proxy: how much the WHOLE reshapes the PART = mixedness of S's reduced state, 1 - Tr(rho_S^2).
  0 when S is a product factor (isolated; eta trivial); max when S is maximally entangled (eta maximal).
magic: stabilizer 2-Renyi entropy M2 of the GLOBAL pure state (Leone-Oliviero-Hamma 2022).
  0 for stabilizer states; >0 for non-stabilizer (magic) states.
entanglement: von Neumann entropy of rho_S.

Test: is eta-proxy correlated with magic (LC34's claim) or with entanglement (the prediction)?
"""
import itertools
import numpy as np

I2 = np.array([[1, 0], [0, 1]], complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}


def kron(mats):
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out


def magic_M2(psi, n):
    """Stabilizer 2-Renyi entropy of pure n-qubit state psi. 0 iff stabilizer."""
    d = 2 ** n
    s = 0.0
    for labels in itertools.product("IXYZ", repeat=n):
        P = kron([PAULI[l] for l in labels])
        exp = np.real(np.vdot(psi, P @ psi))
        xi = (exp ** 2) / d
        s += xi ** 2
    return -np.log2(d * s)


def reduced_S(psi):
    """rho_S for a 2-qubit state psi (trace out qubit E=second qubit)."""
    M = psi.reshape(2, 2)          # rows = S index, cols = E index
    return M @ M.conj().T


def vn_entropy(rho):
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-12]
    return float(-np.sum(ev * np.log2(ev)))


def eta_proxy(rho_S):
    return float(1 - np.real(np.trace(rho_S @ rho_S)))


def report(name, psi, n=2):
    rho_S = reduced_S(psi)
    print(f"{name:28s}  eta-proxy={eta_proxy(rho_S):.3f}  magic_M2={magic_M2(psi,n):.3f}  "
          f"S_ent={vn_entropy(rho_S):.3f}")


s = 1 / np.sqrt(2)
T = np.array([1, np.exp(1j * np.pi / 4)]) * s          # single-qubit magic state |T>
ket0 = np.array([1, 0], complex)

print("=== single-qubit sanity ===")
print(f"|0>  magic_M2 = {magic_M2(ket0,1):.3f} (expect 0, stabilizer)")
print(f"|+>  magic_M2 = {magic_M2(np.array([s,s],complex),1):.3f} (expect 0, stabilizer)")
print(f"|T>  magic_M2 = {magic_M2(T,1):.3f} (expect ~0.415, max single-qubit magic)")

print("\n=== the double dissociation (2-qubit: S = qubit 1) ===")
report("product stabilizer |00>", kron([ket0, ket0]))
report("Bell |Phi+> (entangled stab)", (kron([ket0,ket0]) + kron([np.array([0,1],complex),np.array([0,1],complex)]))*s)
report("product MAGIC |T>|0>", kron([T, ket0]))
report("entangled+magic |T>|0>+|1>|1>", (kron([T,ket0]) + kron([np.array([0,1],complex),np.array([0,1],complex)]))/np.linalg.norm(kron([T,ket0]) + kron([np.array([0,1],complex),np.array([0,1],complex)])))

print("\n=== sweep A: tune ENTANGLEMENT at fixed magic=0 (cos t|00> + sin t|11>) ===")
print("(note: generic theta has magic too; theta=pi/4 is the stabilizer Bell point)")
for t in np.linspace(0, np.pi/2, 5):
    psi = np.cos(t)*kron([ket0,ket0]) + np.sin(t)*kron([np.array([0,1],complex),np.array([0,1],complex)])
    rho_S = reduced_S(psi)
    print(f"  theta={t:.2f}  eta-proxy={eta_proxy(rho_S):.3f}  magic={magic_M2(psi,2):.3f}  S_ent={vn_entropy(rho_S):.3f}")

print("\n=== sweep B: tune MAGIC at fixed entanglement=0 (product |psi(a)>|0>) ===")
for a in np.linspace(0, np.pi/4, 5):
    q = np.cos(a)*ket0 + np.exp(1j*np.pi/4)*np.sin(a)*np.array([0,1],complex)
    q = q/np.linalg.norm(q)
    psi = kron([q, ket0])
    rho_S = reduced_S(psi)
    print(f"  alpha={a:.2f}  eta-proxy={eta_proxy(rho_S):.3f}  magic={magic_M2(psi,2):.3f}  S_ent={vn_entropy(rho_S):.3f}")
