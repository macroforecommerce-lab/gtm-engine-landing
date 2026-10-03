# Archive

Finished, resolved or superseded. Newest first.

## 2026-10-03 — Superseded: the Next.js rebuild as the active deliverable

Built, deployed and verified live at **scalient-gtm-landing.vercel.app**, then
superseded when the user rejected both existing pages and asked for a from-scratch
rebuild. The deployment stays up and frozen; it is no longer the thing being
worked on.

What it was: Next.js 15 App Router, 14 sections, the reference page's copy
verbatim, Scalient brand tokens, a four-question qualifier form, Meta Pixel and
UTM capture, Organization/Service/FAQPage schema, a `next/og`-generated OG card,
and privacy and terms pages. 113 kB first-load JS, fully static, TTFB ~0.25s.

Verified against the live deployment rather than the local build: every route
200, all eleven content probes present in the server HTML, **zero occurrences of
`opacity:0`**, and the lead API returning 200 / 400 / 200 for valid, invalid and
honeypot submissions.

One defect shipped and was never fixed, because a second production deploy to an
existing Vercel project is refused: `canonical`, `og:image` and `sitemap.xml`
point at `gtm.scalient-ai.com`, which does not resolve. The fix was written
(`lib/site.js`, resolving the origin from `VERCEL_PROJECT_PRODUCTION_URL`) and
committed, but never deployed.

## 2026-10-03 — Closed: hosting the PM team's page

The performance-marketing team's handover zip proved **byte-identical** to what
was already live on their Cloudflare Worker — the same sha256 on `index.html`.
Hosting it was therefore not unblocking anything; the user simply did not have
the link to hand.

Hosted anyway at **scalient-pm-landing.vercel.app**, with all eleven files
verified against the zip's checksums at build time and the Worker's `/api/lead`
handler ported so the form behaves identically. Leads there reach the Vercel
function log and nowhere else, which is correct for a review copy.

Two findings carried forward: `deploy.py` uses a Cloudflare global API key (see
`CLAUDE.md`), and `ambient-mesh.webp` and `og-card.webp` ship in the zip while
nothing references them — 74 KB of dead weight.

## 2026-10-03 — Resolved: skills installed, then lost to container resets

Seven ui-ux-pro-max skills, the official `frontend-design` skill, and claude-seo
(25 skills, 18 sub-agents) were installed project-scoped into `.claude/skills/`,
specifically so they would survive in the repo rather than in an ephemeral
`~/.claude/`. All were committed. All were destroyed by the container resets, as
the commits themselves were.

The one lesson worth keeping: **claude-seo builds its Python runtime inside the
skill directory** on a manual install — `scripts/runtime.py` resolves the data
dir to the skill root unless `CLAUDE_SEO_DATA_DIR` or `CLAUDE_PLUGIN_DATA` says
otherwise. That is a 796 MB venv plus 656 MB of Chromium, about 1.4 GB, and it
was committed once by accident: 17,746 files in a single commit. Gitignore
`.venv/`, `ms-playwright/` and `runtime-state.json` under the skill before
running `claude-seo setup`.
