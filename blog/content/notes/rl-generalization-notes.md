---
title: "RL Generalization — Revision Notes"
date: 2026-07-20
---


Source: Kirk et al. 2023 ZSG survey (arXiv 2111.09794) + working sessions, July 2026.

## 1. The problem in one sentence

Train a policy on a finite sample of contexts drawn from p(c); **freeze it**; measure expected
return on contexts never trained on. Zero-shot = **no adaptation at test time** (no gradient
updates, no practice episodes — nothing to do with "one attempt").

- **Generalization gap** = train return − test return. Always report **two numbers**: gap
  (overfitting) AND absolute test return (competence). Random agent: gap ≈ 0, useless.
- **Interpolation** = test contexts inside the convex hull of training values. **Extrapolation**
  = outside. **Combinatorial** = novel combos of seen factor values. Interpolation is a
  favorable prior, not a proof — the test context was still never seen.
- Difficulty order (Kirk §4): interpolation < combinatorial < extrapolation. Extrapolation:
  "unlikely to occur at all with standard RL methods."
- Why zero-shot matters: the only deployment workflow that exists — train in sim/offline,
  freeze, deploy, must work immediately. Every LLM deployment is zero-shot policy transfer.

## 2. CMDP formalism

Tuple: S' (underlying state), A, O, phi (observation fn), T, R, C, p(c), p(s'|c).
A CMDP = a POMDP with state (s', c): sample c ~ p(c) per episode, then s' ~ p(s'|c).

- Context is **frozen within an episode** (T assigns zero probability to any c change) —
  that's what makes it context and not state. Resamples only between episodes.
- Context can parameterize the **functions** (T, R, phi, p(s'|c)) but ⚠ **never the spaces**
  (S', A, O). That's why starpilot and coinrun are separate CMDPs, not two contexts.
- **Observed context** (ID in the observation) → can be an MDP; necessary but not sufficient
  for full observability. **Unobserved** → genuine POMDP even if s' is fully visible.
- The whole train/test story lives in **one object: p(c)**.

**Discrimination test** (which symbol does an intervention touch):
1. Changes *which circumstance gets dealt, or how often*? → p(c)
2. Given the circumstance, changes *how the board starts*? → p(s'|c)
3. Changes *what happens as you act*? → T (R if scoring, phi if what the agent sees)

**Promotion rule:** any T- or p(s'|c)-level knob becomes a p(c)-level knob the moment you
randomize it per episode. That sentence IS domain randomization.

Orbit Wars mapping: **the opponent is the context** (folded into T — survey §6.4 says this
verbatim). Pool sampling = p(c). SSDR = p(s'|c). First-strike reward = R. Timeline features
= phi. 2× ship speed = T.

## 3. Markov ladder

**Markov = memory property, not visibility.** State is Markov ⇔ history adds nothing given
the current state. Separate axis: does the agent *see* the state?

| | hidden state? | moves? | optimal policy needs |
|---|---|---|---|
| MDP | none | — | current state only (reactive) |
| POMDP | arbitrary | every step | memory / belief tracking |
| CMDP (c unobserved) | just c | frozen | belief about c, sharpening within episode |

- "Non-Markov" is never a verdict, it's a **to-do list**: augment the state (velocity;
  chess: castling rights, repetition count, side-to-move) and it's an MDP again.
  Markov-ness is a property of the *representation*, not the world.
- Every POMDP is an MDP over **belief states**. A belief is a function of history.
- CMDP: the *world* is Markov in (s', c), but the agent's best response is **non-Markovian**
  — observations leak c only gradually. Markovian problem, non-Markovian solution.
- Definition 4 types the policy pi: H[O,A] → A (history in) — *permits* memory because
  reactive policies can be strictly worse under unobserved context. Survey §5.2.4 builds
  the whole online-adaptation method family on this clause.
- **Parameter sharing forces generalization** (lookup table = independent cells, network =
  shared weights) — and its evil twin is **interference** (updates corrupting other states).

## 4. Epistemic POMDP — the deep "why RL generalization is hard"

Each training context can be fully observed, but at test time the context is a latent
variable → the problem *becomes* a POMDP. Consequence: optimal behavior under context
uncertainty (information-gathering, hedging, stochasticity) is **strictly suboptimal in every
single training context** — so maximizing training return optimizes a *different objective*
than test performance. Not a data-quantity problem; scale on the wrong objective doesn't fix it.

- **Capacity vs incentive:** memory (RNN) is the capacity for belief-tracking; diverse p(c)
  is the incentive. Either alone fails. Audit any memory architecture with: *what in the
  training distribution makes history worth conditioning on?* If nothing — decoration.
- **Two ways to kill inference** (same casualty): leak the context through phi (opponent-ID
  feature → lookup-table of specialists, no inference machinery built), or collapse p(c) to
  a point (pure self-play: the opponent is always you, nothing to infer, ever). Machinery
  never needed is never built.
- Pool diversity is deeper than coverage: it *creates the training pressure* for inference
  to exist.

## 5. Structural assumptions — generalization's collateral

No free lunch: extrapolation without shared structure is impossible; every method secretly
bets on some structure. The audit nobody does: name the bet, check the benchmark has it.

- **Block MDP:** small latent state wears a high-dimensional costume; observation determines
  latent uniquely (no aliasing — memory not needed, decoder unknown). Payoff: learn the
  decoder, discard nuisance → costume-only variation is free.
- **Factored MDP:** state decomposes into factors with sparse local dynamics. Payoff:
  learn local rules → novel combinations of familiar values handled correctly (each rule
  still in-distribution). "CMDP = factored MDP with 2 factors" is true but content-free;
  value appears only with finer factorization.
- **Mnemonic: block = ignore what doesn't matter; factored = recombine what does.**
  Invariance vs compositionality. Backgrounds → block bet. Layouts → factored bet.
- **Architectures are structural assumptions in disguise.** ConvNet = spatial locality.
  Entity transformer = object factorization (why it survives new maps / variable planet
  counts). MLP on flattened board: size-10 test isn't hard, it's *ill-typed*. Architecture
  makes generalization **representable**; the training distribution makes it **learned**.
- **Three-case reflex** for "should generalize to X": (1) new combination of in-range values
  → factored bet covers it; (2) out-of-range value on a known factor → extrapolation,
  undefined behavior, verify empirically; (3) property not in the features at all → phi
  misspecified, unrepresentable forever, nothing downstream fixes it.

## 6. Latent spaces

Two meanings — always know which is in play: (1) the **world's** latent state (hidden cause
of observations; exists regardless of models); (2) a **model's** latent representation
(invented internal coordinates). Representation learning succeeds when (2) recovers (1).

- **The law: a latent space encodes exactly what its training objective pays for.**
  Audit template: *latent shaped by [objective] → pays for [X] → test variation lives in
  [X / not-X] → variation is [kept / discarded] → generalization [hurt / helped].*
- Autoencoder gotcha: reconstruction pays by pixel *area* → background dominates the latent
  budget. It's a background-preservation machine. (Two objectives in the room — the RL task
  never touches the encoder; audit the one that trains it.)
- **Good latent geometry prices by consequence, not entry count**: stretch tiny observation
  differences when futures diverge (in-flight fleet), collapse huge ones when futures agree
  (backgrounds). Bisimulation = this made into a metric (same rewards + same futures ⇒ same
  point). Timeline features = the stretch, hand-implemented upstream of the network.
- JEPA in one line: predict latent-from-latent so unpredictable nuisance never enters the
  loss.

## 7. Methods map (survey §5)

Three buckets (my framing; the survey slices differently — both are lenses, not truths):
1. **Change the data** — widen p(c): domain randomization, procedural generation,
  environment generation (POET/PAIRED/PLR), opponent pools. Behavior may *differ* per context.
2. **Change the function** — invariance/inductive bias: augmentation-with-consistency,
  regularization, bottlenecks, bisimulation losses, architectures. Asserts behavior must be
  *identical* across variants.
3. **Change the optimization target** — robust/worst-case RL, ensembles, belief-conditioned,
  adaptation. Tell: willing to *lower average training return* to buy worst-case/uncertain
  performance. NOT reward shaping (shaping edits R to fix credit assignment, still maximizes
  average training return).

- Augmentation straddles 1 and 2 (survey says so explicitly). It is **designer-certified
  invariance** — powerful when the certificate is true, poisonous when false (jittering
  garrison counts would certify a lie).
- **Survey verdicts:** near page-tie between buckets 1 and 2; by method count invariance/
  adaptation is the biggest population. Cross-cutting: most methods are *loss-function
  tweaks*; **architecture-level biases and model-based RL are the two named under-explored
  directions**. Robust RL: one thin paragraph. LEEP: "no direct comparison." →
  **most principled ≠ best evidenced** (fields harvest low fruit first).
- **Extrapolation confession:** standard methods won't do it; needs targeted inductive
  biases + online adaptation + prior knowledge/transfer. No general-purpose extrapolator
  exists (No Free Lunch).
- **Streetlight critique:** methods cluster on visual nuisance because supervised-learning
  tricks transfer there; dynamics/state/reward variation equally important, less studied.
  Benchmark evidence is circular: strong numbers on benchmarks built to measure what the
  method fixes.

## 8. Old vs new meaning of "generalization in RL"

- **Old (within-MDP):** function approximation interpolating across unvisited states of one
  environment — instrumental, no train/test split (exploration decides what you see).
- **New (across-MDP):** held-out contexts, frozen policy — generalization as the objective,
  with an **explicit controlled split** (the one ingredient that makes the supervised-learning
  mirror hold). The boundary between the two is a modeling choice (fold contexts into state
  and they merge); what's genuinely new is the measurement protocol.
- Both run simultaneously in any real system (entity transformer interpolates board states
  within-MDP; Ajay/Yijie panel measures across-MDP).

## 9. Reading reflexes (transferable to any paper)

- **Predict before reading results**, then score yourself — prediction failure is the
  fastest leak detector.
- Separate **inherited vs contributed** (Kirk didn't invent POMDPs or CMDPs; contribution =
  the framing that makes the literature snap together).
- For any method: which symbol does it touch / what structure does it bet on / capacity or
  incentive / would it move MY problem?
- A rate compared across different opponents/contexts is confounded — compare like-for-like.
- "More budget" is not an explanation for a flat curve — check the curve.
