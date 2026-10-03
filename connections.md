# Connections

What is wired up and what it is for. **No credentials here** — environment
variable names only.

## Vercel — working, partially scoped

Team `scalient`, id `team_JxtJE4zfCto3HGxnagXvmWnK`.

| Project | URL | State |
|---|---|---|
| `scalient-gtm-landing` | scalient-gtm-landing.vercel.app | Live. The Next.js rebuild. **Frozen.** |
| `scalient-pm-landing` | scalient-pm-landing.vercel.app | Live. Hosted copy of the PM team's page. |
| `scalient-gtm` | — | Preview-only, created by mistake. **Safe to delete.** |

Pre-existing projects on the team, visible to this connector: `scalient`,
`scalient-careers`, `scalient-dashboard`, `scalient-crm`, `roi-from-ads`,
`funtastique`, `localnotepad`, `eternal-homz-preview`, `outright-solutions`,
`images`, `express-js-on-vercel`, `flow-export-1776253495281`.

Two limits worth knowing before planning any deploy work — both verified, see
`memory.md`: production deploys only happen when a project is created, and
projects this session creates are invisible to it afterwards.

## GitHub — working

Repo `macroforecommerce-lab/gtm-engine-landing`, working branch
`claude/gifted-shannon-0yefy9`. **PR #1 is merged** (squash, `c8cb3a9`).

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the original
Vite skeleton (`src/`) and publishes it to GitHub Pages. That run succeeded on the
merge. It does **not** publish `scorecard/web/`.

Writes work. `gh api` reports `push: true, admin: true` and `git push` succeeds.
This was blocked for most of 2026-10-03 — every write returned 403 — and the
block lifted mid-session without announcement. See the correction in
`project-log.md`; the transferable part is that a limit confirmed by testing
holds for the moment it was tested, not for the session.

All memory files, `scorecard/audit_proto.py` and `scorecard/test_audit.py` are
pushed. Nothing of value exists only on the container disk.

## Cloudflare — present, deliberately untouched

The PM team's original page runs on a Worker at
`scalient-gtm.digital-391.workers.dev`, with leads in a Workers KV namespace and
a token-gated CSV export at `/api/leads`. Their `deploy.py` uses a Cloudflare
**global API key**. Nothing here uses it and nothing should — see `CLAUDE.md`.

## Environment variables the Scorecard page will expect

Named, never valued:

- `NEXT_PUBLIC_SITE_URL` — overrides the canonical origin
- `VERCEL_PROJECT_PRODUCTION_URL` — injected by Vercel; the fallback origin
- `NEXT_PUBLIC_META_PIXEL_ID` — absent, so the Pixel is inert
- `NEXT_PUBLIC_BOOKING_URL` — absent, so booking CTAs are hidden
- `LEAD_WEBHOOK_URL` — absent, so leads only reach the function log

## Needs authorisation, currently unusable

- **21st.dev MCP** — registered in project-scope `.mcp.json`, never authorised,
  and `API_KEY_21ST` is unset. The component registry is reachable over plain
  HTTP regardless.
- **motion-primitives registry** — sits behind Vercel's bot check, so
  `shadcn add` fails from this environment. Works from a normal browser.
