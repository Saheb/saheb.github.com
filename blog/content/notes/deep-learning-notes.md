> Every architectural layer is a compression operator. Before using it, ask what information it intentionally throws away, what assumptions justify throwing it away, and whether those assumptions still hold under the distribution shifts you care about.

That's a principle that applies far beyond pooling; to convolutions, transformers, graph neural networks, positional encodings, normalization layers, residual connections, and even loss functions. It's a durable way to think about architecture design rather than memorizing which component is *best*.

Architectural choices are hypotheses about the invariances of the problem.

They often look like implementation details—average pool vs. max pool, CNN vs. attention, absolute vs. relative position—but they're really statements about **what information should be preserved and what should be discarded**.

---

**Architectural operators are inductive biases, not implementation details**

Every architectural choice encodes an assumption about the world.

The question is not

"Which operator is better?"

The question is

"What invariance does this operator assume?"

If the assumption matches the environment, the architecture generalizes.
If it doesn't, the architecture quietly destroys information that later turns out to matter.

--- 

**Think in terms of "what gets averaged away?"**

Whenever I see an aggregation operator, I should immediately ask

What distinctions is this operator intentionally throwing away?

Examples:

Global Average Pooling

Assumption:

Every spatial location contributes equally.

Preserves

average presence
translation invariance

Destroys

count
sparsity
exact location
signal magnitude when irrelevant regions grow

Works well when

object density is stable
every region is equally meaningful
board/image size is fixed

Fails when

relevant signal occupies tiny regions
environment size changes
empty space dominates

---

**Global Max Pooling**

Assumption:

Presence matters; frequency doesn't.

Preserves

strongest activation
local detectors
existence

Destroys

density
multiplicity
averages

Works well for

object detection
danger exists?
feature exists anywhere?

---

Attention Pooling

Assumption:

Not every location matters equally.

Learns

h=
i
∑
	​

α
i
	​

x
i
	​


instead of

h=
N
1
	​

i
∑
	​

x
i
	​


Preserves

relevant regions
ignores irrelevant regions

Costs

more parameters
more compute
can overfit if relevance is unstable

---

I used to think

average pooling should generalize because it removes dependence on board size.

Experiment says something subtler.

Average pooling made the representation decodable.

It failed because it changed the relative scale of competing features.

Specifically,

danger (local, max-pooled) stayed constant
food (global, avg-pooled) shrank

The policy never forgot where food was.

It simply stopped caring enough.

That distinction only became obvious after decomposing the advantage margins.

---

Better design question

Don't ask

Should I use attention?

Ask

Which information should survive aggregation?

Examples

If relevance is

uniform → average pooling

If existence matters

max pooling

If only a few locations matter

attention pooling

If neighborhood matters

local pooling

If relationships matter

graph/transformer attention

---

A mental checklist

Whenever introducing an architectural operator, ask:

What invariance am I assuming?
What information is discarded?
Does the discarded information grow with scale?
Could two competing signals scale differently after this operator?
If the environment doubled in size, what happens to each signal's magnitude?
Could the downstream head rely on the ratio between those signals?

If I can't answer these questions, I probably don't understand the operator yet.

---

General principle

The best architectures don't preserve all information.

They preserve exactly the information the task needs, while discarding nuisance variation.

Generalization isn't about using the most expressive operator.

It's about matching the operator's inductive bias to the problem's structure.