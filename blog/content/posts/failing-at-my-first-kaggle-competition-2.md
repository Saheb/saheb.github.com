---
title: "On failing at my first Kaggle competition (2/n)"
date: 2026-06-26
---

In the first part, we discussed self play and the equilibrium our agent gets stuck in.

In this part, we will talk about features that model takes as input, and how model uses them to learn strategies.

Theme and tone will be the same, more on what not to do.

In Orbit Wars, features fell into 4 categories, planets, fleets, global, and pairwise features.

Planet features will tell the model everything about the planet, its position, owner, radius, production, orbit info, capture cost, distance to nearest owned planet, etc.

Similarly for fleet, position, owner, angle, number of ships, speed of travel, distance to sun, fleet destination, ETA, etc.

Global features were game related, angular velocity of moving planets, economy stats, enemy ships split (on_planets / in fleet)

Entire game was fully observable, so complete information was available to all agents.

Now, when we start we have 1 planet, so we can send fleets from it to some target planet once it has enough ships. Let’s call this combination of source and target a slot. As we capture more planets, our slots increase. So each slot can fire and capture more planets simultaneously.

Features pertaining to slot are pairwise features, that are keyed on target-source pair.

Have I bored you already? Well, then you are like me who wants to just get on with the features so you can get on to the more interesting phase.

But, that’s not what you should do.

Otherwise, you will come back to it, when you conclude model can’t learn this because it’s too hard for it, and you will redo your features.

Like I did a few times during the course of this competition.

It’s expensive as well. You need to start over. Not always.

And error prone — unless you have proper workflows in places to add new features, migrate them or activate them so they can be easily used with older checkpoints.

An example: you can give model the coordinates, and let it learn the math and physics of the environment. 

It’s possible, but isn’t necessary. It’s also hard on the model, and makes its learning slower. Instead do the math, precompute the features, and give that as input to the model.

Another example: you feature incoming threat, the enemy’s fleet coming to capture your planet or a neutral planet. Later you figure out that model knows the incoming fleet is coming, but doesn’t know when. The threat features don’t provide ETA. You might have provided that information in some other feature, but that expects the model to figure that out and do non-trivial math. Sometimes it can do that, sometimes it can’t. I don’t yet know how to figure this out at feature engineering time. A comment from a fellow Kaggler was to just give it all the features, you can’t know which will be useful, which it will ignore because they’re redundant (one way to figure this out is to shuffle the values of a feature and see if it changes the output; if it doesn’t, then it’s not that important — this trick is called permutation importance).

How does the model learn which features are important? How much weight to give to each feature?

That’s the training magic.

It runs a forward pass, and based on the result, optimizes the weight (and bias).

And keeps iterating on it and keep reducing the loss — the difference between predicted value and actual value.

This is the training loop.

During training, you calculate validation loss, to ensure loss is reducing

And after the training run, you evaluate against test dataset to ensure its performance has improved and hasn’t degraded.

Model is the main box, the box where magic really happens, also sometimes referred to as the black box. 

Because you don’t really know what’s happening. You can peek and understand bits of it, but not really all of it.

Entity transformer was the model I used, as I had mentioned in previous post, I just went with a suggestion by an experienced Kaggler, who definitely knew more than I did, and his rank was in top ten, so it was easy to trust his judgement.

Last year, I had spent some time writing a tiny transformer from scratch, to understand how modern LLMs really work. It’s from the Attention is All you Need paper that began the LLM revolution, as transformer architecture allows you to scale, which wasn’t possible in the models that came before it. If you plan to dig into transformer, don’t directly jump to it. Instead go through the journey that made it possible, the neural networks that came before it (AlexNet, ConvNet, RNNs, LSTM); that way you will be able to understand it better and also get a holistic understanding of the journey. Usually a limitation in one model/architecture is fixed in the future models. So it came into being by trying to remove the sequential nature of RNNs, that prevented it from scaling.

Transformer is a neural network, input will be the features I spoke about and output will be the action heads, i.e. fire, ship, and target heads.

Fire head — whether or not to fire.

Ship head — how many ships to send.

Target head — which planet to send the ships to.

Conceptually, this is simple. Something you can reason with. Gaps and flaws come out later, when you don’t see the behavior you want.

The boxes are in place, you run the model through the training data and it will tune its weights, model will be trained, and ready to play. No if else loops, planning, etc. That’s the beauty and magic of it. We lose visibility and reasoning ability that we are so used to in the deterministic world. Let’s dive in.

First thing to wonder is, whether these heads should be independent?

Do they have a causal or dependent relationship?

You can observe the game and figure out that they are dependent, fire head needs to know which planet target head has decided. Similarly ship head needs to know which planet target head has decided.
I kept them truly independent, before figuring out that fire and ship head needs to be conditioned on target. Target comes first.

<img src="/orbit-wars/model-heads.svg" alt="Features flow into the entity transformer, which feeds three action heads; the target head decides first and conditions the fire and ship heads." style="width:100%; max-width:760px;" />


All heads are slot based, so for each combination of src and target planet they emit one output.

Having done this, I observed, multiple owned planets were targeting the same neutral planet, and thereby double ships are reaching the planet; it’s getting captured but it’s inefficient. Ships that can be used to attack or reinforce elsewhere, are being wasted on the same planet. Why would that be?

Because we haven’t accounted for friendly fleet in our capture floor feature, so we go and fix that feature and retrain. And hope that it’s working better now.

It did, but now, the enemy is sending a huge fleet to take over, whereas you are only sending bare minimum. Now what to do? You already had added enemy fleet in the feature.

Digging deeper you find out none of the planets have that many ships to overcome the incoming enemy fleet. 

So you need to coordinate the total from multiple planets — one way to achieve this is staged reinforcement. You don’t coordinate, but signal reaches via global state to other friendly planet of yours and thereby a combined total reaches the target that was outmassed by the enemy.

In the phase 1, I had masked the owned planets, so reinforcement was not possible at all. Masking is a technique where you disable a subset targets, that are illegal according to the game, or not right according to strategy. Like don’t target a planet that has sun in the path.

Having done that, the enemy was still heavy on me.

What was I missing?

You can’t save all planets, you need to stop spraying tiny fleets to every planet, you need to decide which planets are worth saving, and which are hopeless and you need to abandon them.
How was the producer like agent so precise in their attacks?

Because it looked 18 steps ahead, projected the enemy pressure and everything and then planned their attacks with the precise fleet and accurate timing of it all.

I couldn’t beat it, I felt like giving up many times.

But somehow I kept going.

Circling and fixing the flaws, learning to debug the transformer, so all of it felt very satisfying, but not progressing on the win rate made me feel incompetent.

Here are some mistakes worth noting:

I didn’t play the game enough and wasn’t giving replays the attention they deserved. That surfaced edge cases, and fundamental flaws in strategy and features. I should have done that sooner and regularly, instead of once in a while. 

It’s very important to understand why it’s not able to win

Or not able to execute the strategy you desire

Think, as a human, what would you do differently in order to win from here

**If you can’t figure it out yourself, then it’s not fair to expect agent to learn it**

So you need to know it first

Later it will come with novel strategies that human brain can’t fathom or compute, but before it can do all that, it needs to learn the fundamentals well, that is your job to ensure it can do that. You need to provide it with the tools to be able to learn.

Fixing symptom, not the root cause.

I spend a lot of time fixing certain symptom, without fully understanding the root cause.
e.g. fire head is firing less, so let’s tweak the threshold or reward model so it has more incentive to be aggressive.

But why wouldn’t it fire more? Why does it have low probability for firing? 
Because it wasn’t getting the signal… the gradient that firing more results in more win. If firing more results in loss, it won’t build that behavior. Simple.

This skill is crucial to have, that I have barely learned so far.

**To figure out what’s not working in training, is it the gradient that is missing or features that are missing, or some hyper parameter, or if there is a bug messing up everything else.**

There were some ideas that fascinated me big time, but I couldn’t explore it fully for they required starting again from scratch. I was tempted to start over many times for there was no progress. But even then it was critical to make this decision using replay data that was available.

Like wouldn’t having a joint autoregressive head be better than having three independent heads?

This came up when I was questioning whether architecture of the model can even express the coordinated play I am expecting of it?

This joint head felt like the right abstraction, as all heads and decisions were joint. Fire N ships to this planet, fire Total minus N to another planet; or some of it to reinforce, etc.

But checking out replays of the best agent, the metrics showed that they barely do this style of coordination, it wasn’t really required to have that kind of precision in timing. Staged attacks and reinforcement were enough to get to the top.

Another idea was to have planner like features that would plan waves of attacks and provide this as features; this was phase 5 that I planned, spec-ed and then abandoned. 

Because it was likely it would result in similar Nash equilibrium.

All of this back and forth, because I wasn’t confident with the root cause. Little did I know, outmassing — the metric I was relying on so much — was a common way of winning, even in the games that I won against producer-planner like agents, they’d be outmassed just as much, like 98% of the time. And I learned that **the metric we were chasing was a ghost.**

In the next post, we will dig into credit assignment and reward hacking.