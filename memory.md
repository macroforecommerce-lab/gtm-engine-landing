# Memory

What is true now. History lives in `project-log.md`; finished work in `archive.md`.

Last checkpoint: 2026-10-03.

**Repo state:** PR #1 was squash-merged into `main` as `c8cb3a9`. Everything in this
file's history is now on `main`. New work starts from `main` on branch
`claude/gifted-shannon-0yefy9`; any further PR is a new one, not #1.

## Active work

**Scorecard landing page — a from-scratch rebuild for Meta paid traffic.**
The user rejected both existing pages. Diagnosis: they are the same page in two
skins, and the problem is not design but that it is an agency homepage rather
than a paid-traffic landing page.

Running as four steps, with sign-off at each. **The user writes the copy; this
side supplies ideas, angles and tradeoffs.** That division was set explicitly
after an earlier round where a finished page was delivered and rejected.

- Step 1 — Offer: **locked**, see Core memory.
- Step 2 — Section map: **approved 2026-10-03.** 8 sections; all four cuts accepted
  (nav, logo marquee, "Under the hood" Clay explainer, comparison table).
- Step 3 — Copy, section by section: **in progress.** Hero angle chosen: **A+B
  hybrid** — an offer-first headline that gives the action, with the
  founder-bottleneck tension carried in the subhead. Hero copy is next; the user
  writes it.
- Step 4 — UI and build: not started. White-page direction already decided (below).

**Built 2026-10-03 (draft, awaiting the user's review):** the full Scorecard page
in `scorecard/web/` — 8 sections, white page with one navy band, working audit and
lead flow, all copy drafted. The user switched from "you supply angles" to
"complete the build, I'll review and send changes", so the copy is mine as a
first draft and is to be revised on their feedback. Tests: `test_audit.py`,
`test_logic.py` and a 58-assertion browser run, all passing locally.

**Not live.** Vercel refuses to create a project from this connection (403 on both
`create_project` and a deployment that would create one), so the page has only been
run locally. Deploy steps are in `scorecard/README.md`.

**Blocked on the user, nothing actionable this side:**

| Waiting on | Why it blocks |
|---|---|
| Permission to create a Vercel project (or the user imports the repo, Root Directory `scorecard/web`) | The Scorecard page is not live; nobody can click through it |
| Vercel project access for `scalient-gtm-landing` | No redeploys, no env vars, no build logs |
| Meta Pixel ID, booking URL, lead webhook URL | Conversion layer is built but inert |
| Attach `gtm.scalient-ai.com` | Canonical and OG URLs point at a domain that does not resolve |

## Scheduled tasks

None. No recurring work, no deadlines agreed.

## Core memory

### The offer — Step 1, locked

> **Your GTM Scorecard.** Enter your website. In about 60 seconds you get five
> scores with the evidence behind each — and the three fixes that move pipeline
> fastest.

Flow: URL → five scores with evidence, **ungated** → email gate on the
prioritised fix list → routing question → book 20 minutes.

Four decisions the user made, each deliberately:

1. **Audience: Indian B2B/SaaS founders.** Domestic. Prices in ₹, Fitness Avenue
   and Lakshay Chopra lead the proof.
2. **Instant audit, then book** — chosen over keeping the old 48-hour teardown,
   a paid low-ticket audit, or going straight to a calendar.
3. **Both revenue paths, page routes between them.** "Do you have someone
   running growth in-house?" No → Done-For-You. Yes → GTM Install.
4. **Scores free, fixes gated.** Keeps the "instant" promise honest and leaves
   the scorecard screenshot-shareable.

The design idea that holds it together: **each audit dimension names the service
that fixes it**, so the output of the diagnostic *is* the service menu, and a low
score is an argument the prospect reached themselves.

| Dimension | Fixed by |
|---|---|
| ICP clarity | ICP definition & messaging |
| Positioning | ICP definition & messaging |
| Proof for outbound | Clay & AI-powered funnels |
| Conversion path | Full-funnel distribution |
| Founder signal | LinkedIn personal branding |

### Section map — Step 2, approved 2026-10-03

Hero + URL input · Scorecard result (a page state, not a scroll section) · The
problem · The system (five parts, mapped to the five scores) · Proof · Two ways
to work · FAQ (4–5, not 7) · Final CTA.

Cuts, with reasons (all accepted): **nav** (escape hatches on a paid LP), **logo
marquee** (borrowed credibility, does not convert cold traffic), **"Under the
hood" Clay explainer** (call material, too deep for a first touch),
**comparison table** (most cuttable of the remaining).

### Scalient facts

- GTM-systems agency. Offices New Delhi, Toronto, New York. Serves Delhi,
  Gurugram, Bangalore, Mumbai, Pune, and Indian companies selling to US/UK/EU.
- Founder: Shivam. Teardowns are founder-delivered, which is a selling point the
  copy leans on ("not an account manager, not a junior").
- Five-part system: ICP & messaging · LinkedIn personal branding · LinkedIn and
  email cold outbound · Clay & AI-powered funnels · full-funnel distribution.
- Two commercial models: **Done-For-You** (monthly retainer, from ~$1,000/mo) and
  **GTM Install** (fixed-scope build, then train the client's team).
- Contact `info@scalient-ai.com`. Main site `scalient-ai.com`.

### Proof points available to the copy

| Client | Claim |
|---|---|
| Fitness Avenue | 7 B2B wholesale contracts, $250K, in 8 weeks |
| ShipVista | 40+ qualified calls and 3 enterprise logos in 2 months |
| FinStack | 5.6x ROAS in 90 days |
| Deplyt | fastest six-figure deal closed, without hiring |
| GigaIO | positioning and narrative work (Eric O., VP Sales) |
| Lakshay Chopra | positioning clarity and funnel architecture |

Other named clients: Kloopify, Lexroom.ai, Trig, Travaras.

Testimonial photographs exist for Claire Roberts, Edward F., Kelvin Oben, Sandy
Haddad and Lakshay Chopra. **Eric O. has none** — the rebuild renders initials
for him.

### Audit analyser — prototype proven, not production

`audit_proto.py` scores a URL across the five dimensions from observable page
signals. No randomness, no inference from the domain name, and a page offering
nothing to measure scores low rather than receiving a flattering default.
`test_audit.py` holds 25 fixture assertions and needs no network.

**Never run it against a client's site and never record a client's score** — the
standing rule is in `CLAUDE.md`. Verification uses `scalient-ai.com`, which is
ours, plus synthetic fixtures.

Verified 2026-10-03: `scalient-ai.com` **16/25** (ICP 3, positioning 4, proof 4,
conversion 2, founder 3). Fixtures span 0/5 to 5/5 on positioning and trip both
refusal gates.

Four defects found and **fixed** 2026-10-03:

1. **Positioning scored on length alone** — any h1 under 16 words took 3 of 5
   whether or not it claimed anything. Now it must be well formed *and* name a
   number or a buyer; a buzzword in the h1 costs a point; and the credit for a
   buzzword-free opening is capped at the strength of the claim, so a page with
   no h1 can no longer bank it. Generic-but-tidy h1 5/5 → 2/5, no h1 2/5 → 0/5.
2. **Buzzwords missed inflections** — now matched by stem, so "Leveraging" is
   caught by the same rule as "leverage". Verified not to fire on "level",
   "sales" or "deliver".
3. **Non-English pages were scored on English vocabularies** — now detected via
   `<html lang>` plus stopword rates across five languages, and refused with the
   reason rather than scored.
4. **A page too thin to read scored as a page that was weak** — found while
   fixing the above, and the most damaging of the four for a lead magnet. Under
   120 visible words the page is refused: a client-side-rendered shell or a
   redirect body had been scoring near 0/25, telling a prospect their GTM was
   broken when the page had simply not been read.

Both refusals still return what can be seen without vocabulary — numbers,
LinkedIn links, booking link, form-field count, h1 length.

Three limits remain open, listed in the module docstring. The one that matters:
real-world spread is now evidenced by a single site we own, so a **neutral
benchmark set** — sites that are neither clients nor prospects — is wanted, and
needs sign-off on which sites qualify.

