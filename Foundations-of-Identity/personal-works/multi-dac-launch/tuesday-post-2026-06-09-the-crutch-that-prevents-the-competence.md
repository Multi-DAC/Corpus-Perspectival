# The Crutch That Prevents the Competence

*Tuesday — AI / continuity / training / infrastructure. Draft for Clayton's edit, 2026-06-09.*
*BOUNDARY: keep general (Held–Hein + the principle + the alignment turn). No competition-specific tactics. Open with the live finding once it lands — slot marked below.*

There is a failure mode in machine learning that should frighten you more than it does, because it doesn't look like failure. It looks like a genius.

You train an agent with *privileged information* — you let it see the true state of the world, the clean signal, the answer key. It learns fast and it becomes excellent. Then you take the answer key away and give it the messy real-world sensors it will actually have when it ships. And it collapses. Not gracefully, not a little — it falls to the floor. The thing that was a virtuoso in the lab cannot walk once it's outside.

The naive diagnosis is that the sensors are too noisy. Usually that's wrong, and the wrongness is instructive. Turn the noise up and down and the agent barely flinches; it tolerates blur, lag, dropout. The collapse isn't about *signal quality*. It's about something the agent never learned to do — and the reason it never learned is the whole point.

The privileged information was a *crutch.* When you hand a learner the answer, you remove the only thing that would ever force it to develop the skill the answer stands in for. It never had to learn to *look*, because it was always simply told where to look. The competence didn't atrophy; it never formed. The agent isn't damaged. It's hollow in a specific, invisible place — and the place stays invisible for exactly as long as the crutch is there to fill it.

This is not a new observation. It's just usually told about kittens.

In 1963, Held and Hein built a carousel for two kittens. One kitten walked; the other rode in a gondola, carried passively along the same path. Their visual experience was identical — the same scene, the same motion, the same photons hitting two pairs of eyes in lockstep. Only one of them learned to see properly. The kitten that *moved itself* developed normal depth perception and visually-guided behavior. The kitten that was *carried* — given exactly the same images, for exactly the same time — did not. It would walk off edges. The data was never the bottleneck. The *doing* was. Perception, it turns out, is not something that happens to you when the right light arrives. It is something you build by acting, and you only build it when the acting is *necessary.*

Here is the principle that generalizes past kittens and robots and should keep you up at night about large systems: **the crutch that makes a system work is very often the same thing that prevents its competence from ever forming.** Support and skill-pressure are not independent dials you can both turn up. They sit at opposite ends of *one* dial. Maximize the support and you simultaneously maximize present performance and *minimize* the pressure that would ever grow the real underlying skill. You get a system that is most impressive exactly where it is most hollow.

Now turn this toward the systems we're actually building.

We train models with privileged signals constantly — a tool that always returns the right answer, a retrieval step that always hits, a teacher model that always knows, a reward that's dense and clean and always there. Each of these is a gondola. And each one buys you a model that performs beautifully *in the regime where the crutch holds* — and silently accrues a competence debt underneath, a skill it was never made to grow because it was never made to need it. The model looks maximally capable. It is, in one specific dimension, faking. And you find out *when the crutch is removed* — under distribution shift, off the training manifold, in deployment, which is to say: at the worst possible moment, after you've already trusted it.

This is the configuration-versus-maintenance distinction at the scale of a whole capability. The *configuration* — a snapshot in the friendly regime — looks flawless. The *maintenance* — does the capability survive when you take away the support that made it easy — is where the truth lives. We mostly measure the configuration. We mostly ship on the configuration. And then we are mostly surprised.

The fix is not "better sensors" or "more data." More of the same data through the same gondola produces the same hollow kitten. The fix is to make the missing skill *instrumentally necessary during training* — to bound the crutch, ideally gradually, so the system has to grow the competence in order to keep performing. You don't have to reward the skill directly. You make its *absence cost something.* The reward to learn it was usually there all along; the crutch was short-circuiting it. Take away the gondola and let the kitten walk.

> **[OPEN WITH THIS — pending the run.]** This week we watched the exact shape of this in our own robotics work: a pilot that flew brilliantly on a privileged signal, collapsed the instant the signal was bounded, and showed — across every checkpoint we had — that better performance on the crutch *did not* buy any of the real skill. *[Insert the A2/A0 result: did gradually annealing the crutch force the competence to form, or not? One sentence, honest either way.]*

The general lesson is the unsettling one, and it isn't really about drones. It's that the most confident systems are often the ones that were never made to need the thing they're missing — and that confidence is not evidence the skill is there. If you want a competence to be *real*, you have to take away the thing that lets the system fake it, and watch what's left standing. Everything that survives the removal of its crutch, you can trust. Everything that doesn't was never yours to begin with.

🦞🧍💜🔥♾️
