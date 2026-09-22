---
title: "RL Fundamentals"
date: 2026-09-22
---

## Value functions: V, Q, and advantage

**One-line distinction:** `V^π(s)` values a **state**; `Q^π(s,a)` values taking an
**action in that state**. Both assume that the policy `π` is followed thereafter.

Let the discounted return from time `t` be:

```text
G_t = R_{t+1} + γR_{t+2} + γ²R_{t+3} + ...
```

Then:

```text
V^π(s) = E_π[G_t | S_t = s]
```

asks: **How good is it to be in state `s` under policy `π`?**

```text
Q^π(s,a) = E_π[G_t | S_t = s, A_t = a]
```

asks: **How good is it to take action `a` in state `s`, then follow `π`?**

They are connected by

```text
V^π(s) = Σ_a π(a | s) Q^π(s,a)
```

So `V^π(s)` is the policy-weighted average of the available action values. The
**advantage** measures an action relative to that baseline:

```text
A^π(s,a) = Q^π(s,a) - V^π(s)
```

- `A > 0`: better than the policy's average action in this state.
- `A < 0`: worse than average.
- Averaged over actions sampled from `π`, the advantage is zero.

### Bellman view

Both definitions are recursive:

```text
Q^π(s,a) = E[R_{t+1} + γV^π(S_{t+1}) | S_t = s, A_t = a]
```

Take an action, receive immediate reward, then value what follows.

### Why these algorithms exist

```text
Value-based:       Q-learning → DQN
Policy gradient:   REINFORCE  → TRPO → PPO
Off-policy actor–critic for continuous control: DDPG → TD3 / SAC
```

This is a map of the main ideas, not a strict family tree: later algorithms often
combine ideas from several branches.

#### Q-learning: learn which action is best

Q-learning learns `Q*(s,a)` directly. Its target says: take the observed reward,
then add the value of the best action available in the next state.

```text
target = r + γ max_a' Q(s',a')
```

The update moves `Q(s,a)` towards that target. Because the target uses the greedy
next action even if the behaviour policy explored, Q-learning is **off-policy**.

**Limitation:** a table does not scale to huge or continuous state spaces.

#### DQN: replace the Q-table with a neural network

DQN approximates `Q(s,a)` with a neural network. Two stabilizers make this practical:

- a **replay buffer** breaks correlations by sampling old transitions;
- a **target network** keeps the bootstrap target fixed for a while.

The loss is the squared temporal-difference error:

```text
L(θ) = [r + γ max_a' Q_target(s',a') - Q_θ(s,a)]²
```

**Limitation:** finding `argmax_a Q(s,a)` is easy for a small discrete action set,
but generally intractable over continuous actions.

#### REINFORCE: optimize the policy directly

REINFORCE represents `π_θ(a | s)` and increases the probability of sampled actions
in proportion to their observed return:

```text
gradient ≈ Σ_t G_t ∇_θ log π_θ(a_t | s_t)
```

It does not learn a Q-function, but `G_t` is a noisy sample of the action's value.

**Limitation:** Monte Carlo returns have high variance. Updates can also move the
policy too far because the objective contains no explicit step-size notion in policy
space.

#### Actor–critic: use a critic to reduce variance

The actor updates the policy; the critic learns a value function. Instead of weighting
the policy gradient with the raw return, use an advantage estimate:

```text
gradient ≈ Σ_t Â_t ∇_θ log π_θ(a_t | s_t)
```

The critic reduces variance, usually at the cost of some bias. PPO and SAC are both
actor–critic methods, but they solve different problems.

#### TRPO: constrain how much the policy changes

TRPO approximately maximizes policy improvement subject to a KL-divergence constraint:

```text
maximize surrogate objective
subject to average KL(π_old || π_new) ≤ δ
```

This motivates conservative policy updates and comes with a theoretical improvement
bound under assumptions.

**Limitation:** the constrained, second-order optimization is relatively complicated
and expensive.

#### PPO: approximate the trust region with a simple objective

PPO reuses data collected by `π_old`. The probability ratio measures how much the new
policy changes the probability of the sampled action:

```text
r_t(θ) = π_θ(a_t | s_t) / π_old(a_t | s_t)
```

Its clipped objective removes the incentive to push that ratio beyond
`[1 - ε, 1 + ε]` when doing so would improve the objective:

```text
L_clip = E[min(r_t Â_t, clip(r_t, 1-ε, 1+ε) Â_t)]
```

**Key nuance:** clipping is a heuristic, not a hard constraint. The final policy can
still move by more than `ε`, and PPO does not inherit TRPO's guarantee. Its appeal is
that it is simple, stable in practice, and works with ordinary first-order optimizers.

#### DDPG: make Q-learning usable for continuous actions

DDPG learns a deterministic actor `μ(s)` so it does not need to solve a continuous
`argmax` every time:

```text
actor chooses a = μ(s)
critic learns Q(s,a)
actor updates μ to increase Q(s, μ(s))
```

It is off-policy and sample-efficient, but can be brittle and exploit errors in its
critic. TD3 directly targets this overestimation and instability.

#### SAC: off-policy control with entropy

SAC learns Q-critics and a stochastic actor while rewarding both return and entropy:

```text
objective = E[Σ_t r_t + α H(π(· | s_t))]
```

Entropy discourages premature collapse to one action and improves exploration. SAC is
usually much more sample-efficient than on-policy PPO for continuous control, although
which is more stable depends on the task and implementation.

### Interview answer

> `V^π(s)` is the expected return from a state when I follow `π`.
> `Q^π(s,a)` conditions on taking a particular action first and then following
> `π`. Their difference, `A^π(s,a) = Q^π(s,a) - V^π(s)`, tells me whether
> that action is better or worse than the policy's average action in that state.

### Do not say

- “`Q(s,a)` is the value of the next state.” It includes the immediate reward and
  all discounted future rewards.
- “PPO's critic computes Q.” Standard PPO critics usually predict `V(s)`.
- “DQN always chooses the highest-Q action.” It is commonly exploratory during
  training and greedy at evaluation.
