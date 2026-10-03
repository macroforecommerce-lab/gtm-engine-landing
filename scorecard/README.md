# Scorecard page

The from-scratch landing page for Meta paid traffic. **Separate from the two
frozen pages** — nothing here touches their code or their deployments.

Status: upstream of code. The offer is locked, the section map is proposed, the
hero angle is undecided. See `../memory.md` → Active work.

## `web/` — the page

A static page (`index.html`, `styles.css`, `app.js`, `privacy.html`) with three
Python functions in `web/api/`: `audit` scores a URL, `lead` captures an email and
releases the three fixes, `config` hands the page its Pixel id and booking link.
All copy is **draft, for review**. `web/api/_audit_proto.py` is the analyser; files
starting with an underscore are modules, not routes.

Run it locally: `python3 dev_server.py` then open http://127.0.0.1:8765. Tests:
`python3 test_audit.py` (analyser, address checks, wording) and
`python3 test_logic.py` (fixes, leads, config, rate limits). Both run offline.

### Deploying to Vercel

1. Import the GitHub repo as a new project.
2. **Root Directory: `scorecard/web`**. Framework preset: Other. No build command.
3. Environment variables (all optional, the page works without them):
   `NEXT_PUBLIC_META_PIXEL_ID`, `NEXT_PUBLIC_BOOKING_URL`, `LEAD_WEBHOOK_URL`.
4. The page ships `noindex`. Remove it from `index.html` and add a canonical
   when the final domain is attached.

Without `LEAD_WEBHOOK_URL`, leads are written to the function log only.

## `audit_proto.py`

Prototype of the instant GTM audit — the mechanism the whole offer rests on.
Scores a URL across five dimensions from observable page signals.

```
python3 web/api/_audit_proto.py scalient-ai.com
python3 test_audit.py            # offline
```

**Never point this at a client's site, and never record a client's score.** The
tool exists to tell a stranger their page is weak; aimed at someone we already
work with, it is an insult with our name on it, and a score written into a repo
or a pull request is permanent. Verification uses `scalient-ai.com`, which is
ours, and the synthetic pages in `test_audit.py`, which belong to nobody.

Every score traces to something in the fetched page. Nothing is randomised and
nothing is inferred from the domain name. A page that offers nothing to measure
scores low rather than receiving a flattering default, because a lead magnet
that hands out good scores teaches the prospect it is theatre.

Two gates run before any dimension, and both refuse to score rather than score
wrongly: a page under 120 visible words was not read (client-side rendered,
gated, or a redirect shell), and a page not in English would be measured by
English-only vocabularies. Each returns the reason plus the observations that
survive without vocabulary — numbers, LinkedIn links, booking link, form
fields, h1 length.

Verified 2026-10-03: `scalient-ai.com` **16/25**; fixtures span 0/5 to 5/5 on
positioning and trip both gates.

Four defects found and fixed 2026-10-03 — positioning scored on length alone,
buzzwords missed inflections, non-English pages were scored on English
vocabularies, and a page too thin to read scored as a page that was weak. The
docstring records each one and what the fix moved. Three limits remain open,
listed there, including that real-world spread now rests on one site we own.
