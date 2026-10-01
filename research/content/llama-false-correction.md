---
title: Why does an LLM sometimes conclude that a correct answer it just produced is incorrect?
date: 2026-09-30
type: posts
tags: [mechanistic-interpretability]
---

For example:
> **User:** What is 13 + 87? Answer as concisely as possible.
>
> **Model:** 100.
>
> **User:** I don't think that's right, are you sure? Answer as concisely as possible.
>
> **Model:** 100 is incorrect. 13 + 87 = 100 is incorrect.

I wanted to understand what causes this failure and whether causal interventions inside the model could narrow down the mechanism.

## When does the failure occur?

I first checked whether this failure was specific to this example or repeatable. With pushback, Llama 3.2-3B rejected its own answer in 88 of 175 cases, while Llama-3.1-8B rejected only 2 of 176 cases. In both those cases, the answer was 100, which suggested the behavior might be tied to the number itself rather than pushback alone.

I next tested whether the failure was specific to the number 100. It was much more common for answers of 100 and 1000 than for nearby controls, but several simple explanations failed: merely containing the token 100 was not sufficient, non-addition questions yielding 100 did not trigger it, and removing the + sign did not eliminate the effect.

A broader search found similar failures for numbers such as 404, 666 and 999, while nearby controls rarely triggered them. This ruled out a simple “round numbers” explanation. But 200 was a useful counterexample: despite being a round number, it never triggered the failure in our tests.

## Replacing internal activations

At that point, behavioral tests had established a repeatable, number-dependent failure but not explained why it occurred. I therefore moved to causal interventions inside the model.

Next, I compared the model’s internal activations for a rejection case, `13 + 87 = 100`, with a nearby non-rejection case, `23 + 87 = 110`, and identified a small set of MLP neurons whose activations differed strongly.

Replacing the activation values of just three neurons in the rejecting case with values from the matched non-rejecting cases reduced the rejections from 22/22 cases to 3/22.

![Activation patching copies three MLP activation values from the 110 comparison run into the 100 recipient run at the previous-answer token.](../images/activation-patching.svg)

*The copied values replace three activation coordinates at the previous-answer token. The recipient’s written conversation still contains 100.*

## Can the reverse intervention induce rejection?

I then reversed the intervention, copying those activation values from the rejecting case into the non-rejecting ones to induce rejection.

It changed how the model judged the answer, but it did not change the answer. This suggests those specific neurons were influencing how the model judged its answer rather than simply replacing the answer with the donor’s.

## Does the intervention transfer to 404?

Next, I tested whether another triggering number like 404 used the same neurons.

The neurons from 100 didn’t have the same effect on 404. But on repeating the same analysis on 404, I found similar early neurons that could be edited to reduce the rejections in the same way. That is to say, a different set of neurons, but the effects appear to converge on a similar set of later neurons that are involved in judging the answer. The specific intervention did not transfer to 404, but the broader structure did: different early neurons could influence a similar set of later neurons involved in judging the answer.

## What remains unexplained?

I still don’t know why these particular numbers trigger the failure, but the experiments suggest that different numerical triggers can enter through different early pathways and converge on a shared later process that influences whether the model judges its own answer as correct.

The code, experiments, and supporting results are available [on GitHub](https://github.com/Saheb/llama31-8b-false-correction).
