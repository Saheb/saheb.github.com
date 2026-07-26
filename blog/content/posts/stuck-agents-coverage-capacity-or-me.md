---
title: "Stuck agents: coverage, capacity, or me"
date: 2026-07-26
---

It's one thing to be aware of Sutton's [bitter lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html), quite another to internalise it; and even harder to resist encoding human bias, that we might think of as human knowledge into our agents.

It's not at all hard to notice the beauty of it; it's omnipresent and most of us know that the role of the teacher is not to give the answer, but to teach the student *how to find the answer*.

These abstract ideas were present in some concrete form in my side projects. Across Snake, poker, and Orbit Wars, the thing that mattered most was not scale, but whether the training distribution actually contained the behaviour I wanted. I'll share a few examples.

In [Snake](https://saheb.github.io/blog/posts/lessons-from-my-rl-experiments-with-snake/), the agent wouldn't move closer to food, because it thought surviving in circles and not dying was enough. On running a linear probe on the hidden state I found out that the agent knew where the food was; the direction was present in the representation. So this wasn't the case where model was unable to learn something. Digging deeper into states, I found that agent trained on smaller boards was never exposed to situations that dominated bigger boards: food far away, open space with no wall nearby. Scale or architecture wasn't going to fix this. It needed better exposure: a wider training distribution that included bigger board sizes. An agent trained on mixed board sizes 10 and 20 was able to zero-shot a 100×100 board (97.6% toward-food ~86 food/game; a 5× extrapolation with no degradation; performance actually improves with size).

Snake has no opponent, so the training distribution is whatever sizes it is trained on; the clean case.

In self-play it gets harder, the agent generates its own training data, so it can only learn what its own self play reveals; scale amplifies that but it can't generate what the distribution never contains. When self-play contains the right situations it bootstraps and works wonders; this happened in [Orbit Wars](https://saheb.github.io/blog/posts/failing-at-my-first-kaggle-competition/), the agent trained from 0 to 98% win rate against planner-like agents. On the other hand, in poker it collapsed into a self-referential equilibrium and learned nothing new; agent became aggressive and the self-copy it was playing with kept calling, thereby staying stuck in this cycle, which I'll write up separately.

Pure self play is when you don't use an external teacher. Start from zero. Even in that, you can further break it down, by what input you are giving the agent. Just raw pixels, so it also needs to learn the physics, geometry, rules of the game, everything. Or you are computing the physics, geometry of the game and giving it directly to the agent, so it doesn't spend time learning them and can focus on strategy.

The Orbit Wars pure self-play agent was able to beat a mid-tier planner agent 98% of the time. This was at 57% before two big jumps that happened post-submission. Timeline (future projection) features took it from 57.4% → 74.6%. Removing my own hardcoded gates took 80.5% → 98.0%. It's far from solved though. The same checkpoint was still losing against better agents: 14.1% vs Yijie (rank 13) and 0 of 32 games vs Ender (top 10). Perhaps there are more inductive biases that I need to remove before I can take it further.

Those gates are worth describing, because they're the clearest case of me getting in the agent's way. I'd written rules deciding when a planet was allowed to commit its ships: don't attack unless a single source can afford the capture, don't reinforce unless enemy ships are already inbound. Sensible rules. I wrote them because the agent kept doing silly things.

When I finally measured what they cost, they had deleted 80% of the agent's legal options. The affordability rule blocked 62% of attacks, so two planets could never pincer one target. The threat rule blocked 73% of reinforcements, so moving ships before a threat appeared wasn't a bad move in my agent's world, it wasn't a move at all. Removing them took the legal action space from 20% to 84%.

The part that took me longest to see is that every feature those rules consulted was already an input to the model. I handed it the information and then overruled whatever it concluded. Isaiah (the competition winner) hit the same thing from the other side: he masked out obviously bad moves like firing ships into the sun, and the trained model came out worse. His guess is that being unmasked forced the model to internalise more of the physics.

I wanted the agent to learn these future projections on its own, but I couldn't get that to work. But I was glad to learn Isaiah was able to achieve that using scale. He started at 1–5M params and scaled *because each increase helped*, stopping at 200M only because of the 100MiB submission limit. So capacity paid off, but coupled with 15B steps. Mine was 0.5M and it improved up to max 120M steps before plateauing. I tried a bigger model, 1.5M, that tracked below baseline. Yijie, the rank-13 agent I benchmark against, found the same thing: his best model was 1.2M params, and 4M was worse. I was ready to run it longer, as much as needed, but training plateaued or collapsed before then. I couldn't buy the scaling because the run degenerated first.

Let me reiterate this trade off using snake. Hand-crafted features and reward shaping are the fastest way to get an agent working and see it move in the direction you desired. But they will also make it harder to reason, destabilise training, and become the reason model performance plateaus. When I hand the agent a feature, I've decided what matters, instead of allowing the agent to learn based on the final outcome. Similarly a shaped reward will let the snake circle forever and still look fine on score; or planets will sit idle without attacking because the shaped reward implies that's a good move, and better than losing ships, and risking losing owned planets. Both carry my bias; they are not rules of the game. I've encoded my insight into the agent. But my insight could become a crutch for the agent and interfere with the learning process. The catch is removing these crutches isn't free; they were added to solve problems like sparse rewards and slow learning from raw features. So you need the scale or the exposure to make up for what you took away.

Here's the same lesson from Sutton's bitter lesson post:

> ... this always helps in the short term, and is personally satisfying to the researcher, but in the long run it plateaus and even inhibits further progress

In this paper, [Scaling Laws vs Model Architectures: How does Inductive Bias Influence Scaling?](https://arxiv.org/abs/2207.10551), they find out amongst their ten variants of transformers, vanilla transformers scale best. So far we were referring to the bias in reward modelling and feature engineering, but even the model architecture itself is a collection of inductive bias; each component within it decides what to carry forward and what to strip away. For specific use cases, where compute is limited, it might make sense to have some inductive bias, but as a general principle, one should get it to the bare minimum. As the paper states, novel inductive bias can indeed be quite risky which might explain why most state-of-the-art large language models are based on relatively vanilla architectures.

External opponents are often used to take game play into situations where the agent is forced to learn new strategies. This improves the training distribution coverage, thereby increasing model performance. In Orbit Wars, there were several public agents available that could be used for this purpose, but it didn't help much; it raised the floor and not the ceiling. An opponent can only create the situations it is itself capable of creating, so a mid-tier pool widens your distribution up to mid-tier and no further. On the other hand in poker, the AlphaStar-style league/population is worth exploring; building opponents specifically to exploit the agent's weaknesses.

Like many others, I've asked one LLM to review the work of another, and the combined output is usually better than the first response alone. Post-training already does a version of this automatically. RLHF trains a reward model on human comparisons and then optimises the policy against that model, and Constitutional AI writes the principles down instead of learning them only from preference data. Adversarial versions exist too, like debate and red-teaming.

What connects to my own problem is what the agent measures itself against. In poker each agent's only reference was the other, so both moved together and neither had a reason to improve. In RLHF the reward model stays fixed while the policy keeps moving, which is how reward hacking happens. I don't know what belongs in between, but it's the question I keep coming back to.

### Diagnosis

In all three projects, the thing that moved me forward wasn't a new algorithm — it was being able to look at a stuck agent,  investigate *why* it was stuck, and know which failure mode it was in. When an agent won't do something it should, there are only a few reasons, and each one needs a different fix:

- Can the architecture *express* the action? (capacity)
- Does it have the necessary *data* — has its own training ever put it in that situation? (coverage)
- Is the reward even making the behaviour worth it, or does an easier, do-little policy already score well enough? (the Snake circling for survival points, the planets holding ships instead of attacking)
- Is the signal there but going *unused*? (the Snake case — it knew where the food was and walked away anyway)
- Have we encoded human bias into the features?
- Or is it just a *bug* in the pipeline or the scaffolding? (the boring one, and more common than I'd like)

Getting this attribution wrong is expensive. You scale when you should have fixed coverage; you re-architect when it was a masking bug; you burn a GPU run answering a question a cheap probe could have answered first.

So ask small, sharp questions and watch the agent directly to answer them.

Why is it sitting on a huge fleet and not attacking? Why are two of my own planets attacking the same neutral? Why is the poker agent just calling and raising forever?

Take the first one. My agent commits half a garrison where the top agents commit everything. I'd already scoped the fix: a third action between doing nothing and going all in, a new action head, a full retrain. Thirty hours of GPU.

Before starting I spent twenty minutes counting what a top-10 agent actually does. It goes all in on 97.3% of its launches, and 97.7% when playing a copy of itself. A learned middle is worth at most 3% of what it does. The experiment died before it started.

A broken metric cost me longer. I was tracking how often my agent lost planets it had just captured, as a measure of whether it could hold ground. Against the top-10 agent the number was 0.99, which looked like a devastating diagnosis. It was arithmetic. That agent wipes me off the board in 100% of games, so every capture I make is lost by construction, and the metric could not have returned anything else. It only means something against opponents I sometimes beat.

Evals tell you the agent is stuck; watching and probing tell you why. The Snake win rate looked fine while the agent circled forever; what exposed that was one minimal, high-signal metric: the fraction of moves that went *toward* the food. A few highly discriminating signals beat a dashboard of them.

### Where this leaves me

The thread through all three is the same: an agent learns what its training distribution contains, and in self-play it *is* the distribution; it can only learn from the situations its own play produces. Scale amplifies that; it doesn't create what was never there. When the distribution covers the right situations, self-play bootstraps into something strong on its own. When it doesn't, the agent either never learns it (Snake on bigger boards) or settles into a comfortable self-referential equilibrium (poker), and no amount of scale moves it.

Three probes did more for me than any algorithm change, and they share a shape. Each cost under an hour, each ran before a training run rather than after, and each killed something I believed:

- Count what a strong agent actually does, before building the capability you assume it needs.
- Measure how much of the action space your own rules removed.
- Check whether your metric can return more than one value.

The questions I keep coming back to, and want to spend more time on:

- Can we tell *ahead of time*, cheaply, whether a plateau is coverage, capacity, or a bug? The three probes above worked, but I only thought to run each one *after* I was already stuck. I don't have the version I can run before committing to a large run, and I think a lot of it can be made empirical.
- Self-play bootstrapped to 98% in one game and settled into a dead equilibrium in another. What decides which one you get? The known fix is a league with exploiters trained against your current agent, but that's a remedy, not a predictor. I'd want to know which way it's going to go before spending the compute, not after.
- Snake showed a model represented the right thing and still didn't use it. I found that with a linear probe in an afternoon, and it changed what I thought the problem was. The version of that question I can't answer is what it looks like in a language model: whether the activations carry something the outputs don't act on, and how to tell a model that doesn't know from one that knows and doesn't use it. That's where probing work sits and I don't know how you'd measure it cleanly at scale.

None of these are new problems. But I've now hit them, concretely, in three different games, and I'd rather work on making these decisions empirical than keep making them on vibes.