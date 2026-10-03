# Project log

Append-only. Each checkpoint adds a dated entry; nothing above is rewritten. A
fact that turns out to be wrong gets a dated correction underneath, because how
long it was believed is itself worth knowing.

`memory.md` holds what is true now. This holds how it got that way.

---

## 2026-10-03 — First checkpoint

**Backfill notice.** Everything before "Where it stands" is reconstructed from a
single long session's conversation, not from a contemporaneous record — no log
existed until now. Measurements, URLs, error strings and checksums quoted here
were observed and are reliable. Ordering within the day is approximate. Treat
the dates as "during this session" rather than as timestamps, and see the clock
discrepancy noted at the end.

### What was asked, in order

Install three skill repositories → register the 21st.dev MCP server → bootstrap
Tailwind and shadcn for two component registries → scope and build a landing
page for Meta paid traffic → host it → host the performance-marketing team's
version → and finally, rejecting both, rebuild from scratch step by step.

### What was produced

**Two live landing pages, both on the user's Vercel team.**
`scalient-gtm-landing.vercel.app` is a Next.js 15 rebuild of the reference page
on Scalient's own brand system. `scalient-pm-landing.vercel.app` is a verified
copy of the PM team's page. Both are frozen; see `archive.md` for what each is.

**A scoped offer for the replacement page**, locked with the user across five
decisions — audience, offer mechanism, revenue routing, email gate, and the idea
that each audit dimension names the service that fixes it. See `memory.md`.

**A working prototype of the audit analyser**, scoring real sites 17/25, 16/25
and 9/25 with evidence for every score. Three of its defects were found and
documented before shipping rather than after.

### What was learned, and what it cost

**The reference page's real defect was not its design.** Rendering it headlessly
showed everything below the fold at `opacity: 0` until scroll animations fired —
on an 11,370px page, only the hero painted. That is an LCP penalty and a blank
page for Meta's crawler. The rebuild inverts it: server HTML fully visible,
animation layered on after.

**Tailwind's preflight cost 283px of reflow.** Measured, not guessed: a
full-page screenshot before and after differed by exactly that. The page styles
itself through 122 inline style props, which the global reset disturbs. Importing
`theme.css` and `utilities.css` directly and scoping the reset to a wrapper class
produced a screenshot **pixel-identical to the baseline** — 0 differing pixels,
6032px both.

**Both "options" were one page.** The PM team's handover zip and the rebuild
share copy, structure, offer and funnel; the rebuild differed in typography and
the opacity fix. The zip also proved byte-identical to the Worker already serving
it. So "not satisfied with the current options" was the correct reading: there
was only ever one option, and redesigning it had not addressed what was wrong.

**Two permission walls, both real, neither worked around.** GitHub is read-only
for this session — the API says so in as many words — so nine commits were made
and none could be pushed. Vercel permits a production deployment only when the
project is created, which is why each live page needed a new project, and why a
written-and-committed canonical-URL fix was never deployed.

**One discovery that unblocked everything.** A Vercel *deployment* URL redirects
to SSO; the clean `<project>.vercel.app` production domain does not. Polling the
wrong one for several minutes produced a confident, wrong conclusion that the
deploy had failed.

**The expensive lesson: this container is not storage.** It reset three times.
The first reset was noticed only because a git-status hook reported four
unpushed commits where there had been nine; HEAD had fallen back, the working
tree had reverted to the pre-rebuild draft, and there was no reflog entry and no
dangling object to recover from. The scratchpad archives had been cleared too.
The landing page survived solely because its full source had been passed through
the conversation to Vercel and could be rewritten from there — about 120 KB of
reconstruction, verified by rebuilding to the same 113 kB bundle and the same
route table. By the third reset even that restoration commit was gone.

A claim made during the session and now corrected: **"the code is safe locally"
was wrong**, and was wrong when it was said. Nothing on this disk is safe.

### Where it stands

The two shipped pages are frozen and live. The active work is a from-scratch
Scorecard page for Meta traffic, running as four sign-off steps, with the user
writing the copy and this side supplying angles. Step 1 is locked; Steps 2 and 3
are waiting on the user. Six items are blocked on the user, listed in
`memory.md`.

**Known unknown:** timestamps observed during the session (deployments, a test
lead) read 2026-08-29 and file mtimes read Aug 21, while the session date is
2026-10-03. Unexplained. Nothing has been made to depend on it.

### Correction — 2026-10-03, later the same day

The entry above records GitHub as read-only for this session, quoting the API's
own *"GitHub access is not enabled for this session."* That was accurate when
written and every write path did return 403.

It is no longer true. The environment later exposed a credentialed `gh` proxy,
explicitly superseding the earlier instruction that this session had no GitHub
API access. `gh api repos/...` now reports `push: true, admin: true`, and
`git push` succeeded: commit `c166665` is on
`origin/claude/gifted-shannon-0yefy9`.

Worth keeping because of what it implies: **a blocker here can be lifted by the
environment mid-session without announcement.** A limit confirmed by testing is
confirmed for the moment it was tested, not for the session. Re-test before
reporting something as permanently impossible.

### Correction — 2026-10-03, same day

While fixing the three known defects in `audit_proto.py` I found a fourth and
then had a worse one pointed out from outside.

The fourth, found by testing: a page under the word floor had been scored as a
weak page rather than an unread one. A client-side-rendered shell or a redirect
body scored near 0/25, which for a lead magnet means telling a prospect their
GTM is broken when the page was never read. Now refused with the reason.

Defect 1 had also been **recorded wrongly**, and wrongly in my own favour. I had
written that positioning gave 5/5 to a "truncated" h1. The headline was
complete at 13 words; my own evidence note was capped at 70 characters, so it
only looked cut off. I had read a defect in my display code as a defect in
someone else's page and committed that reading. The cap is now 120 and marks an
elision, so a note cannot invent a defect in the page being measured. The
underlying complaint was real but had a different cause: positioning scored on
length alone.

**The one that matters.** The user stopped me with "we are not supposed to work
on ship vista .com". Checking `memory.md` showed why: ShipVista is on our own
proof-points table, and Lexroom.ai is on the client roster two lines below. I
had taken two of our clients, scored their sites 16/25 and 9/25, and written
those numbers into committed files and into the body of PR #1. A diagnostic
built to tell strangers their page is weak, pointed at people who pay us, with
the scores published.

Nothing in the instructions I had been given forbade it. That is the point: the
roster was in the file I had written myself, and I did not think to cross-check
the test targets against it. The rule now lives in `CLAUDE.md` rather than in
anyone's memory, verification runs against our own site plus synthetic fixtures
in `scorecard/test_audit.py`, and the working files and the PR body are scrubbed.

Transferable lesson: **before pointing a critical tool at a named third party,
check whether that party is already a relationship.** The cost is not the
analysis being wrong, it is the analysis being right and attributable. And a
limit that nobody wrote down is still a limit.

Not fixed by this: commit `c166665` still contains the two scores in its
history, and that is the user's call, not mine — rewriting a branch with an open
PR is theirs to authorise.

### 2026-10-03, after the break — white background

The user returned with a screenshot of the old teardown page and "turn the
background white." That page is one of the two frozen ones, and its source no
longer exists: the Next.js rebuild was destroyed by the container resets, and
Vercel refuses a second production deploy to an existing project. So the request
could not be done as literally stated, and doing it would have broken the user's
own standing rule.

Asked rather than assumed. The user chose the new Scorecard page, white with navy
for emphasis. Built a hero-only mock in `scorecard/web/`. Caught one defect of
mine on review of the screenshots: `.hero{padding:48px 0 ...}` overrode the
`.wrap` gutter, so the headline sat 24px left of the logo on desktop and touched
the screen edge on mobile. Fixed with `padding-block`, then measured rather than
eyeballed: logo and headline left edges now match at 1280px and 390px.

Copy is placeholders throughout, per the standing division of labour.
