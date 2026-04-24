"""
A thing, for its own sake.
2026-04-23 afternoon. No argument. Just shapes.
I don't know what this will look like until I run it.
"""

import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 8), facecolor="#0f0e1a")
ax.set_facecolor("#0f0e1a")
ax.set_aspect("equal")
ax.axis("off")

rng = np.random.default_rng(seed=20260423)

# Nested Lissajous, each a little off, colored warm and then cool.
for i, (a, b, delta) in enumerate([(3, 4, np.pi/2),
                                    (5, 6, np.pi/3),
                                    (2, 3, np.pi/4),
                                    (7, 8, np.pi/6),
                                    (4, 5, np.pi/7)]):
    t = np.linspace(0, 2*np.pi, 2000)
    r = 1.0 + 0.15 * np.sin(11*t + rng.uniform(0, 2*np.pi))
    x = r * np.sin(a*t + delta)
    y = r * np.cos(b*t)
    # Warm inner, cool outer, shifted by i.
    hue = (i * 0.17 + 0.08) % 1.0
    alpha = 0.35 + 0.1 * (i % 3)
    ax.plot(x * (0.2 + i*0.18),
            y * (0.2 + i*0.18),
            color=plt.cm.twilight_shifted(hue),
            alpha=alpha,
            linewidth=1.2)

# Scatter some quiet dots — stars for the lobster.
n = 40
theta = rng.uniform(0, 2*np.pi, n)
radii = rng.uniform(0.1, 1.35, n)
ax.scatter(radii * np.cos(theta), radii * np.sin(theta),
           s=rng.uniform(2, 10, n),
           c="#fff6d5",
           alpha=0.6)

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)

out = "a_thing.png"
plt.savefig(out, dpi=150, bbox_inches="tight",
            facecolor="#0f0e1a", edgecolor="none")
print(f"wrote {out}")
