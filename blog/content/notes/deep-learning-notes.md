---
title: "Deep Learning Notes"
date: 2026-07-22
---

> **Every architectural layer is a compression operator. Before using it, ask what information it intentionally throws away, what assumptions justify throwing it away, and whether those assumptions still hold under the distribution shifts you care about.**

This principle applies far beyond pooling—to convolutions, transformers, graph neural networks, positional encodings, normalization layers, residual connections, and even loss functions. It's a durable way to think about architecture design rather than memorizing which component is *best*.

---

## Architectural choices are hypotheses about the problem

Every architectural choice encodes an assumption about the world.

The question is **not**

> *Which operator is better?*

The question is

> **What invariance does this operator assume?**

If the assumption matches the environment, the architecture generalizes.

If it doesn't, the architecture quietly destroys information that later turns out to matter.

---

# Think in terms of "What gets averaged away?"

Whenever I see an aggregation operator, I should immediately ask:

> **What distinctions is this operator intentionally throwing away?**

---

## Global Average Pooling

### Assumption

> Every spatial location contributes equally.

### Computes

\[
h = \frac{1}{N}\sum_{i=1}^{N} x_i
\]

### Preserves

- Average presence
- Translation invariance

### Discards

- Count
- Sparsity
- Exact location
- Relative magnitude when irrelevant regions grow

### Works well when

- Object density is stable
- Every region is equally meaningful
- Input size is fixed
- Signal is naturally distributed over the whole image

### Fails when

- Relevant signal occupies a tiny fraction of the input
- Environment size changes
- Empty space dominates
- Signal magnitude itself carries meaning

---

## Global Max Pooling

### Assumption

> Presence matters; frequency does not.

### Computes

\[
h = \max_i x_i
\]

### Preserves

- Strongest activation
- Existence of a feature
- Local detectors

### Discards

- Density
- Multiplicity
- Average strength

### Works well for

- Object detection
- "Danger exists?"
- "Does this feature appear anywhere?"

---

## Attention Pooling

### Assumption

> Not every location matters equally.

Instead of averaging uniformly,

\[
h = \frac{1}{N}\sum_i x_i,
\]

the network learns

\[
h=\sum_i \alpha_i x_i,
\]

where

\[
\alpha_i=\frac{\exp(s_i)}
{\sum_j \exp(s_j)}.
\]

The weights are learned from the input itself.

### Preserves

- Relevant regions
- Informative objects
- Scale of important features

### Ignores

- Irrelevant regions
- Background
- Empty space

### Costs

- More parameters
- More compute
- Greater overfitting risk
- More optimization complexity

---

# Orbit Wars lesson

Initially I thought

> Average pooling should generalize because it removes dependence on board size.

The experiments revealed something subtler.

Average pooling **did not destroy the information.**

The representation remained linearly decodable.

Instead, average pooling changed the **relative scale of competing signals.**

Specifically,

- Danger (local, max-pooled) remained essentially constant.
- Food direction (global, substantially average-pooled) shrank with board size.

The policy never forgot where food was.

It simply stopped caring enough.

That distinction only became visible after decomposing the advantage margins.

---

# Local-box oracle vs Attention Pooling

The local-box oracle effectively said

> Only aggregate over the region that matters.

Attention pooling learns exactly this idea instead of hard-coding it.

Local-box pooling can be written as

\[
h=\sum_i w_i x_i,
\]

where

\[
w_i=
\begin{cases}
1/k, & \text{inside box} \\
0, & \text{outside}
\end{cases}
\]

Attention pooling has exactly the same form,

\[
h=\sum_i \alpha_i x_i,
\]

except the weights are learned rather than fixed.

This is why attention pooling can be viewed as a learned version of the oracle.

Crucially, it can assign almost zero weight to feature vectors coming from uninformative regions, even if those activations are positive.

Unlike average pooling, adding more empty space does not automatically dilute the representation.

---

# Better design question

Don't ask

> **Should I use attention?**

Instead ask

> **Which information should survive aggregation?**

| Situation | Appropriate operator |
|-----------|----------------------|
| Every location equally informative | Average pooling |
| Only existence matters | Max pooling |
| Only a few locations matter | Attention pooling |
| Local neighborhood matters | Local pooling |
| Relationships matter | Graph attention / Transformer |

---

# A mental checklist

Whenever introducing an architectural operator, ask:

1. What invariance am I assuming?
2. What information is intentionally discarded?
3. Does the discarded information grow with scale?
4. Could competing signals scale differently after this operator?
5. If the environment doubled in size, what happens to each signal?
6. Is the downstream head implicitly calibrated to the ratio between those signals?
7. Under the distribution shifts I care about, will those assumptions still hold?

If I can't answer these questions, I probably don't understand the operator yet.

---

# General Principle

The best architectures do **not** preserve all information.

They preserve **exactly the information the task needs**, while discarding nuisance variation.

Generalization is not about choosing the most expressive architecture.

It is about matching the architecture's inductive bias to the structure of the problem.

---

# Personal takeaway

Tiny architectural decisions are rarely "just implementation details."

Average pooling, max pooling, attention, convolutions, positional encodings, normalization layers—each one quietly decides **what information survives** to the next layer.

When a model generalizes or fails under distribution shift, the reason is often hidden in these assumptions.

The goal isn't to memorize which operator is best.

The goal is to develop the instinct to ask:

> **What information is this layer preserving, what is it throwing away, and are those the right assumptions for my problem?**