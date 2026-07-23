---
title: "Lessons from my RL experiments with snake"
date: 2026-07-23
---

An AI agent trained on a smaller board should be able to play well on a big board.

Train on 6x6, or 10x10 and test it on 100x100.

If we can do it, so should an AI agent.

Simple concepts to learn:
- move closer to the apple
- do not collide with the wall
- do not collide with yourself (body)

I didn't expect to learn breadth and depth of RL from this toy problem, but I was pleasantly surprised. I even learned more about the process of research and lingo used in the field.

Feel free to [jump directly to Phase 4](#phase-4) to see the convnet size-invariant results.

## Phase 1

In the first phase I applied the classic RL algorithms to snake:
- Tabular Q learning, which is like a giant lookup table, that maps every state S with action A. It was quite close to dynamic programming I was familiar with. You update Q values based on rewards of the action.
- Followed it up with Double Q learning, that decouples action selection from action evaluation, so two value functions. (Value functions determine the value of state by estimating future return)
- Then I jumped to policy gradient methods like Reinforce, PPO. Unlike the value based methods where you learn a value function to derive a policy, in these methods you directly learn the policy.

- PPO worked for 5x5, but it didn't generalise to 10x10. 
Tried curriculum next, 5x5->8x8->10x10. 
Started with imitation learning using the replays from Reinforce.
Then train it on 8x8 and it worked. Collected replays.
Similarly train it on 10x10 and it worked.

But this felt like cheating and sort of silly. 
Humans don't have to train on each board to play on 100x100

In this phase I did a lot of reward modelling and feature engineering. It often felt like an overkill, if you do have to encode so much manually, then what is it actually learning if you give it everything. Reward modelling loopholes being exploited was a lot of fun to observe. Like snake just going looping forever without growing; not even caring about the apple.

We do see the board and see the apple instantly, and we know we need to move closer. Convolution Neural Network felt right for this problem, I don't know why I resisted it for so long. The filter/kernel sliding through the board should generalise to larger boards.

## Phase 2

Phase two was a detour where I stumbled upon curiosity based learning paper and applied it to my snake agent. Instead of handcrafting rewards, I let the agent learn from its own experience by rewarding novel states. This approach naturally encouraged exploration without explicit feature engineering.

Intrinsic Curiosity Module didn't help DQN, but it did help PPO with sparse rewards. 

## Phase 3

Phase three was about finding out if raw 3 channel grid ConvNet can beat the 24 hand crafted feature DQN?

As expected, it did easily beat DQN and PPO, but I still wanted to test if it could generalise to larger board sizes without retraining.

## Phase 4

First we had to build a size agnostic ConvNet (global pooling head) that trained and ran on all board sizes.

Trained on 6x6 worked well, held till ~10–12, but the performance degraded to random by ~16.

Trained on 10x10 worked well, held till board ~14–16, but the performance gradually degraded to random by ~32.

Interpolation worked: 10x10 trained agent performed well on all smaller boards, extrapolation didn't.

It was time to dig into the magical neural network.

Using mechanistic probes, I found out that agent could see where the food was but walked away anyway. Decoded concept wasn't being used. The food steering signal collapsed while the survival signal held.

Global pooling was using aggregation operators avg and max that were board size dependent. This caused empty-background flooding on bigger boards.

GAP+GMP squash the board into a 256-vector. On small boards the single-cell head/food signals dominate the pool enough to steer; as the board grows they are diluted among hundreds of cells (avg-pool → ~0; max-pool keeps "food exists" but loses where). Past a threshold the pooled representation can't encode direction to food → navigation collapses. Predicts a cliff, and predicts its location.

I wasn't paying close attention to what each operator inside the net was doing; what information it was keeping and what it was throwing away.

We introduced attention pooling to fix empty-background flooding. But that surfaced another issue: long-range direction. 
The reason was subtle: attention pooling suppresses the background and softly picks out the food cell, but the features it pools are translation-invariant; the conv produces the same feature vector for "food" no matter where the food sits. So the pooled vector could say "food exists" but carried no information about where it was. With only a ~5×5 receptive field, nothing in the network could relate the head's position to the food's at a distance. The pooled representation had no notion of position at all.

I added absolute normalized coordinate channels to the input: turning the 3-channel grid [body, head, food] into 5 channels by stamping every cell with its position, row/(H−1) and col/(W−1), both in [0,1]. The idea: now when attention selects the food cell, the pooled vector inherits that cell's coordinates, so the head could in principle read out food-position-minus-head-position and get direction at any range. Trained on 6×6 only (we were changing one variable at a time — no curriculum yet).

A small win in the marginal zone (boards ~12–16 nudged up over attention-only), but real play still collapsed to chance by board ~24, and it was dead — 0 food, 50% toward-food — at 48/64/100. Coordinate channels alone were not enough.

Why it fell short: normalized coordinates rescale with board size, so "food 3 to my right" meant 0.6 on 6×6 and 0.03 on 100×100, and a 6×6-only agent only ever saw the large-fraction regime. The coords supplied the information for direction, but single-size training never forced the network to use it size-invariantly; it just memorized a 6×6-specific mapping. That result is precisely what motivated the next step, which was to stop encoding absolute position and encode position relative to the head: the egocentric channels.

Instead of stamping each cell with its absolute position, I stamped it with its offset from the snake's own head, in raw cells, squashed through a tanh — tanh((i − head_i)/κ). Now board size cancels out: "food 3 cells to my right" is the identical value on a 6×6 or a 100×100 board, because it's measured in cells from the head, not as a fraction of the board. The tiny offsets of the final approach are already seen constantly on small boards, and far offsets saturate toward ±1, so a food distance larger than anything in training just collapses onto a "far in this direction" signal the agent has already seen thousands of times. All a move really needs is the sign of the offset on each axis (up/down, left/right), and that never depends on how big the board is.

**The probe-validated fixes made real-play transfer WORSE, not better**

Fine-grained real-play sweep (toward-food% and avg score, all trained on 6×6, greedy):

| board | baseline avg-pool | attention pool | ego + attention |
|---|---|---|---|
| 6  | 87% (13.6) | 89% (13.9) | 90% (15.0) |
| 8  | **87% (17.4)** | 82% (15.1) | 66% (7.9) |
| 10 | **75% (15.0)** | 70% (12.0) | 53% (1.6) |
| 11 | 61% (7.1) | 61% (6.5) | 52% (1.1) |
| 12 | 56% (4.2) | 55% (3.8) | 51% (0.8) |
| 14 | 55% (4.2) | 53% (2.4) | 50% (0.1) |
| 16 | 51% (1.1) | 51% (1.1) | 50% (0.2) |
| 25 | 50% | 50% | 50% |

Stop tweaking architecture; characterize the actual STATES. Rolling out a FIXED scripted competent policy (greedy-to-food + collision avoidance — identical behavior at every size, so any change is pure board-size) gives:

| statistic | 6 | 10 | 16 | 25 |
|---|---|---|---|---|
| food dist (mean) | 3.2 | 4.9 | 7.2 | 11.0 |
| % food beyond 5×5 RF | 44% | 67% | 79% | 87% |
| wall dist (mean) | 0.8 | 1.7 | 3.1 | 5.3 |
| **% far from ALL walls (>2)** | **0%** | 27% | 60% | 79% |
| steps per food | 4.7 | 7.9 | 11.8 | 17.5 |
| **% states OUTSIDE 6×6 support** | **0%** | **31%** | **71%** | **88%** |

On 6×6 it is **geometrically impossible** to be >2 cells from every wall, yet that "open space" regime is **60% of 16×16 play and 79% of 25×25 play**. Aggregate, 71% of 16×16 and 88% of 25×25 competent play is *outside* the 6×6 training support (food farther than any 6×6 food, or farther from walls than any 6×6 cell). The 6×6 policy was never in those states — not rarely, *never*.

From:

Size-agnostic architecture ≠ size-general behavior

to:

single-size training ≠ coverage of multi-size state distributions

<img src="/snake/arch_final.svg" alt="Final architecture: egocentric 5-channel input (body, head, food, head-relative row/col) into a conv trunk, then attention pool alongside global max-pool, into a dueling head." style="width:100%; max-width:720px; background:#fff; border-radius:8px; padding:12px;" />

Egocentric arch (attention pool + head-relative squashed coords) trained on a curriculum of sizes {6,10,14,18,22} (per-size replay buffers so mixed sizes don't share a ragged batch), evaluated zero-shot:

| board | toward-food% | avg food | region |
|---|---|---|---|
| 6 | 88.5% | 14.7 | train |
| 14 | 93.0% | 31.3 | train |
| 22 | 93.9% | 42.5 | train |
| **32** | 95.6% | 46.1 | **extrap** |
| **48** | 97.4% | 58.0 | **extrap** |
| **64** | 98.0% | 66.5 | **extrap** |
| **100** | 97.6% | 86.5 | **extrap** |

**A single agent, trained only up to 22×22, plays 100×100 zero-shot at 97.6% toward-food (~86 food/game) — a 4.5× extrapolation with NO degradation (it actually improves with size).** Baseline single-size agents were at chance (50%) by board 16.

And "improves with size" isn't magic; bigger boards are easier. More open space means fewer walls to crash into and more room to run: collisions were ~22× rarer at 100×100 than at 6×6, and the snake survived ~90× longer, so a competent agent simply lives longer and eats more. The empty space that broke the naive agent turns out to be the safest place to play, once it's learned how to live there.

Pushing further to a leaner curriculum, I found even {10, 20} curriculum was enough to achieve the same zero shot perf as {6,10,14,18,22}.

We didn't have a learning problem, we had a representation that broke an invariance the task already had.

---

- **Code:** [github.com/Saheb/rl-snake](https://github.com/Saheb/rl-snake)
- **Interactive results & demos:** [saheb.github.io/rl-snake](https://saheb.github.io/rl-snake/)
- **Full write-up** — every probe, ablation, and dead-end: [size_transfer/FINDINGS.md](https://github.com/Saheb/rl-snake/blob/main/size_transfer/FINDINGS.md)


