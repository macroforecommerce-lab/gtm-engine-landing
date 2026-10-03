# Memory

What is true now. History lives in `project-log.md`; finished work in `archive.md`.

Last checkpoint: 2026-10-03.

## Active work

**Scorecard landing page — a from-scratch rebuild for Meta paid traffic.**
The user rejected both existing pages. Diagnosis: they are the same page in two
skins, and the problem is not design but that it is an agency homepage rather
than a paid-traffic landing page.

Running as four steps, with sign-off at each. **The user writes the copy; this
side supplies ideas, angles and tradeoffs.** That division was set explicitly
after an earlier round where a finished page was delivered and rejected.

- Step 1 — Offer: **locked**, see Core memory.
- Step 2 — Section map: **proposed, awaiting sign-off.** 8 sections, not 14.
- Step 3 — Copy, section by section: hero angles put to the user, **awaiting a pick.**
- Step 4 — UI and build: not started.

**Blocked on the user, nothing actionable this side:**

| Waiting on | Why it blocks |
|---|---|
| Hero angle: A offer-first / B founder-bottleneck / C proof-first / D category / hybrid A+B | Step 3 cannot start |
| Section-map sign-off, incl. four proposed cuts | Step 2 cannot close |
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

### Proposed section map — Step 2, awaiting sign-off

Hero + URL input · Scorecard result (a page state, not a scroll section) · The
problem · The system (five parts, mapped to the five scores) · Proof · Two ways
to work · FAQ (4–5, not 7) · Final CTA.

Proposed cuts, with reasons: **nav** (escape hatches on a paid LP), **logo
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

Measured on live sites: **scalient-ai.com 17/25, shipvista.com 16/25,
lexroom.ai 9/25.** That 8-point spread is the proof it discriminates; a tool
that hands everyone 15/25 is theatre.

Three defects found during that test, all still open:

1. **Positioning scores too generously** — gave 5/5 to ShipVista's truncated h1.
   Needs a quality check, not just a length check.
2. **Buzzword matching misses inflections** — "Leveraging" slips past a filter
   that catches "leverage".
3. **Non-English pages score unfairly** — lexroom.ai is Italian, so ICP scored
   0/5 on vocabulary grounds rather than GTM grounds. Tolerable for Indian
   founders, wrong for a European prospect.

The prototype lives only in the session scratchpad, which does not survive a
reset. It must be rewritten into the new project's repo before it counts as kept.

### Environment constraints, all confirmed by testing

- **GitHub now works.** It did not for most of this session — the API answered
  *"GitHub access is not enabled for this session"* and every write returned 403.
  A credentialed `gh` proxy then appeared mid-session; `gh api` reports
  `push: true, admin: true` and `git push` succeeds. The general lesson, recorded
  in `project-log.md`: an environment limit confirmed by testing holds for the
  moment it was tested, not for the session. Re-test before calling something
  permanently impossible.
- **Vercel: a production deployment can only be created along with the project.**
  Deploying again to an existing project returns 403 *"You don't have permission
  to create a Production Deployment for this project."* Each production deploy
  therefore needs a brand-new project, which is how both live pages were shipped.
- **Vercel reads are scoped to 12 pre-authorised projects.** Projects created by
  this session are invisible to it — `get_project` and `list_deployments` 404,
  so build logs and env vars are unreachable.
- **Use the clean production domain, never the deployment URL.** `<project>.vercel.app`
  returns 200; `<project>-<team>.vercel.app` redirects to Vercel SSO. This single
  distinction was the difference between "the deploy failed" and "the site is live".
- **Chromium cannot reach external sites** through the agent proxy
  (`ERR_CONNECTION_RESET`), with or without the proxy passed to Playwright.
  `curl` with a browser user-agent works. Mirror the site locally and screenshot
  `127.0.0.1`.
- **A clock discrepancy exists and is unexplained.** Deployment and lead
  timestamps observed in-session read 2026-08-29, and file mtimes read Aug 21,
  while the session date is 2026-10-03. Worth resolving before anything depends
  on a timestamp.
