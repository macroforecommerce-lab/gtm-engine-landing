# Scorecard page

The from-scratch landing page for Meta paid traffic. **Separate from the two
frozen pages** — nothing here touches their code or their deployments.

Status: upstream of code. The offer is locked, the section map is proposed, the
hero angle is undecided. See `../memory.md` → Active work.

## `audit_proto.py`

Prototype of the instant GTM audit — the mechanism the whole offer rests on.
Scores a URL across five dimensions from observable page signals.

```
python3 audit_proto.py scalient-ai.com shipvista.com lexroom.ai
```

Every score traces to something in the fetched page. Nothing is randomised and
nothing is inferred from the domain name; a page that offers nothing to measure
scores low rather than receiving a flattering default, because a lead magnet that
hands out good scores teaches the prospect it is theatre.

Measured on live sites: scalient-ai.com **17/25**, shipvista.com **16/25**,
lexroom.ai **9/25**. That spread is the evidence it discriminates.

Three known defects, all open — see `../memory.md` for detail: positioning scores
too generously, buzzword matching misses inflections, and non-English pages are
scored unfairly on ICP.
