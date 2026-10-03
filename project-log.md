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
