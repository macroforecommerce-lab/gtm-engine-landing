"""
Prototype for the Scalient instant GTM audit.

Every score below is derived from something observable in the fetched page.
Nothing is randomised, nothing is inferred from the domain name, and a site
that gives us nothing to measure scores low rather than getting a flattering
default - a lead magnet that hands out good scores teaches the prospect the
tool is theatre.

The five dimensions deliberately mirror Scalient's five-part system, so a weak
score points at a specific service rather than a vague "you need help".

The analyser refuses to score rather than score wrongly. Two gates run before
any dimension: a page too thin to read, and a page not in English. Both return
"not scored" with the reason, because a confident wrong number aimed at a
prospect's own homepage costs more than an honest abstention.

Never point this at a client's site, and never record a client's score.
See CLAUDE.md. Verification uses scalient-ai.com, which is ours, plus the
synthetic pages in test_audit.py, which belong to nobody.

Verified 2026-10-03: scalient-ai.com 16/25; test_audit.py fixtures span 0/5 to
5/5 on positioning and trip both refusal gates.

Fixed 2026-10-03, with what the fix changed:
  1. Positioning was length-only: any h1 under 16 words took 3 of 5 whether or
     not it claimed anything. It now has to be well formed AND specific, a
     buzzword inside the h1 costs a point, and the credit for an opening free
     of buzzwords is capped at the strength of the claim, so a page with no h1
     can no longer bank it. A generic-but-tidy h1 drops 5/5 -> 2/5; a page with
     no h1 at all drops 2/5 -> 0/5.
     The defect note this replaces blamed a "truncated" h1. That was wrong, and
     wrong in my own favour: the headline was complete, and the evidence note
     had been capped at 70 characters so it only looked cut off. The cap is now
     120 and marks an elision with an ellipsis, so a note can no longer invent
     a defect in the page being measured.
  2. Buzzwords are matched by stem, so "Leveraging" no longer slips past
     "leverage". Inflections had been reading as clean copy.
  3. Non-English pages are detected and not scored. The English-only
     vocabularies had been scoring an Italian page 0/5 on ICP while its own
     navigation named its buyer precisely - a verdict on the language, not the
     GTM.
  4. New gate, found while fixing the above: a page under 120 visible words is
     not scored. Before, a client-side-rendered shell or a redirect body scored
     near 0/25 and the prospect was told their GTM was broken when the page had
     simply not been read.

Hardened 2026-10-03 for public use: fetch() refuses non-public addresses on the
first request and on every redirect (see check_public_url), because a hosted
version fetches whatever a visitor types.

Open, not yet fixed:
  - Specificity is keyword-based, so an h1 can make a sharp claim in words the
    vocabulary does not carry and miss the bonus.
  - The language gate knows five languages. A sixth reads as "unknown".
  - Real-world spread is evidenced by one site we own plus synthetic fixtures.
    A neutral benchmark set - sites that are neither clients nor prospects -
    would evidence it better, and needs sign-off on which sites qualify.
"""
import ipaddress
import re
import socket
import sys
import urllib.request
from html import unescape
from urllib.parse import urlparse

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

MIN_WORDS = 120          # below this the page was not read, not weak
LANG_MARGIN = 0.04       # how far ahead English must be to count as English

# --- vocabularies -----------------------------------------------------------

# Words that name a buyer. Presence near the top = the page knows who it's for.
ROLE_WORDS = r"(founder|ceo|cto|cmo|revops|sales|marketer|marketing lead|head of|vp of|operator|recruiter|accountant|clinic|agency|manufacturer|distributor|retailer|developer|engineer|designer|hr |procurement|logistics)"
# Company-shape qualifiers: stage, size, model.
SHAPE_WORDS = r"(series [abc]|seed|pre-seed|bootstrapped|smb|mid-market|enterprise|d2c|b2b|saas|ecommerce|e-commerce|marketplace|\d+\s*[-–to]+\s*\d+\s*(people|employees|person)|\d+\+?\s*(employees|people))"
# The tell-tale of an ICP that excludes nobody.
GENERIC_AUDIENCE = r"\b(businesses|companies|teams|organisations|organizations|brands|clients|customers|everyone|anyone|any business|all sizes|businesses of all)\b"

# Matched by stem so inflections are caught: leverage/leverages/leveraging.
BUZZ_STEMS = (
    "innovat", "seamless", "empower", "leverag", "synerg", "robust",
    "holistic", "revolutionar", "revolutioniz", "disrupt", "supercharg",
    "turnkey", "game[- ]chang", "best[- ]in[- ]class", "world[- ]class",
    "cutting[- ]edge", "next[- ]gen", "state[- ]of[- ]the[- ]art",
)
BUZZ_PHRASES = ("unlock your", "transform your business", "one[- ]stop",
                "end[- ]to[- ]end solution")
BUZZWORDS = (r"\b(?:" + "|".join(s + r"\w*" for s in BUZZ_STEMS)
             + "|" + "|".join(BUZZ_PHRASES) + r")")

CTA_WORDS = r"\b(book a|schedule a|get started|start free|request a demo|talk to|contact us|get a quote|sign up|try free|free trial|apply now|get in touch)\b"

SIGNAL_WORDS = r"\b(we're hiring|we are hiring|careers|raised|funding|series [abc]|launched|new release|changelog|press|announcement)\b"

# An h1 ending on one of these continues somewhere else, or was cut off.
DANGLING = {
    "by", "with", "for", "to", "of", "the", "a", "an", "and", "or", "that",
    "this", "your", "our", "in", "on", "at", "from", "is", "are", "as", "it",
    "but", "so", "than", "then", "into", "when", "while", "if", "about",
}

STOPWORDS = {
    "en": "the and of to for with your our is are you we that this from by on at be have will can",
    "it": "il lo la gli le di da in con su per tra che non si una uno dei della delle come anche sono",
    "es": "el la los las de del y en con para que no se una por como su lo al",
    "fr": "le la les de du des et en avec pour que ne se une par comme sur au",
    "de": "der die das und von zu mit fur ist sind sie wir auf im ein eine nicht auch als",
}
STOPWORDS = {k: set(v.split()) for k, v in STOPWORDS.items()}


class UnsafeURL(ValueError):
    """The address cannot be scored. The message is safe to show the visitor."""


def check_public_url(url):
    """Refuse anything that is not an ordinary public web address.

    The server fetches whatever a visitor types, so without this the tool can be
    pointed at the host's own network, a cloud metadata address, or a local file.
    Applied to the first request and to every redirect.

    Residual risk, accepted for now: the name is resolved here and again when the
    connection is made, so a DNS record that changes between the two could slip
    through. Closing it means connecting to the resolved address directly.
    """
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise UnsafeURL("Only http and https addresses can be scored.")
    if p.username or p.password:
        raise UnsafeURL("Addresses with a username or password cannot be scored.")
    if p.port not in (None, 80, 443):
        raise UnsafeURL("Only standard web ports can be scored.")
    host = p.hostname
    if not host or "." not in host:
        raise UnsafeURL("That does not look like a website address.")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise UnsafeURL("We could not find that website. Check the address and try again.")
    for info in infos:
        if not ipaddress.ip_address(info[4][0].split("%")[0]).is_global:
            raise UnsafeURL("That address is not a public website.")
    return host


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=25):
    url = (url or "").strip()
    if len(url) > 300:
        raise UnsafeURL("That address is too long.")
    if "://" not in url:
        url = "https://" + url
    check_public_url(url)
    opener = urllib.request.build_opener(_CheckedRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with opener.open(req, timeout=timeout) as r:
        raw = r.read(1_500_000)
        final = r.geturl()
    return raw.decode("utf-8", "replace"), final


def pl(n, word, plural=None):
    """'1 role', '2 roles'. User-facing notes must not say 'role(s)'."""
    return f"{n} {word if n == 1 else (plural or word + 's')}"


def visible_text(html):
    t = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", unescape(t)).strip()


def head_text(html):
    """Text most likely to be above the fold - h1/h2 and the first chunk of body."""
    heads = " ".join(re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, flags=re.S | re.I))
    heads = re.sub(r"<[^>]+>", " ", heads)
    return re.sub(r"\s+", " ", unescape(heads)).strip()


def h1_of(html):
    m = re.findall(r"<h1[^>]*>(.*?)</h1>", html, flags=re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m[0]))).strip()


def show(s, cap=120):
    """Quote page text without inventing a truncation: elision is marked."""
    return s if len(s) <= cap else s[:cap].rstrip() + "…"


def detect_language(html, text):
    """Return (code, evidence). The lang attribute wins; stopwords break ties."""
    attr = re.findall(r"<html[^>]*\blang=[\"']?([A-Za-z]{2})", html, flags=re.I)
    words = re.findall(r"[a-zà-ÿ']+", text.lower())
    rates = {k: sum(1 for w in words if w in v) / max(1, len(words))
             for k, v in STOPWORDS.items()}
    best = max(rates, key=rates.get)
    if attr:
        code = attr[0].lower()
        return code, f'<html lang="{attr[0]}">, {code} stopword rate {rates.get(code, 0):.3f}'
    if rates["en"] >= 0.05 and rates["en"] >= rates[best] - LANG_MARGIN:
        return "en", f'no lang attribute, en stopword rate {rates["en"]:.3f}'
    if rates[best] >= 0.05:
        return best, f'no lang attribute, {best} stopword rate {rates[best]:.3f} vs en {rates["en"]:.3f}'
    return "unknown", f'no lang attribute, no stopword vocabulary above 0.05 (en {rates["en"]:.3f})'


def score_icp(html, text, head):
    """Dimension 1 -> ICP definition. Does the page name a buyer, or address the void?"""
    hits, notes = 0, []
    top = (head + " " + text[:1200]).lower()
    roles = len(set(re.findall(ROLE_WORDS, top)))
    shapes = len(set(m if isinstance(m, str) else m[0] for m in re.findall(SHAPE_WORDS, top)))
    generic = len(re.findall(GENERIC_AUDIENCE, top))

    if roles:
        hits += 2; notes.append(f"names {pl(roles, 'buyer role')} up top")
    else:
        notes.append("no buyer role named above the fold")
    if shapes:
        hits += 2; notes.append(f"qualifies company shape ({pl(shapes, 'signal')})")
    else:
        notes.append("no company stage/size/model qualifier")
    if generic >= 3:
        hits -= 1; notes.append(f"leans on generic audience words {generic}x")
    elif generic == 0 and roles:
        hits += 1; notes.append("avoids generic audience language")
    return max(0, min(5, hits)), notes


def score_positioning(html, text, head):
    """Dimension 2 -> messaging. Is there one sharp claim, or fog?

    A claim has to be well formed *and* say something. Length alone was the old
    test and it passed anything short enough to fit.

    Clean language is credited only up to the strength of the claim it is
    keeping clean: a page with no h1 cannot earn points for an opening free of
    buzzwords, because there is no claim there to dilute.
    """
    notes = []
    h1 = h1_of(html)
    words = h1.split()

    if not h1:
        claim = 0
        notes.append("no <h1>, so nothing claims the page")
    elif words[-1].strip(".,:;!?-\u2013").lower() in DANGLING:
        claim = 1
        notes.append(f'h1 ends on "{words[-1]}", so the claim continues elsewhere or was cut')
    elif len(words) < 4:
        claim = 1
        notes.append(f'h1 is {len(words)} words, a slogan and not a claim: "{show(h1)}"')
    elif len(words) > 16:
        claim = 1
        notes.append(f"h1 is {len(words)} words, too long to land")
    else:
        claim = 2
        notes.append(f'h1 reads: "{show(h1)}"')
        if (re.search(r"\d", h1) or re.search(ROLE_WORDS, h1, flags=re.I)
                or re.search(r"[%$\u20b9]", h1)):
            claim += 1; notes.append("h1 is specific: it names a number or a buyer")
        else:
            notes.append("h1 is well formed but names no number and no buyer")

    if h1 and re.search(BUZZWORDS, h1, flags=re.I):
        found = re.findall(BUZZWORDS, h1, flags=re.I)
        claim -= 1; notes.append(f"buzzword in the h1 itself: {', '.join(found)}")
    claim = max(0, claim)

    buzz = len(re.findall(BUZZWORDS, text[:4000], flags=re.I))
    if buzz == 0:
        bonus = 2; notes.append("no filler buzzwords in the opening")
    elif buzz <= 2:
        bonus = 1; notes.append(f"{pl(buzz, 'buzzword')} in the opening")
    else:
        bonus = 0; notes.append(f"{buzz} buzzwords in the opening, so the claim is diluted")

    if bonus > claim:
        notes.append(f"clean-language credit held to {claim}: it cannot outrank the claim")
        bonus = claim
    return max(0, min(5, claim + bonus)), notes


def score_proof(html, text):
    """Dimension 3 -> what outbound can actually cite."""
    hits, notes = 0, []
    numbers = re.findall(r"(?<![\w])(?:[₹$]\s?\d[\d,.]*\s?[KkMmLl]?|\d[\d,.]*\s?(?:%|x\b)|\d{2,}\+)", text[:9000])
    quotes = len(re.findall(r"[“\"][^”\"]{60,400}[”\"]", text[:14000]))
    testimonial_markers = len(re.findall(r"\b(founder|ceo|cto|director|head of|vp)\s*(,|at|of)\s*[A-Z]", text[:14000]))

    if len(numbers) >= 5:
        hits += 3; notes.append(f"{len(numbers)} concrete numbers on the page")
    elif numbers:
        hits += 1; notes.append(f"only {pl(len(numbers), 'concrete number')}")
    else:
        notes.append("no concrete numbers, so nothing for outbound to quote")

    if quotes and testimonial_markers:
        hits += 2; notes.append(f"{pl(quotes, 'quote')} with attributed titles")
    elif quotes:
        hits += 1; notes.append(f"{pl(quotes, 'quote')}, attribution unclear")
    else:
        notes.append("no attributed customer quotes")
    return max(0, min(5, hits)), notes


def score_conversion(html, text):
    """Dimension 4 -> full-funnel distribution. One road in, or twelve?"""
    hits, notes = 0, []
    ctas = re.findall(CTA_WORDS, text[:14000], flags=re.I)
    distinct = len(set(c.lower().strip() for c in ctas))
    inputs = len(re.findall(r"<input[^>]*type=[\"']?(?!hidden)", html, flags=re.I))
    booking = bool(re.search(r"(calendly|cal\.com|hubspot\.com/meetings|savvycal|book(ing)?[- ]a[- ]call)", html, flags=re.I))

    if distinct == 0:
        notes.append("no clear call to action found")
    elif distinct <= 2:
        hits += 3; notes.append(f"{pl(distinct, 'distinct call to action')}: focused")
    else:
        hits += 1; notes.append(f"{distinct} competing CTA types, so attention is split")

    if booking:
        hits += 2; notes.append("direct booking link present")
    else:
        notes.append("no direct booking path")

    if inputs > 6:
        hits -= 1; notes.append(f"{inputs} visible form fields, heavy for cold traffic")
    return max(0, min(5, hits)), notes


def score_founder(html, text):
    """Dimension 5 -> founder-led signal. Warm outbound needs a face."""
    hits, notes = 0, []
    li_personal = re.findall(r"linkedin\.com/in/[A-Za-z0-9\-_%]+", html)
    li_company = re.findall(r"linkedin\.com/company/[A-Za-z0-9\-_%]+", html)
    about = bool(re.search(r"\b(about us|our team|meet the team|founded by|our story)\b", text, flags=re.I))
    signals = len(set(re.findall(SIGNAL_WORDS, text, flags=re.I)))

    if li_personal:
        hits += 3; notes.append(f"{pl(len(set(li_personal)), 'personal LinkedIn profile')} linked")
    elif li_company:
        hits += 1; notes.append("company LinkedIn only, no person to follow")
    else:
        notes.append("no LinkedIn presence linked at all")

    if about:
        hits += 1; notes.append("has an about/team page")
    if signals:
        hits += 1; notes.append(f"{pl(signals, 'outbound-usable signal')} (hiring, funding, launches)")
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


def neutral_observations(html, text):
    """What can still be said when the vocabularies do not apply."""
    out = []
    nums = re.findall(r"(?<![\w])(?:[₹$]\s?\d[\d,.]*\s?[KkMmLl]?|\d[\d,.]*\s?(?:%|x\b)|\d{2,}\+)", text[:9000])
    out.append(f"{pl(len(nums), 'concrete number')} on the page")
    personal = len(set(re.findall(r"linkedin\.com/in/[A-Za-z0-9\-_%]+", html)))
    company = len(set(re.findall(r"linkedin\.com/company/[A-Za-z0-9\-_%]+", html)))
    out.append(f"{pl(personal, 'personal LinkedIn link')} and {pl(company, 'company LinkedIn link')}")
    booking = bool(re.search(r"(calendly|cal\.com|hubspot\.com/meetings|savvycal)", html, flags=re.I))
    out.append("booking link present" if booking else "no booking link")
    inputs = len(re.findall(r"<input[^>]*type=[\"']?(?!hidden)", html, flags=re.I))
    out.append(f"{pl(inputs, 'visible form field')}")
    h1 = h1_of(html)
    out.append(f'h1 is {len(h1.split())} words: "{show(h1)}"' if h1 else "no <h1>")
    return out


LANGUAGE_NAMES = {"it": "Italian", "es": "Spanish", "fr": "French", "de": "German",
                  "pt": "Portuguese", "nl": "Dutch", "ja": "Japanese", "zh": "Chinese",
                  "ar": "Arabic", "hi": "Hindi", "ru": "Russian"}


def audit(url, timeout=25):
    html, final = fetch(url, timeout=timeout)
    text = visible_text(html)
    head = head_text(html)
    words = len(text.split())

    if words < MIN_WORDS:
        return {"url": final, "scorable": False,
                "reason": f"We could only find {pl(words, 'word')} of text on that page, which is too little to judge. "
                          "It may load its content with JavaScript, sit behind a login, or just redirect somewhere else.",
                "detail": f"{words} visible words, under the {MIN_WORDS}-word floor",
                "neutral": neutral_observations(html, text)}

    lang, evidence = detect_language(html, text)
    if lang != "en":
        name = LANGUAGE_NAMES.get(lang)
        what = f"in {name}" if name else "not in English"
        return {"url": final, "scorable": False, "language": lang,
                "reason": f"That page looks {what}, and the scorecard only reads English. "
                          "Any score would reflect the language and not your go-to-market, so we have not given one.",
                "detail": f"language {lang}: {evidence}",
                "neutral": neutral_observations(html, text)}

    out, total = [], 0
    for name, fn, fix in DIMENSIONS:
        args = (html, text, head) if fn in (score_icp, score_positioning) else (html, text)
        s, notes = fn(*args)
        total += s
        out.append({"dimension": name, "score": s, "fixed_by": fix, "evidence": notes})
    return {"url": final, "scorable": True, "language": lang,
            "total": total, "max": len(DIMENSIONS) * 5, "dimensions": out}


if __name__ == "__main__":
    for target in sys.argv[1:]:
        try:
            r = audit(target)
        except UnsafeURL as e:
            print(f"\n{target}\n  REFUSED: {e}")
            continue
        except Exception as e:
            print(f"\n{target}\n  FETCH FAILED: {type(e).__name__}: {e}")
            continue
        print(f"\n{'=' * 74}")
        if not r["scorable"]:
            print(f"{r['url']}   ->   NOT SCORED")
            print(f"  {r['reason']}")
            if r.get("detail"):
                print(f"  ({r['detail']})")
            print("  What can still be seen:")
            for e in r["neutral"]:
                print(f"          - {e}")
            continue
        print(f"{r['url']}   ->   {r['total']}/{r['max']}")
        for d in r["dimensions"]:
            bar = "●" * d["score"] + "○" * (5 - d["score"])
            print(f"  {bar}  {d['dimension']:<19} {d['score']}/5   fix: {d['fixed_by']}")
            for e in d["evidence"]:
                print(f"          - {e}")
