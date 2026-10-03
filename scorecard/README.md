# Scorecard page

The from-scratch landing page for Meta paid traffic. **Separate from the two
frozen pages** — nothing here touches their code or their deployments.

Status: upstream of code. The offer is locked, the section map is proposed, the
hero angle is undecided. See `../memory.md` → Active work.

## `web/` — hero mock

`web/index.html`: static hero plus one navy band, on a white base. Every line of
copy is a bracketed placeholder for the user to fill; only the locked offer
sentence and the five dimension names are real. Open it directly in a browser.
Fonts load from Google Fonts, so offline it falls back to Arial.

## `audit_proto.py`

Prototype of the instant GTM audit — the mechanism the whole offer rests on.
Scores a URL across five dimensions from observable page signals.

```
python3 audit_proto.py scalient-ai.com
python3 test_audit.py            # 25 fixture assertions, no network
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
