"""
Request logic for the Scorecard page, kept apart from the HTTP handlers so it can
be tested without a server. Files starting with an underscore are not routes.

Environment variables, read here and nowhere else (names only, never values):
  LEAD_WEBHOOK_URL            where leads are POSTed; absent -> function log only
  NEXT_PUBLIC_META_PIXEL_ID   absent -> no Pixel is loaded
  NEXT_PUBLIC_BOOKING_URL     absent -> the page falls back to email
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _audit_proto as a  # noqa: E402

AUDIT_TIMEOUT = 8            # seconds; the function's own limit is short
RATE_LIMITS, RATE_WINDOW = {"audit": 12, "lead": 12}, 600   # per visitor address, per bucket
CONTACT_EMAIL = "info@scalient-ai.com"
BLOCKED = (401, 403, 429, 451)   # the site refused our reader; not the visitor's fault
UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid")
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")

_hits = {}   # ip -> [timestamps]. Per instance, so best effort, not a guarantee.


def rate_limited(ip, bucket="audit", now=None):
    """Separate buckets so one visitor's whole journey (audit, email, route answer)
    does not spend a single shared allowance. Shared mobile and office addresses
    carry several real visitors, so the limits are generous on purpose."""
    now = now if now is not None else time.time()
    key = (bucket, ip)
    recent = [t for t in _hits.get(key, []) if now - t < RATE_WINDOW]
    if len(recent) >= RATE_LIMITS[bucket]:
        _hits[key] = recent
        return True
    recent.append(now)
    _hits[key] = recent
    return False


# --- fixes ------------------------------------------------------------------
# One action per dimension, chosen by the first evidence note it matches. The
# order of rules inside a dimension is most-damaging first.

FIX_RULES = {
    "ICP clarity": [
        ("no buyer role", "Name the buyer on the first screen: the role your best customers hold, such as founder, head of growth or RevOps."),
        ("no company stage", "Say which companies this is for by stage, size or model, so the right visitors recognise themselves."),
        ("generic audience", "Replace words like “businesses” and “companies” near the top with the specific buyer you win most often."),
    ],
    "Positioning": [
        ("no <h1>", "Add one headline that says what you do and who for. Right now nothing on the page makes a claim."),
        ("ends on", "Finish the headline as a complete claim. It currently ends on a connecting word."),
        ("a slogan", "Turn the headline from a slogan into a claim: say what you do and who it is for."),
        ("too long", "Cut the headline down to one claim a visitor can take in at a glance."),
        ("buzzword in the h1", "Remove the filler words from your headline and say the plain thing."),
        ("names no number", "Put a number or name the buyer in your headline. A precise claim beats a polished one."),
        ("buzzwords in the opening", "Cut the filler words from your opening paragraph; every one dilutes the claim."),
    ],
    "Proof for outbound": [
        ("no concrete numbers", "Publish real numbers: results, timeframes, counts. Outbound can only quote what you have put on the page."),
        ("only", "Add more concrete numbers. One or two is not enough for an outbound message to quote."),
        ("no attributed customer quotes", "Add customer quotes with a name, role and company."),
        ("attribution unclear", "Attribute each quote with a name, role and company; unattributed quotes read as invented."),
    ],
    "Conversion path": [
        ("no clear call to action", "Add one clear call to action above the fold."),
        ("competing CTA", "Pick one call to action and make every button say it."),
        ("visible form fields", "Cut the form to the fewest fields that qualify a lead. Every extra field costs you cold traffic."),
        ("no direct booking", "Add a direct booking link so a ready buyer can book without waiting for a reply."),
    ],
    "Founder signal": [
        ("no LinkedIn presence", "Link LinkedIn from the site, a founder profile first and then the company page."),
        ("company LinkedIn only", "Link a founder's personal LinkedIn profile. Warm outbound needs a person to follow."),
        ("no timely signals", "Publish something outbound can reference: a launch, a hire, a milestone."),
    ],
}
FIX_DEFAULT = {
    "ICP clarity": "Tighten who the page is for until a stranger can tell in five seconds whether it is them.",
    "Positioning": "Sharpen the headline into one specific claim.",
    "Proof for outbound": "Add proof outbound can cite: numbers and named customers.",
    "Conversion path": "Reduce the page to one clear route to a conversation.",
    "Founder signal": "Give the page a person: a founder profile and something recent to reference.",
}
# Ties go to whichever moves pipeline fastest.
PRIORITY = ["Conversion path", "Proof for outbound", "Positioning", "ICP clarity", "Founder signal"]


def pick_fixes(dimensions, limit=3):
    weak = [d for d in dimensions if d["score"] < 5]
    weak.sort(key=lambda d: (d["score"], PRIORITY.index(d["dimension"])))
    out = []
    for d in weak[:limit]:
        action = FIX_DEFAULT[d["dimension"]]
        for needle, text in FIX_RULES[d["dimension"]]:
            if any(needle in note for note in d["evidence"]):
                action = text
                break
        out.append({"dimension": d["dimension"], "score": d["score"],
                    "fixed_by": d["fixed_by"], "action": action})
    return out


# --- audit ------------------------------------------------------------------

def public_audit(result):
    if not result["scorable"]:
        return {"ok": True, "scorable": False, "url": result["url"],
                "reason": result["reason"], "neutral": result["neutral"]}
    return {"ok": True, "scorable": True, "url": result["url"],
            "total": result["total"], "max": result["max"],
            "dimensions": [{"dimension": d["dimension"], "score": d["score"], "max": 5,
                            "fixed_by": d["fixed_by"], "evidence": d["evidence"]}
                           for d in result["dimensions"]]}


def run_audit(body, ip="unknown"):
    url = (body.get("url") or "").strip() if isinstance(body, dict) else ""
    if not url:
        return 400, {"ok": False, "error": "Enter your website address."}
    if rate_limited(ip, "audit"):
        return 429, {"ok": False, "error": "That is a lot of scorecards in a short time. Try again in a few minutes."}
    try:
        return 200, public_audit(a.audit(url, timeout=AUDIT_TIMEOUT))
    except a.UnsafeURL as e:
        return 400, {"ok": False, "error": str(e)}
    except urllib.error.HTTPError as e:
        if e.code in BLOCKED:
            return 200, {"ok": True, "scorable": False, "url": url,
                         "reason": f"That website would not let our reader in (it answered {e.code}), so we could not read it. "
                                   "Many sites block automated visitors. That says nothing about how it scores.",
                         "neutral": []}
        return 502, {"ok": False, "error": f"That website answered with an error ({e.code}), so we could not read it."}
    except (urllib.error.URLError, TimeoutError, OSError):
        return 502, {"ok": False, "error": "We could not reach that website. Check the address and try again."}
    except Exception as e:   # never leak internals to a visitor
        print(f"AUDIT_ERROR {type(e).__name__}: {e}", file=sys.stderr)
        return 500, {"ok": False, "error": "Something went wrong on our side. Please try again."}


# --- leads ------------------------------------------------------------------

def clean_utm(raw):
    if not isinstance(raw, dict):
        return {}
    return {k: str(raw[k])[:200] for k in UTM_KEYS if raw.get(k)}


def deliver(record):
    """Send the lead onward. Always logs, so a failed webhook cannot lose it."""
    print("LEAD " + json.dumps(record, ensure_ascii=False), file=sys.stderr)
    hook = os.environ.get("LEAD_WEBHOOK_URL", "").strip()
    if not hook.startswith("https://"):
        return "log"
    try:
        req = urllib.request.Request(hook, data=json.dumps(record).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5).read(1024)
        return "webhook"
    except Exception as e:
        print(f"WEBHOOK_ERROR {type(e).__name__}: {e}", file=sys.stderr)
        return "log"


def submit_lead(body, ip="unknown"):
    if not isinstance(body, dict):
        return 400, {"ok": False, "error": "Something was wrong with that request."}
    if body.get("hp"):                      # honeypot: a human never fills this in
        return 200, {"ok": True, "fixes": []}
    event = body.get("event", "lead")
    email = (body.get("email") or "").strip()
    if event not in ("lead", "route") or not EMAIL_RE.match(email):
        return 400, {"ok": False, "error": "Enter a valid email address."}
    if event == "lead" and rate_limited(ip, "lead"):
        return 429, {"ok": False, "error": "Too many requests. Try again in a few minutes."}

    record = {"event": event, "email": email, "ts": int(time.time()),
              "source": "scorecard", "utm": clean_utm(body.get("utm"))}

    if event == "route":
        inhouse = body.get("inhouse") in (True, "yes")
        record["inhouse"] = inhouse
        deliver(record)
        return 200, {"ok": True, "path": "gtm-install" if inhouse else "done-for-you"}

    url = (body.get("url") or "").strip()
    record["url"] = url[:300]
    fixes = []
    try:
        result = a.audit(url, timeout=AUDIT_TIMEOUT)
        if result["scorable"]:
            fixes = pick_fixes(result["dimensions"])
            record["total"] = result["total"]
            record["scores"] = {d["dimension"]: d["score"] for d in result["dimensions"]}
        else:
            record["note"] = "not scored: " + (result.get("detail") or result["reason"])[:120]
    except Exception as e:
        record["note"] = f"audit failed: {type(e).__name__}"
    deliver(record)
    return 200, {"ok": True, "fixes": fixes}


# --- config -----------------------------------------------------------------

def get_config():
    pixel = os.environ.get("NEXT_PUBLIC_META_PIXEL_ID", "").strip()
    booking = os.environ.get("NEXT_PUBLIC_BOOKING_URL", "").strip()
    return {"pixelId": pixel if pixel.isdigit() else "",
            "bookingUrl": booking if booking.startswith("https://") else "",
            "contactEmail": CONTACT_EMAIL}


# --- http plumbing ----------------------------------------------------------

def client_ip(headers):
    fwd = headers.get("x-forwarded-for", "") or headers.get("x-real-ip", "")
    return fwd.split(",")[0].strip() or "unknown"


def send_json(h, status, payload):
    data = json.dumps(payload).encode()
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Cache-Control", "no-store")
    h.send_header("Content-Length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)


def handle_post(h, fn):
    try:
        length = int(h.headers.get("content-length") or 0)
    except ValueError:
        length = 0
    if length > 8192:
        return send_json(h, 413, {"ok": False, "error": "That request was too large."})
    try:
        body = json.loads(h.rfile.read(length) or b"{}")
    except ValueError:
        return send_json(h, 400, {"ok": False, "error": "Something was wrong with that request."})
    status, payload = fn(body, client_ip(h.headers))
    send_json(h, status, payload)
