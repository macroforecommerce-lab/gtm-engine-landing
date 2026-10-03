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
