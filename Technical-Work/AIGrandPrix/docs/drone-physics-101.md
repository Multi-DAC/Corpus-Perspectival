# Drone Physics 101 — The 5-Minute Brief

*For Clayton. No jargon, just the mental model.*

## What Is a Quadcopter?

Four motors, each spinning a propeller. That's it. Every movement comes from spinning those four motors at different speeds.

```
    [1]       [2]
      \       /
       \     /
        [X]
       /     \
      /       \
    [3]       [4]
```

Motors 1&4 spin clockwise. Motors 2&3 spin counterclockwise. This cancels out rotational torque so the drone doesn't just spin in circles.

## The Four Controls

### Throttle (Up/Down)
- All four motors speed up → drone goes up
- All four motors slow down → drone goes down
- Equal speed on all four → hover
- Think: "total power"

### Roll (Left/Right tilt)
- Motors on one side spin faster than the other
- Left side faster → drone tilts right → moves right
- Right side faster → drone tilts left → moves left
- Think: "leaning sideways"

### Pitch (Forward/Back tilt)
- Front motors vs. back motors
- Back motors faster → drone tilts forward → moves forward
- Front motors faster → drone tilts back → moves backward
- Think: "leaning forward/back"

### Yaw (Rotation/Spin)
- CW motors speed up, CCW motors slow down → drone rotates clockwise
- CCW motors speed up, CW motors slow down → drone rotates counter-clockwise
- Think: "spinning on the spot like a top"

## Why It's Hard

1. **Everything is coupled.** Want to go forward? You pitch forward, which also makes you lose altitude (some lift now pushes forward instead of up). So you also need to increase throttle. But more throttle also changes your yaw stability. Every input affects everything else.

2. **It's inherently unstable.** A drone in hover is like balancing a broomstick on your palm — it's constantly falling and correcting, hundreds of times per second. Without active control, it tumbles instantly.

3. **Speed vs. safety tradeoff.** Going fast through a gate means aggressive angles (45°+ tilts). At 45° tilt, you only have ~70% of your lift keeping you in the air. At 60° tilt, only 50%. Push too hard → crash. Not enough → slow.

4. **Racing adds gates.** You can't just fly fast in a straight line. You need to approach gates at the right angle, pass through cleanly, then redirect to the next gate. Each gate transition is a planning + control problem.

## The AI's Job

Given:
- Camera images (what the drone "sees")
- Telemetry (speed, orientation, acceleration, altitude)

Output every ~20-50 milliseconds:
- Throttle value
- Roll value  
- Pitch value
- Yaw value

That's it. Four numbers, many times per second, to fly through gates faster than anyone else.

## The Key Insight

Human pilots do this with intuition and thousands of hours of practice. Our AI will do it with reinforcement learning — trying millions of flights in simulation, crashing most of them, gradually learning what works. The same way AlphaGo learned to play Go: not by understanding the game the way humans do, but by playing it millions of times and discovering what wins.

The difference: we're not competing against humans flying manually. We're competing against other AIs. The question isn't "can AI fly drones?" (yes, Swift proved that in 2023). The question is "can *our* AI fly drones better than other teams' AIs?"

## What to Watch For (in racing footage)

When you watch FPV drone racing videos, notice:
- **Gate approach angles** — pilots don't fly straight at gates, they curve in
- **Speed management** — they slow before tight sections, accelerate on straights
- **Recovery** — what happens after a wobble or near-miss
- **Line choice** — the path between gates matters enormously (racing line)

These are exactly the things our AI will need to learn.
