---
title: "On failing at my first Kaggle competition (3/n)"
date: 2026-06-27
---

In the second part we talked about transformer heads and features.

In this part, we will dive into credit assignment and reward hacking problems that I faced.

Giving +1 reward when you win a game and -1 when you lose is clean and eventually you want to reach that state where it suffices but before you get there, you need more signals, i.e. dense rewards to teach the agent the behavior you want.

The problem with dense rewards is that it’s hard to get it right — it can either be exploited, or has adverse side effect that will impact the overall performance.

Let’s add more context so you can engage with the problem.

In a 500/N step game, how will you know the move at step 3 was beneficial for the overall outcome of the game or not?

In order for reward to work in RL, credit assignment needs to work as well. How to attribute credit correctly is the problem.

With sparse rewards like +1/-1, it’s hard to do credit assignment correctly, therefore you need dense rewards to drive the behavior and develop the traits you want in your agent.

If you value capturing a planet early, you can give additional reward for captures in steps less than 50; thinking along these lines, you’d say we should value higher production planets over lower production so lets give it some reward so it knows to rank higher production planets above lower ones. As you can imagine this line of thinking is error prone and also feels more like modeling heuristics — not via if-else loops but reward models.

You might wonder wasn’t the entire idea of RL and self play was that agent figures this out on its own and we don’t have to hard code these values?

And also the obvious question, how the hell can we weight a better long term move in comparison to greedy short term move? For example abandoning a planet is better for the overall goal of the team, but the nearby planet might still send all its ships/garrison to save the planet if you reward saving highly.

And what about capturing a planet at step 5 versus step 50 should have different rewards right?

Yes, these temporal rewards are managed via discounted rewards, bellman equations solve it perfectly. 

Future rewards are given less weight in comparison to immediate rewards. And that weight is a function of time/steps, reduces further you go. Overall value at a given state if the sum of immediate reward and discounted future value.

In a single agent system, credit assignment is relatively easier, because only one agent’s action determines the end result. In a multi agent system like Orbit Wars, where each planet’s action can impact the team’s result, we need to do some aggregation to traverse the credit back to the action that produced it.

But our system didn’t really do this. At every step, it collected a single scalar advantage that says this turn was better or worse. But this step is not a single decision, it’s a bundle of independent per planet decisions — one planet attacks a neutral planet, another reinforces a frontier planet against the enemy and third one sits idle. When we compute policy gradient, we multiply the step’s scalar advantage with log probabilities of all those per planet choices. The effect is that every planet’s decision receives exactly the same credit or blame, regardless of which one was actually responsible for the outcome. At turn that wins reinforces lazy idle behavior alongside a decisive attack; a turn that loses punishes a well-timed reinforcement.

This multi-agent credit problem wasn’t something hidden, but the multiple attempts at overcoming it resulted in different kind of failures.

Before I describe the attempts, it’d worth knowing a little about PPO, Proximal Policy Optimization. It’s a policy gradient RL algorithm, based on actor critic architecture. Actor decides what action to take, and critic evaluates how good/bad a given state is V(s). Advantage is derived from the critic (A = r + γV(s′) − V(s)).  So far we have talked about fire/ship/target heads, they are actors in our model; along with these three heads, there is another value head, and that’s the critic. We can have two networks, one for actor and one for critic, but they can also share the neural net, and that’s what happens in our entity transformer.

Actor’s actions are controlled by the policy, and during training, big step updates to the policy can make it collapse; in order to stabilize it PPO clips the policy such that it doesn’t go too far, and stays within a trusted region. What I want you to remember is this clipping has nothing to do with credit assignment or calculation of advantages, that’s the job for the critic.
I explored per planet clipping, one trust region per planet, together they get summed after. This resulted in under-commitment of ships. 

Following this, we moved to fixing the credit assignment; per planet advantage instead of single shared advantage for all planets. This factorization destabilized training into a hoarding policy (visible first as the value collapsing).

And we concluded that joint credit is the reason baseline was working, where all planets coupled under one advantage

The second attempt later was to explore the ideal way of calculating counterfactuals to isolate per planet contribution — what would the outcome be if this planet hadn’t acted, while other planets acted as they did?

Turned out structural credit assignment wasn’t the problem, because even with the credit correctly assigned, the behavior it would reinforce (under concentrated and under-expanded play) is the same losing equilibrium self-play keeps forming. What I concluded was that actions worth crediting, traits worth developing weren’t being produced in the first place. And then would jump to improving the training signal of self play opponents, such that they’d force the agent to produce these actions, and learn that it can win by these actions.

I found it difficult to trust these conclusions because I kept going in cycles; a simple bug could’ve lead to the wrong conclusion and dropping of a direction worth pursuing. It might still be true. Once I know one of the top agents won with this approach, I shall revisit with fresh eyes hunting for bugs and bad assumptions. (Would it have been different had I written all the code myself?)

Why isn’t agent producing these actions?

Because the policy generates the data. You can only reach states that your policy takes you towards.
Unlike supervised learning where the training of the model doesn’t affect the data it trains on, in self play it does.

current policy π  ──acts in the env──►  rollout (states, actions, rewards)
        ▲                                          │
        └────────── PPO update on that data ───────┘

If the current policy doesn’t send 50 ships to contested neutral planets, then you collect zero samples of how that turns out. The policy can be blind to its own blind spots and stay that way.

Because of this continuous feedback cycle in RL, a bad update in policy compound instead of getting washed out. Policy gets worse, it generates worse data, then trains on worse data.

Data’s life is dependent on how many PPO epochs you use the data for.

It can be short, if number of PPO epochs is 1. 

Policy used to generate the rollout gets updated at the end of the rollout and that data is thrown away.

If number of PPOs epochs is 2, then a second pass is done over the same data.

If it’s 4, then 4 passes over same data, so more learning, and policy will drift further from the initial policy that generated the data.

More epochs = More reuse = More sample efficient but more off-policy drift.

Adding external opponents to the pool will increase the state/board distribution your agent faces and learns from but it won’t fix the agent’s blind spots.

What will then?

Entropy, curriculum, and reward signal.

To be continued...