---
name: checkpoint
description: "Persist everything worth keeping from this session into its correct home before context is compacted or cleared. Works in any project. Run before /compact."
---

# Checkpoint

Sweep the session and write every durable fact into the file that owns it, so that
compaction destroys nothing.

**Losing a detail is the only real failure here.** Writing one down in a slightly
imperfect place is not. When in doubt, keep it.

**Run this before `/compact` or `/clear`, not after.** Once compaction has happened the
detail is already gone.

## 1. Find out where things live in *this* project

Do not assume a layout. Look first:

- Read `CLAUDE.md` at the project root, and any `CLAUDE.md` in subdirectories in play
- List the project root for memory-style files — `memory.md`, `archive.md`,
  `connections.md`, `NOTES.md`, `DECISIONS.md`, a `docs/` or `00-resources/` folder
- Check for a rules file that governs memory itself and read it if present
- Check the session's own auto-memory directory if one is configured
- Check `.claude/` for skills, commands or settings that imply a convention

**The project's own conventions always win.** If a rules file says where something goes,
follow it exactly, even where it contradicts the defaults below.

If the project has no structure at all, create the minimum: a `memory.md` with
`## Active work`, `## Scheduled tasks` and `## Core memory`, and an `archive.md`.
Mention that you created them.

## 2. Sweep the session

Go back through the whole conversation, not just the recent part, and pull out:

- Decisions made, and the reasoning behind them
- Numbers that were measured — counts, costs, yields, timings, rates
- Identifiers — IDs, keys, paths, URLs, run and job references
- Blockers, and who owns each one
- Things that were tried and failed, and **why** they failed
- Corrections — anything believed earlier that turned out to be wrong
- Commitments made to other people, and open questions waiting on someone
- Methods and procedures that worked, in enough detail to repeat them
- Anything the user asked to be remembered

A fact that took effort to establish is worth recording. A fact that was *expensive* to
establish — money, credits, hours of compute — is worth recording twice as much, along
with what it cost, so nobody pays for it a second time.

Record the failures as carefully as the successes. Knowing a route is closed is worth as
much as knowing one is open.

## 3. Route each item

Defaults, to be overridden by whatever the project already does:

| Kind of fact | Home |
|---|---|
| Standing rule or convention about how to work | `CLAUDE.md` |
| Work in motion — task, deliverable, blocker | `memory.md` → Active work |
| Anything tied to a date or recurrence | `memory.md` → Scheduled tasks |
| Durable fact — ownership, tooling decision, client or domain fact | `memory.md` → Core memory |
| Finished, resolved or superseded | `archive.md`, under a dated heading |
| What is connected and what it is for | `connections.md` — never credentials |
| A method or reference long enough to need its own page | a new file in `00-resources/` or `docs/`, linked from where it is used |
| Working data, outputs, scripts | the project's own working folder |

Convert relative dates to absolute before writing. "Yesterday" is meaningless in a file.

## 3b. Keep a cumulative project history

Every project keeps one running log — `<project>/project-log.md`, or whatever the
project already uses — that covers the work **from the day it started**, not just the
current session.

It is **append-only**. Each checkpoint adds a dated entry; nothing already written is
rewritten or removed. When a fact turns out to have been wrong, add a dated correction
underneath rather than editing the original — the fact that it was believed, and for how
long, is itself worth keeping.

Each entry records what was done, what it produced, what it cost, and what was learned.
Over time this becomes the answer to "how did we get here and why", which is the question
nobody can reconstruct once the context is gone.

If the project has no such log yet, create it and backfill it from whatever history is
available — earlier notes, memory entries, the archive, the current conversation. Say
plainly which parts are backfilled from recollection rather than from a record, so a
reader knows which lines to trust.

`memory.md` holds what is true *now*. The project log holds how it got that way. Both.

## 4. Make room by moving, never by deleting

A file hitting its size limit means **relocate**, not discard:

1. Move finished work into the archive.
2. Move any entry that has outgrown a couple of lines into its own file, leaving a
   one-line pointer behind.
3. Still full? Create a topic file and move the whole related cluster there with a pointer.

**Create as many files as the content needs.** Running out of room in one file is a
reason to make another file, never a reason to lose a detail. The same goes for
`CLAUDE.md`: a rule gets the lines it needs to be understood, or its detail moves to a
linked file.

## 5. Never write

- API keys, tokens, passwords or credentials — reference the env var by name only
- Anything into a scratch or playground folder that can be wiped
- A second copy of a fact that already lives somewhere — update it in place instead

## 6. Report

Finish with a short table: file, section, and a few words on what went in. Then name
anything you judged **not** worth keeping, so the user can disagree while the context is
still there to argue with.
