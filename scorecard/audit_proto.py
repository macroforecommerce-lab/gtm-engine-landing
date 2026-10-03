#!/usr/bin/env python3
"""
Prototype for the Scalient instant GTM audit.

Every score below is derived from something observable in the fetched page.
Nothing is randomised, nothing is inferred from the domain name, and a site
that gives us nothing to measure scores low rather than getting a flattering
default — a lead magnet that hands out good scores teaches the prospect the
tool is theatre.

The five dimensions deliberately mirror Scalient's five-part system, so a weak
score points at a specific service rather than a vague "you need help".

Measured on live sites 2026-10-03:
    scalient-ai.com 17/25 · shipvista.com 16/25 · lexroom.ai 9/25

Known defects, all open:
  1. Positioning scores too generously — gave 5/5 to a truncated h1. Needs a
     quality check, not just a length check.
  2. Buzzword matching misses inflections — "Leveraging" slips past "leverage".
  3. Non-English pages score unfairly on ICP: the vocabularies are English-only,
     so an Italian site scored 0/5 for linguistic rather than GTM reasons.
"""
import re
import sys
import urllib.request
from html import unescape

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# --- vocabularies -----------------------------------------------------------

# Words that name a buyer. Presence near the top = the page knows who it's for.
ROLE_WORDS = r"(founder|ceo|cto|cmo|revops|sales|marketer|marketing lead|head of|vp of|operator|recruiter|accountant|clinic|agency|manufacturer|distributor|retailer|developer|engineer|designer|hr |procurement|logistics)"
# Company-shape qualifiers: stage, size, model.
SHAPE_WORDS = r"(series [abc]|seed|pre-seed|bootstrapped|smb|mid-market|enterprise|d2c|b2b|saas|ecommerce|e-commerce|marketplace|\d+\s*[-–to]+\s*\d+\s*(people|employees|person)|\d+\+?\s*(employees|people))"
# The tell-tale of an ICP that excludes nobody.
GENERIC_AUDIENCE = r"\b(businesses|companies|teams|organisations|organizations|brands|clients|customers|everyone|anyone|any business|all sizes|businesses of all)\b"

BUZZWORDS = r"\b(innovative|cutting[- ]edge|world[- ]class|best[- ]in[- ]class|seamless|empower|leverage|synergy|robust|holistic|next[- ]generation|state[- ]of[- ]the[- ]art|revolutionary|game[- ]chang|unlock your|transform your business|one[- ]stop|end[- ]to[- ]end solution)\b"

CTA_WORDS = r"\b(book a|schedule a|get started|start free|request a demo|talk to|contact us|get a quote|sign up|try free|free trial|apply now|get in touch)\b"

SIGNAL_WORDS = r"\b(we're hiring|we are hiring|careers|raised|funding|series [abc]|launched|new release|changelog|press|announcement)\b"


def fetch(url):
    if not url.startswith("http"):
        url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read(1_500_000)
    return raw.decode("utf-8", "replace"), url


def visible_text(html):
    t = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", unescape(t)).strip()


def head_text(html):
    """Text most likely to be above the fold — h1/h2 and the first chunk of body."""
    heads = " ".join(re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, flags=re.S | re.I))
    heads = re.sub(r"<[^>]+>", " ", heads)
    return re.sub(r"\s+", " ", unescape(heads)).strip()


def score_icp(html, text, head):
    """Dimension 1 → ICP definition. Does the page name a buyer, or address the void?"""
    hits, notes = 0, []
    top = (head + " " + text[:1200]).lower()
    roles = len(set(re.findall(ROLE_WORDS, top)))
    shapes = len(set(m if isinstance(m, str) else m[0] for m in re.findall(SHAPE_WORDS, top)))
    generic = len(re.findall(GENERIC_AUDIENCE, top))

    if roles:
        hits += 2; notes.append(f"names {roles} buyer role(s) up top")
    else:
        notes.append("no buyer role named above the fold")
    if shapes:
        hits += 2; notes.append(f"qualifies company shape ({shapes} signal(s))")
    else:
        notes.append("no company stage/size/model qualifier")
    if generic >= 3:
        hits -= 1; notes.append(f"leans on generic audience words {generic}x")
    elif generic == 0 and roles:
        hits += 1; notes.append("avoids generic audience language")
    return max(0, min(5, hits)), notes


def score_positioning(html, text, head):
    """Dimension 2 → messaging. Is there one sharp claim, or fog?"""
    hits, notes = 0, []
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, flags=re.S | re.I)
    h1_text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", h1[0]))).strip() if h1 else ""

    if not h1_text:
        notes.append("no <h1> — nothing claims the page")
    elif len(h1_text.split()) > 16:
        hits += 1; notes.append(f"h1 is {len(h1_text.split())} words — too long to land")
    else:
        hits += 3; notes.append(f'h1 reads: "{h1_text[:70]}"')

    buzz = len(re.findall(BUZZWORDS, text[:4000], flags=re.I))
    if buzz == 0:
        hits += 2; notes.append("no filler buzzwords in the opening")
    elif buzz <= 2:
        hits += 1; notes.append(f"{buzz} buzzword(s) in the opening")
    else:
        notes.append(f"{buzz} buzzwords in the opening — claim is diluted")
    return max(0, min(5, hits)), notes


def score_proof(html, text):
    """Dimension 3 → what outbound can actually cite."""
    hits, notes = 0, []
    numbers = re.findall(r"(?<![\w])(?:[₹$]\s?\d[\d,.]*\s?[KkMmLl]?|\d[\d,.]*\s?(?:%|x\b)|\d{2,}\+)", text[:9000])
    quotes = len(re.findall(r"[“\"][^”\"]{60,400}[”\"]", text[:14000]))
    testimonial_markers = len(re.findall(r"\b(founder|ceo|cto|director|head of|vp)\s*(,|at|of)\s*[A-Z]", text[:14000]))

    if len(numbers) >= 5:
        hits += 3; notes.append(f"{len(numbers)} concrete numbers on the page")
    elif numbers:
        hits += 1; notes.append(f"only {len(numbers)} concrete number(s)")
    else:
        notes.append("no concrete numbers — nothing for outbound to quote")

    if quotes and testimonial_markers:
        hits += 2; notes.append(f"{quotes} quote(s) with attributed titles")
    elif quotes:
        hits += 1; notes.append(f"{quotes} quote(s), attribution unclear")
    else:
        notes.append("no attributed customer quotes")
    return max(0, min(5, hits)), notes


def score_conversion(html, text):
    """Dimension 4 → full-funnel distribution. One road in, or twelve?"""
    hits, notes = 0, []
    ctas = re.findall(CTA_WORDS, text[:14000], flags=re.I)
    distinct = len(set(c.lower().strip() for c in ctas))
    inputs = len(re.findall(r"<input[^>]*type=[\"']?(?!hidden)", html, flags=re.I))
    booking = bool(re.search(r"(calendly|cal\.com|hubspot\.com/meetings|savvycal|book(ing)?[- ]a[- ]call)", html, flags=re.I))

    if distinct == 0:
        notes.append("no clear call to action found")
    elif distinct <= 2:
        hits += 3; notes.append(f"{distinct} distinct CTA type(s) — focused")
    else:
        hits += 1; notes.append(f"{distinct} competing CTA types — attention is split")

    if booking:
        hits += 2; notes.append("direct booking link present")
    else:
        notes.append("no direct booking path")

    if inputs > 6:
        hits -= 1; notes.append(f"{inputs} visible form fields — heavy for cold traffic")
    return max(0, min(5, hits)), notes


def score_founder(html, text):
    """Dimension 5 → founder-led signal. Warm outbound needs a face."""
    hits, notes = 0, []
    li_personal = re.findall(r"linkedin\.com/in/[A-Za-z0-9\-_%]+", html)
    li_company = re.findall(r"linkedin\.com/company/[A-Za-z0-9\-_%]+", html)
    about = bool(re.search(r"\b(about us|our team|meet the team|founded by|our story)\b", text, flags=re.I))
    signals = len(set(re.findall(SIGNAL_WORDS, text, flags=re.I)))

    if li_personal:
        hits += 3; notes.append(f"{len(set(li_personal))} personal LinkedIn profile(s) linked")
    elif li_company:
        hits += 1; notes.append("company LinkedIn only — no person to follow")
    else:
        notes.append("no LinkedIn presence linked at all")

    if about:
        hits += 1; notes.append("has an about/team page")
    if signals:
        hits += 1; notes.append(f"{signals} outbound-usable signal(s) (hiring, funding, launches)")
    else:
        notes.append("no timely signals a cold email could reference")
    return max(0, min(5, hits)), notes


DIMENSIONS = [
    ("ICP clarity",        score_icp,         "ICP definition & messaging"),
    ("Positioning",        score_positioning, "ICP definition & messaging"),
    ("Proof for outbound", score_proof,       "Clay & AI-powered funnels"),
    ("Conversion path",    score_conversion,  "Full-funnel distribution"),
    ("Founder signal",     score_founder,     "LinkedIn personal branding"),
]


def audit(url):
    html, final = fetch(url)
    text = visible_text(html)
    head = head_text(html)
    out, total = [], 0
    for name, fn, fix in DIMENSIONS:
        args = (html, text, head) if fn in (score_icp, score_positioning) else (html, text)
        s, notes = fn(*args)
        total += s
        out.append({"dimension": name, "score": s, "fixed_by": fix, "evidence": notes})
    return {"url": final, "total": total, "max": len(DIMENSIONS) * 5, "dimensions": out}


if __name__ == "__main__":
    for target in sys.argv[1:]:
        try:
            r = audit(target)
        except Exception as e:
            print(f"\n{target}\n  FETCH FAILED: {type(e).__name__}: {e}")
            continue
        print(f"\n{'=' * 74}\n{r['url']}   →   {r['total']}/{r['max']}")
        for d in r["dimensions"]:
            bar = "●" * d["score"] + "○" * (5 - d["score"])
            print(f"  {bar}  {d['dimension']:<19} {d['score']}/5   fix: {d['fixed_by']}")
            for e in d["evidence"]:
                print(f"          · {e}")
