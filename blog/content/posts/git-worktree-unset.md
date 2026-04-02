---
title: "The Day My AI Editor Went Silent: Debugging Git Worktrees, Phantom Configs, and Lost Weights"
date: 2026-03-30
---

Building reinforcement learning environments is already a complex exercise in managing state, rewards, and training loops. You expect the agent you are training to act unpredictably. You don't expect the AI agent writing your code to completely flatline.

While working on some recent RL projects, my AI code editor—Google Antigravity—just gave up. Every time I hit send, it would emit a single beep. No error message. No spinning loader. Just a beep and a dead UI.

What followed was a deep dive into IDE architectures, the hidden dangers of running multiple AI tools, and a brutal lesson in version control cleanup that cost me my local model weights.

Here is what I learned about how our tools actually work under the hood, and why they sometimes destroy each other.

## The Mystery of the Silent Beep

At first, I assumed I had hit a quota limit or an authentication bug. I'll be honest: I had been cycling through multiple Google accounts to maximize free tokens — we all need more tokens, don't we? — and my first thought was that Antigravity had started actively detecting and blocking that abuse. I cleared the keychain, purged the global state databases, and reset the local workspace caches, half expecting a ban message to surface. Nothing. What made it especially maddening was that some workspaces were completely fine — the AI connected instantly and behaved normally. But two specific project directories were dead on arrival. It wasn't a global outage. It wasn't my account. Something was different about those particular workspaces, and I had no idea what.

To catch the error before the UI swallowed it, I had to open the IDE's internal Developer Tools and watch the raw JSON payload of the language server.

When I finally caught the payload, it revealed the agent was registering my input, reading my project path, and instantly dropping its status to IDLE without throwing a network request. It wasn't a server issue; the agent was crashing locally before it could even formulate a thought.

## The Smoking Gun: Claude Code and Git Worktrees

The JSON logs finally coughed up the fatal error:

```
"message": "core.repositoryformatversion does not support extension: worktreeconfig"
```

This wasn't an IDE bug. It was a Git parsing crash.

To understand why this happens, you have to look at how modern AI coding assistants interact with version control. To build a context window, the editor's language server parses your Git history. Antigravity relies on a Git parsing library under the hood that lacks support for the `worktreeConfig` extension — a limitation shared by several popular open-source parsers, including `libgit2` and `go-git`.

The plot twist? I had been using Claude Code in those exact same folders earlier in the week.

When Claude Code runs in certain agentic task configurations, it creates a temporary Git worktree to operate safely. To do this, it injects `extensions.worktreeConfig = true` into the project's `.git/config` file. The fatal flaw is that when Claude finishes and deletes the worktree, it leaves that configuration setting orphaned in the file.

When I opened that repository in Antigravity, its parser hit that orphaned setting, panicked, and silently crashed the background extension host (the invisible process that runs AI features in the background). The fix was a single terminal command:

```
git config --unset extensions.worktreeConfig
```

Finding that one line took hours.

## The Multi-Tool Meltdown

Tracking down that worktree bug also threw into sharp relief a problem I'd been half-ignoring: you cannot run every new AI tool simultaneously.

At one point, I had Antigravity, VS Code (Github Copilot, Cline, Ollama), Claude Code, OpenCode, and Codex all running on the same machine. These tools are built on similar underlying architectures (like Electron and Node.js) and they will aggressively fight over the same local ports, IPC sockets, and file-watching limits.

When multiple AI tools simultaneously poll your version control, they hit each other's `.git/index.lock` files, denying access and crashing background loops. We are pushing our local OS limits just by having these tools actively monitor our file trees.

## The Collateral Damage (RIP Untracked Models)

The most painful lesson came at the very end. With the root cause identified, I started manually removing the corrupted worktrees one by one. It felt like cleanup — routine, mechanical, nearly done. I wasn't being careful enough.

One of those worktrees contained a PyTorch model checkpoint I had never committed to Git. A file that represented 39 hours of continuous training. Because it was untracked, removing the worktree via the terminal most likely bypassed the macOS Trash entirely — and even if it hadn't, I have a habit of emptying the Trash on autopilot. Either way, it was gone.

Experienced ML practitioners treat model artifacts as first-class infrastructure from day one, precisely because of moments like this. The standard pattern is to never let a checkpoint exist only on local disk: tools like DVC (Data Version Control) track large binary files outside of Git and sync them to remote storage, while experiment tracking platforms like Weights & Biases or MLflow automatically upload checkpoints during training. Even a simple rclone script pushing to S3 or Google Cloud Storage after each epoch would have saved those weights. The rule of thumb is simple — if it took more than an hour to produce, it should exist in at least two places before you touch anything around it.

## The Takeaways

Transitioning into heavy Machine Learning engineering means your environments are no longer just lightweight text files; they are massive data pipelines, model checkpoints, and training logs.

**Add `.gitignore` and `.antigravityignore` entries for your model artifacts.** Explicitly prevent AI file-watchers from attempting to index massive dataset directories or `.git` files in worktrees. If your tools can't see the files, they can't corrupt them.

**Isolate your tools.** Pick one AI assistant per active workspace. Let them own the local ports and sockets without competition.

**Never run a forced terminal removal without a dry run (`git clean -nd`).** And if you are doing serious ML work, treat your checkpoints as infrastructure: use DVC, W&B, or MLflow to sync artifacts to remote storage during training. Your code is easily recoverable; your compute time is not. The weights are gone, but the hard-won knowledge of why they're gone sticks around. One of these things can be regenerated overnight. The other just became a permanent part of your stack.