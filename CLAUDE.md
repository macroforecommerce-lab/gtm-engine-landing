# gtm-engine-landing

Landing-page work for **Scalient**, a GTM-systems agency (B2B/SaaS/AI), for paid
Meta traffic.

See `memory.md` for what is true now, `project-log.md` for how it got that way,
`connections.md` for what is wired up.

## Standing rules

**This container is ephemeral and has reset three times.** Each reset returned
the repo to an earlier commit and wiped the working tree, destroying committed
work with no reflog and no dangling objects. Treat anything that exists only on
this disk as already lost. Deliverables belong on Vercel, in a git bundle sent
to the user, or both.

**Do not modify the two frozen landing pages.** Their code is not to be edited
and their deployments are not to be replaced:

- `scalient-gtm-landing.vercel.app` — the Next.js rebuild
- `scalient-pm-landing.vercel.app` — the performance-marketing team's page

New landing-page work goes in its own directory and its own Vercel project.

**Never run the audit analyser against a client's site, and never record a
client's score.** `scorecard/audit_proto.py` exists to tell a stranger their
page is weak. Aimed at someone we already work with it is an insult with our
name on it, and a score committed to a repo or written into a pull request is
permanent and public. The client roster in `memory.md` is the list to check
against — ShipVista and Lexroom.ai are both on it, and both were used as test
targets before this rule existed. Verify against `scalient-ai.com`, which is
ours, and the synthetic fixtures in `scorecard/test_audit.py`, which belong to
nobody. A neutral benchmark set needs sign-off on which sites qualify before
any third-party domain goes into the test record.

**Never run `deploy.py` from the PM team's handover zip.** It authenticates with
a Cloudflare *global* API key read from a credentials file on disk. A global key
can do anything on the account. If that page needs redeploying, it is the PM
team's job, and they should be moved to a scoped Workers token.

## Brand

From the brand kit PDF (`Brand_Kit_Scalient_.pdf`), which is authoritative:

| | |
|---|---|
| Display / headings | Montserrat |
| Body | DM Sans |
| Blue | `#0464F6` |
| Cyan | `#04B1DB` |
| Gradient | blue → cyan, 92deg |
| Navy | `#010D3F` |
| Off-white | `#F4F4F4` |
| Charcoal | `#2A2A2A` |

Logo and testimonial photographs are served from the live site and can be pulled
at build time rather than committed: `scalient-ai.com/navbar/scalient-logo.svg`,
`scalient-ai.com/testimonials/*.webp`.

## Working conventions established here

- **Tailwind without preflight.** The stock `@import "tailwindcss"` reflowed the
  page by 283px, because the original styles itself through inline style props.
  Import `tailwindcss/theme.css` and `tailwindcss/utilities.css` directly and
  scope the reset to a wrapper class. Verified pixel-identical afterwards.
- **Scroll reveals must be visible by default.** Server HTML renders fully
  visible; hiding is applied only after hydration, only to elements still below
  the viewport, never under `prefers-reduced-motion`. The page this work
  replaced rendered everything below the fold at `opacity: 0`.
- **Keep deploy trees text-only.** Binary assets are fetched at build time and
  verified against pinned sha256 hashes, so a mismatch fails the build instead
  of silently publishing something unreviewed.
