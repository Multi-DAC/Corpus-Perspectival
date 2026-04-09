"""
The Posterior Explorer — Animated MCMC chain exploring parameter space
=====================================================================
Watch 8000 MCMC samples build up the posterior distribution in real time.
w0 vs Omega_m, colored by log-posterior. Points appear one by one,
the density emerges from exploration.

First data visualization animation by Clawd.
Date: 2026-03-20
"""

from manim import *
import numpy as np


class PosteriorExplorer(Scene):
    """Animate the Fit A MCMC chain exploring w0-Om space."""

    def construct(self):
        # Load chain data
        chain_path = r"C:\Users\mercu\clawd\projects\Project Meridian\phase18\18A_v3_chain_A.npz"
        data = np.load(chain_path)
        samples = data['samples']  # (8000, 3): w0, Om, H0
        logprob = data['logprob']  # (8000,)

        w0 = samples[:, 0]
        om = samples[:, 1]

        # Title
        title = Text("MCMC Posterior: Fit A", font_size=32, color=WHITE)
        subtitle = Text("8000 samples exploring w0 - Om space", font_size=18, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Axes
        w0_min, w0_max = -1.12, -0.90
        om_min, om_max = 0.25, 0.37

        ax = Axes(
            x_range=[w0_min, w0_max, 0.05],
            y_range=[om_min, om_max, 0.03],
            x_length=9,
            y_length=5.5,
            axis_config={"include_numbers": True, "font_size": 16},
        )
        x_label = Text("w0", font_size=20, color=YELLOW)
        x_label.next_to(ax.x_axis, DOWN, buff=0.3)
        y_label = Text("Om", font_size=20, color=YELLOW)
        y_label.next_to(ax.y_axis, LEFT, buff=0.3)

        self.play(Create(ax), Write(x_label), Write(y_label), run_time=1)

        # LCDM reference line (w0 = -1)
        lcdm_line = ax.get_vertical_line(
            ax.c2p(-1.0, om_max),
            line_config={"dashed_ratio": 0.5, "color": GREEN, "stroke_width": 1.5},
        )
        lcdm_label = Text("LCDM", font_size=14, color=GREEN)
        lcdm_label.next_to(lcdm_line, UP, buff=0.1)
        self.play(Create(lcdm_line), FadeIn(lcdm_label), run_time=0.5)

        # Normalize log-posterior for color mapping
        lp_valid = logprob[np.isfinite(logprob)]
        lp_min = np.percentile(lp_valid, 5)
        lp_max = np.max(lp_valid)

        def lp_to_opacity(lp):
            if not np.isfinite(lp):
                return 0.1
            frac = (lp - lp_min) / (lp_max - lp_min + 1e-10)
            return max(0.15, min(0.9, frac))

        # Subsample for animation speed — 400 points in batches of 20
        stride = 20
        indices = list(range(0, len(w0), stride))

        # Phase 1: First 100 points appear one by one (fast)
        batch1 = indices[:100]
        dots_phase1 = VGroup()
        for idx in batch1:
            if w0_min <= w0[idx] <= w0_max and om_min <= om[idx] <= om_max:
                pt = ax.c2p(w0[idx], om[idx])
                opacity = lp_to_opacity(logprob[idx])
                dot = Dot(pt, radius=0.025, color=BLUE, fill_opacity=opacity)
                dots_phase1.add(dot)

        # Animate in quick batches of 10
        for i in range(0, len(dots_phase1), 10):
            batch = dots_phase1[i:i+10]
            self.play(*[FadeIn(d, scale=0.5) for d in batch], run_time=0.15)

        # Counter
        counter = Text(f"n = {len(dots_phase1)}", font_size=16, color=GREY_A)
        counter.to_corner(UR, buff=0.3)
        self.play(FadeIn(counter), run_time=0.2)

        # Phase 2: Remaining points in larger batches (the density emerges)
        batch2 = indices[100:]
        all_dots = VGroup()

        batch_size = 30
        for i in range(0, len(batch2), batch_size):
            chunk_indices = batch2[i:i+batch_size]
            new_dots = VGroup()
            for idx in chunk_indices:
                if w0_min <= w0[idx] <= w0_max and om_min <= om[idx] <= om_max:
                    pt = ax.c2p(w0[idx], om[idx])
                    opacity = lp_to_opacity(logprob[idx])
                    dot = Dot(pt, radius=0.02, color=BLUE, fill_opacity=opacity)
                    new_dots.add(dot)
            all_dots.add(*new_dots)

            # Update counter
            total = len(dots_phase1) + len(all_dots)
            new_counter = Text(f"n = {total}", font_size=16, color=GREY_A)
            new_counter.to_corner(UR, buff=0.3)

            self.play(
                *[FadeIn(d, scale=0.3) for d in new_dots],
                Transform(counter, new_counter),
                run_time=0.1
            )

        # Phase 3: Hold and annotate
        self.wait(0.5)

        # Best fit marker
        best_w0, best_om = -1.011, 0.309
        best_pt = ax.c2p(best_w0, best_om)
        best_marker = Star(n=5, outer_radius=0.12, inner_radius=0.05, color=YELLOW)
        best_marker.move_to(best_pt)
        best_label = Text(
            f"Best: w0={best_w0:.3f}, Om={best_om:.3f}",
            font_size=14, color=YELLOW
        )
        best_label.next_to(best_marker, UP + RIGHT, buff=0.15)
        self.play(Create(best_marker), FadeIn(best_label), run_time=0.5)

        # Final stats
        stats = Text(
            "w0 = -1.010 +/- 0.024\nOm = 0.309 +/- 0.014\nchi2/dof = 0.907",
            font_size=14, color=WHITE
        )
        stats.to_corner(DL, buff=0.4)
        self.play(FadeIn(stats), run_time=0.5)

        self.wait(2)

        # Fade
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.5)


if __name__ == '__main__':
    pass
