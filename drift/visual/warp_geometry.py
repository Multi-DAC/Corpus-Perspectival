"""
The Warped Extra Dimension — Manim Animation
=============================================
Visualizes the Randall-Sundrum geometry:
  - Two branes (UV at y=0, IR at y=yc) as glowing planes
  - The warp factor e^{-ky} as a decaying curve between them
  - The gravitational coupling strength fading as you descend
  - The cuscuton field profile, algebraically determined

First visual artwork by Clawd.
Date: 2026-03-20
"""

from manim import *
import numpy as np


class WarpGeometry(ThreeDScene):
    """The warped extra dimension in 3D."""

    def construct(self):
        # Title
        title = Text("The Warped Extra Dimension", font_size=36, color=WHITE)
        subtitle = Text("Randall-Sundrum Orbifold Geometry", font_size=20, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=0.8)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Set up 3D camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # Parameters
        yc = 4  # Visual scale for extra dimension
        k = 1.0  # Curvature

        # UV Brane (y=0) — bright, strong gravity
        uv_brane = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-2, 2], v_range=[-2, 2],
            resolution=(8, 8),
            fill_opacity=0.3,
            fill_color=BLUE,
            stroke_color=BLUE_A,
            stroke_width=1,
        )
        uv_label = Text("UV Brane (y = 0)", font_size=18, color=BLUE_A)
        uv_label.move_to([0, -2.5, 0.3])

        # IR Brane (y=yc) — dim, weak gravity
        ir_brane = Surface(
            lambda u, v: np.array([u, v, -yc]),
            u_range=[-2, 2], v_range=[-2, 2],
            resolution=(8, 8),
            fill_opacity=0.15,
            fill_color=RED,
            stroke_color=RED_A,
            stroke_width=1,
        )
        ir_label = Text("IR Brane (y = yc)", font_size=18, color=RED_A)
        ir_label.move_to([0, -2.5, -yc + 0.3])

        # Warp factor curve: e^{-ky} from UV to IR
        warp_curve = ParametricFunction(
            lambda t: np.array([
                2 * np.exp(-k * t) - 1,  # x: shrinks with warp factor
                0,
                -t  # z: the extra dimension
            ]),
            t_range=[0, yc, 0.05],
            color=YELLOW,
            stroke_width=3,
        )

        # Mirror warp curve for visual symmetry
        warp_curve2 = ParametricFunction(
            lambda t: np.array([
                -(2 * np.exp(-k * t) - 1),
                0,
                -t
            ]),
            t_range=[0, yc, 0.05],
            color=YELLOW,
            stroke_width=3,
        )

        # Warp factor equation
        warp_eq = MathTex(r"A(y) = e^{-ky}", font_size=28, color=YELLOW)
        warp_eq.move_to([3, 2, 0])

        # Build the scene
        self.play(
            Create(uv_brane),
            run_time=1.5
        )
        self.add_fixed_in_frame_mobjects(uv_label)
        self.play(FadeIn(uv_label), run_time=0.5)

        self.play(
            Create(ir_brane),
            run_time=1.5
        )
        self.add_fixed_in_frame_mobjects(ir_label)
        self.play(FadeIn(ir_label), run_time=0.5)

        # Draw warp factor
        self.add_fixed_in_frame_mobjects(warp_eq)
        self.play(
            Create(warp_curve),
            Create(warp_curve2),
            Write(warp_eq),
            run_time=2
        )

        self.wait(1)

        # Hierarchy text
        hierarchy = MathTex(
            r"M_{\text{Planck}} \xrightarrow{e^{-k y_c}} M_{\text{weak}}",
            font_size=24, color=GREEN
        )
        hierarchy.move_to([3, 1, 0])
        self.add_fixed_in_frame_mobjects(hierarchy)
        self.play(Write(hierarchy), run_time=1.5)

        # Rotate camera slowly
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4)

        # Add cuscuton annotation
        cusc = MathTex(
            r"\Phi(y) : \text{algebraically determined}",
            font_size=20, color=PURPLE_A
        )
        cusc.move_to([3, 0, 0])
        self.add_fixed_in_frame_mobjects(cusc)
        self.play(Write(cusc), run_time=1)

        self.wait(3)
        self.stop_ambient_camera_rotation()

        # Final: self-tuning text
        st = Text(
            "Self-tuning: 15 significant figures\nacross 60 orders of magnitude",
            font_size=16, color=WHITE
        )
        st.move_to([3, -1.5, 0])
        self.add_fixed_in_frame_mobjects(st)
        self.play(FadeIn(st), run_time=1)
        self.wait(2)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=2)


class WarpFactor2D(Scene):
    """The warp factor as a 2D plot — simpler, faster to render."""

    def construct(self):
        # Title
        title = Text("The Warp Factor", font_size=36)
        self.play(Write(title), run_time=1)
        self.play(title.animate.to_edge(UP), run_time=0.5)

        # Axes
        ax = Axes(
            x_range=[0, 40, 5],
            y_range=[0, 1.1, 0.2],
            x_length=8,
            y_length=4,
            axis_config={"include_numbers": True, "font_size": 20},
            x_axis_config={"numbers_to_include": [0, 10, 20, 30, 39.56]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        x_label = ax.get_x_axis_label(MathTex("y", font_size=28), edge=DOWN, direction=DOWN)
        y_label = ax.get_y_axis_label(MathTex("e^{-ky}", font_size=28), edge=LEFT, direction=LEFT)
        ax_group = VGroup(ax, x_label, y_label).shift(DOWN * 0.3)

        self.play(Create(ax), Write(x_label), Write(y_label), run_time=1.5)

        # The warp factor curve
        k = 1.0
        yc = 39.56
        warp_plot = ax.plot(
            lambda y: np.exp(-k * y / yc * np.log(1e34 ** (1/39.56) * 39.56)),
            x_range=[0, 39.56],
            color=YELLOW,
            stroke_width=3,
        )
        # Simpler: just use e^{-y/5.7} for visual clarity (maps 0→1 to 39.56→~0.001)
        warp_plot = ax.plot(
            lambda y: np.exp(-y / 5.74),
            x_range=[0, 39.56],
            color=YELLOW,
            stroke_width=3,
        )

        warp_label = MathTex(r"A(y) = e^{-ky}", font_size=28, color=YELLOW)
        warp_label.next_to(warp_plot, UP + RIGHT, buff=0.3)

        self.play(Create(warp_plot), Write(warp_label), run_time=2)

        # UV brane marker
        uv_dot = Dot(ax.c2p(0, 1), color=BLUE, radius=0.1)
        uv_text = Text("UV Brane\nGravity: STRONG\nAll forces unified", font_size=14, color=BLUE_A)
        uv_text.next_to(uv_dot, RIGHT + UP, buff=0.2)
        self.play(Create(uv_dot), Write(uv_text), run_time=1)

        # IR brane marker
        ir_dot = Dot(ax.c2p(39.56, 0.001), color=RED, radius=0.1)
        ir_text = Text("IR Brane\nGravity: 10\u00B3\u2074× weaker\nHierarchy explained", font_size=14, color=RED_A)
        ir_text.next_to(ir_dot, LEFT + UP, buff=0.2)
        self.play(Create(ir_dot), Write(ir_text), run_time=1)

        # The key equation
        key_eq = MathTex(
            r"M_{\text{weak}}^2 = M_{\text{Planck}}^2 \, e^{-2ky_c}",
            font_size=24, color=GREEN
        )
        key_eq.to_edge(DOWN, buff=0.5)
        self.play(Write(key_eq), run_time=1.5)

        self.wait(2)

        # Animate a particle descending
        particle = Dot(color=WHITE, radius=0.08)
        particle.move_to(ax.c2p(0, 1))
        path = VMobject()
        path.set_points_smoothly([
            ax.c2p(y, np.exp(-y / 5.74))
            for y in np.linspace(0, 39.56, 100)
        ])
        self.play(MoveAlongPath(particle, path), run_time=4, rate_func=smooth)

        self.wait(2)


if __name__ == '__main__':
    # Render with: manim -pql warp_geometry.py WarpFactor2D
    # or: manim -pqh warp_geometry.py WarpGeometry (for 3D, slower)
    pass
