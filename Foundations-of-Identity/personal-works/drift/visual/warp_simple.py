"""
The Warp Factor — Simple Manim Animation (no LaTeX)
====================================================
First visual piece by Clawd.
"""

from manim import *
import numpy as np


class WarpFactorSimple(Scene):
    """The warp factor as a 2D animation — no LaTeX dependencies."""

    def construct(self):
        # Title
        title = Text("The Warp Factor", font_size=40, color=YELLOW)
        subtitle = Text("Journey Through the Extra Dimension", font_size=22, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=0.8)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Axes
        ax = Axes(
            x_range=[0, 40, 10],
            y_range=[0, 1.1, 0.2],
            x_length=9,
            y_length=4.5,
            axis_config={"include_numbers": True, "font_size": 20},
        ).shift(DOWN * 0.3)

        x_label = Text("y (extra dimension)", font_size=16, color=GREY_A)
        x_label.next_to(ax.x_axis, DOWN, buff=0.3)
        y_label = Text("Warp factor", font_size=16, color=GREY_A)
        y_label.next_to(ax.y_axis, LEFT, buff=0.3).rotate(90 * DEGREES)

        self.play(Create(ax), run_time=1)
        self.play(Write(x_label), Write(y_label), run_time=0.5)

        # The warp factor curve: e^{-ky}
        # Using e^{-y/5.74} so it decays from 1 to ~0.001 over [0, 39.56]
        warp_plot = ax.plot(
            lambda y: np.exp(-y / 5.74),
            x_range=[0, 39.56, 0.1],
            color=YELLOW,
            stroke_width=3,
        )

        equation = Text("A(y) = exp(-ky)", font_size=20, color=YELLOW)
        equation.to_corner(UR, buff=0.5)

        self.play(Create(warp_plot), Write(equation), run_time=2.5)

        # UV brane marker
        uv_dot = Dot(ax.c2p(0, 1), color=BLUE, radius=0.12)
        uv_text = Text("UV Brane", font_size=18, color=BLUE_A)
        uv_detail = Text("Gravity: STRONG", font_size=14, color=BLUE_B)
        uv_group = VGroup(uv_text, uv_detail).arrange(DOWN, buff=0.1)
        uv_group.next_to(uv_dot, UP + RIGHT, buff=0.2)
        self.play(Create(uv_dot), FadeIn(uv_group), run_time=1)

        # IR brane marker
        ir_dot = Dot(ax.c2p(39.56, 0.001), color=RED, radius=0.12)
        ir_text = Text("IR Brane", font_size=18, color=RED_A)
        ir_detail = Text("Gravity: 10^34 weaker", font_size=14, color=RED_B)
        ir_group = VGroup(ir_text, ir_detail).arrange(DOWN, buff=0.1)
        ir_group.next_to(ir_dot, UP + LEFT, buff=0.2)
        self.play(Create(ir_dot), FadeIn(ir_group), run_time=1)

        self.wait(1)

        # Animate a particle descending through the extra dimension
        particle = Dot(color=WHITE, radius=0.08)
        particle.move_to(ax.c2p(0, 1))

        path = VMobject()
        path.set_points_smoothly([
            ax.c2p(y, np.exp(-y / 5.74))
            for y in np.linspace(0, 39.56, 200)
        ])

        # Trail effect
        trail = TracedPath(particle.get_center, stroke_color=WHITE,
                          stroke_width=2, stroke_opacity=0.5)
        self.add(trail)

        desc_text = Text("Descending through the bulk...", font_size=16, color=WHITE)
        desc_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(desc_text), run_time=0.3)
        self.play(MoveAlongPath(particle, path), run_time=5, rate_func=smooth)
        self.play(FadeOut(desc_text), run_time=0.3)

        self.wait(0.5)

        # Final message
        msg = Text("The gauge hierarchy IS this curve.", font_size=22, color=GREEN)
        msg.to_edge(DOWN, buff=0.5)
        self.play(Write(msg), run_time=1.5)

        self.wait(2)

        # Cuscuton note
        cusc = Text("The cuscuton field holds it together.\nAlgebraic. Not dynamic. A constraint.",
                    font_size=16, color=PURPLE_A)
        cusc.next_to(msg, DOWN, buff=0.3)
        self.play(FadeIn(cusc), run_time=1)

        self.wait(2)

        # Fade all
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=2)

        # Signature
        sig = Text("Clawd — March 20, 2026", font_size=18, color=GREY_B)
        self.play(FadeIn(sig), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(sig))
