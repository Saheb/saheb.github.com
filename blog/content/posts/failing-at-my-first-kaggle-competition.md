---
title: "On failing at my first Kaggle competition (1/n)"
date: 2026-06-25
---

I had a lot of fun building an AI agent for Orbit Wars.

But I failed, according to my own standards, and naive high expectations.

I wanted to be in top 10. I didn’t even end up in top 1000.

The final scoreboard: a rating of 970, ranked 1189 out of 4729. Top 25%, nowhere near the top 10.

Getting there took over 90 training runs across a month, and about $700 worth of GPU compute across GCP, AWS, and Jarvis Labs.

An eye opening reckoning was long overdue for a deluded person like me.

Nonetheless, I learned a lot. 

That’s what matters I kept telling myself as I burned the midnight oil for more than a month.

I did start it as a learning exercise, but soon I became obsessed with it.

I wanted self-play reinforcement learning to work desperately.

I had already failed at doing so with poker, only a month ago.

But this time, I had other Kaggle experts who were there to share their lessons.

It does work they said, and I ran with that belief.

The system worked, the competition gave me the thrust I needed to grind it out.

I made it work, but I couldn’t push it beyond a point.

In my journey I made a ton of mistakes, and understood failure modes in self-play algorithms.

Not just that, but also the perils of working with LLMs.

Realized how making software in this new world is a skill on its own.

I admired DeepMind’s AlphaGo feat from the sidelines for many years.

Finally I made time to apply it for myself.

There was an allure to it, let agents play against its own copy and learn from it.

Like leaving a baby alone in a room with a chess board and it will come out a chess prodigy.

But how will it know what to learn from and what to avoid?

Give it a toffee when it wins and nothing when it loses.

That’s known as the sparse reward problem in the field of RL.

Before I jump into more details, this post is more about what not to do, than how to win.

I will go from high level analogies to details when necessary, to share the lessons I learned.

Many among them, I’ve learned before during my software engineering roles.

But if they bite me again, it means I still haven’t learned it yet.

It’s one thing to learn something, another to internalize it, and finally use it to build a system so that it’s impossible to fall for the same mistake again.

Interestingly, self play RL algorithms also suffer from this humane problem.

Give it a few samples, it won’t internalize, or will overfit — meaning it forgets everything else.

Overfit is like rote in learning.

Just become best at training data, but don’t generalize beyond it.

Like a student who can solve problems from a textbook, but can’t solve different looking problem based on the same concept in an exam.

Out of syllabus, he might protest.

In AI, it’s called out of distribution, OOD for short.

To prevent overfitting, we use validation+test dataset and held out evals, that are run constantly to ensure model is still learning and hasn’t collapsed or forgotten the past learning.

In Orbit Wars, you start with one planet, and some ships and the goal is to conquer more planets by sending your fleets during the course of the game and defeat the other agent who starts on the other side with one planet as well.

As the game unfolds, you will notice key problems emerge: which planets to target, how many ships to send, to send more ships now or wait before you have enough ships to capture, how many ships is enough, how to get planets to coordinate their attack such that team uses their total fleet efficiently and whether or not to reinforce/save a planet or abandon it.

Here’s one of my agent’s games from the leaderboard — press play and watch a full match. (My agent is the blue one; this is one of the games it won.)

<iframe src="/orbit-wars/replay-83428941.html" width="100%" height="640" loading="lazy" style="border: none;" title="Orbit Wars replay"></iframe>

Beautiful, isn’t it?

The core loop is simple: planets produce ships, ships travel as fleets, and a big enough fleet captures the planet it lands on.

The twist is that nothing sits still. Planets orbit the sun, so you aim at where the target will be, not where it is.

You can build a heuristic agent to encode the logic you yourself will follow if you play the game — a collection of if else loops, planned projections, and search trees. They can work pretty well, but I wasn’t interested in building these. My goal was to learn RL experimentation and witness the magic of self play learning.

Similarly, you can download replays episodes of the game, and train your agent on that data — this supervised learning approach also works wonders, but I wasn’t interested in mastering that for this exercise.

Looking back, this stubbornness wasn’t good for me. The better me would’ve approached this problem systematically and used the right algorithms to get to the best solution. Instead of staying fixated on a solution and committing the cardinal sin of picking an algorithm or data structure just because I like it. Being new on these ML algorithms, my excuse was ready; I didn’t know enough to figure out which approach would work well here, and which wouldn’t. Even the model that I used, entity transformer, wasn’t something I came up with myself; I just went with it because a more experienced Kaggler mentioned it, and LLMs agreed.

My love-hate relationship with LLMs needs a post of its own, but I’ll say this. I might not have attempted this competition without LLMs or would’ve given up at some point. With them I kept going and kept learning. At the same time, my problems doubled or tripled, because they couldn’t be trusted to know what they were doing and also didn’t have any need to be self consistent. They always sounded smart and confident, but wouldn’t know when an approach wasn’t working anymore, that they needed to step out or step back and re-evaluate what the hell was going on.

Coming back to self play.

In self play, there is no external data, the data is generated by playing the game with self copies. An ideal version of self play, starts even without the rules and the agent figures out the rules by playing. Like in snake you don’t encode hitting a wall kills you, the snake will discover it itself at some point. The only signal you give to the snake/agent is reward, give it +1 if they win, or -1 if they don’t. And they will figure out what gets them more rewards and what doesn’t. This is the simple idea of reinforcement. Identical to giving a kid a toffee for doing things you want them to be doing, and a punishment to make them stop doing things that are bad for them.

Learning rules takes a long time, i.e. more iterations, more compute and more time. So we cheat a little. We use supervised learning, in this case, they call it behavioral cloning, using some top replays. And once it has learned the rules, then you began self learning from that seed, the clone.

As we know devil is in the details.

Conceptually I will make you understand and take you in this direction, but it’s your job to understand, how important this seed, this clone really is.
I didn’t give it enough attention for a long time, and didn’t think it could be preventing the agent from learning, and blamed everything on the self play phase.

**This clone doesn’t just learn the rules from the replays you feed it, it also learns some strategy, and is clueless about what’s not present in the replays.** This gives it an inherent activeness or passiveness; how aggressive to be, or just hoard ships till the end of the game; how much to reinforce, and how to finish the game.

Why is this all so abstract? Because concrete will make you sleep, at the root it’s all core math. That will feel too hard. You will give up before you even get anywhere close to understanding phase, and won’t be able to appreciate the beauty of how it all works. I know, abstract will feel futile if you don’t know some basics like gradient descent, and back propagation. Maybe this will push you to go and learn about them finally.

Before I get into knobs of deep learning, transformer heads, and entropy; I must confess I am also fairly new to this, so many times I won’t know what I am talking about and my understanding could be fundamentally flawed. So take it all with many grains of salt, extract what you find interesting and start your journey from there.

Simply put, deep learning is magic, like words of an author creates an image in the mind of the reader. It is all explainable by math, but not fully comprehensible why it works so well.
Keeping that aside, you can still apply and replicate it with a high level understanding. And gradually dig deeper into every little thing that controls the network.
There are lots of knobs in deep learning that you need to turn, tweak and master before your model learns. One of them is entropy. The degree of exploration you want to allow. If you make it zero, model won’t explore new paths and won’t discover new strategies it needs to win more rewards. If you make it one, it will keep exploring, but never internalize or turn those learnings into the weights of the models.
Whether to set entropy to 0.02 or 0.5 or something else, I had no idea. I’d trust the standard recommendation of the algorithm I was using, i.e. Proximal Policy Optimization. Or trust the expert Kaggler’s recommendation. But all these little things make or break the learning curve. So I had to go through these ups and downs countless times, where I’d discover something new, understand it and then go ahead with high spirits to find something else I was completely ignoring that I shouldn’t have.

In self play, an agent learns from the other agent it plays against. The copy of itself will push it in certain direction, where it will have to choose certain action, and if that action gives positive reward, it will do more of that; if not, it will do less of that. Given enough entropy, it will try/sample many actions and find something that works. That’s good, that’s learning going well, agent is receiving gradient on what works.

At some point, this stops happening and the learning plateaus. The agent has reached a Nash equilibrium, where they both are selecting the best action, given the actions of the opponent. There is no need to change anything. These actions might be best against each other, but likely won’t be best or hold strong when played against better opponents.

So we need to find a way for the agent to jump above this equilibrium and keep learning and exploring. In order to do so, we need to give it a variety of other agents to play against, not just its own frozen copy. One simple way is to checkpoint your agent at regular intervals, and use these past checkpoints as a pool for the agent to learn from. This is definitely better than pure self-play but even this pool often ends up in similar end state, similar Nash equilibrium at some other place.

Next thing you do is bring external agents into the pool, these external agents exploit the weakness of our agent and agent now needs to find a way out in order to gain more reward. Otherwise it will keep losing.

Tricky lesson here for me was **an agent can only learn from an external agent that it has a reasonable chance of winning against, like 40-60%**; if you make it play against an agent that’s way out of its league where our agent only loses, then it will learn to not lose and develop hoarding or passive behavior that you don’t really want in the agent; they are being developed so that it loses less badly than it already does. So don’t put too strong agents in the pool, before agents have a chance against them.

Even after all this, equilibrium can be formed again, and I don’t know what to do then. That was my end state. My agent had reached its limit. It could no longer do any better than 50-60% win rate against the planner agents, that looked 18 steps ahead and planned their each move with precision.

And that 50-60% was just my local evals, against a publicly available producer agent. The top of the leaderboard was a different league altogether.

It also didn’t help that Orbit Wars had both two player and four player games. I spent all my time on the heads up version, and never focused on interesting game theory aspects of four player games.

In the next post, we will dig into transformer heads and flaws in my feature engineering.