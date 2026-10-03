#!/usr/bin/env python3
"""
Offline tests for web/api/_logic.py. No network, no server. Run: python3 test_logic.py
"""
import contextlib
import io
import json
import os
import sys
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "api"))
import _audit_proto as a
import _logic as L

failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name:58} {detail}")


def fake_result(scores, evidence=None):
    names = ["ICP clarity", "Positioning", "Proof for outbound", "Conversion path", "Founder signal"]
    fixed = ["ICP definition & messaging", "ICP definition & messaging", "Clay & AI-powered funnels",
             "Full-funnel distribution", "LinkedIn personal branding"]
    evidence = evidence or {}
    dims = [{"dimension": n, "score": s, "fixed_by": f, "evidence": evidence.get(n, [])}
            for n, s, f in zip(names, scores, fixed)]
    return {"url": "https://x.test", "scorable": True, "total": sum(scores), "max": 25, "dimensions": dims}


def quiet(fn, *args, **kw):
    with contextlib.redirect_stderr(io.StringIO()) as buf:
        out = fn(*args, **kw)
    return out, buf.getvalue()


print("fix selection")
r = fake_result([3, 4, 4, 2, 3], {"Conversion path": ["no direct booking path"], "ICP clarity": ["no company stage/size/model qualifier"]})
fx = L.pick_fixes(r["dimensions"])
check("returns exactly three fixes", len(fx) == 3)
check("lowest score first", fx[0]["dimension"] == "Conversion path" and fx[0]["score"] == 2)
check("tie broken by priority, not alphabet", [f["dimension"] for f in fx[1:]] == ["ICP clarity", "Founder signal"], str([f["dimension"] for f in fx]))
check("action follows the evidence", "booking link" in fx[0]["action"], fx[0]["action"][:46])
check("each fix names its service", all(f["fixed_by"] for f in fx))
check("perfect score gets no fixes", L.pick_fixes(fake_result([5, 5, 5, 5, 5])["dimensions"]) == [])
check("only weak dimensions are listed", len(L.pick_fixes(fake_result([5, 5, 5, 5, 4])["dimensions"])) == 1)
check("falls back when no rule matches", L.pick_fixes(fake_result([1, 5, 5, 5, 5])["dimensions"])[0]["action"] == L.FIX_DEFAULT["ICP clarity"])

print("\nconfig is validated, not trusted")
for env, val, key, want in [
    ("NEXT_PUBLIC_META_PIXEL_ID", "1234567890", "pixelId", "1234567890"),
    ("NEXT_PUBLIC_META_PIXEL_ID", "12345');alert(1);//", "pixelId", ""),
    ("NEXT_PUBLIC_BOOKING_URL", "https://cal.example/x", "bookingUrl", "https://cal.example/x"),
    ("NEXT_PUBLIC_BOOKING_URL", "javascript:alert(1)", "bookingUrl", ""),
    ("NEXT_PUBLIC_BOOKING_URL", "http://insecure.example", "bookingUrl", ""),
]:
    os.environ[env] = val
    got = L.get_config()[key]
    check(f"{env.split('_')[-2]}={val[:30]!r}", got == want, f"-> {got!r}")
    del os.environ[env]
check("unset env gives empty strings", L.get_config()["pixelId"] == "" and L.get_config()["bookingUrl"] == "")

print("\nlead handling")
real_audit = a.audit
a.audit = lambda url, timeout=8: fake_result([3, 4, 4, 2, 3], {"Conversion path": ["no direct booking path"]})
(code, body), log = quiet(L.submit_lead, {"email": "founder@startup.in", "url": "startup.in", "utm": {"utm_source": "meta", "evil": "x", "fbclid": "abc"}})
check("valid lead accepted", code == 200 and body["ok"] and len(body["fixes"]) == 3)
check("lead is logged even with no webhook", "LEAD " in log and "founder@startup.in" in log)
check("only known utm keys survive", '"evil"' not in log and '"utm_source": "meta"' in log)
check("score is recorded with the lead", '"total": 16' in log)
(code, body), log = quiet(L.submit_lead, {"email": "bot@spam.com", "url": "x.com", "hp": "http://spam"})
check("honeypot returns ok but does nothing", code == 200 and body["fixes"] == [] and log == "")
for bad in ["", "nope", "a@b", "a b@c.com", "@c.com"]:
    (code, body), _ = quiet(L.submit_lead, {"email": bad, "url": "x.com"})
    check(f"rejects email {bad!r}", code == 400)
(code, body), log = quiet(L.submit_lead, {"event": "route", "email": "f@s.in", "inhouse": "yes"})
check("in-house growth routes to GTM Install", body.get("path") == "gtm-install")
(code, body), _ = quiet(L.submit_lead, {"event": "route", "email": "f@s.in", "inhouse": "no"})
check("no in-house growth routes to Done-For-You", body.get("path") == "done-for-you")
(code, body), _ = quiet(L.submit_lead, {"event": "bogus", "email": "f@s.in"})
check("unknown event rejected", code == 400)
(code, body), _ = quiet(L.submit_lead, ["not", "a", "dict"])
check("non-object body rejected", code == 400)

a.audit = lambda url, timeout=8: (_ for _ in ()).throw(RuntimeError("boom"))
(code, body), log = quiet(L.submit_lead, {"email": "f@s.in", "url": "x.com"})
check("a failed audit still keeps the lead", code == 200 and body["fixes"] == [] and "f@s.in" in log)

print("\nwebhook failure cannot lose a lead")
os.environ["LEAD_WEBHOOK_URL"] = "https://127.0.0.1:1/hook"
rec = {"event": "lead", "email": "keep@me.in"}
where, log = quiet(L.deliver, rec)
check("falls back to the log", where == "log" and "keep@me.in" in log)
os.environ["LEAD_WEBHOOK_URL"] = "http://not-https.example"
where, _ = quiet(L.deliver, rec)
check("non-https webhook is ignored", where == "log")
del os.environ["LEAD_WEBHOOK_URL"]

print("\naudit endpoint")
a.audit = real_audit
(code, body), _ = quiet(L.run_audit, {})
check("empty url rejected", code == 400)
(code, body), _ = quiet(L.run_audit, {"url": "http://169.254.169.254/latest/meta-data/"})
check("metadata address refused, with a polite message", code == 400 and "public website" in body["error"], body.get("error", "")[:40])
(code, body), _ = quiet(L.run_audit, {"url": "file:///etc/passwd"})
check("file:// refused", code == 400)
a.audit = lambda url, timeout=8: (_ for _ in ()).throw(RuntimeError("secret internal detail"))
(code, body), log = quiet(L.run_audit, {"url": "x.com"})
check("internal errors are not shown to visitors", code == 500 and "secret" not in json.dumps(body) and "secret" in log)
a.audit = lambda url, timeout=8: fake_result([3, 4, 4, 2, 3], {"Positioning": ['h1 reads: "<img src=x onerror=alert(1)>"']})
(code, body), _ = quiet(L.run_audit, {"url": "x.com"})
check("response carries scores and evidence, not fixes", code == 200 and "fixes" not in body and body["total"] == 16)
check("evidence passes through as plain strings", isinstance(body["dimensions"][1]["evidence"][0], str))
a.audit = real_audit

print("\nrate limit")
L._hits.clear()
hits = [L.rate_limited("1.2.3.4", now=1000 + i) for i in range(15)]
check("first twelve audits allowed, then limited", hits == [False] * 12 + [True] * 3)
check("a different visitor is unaffected", L.rate_limited("5.6.7.8", now=1015) is False)
check("the lead bucket is separate from the audit bucket", L.rate_limited("1.2.3.4", "lead", now=1015) is False)
check("window expires", L.rate_limited("1.2.3.4", now=1000 + L.RATE_WINDOW + 20) is False)

L._hits.clear()
a.audit = lambda url, timeout=8: fake_result([3, 4, 4, 2, 3])
for _ in range(12):
    quiet(L.run_audit, {"url": "x.com"}, "9.9.9.9")
(code, _), _ = quiet(L.run_audit, {"url": "x.com"}, "9.9.9.9")
check("audit limit returns 429 for a heavy address", code == 429)
(code, body), _ = quiet(L.submit_lead, {"email": "f@s.in", "url": "x.com"}, "9.9.9.9")
check("exhausting audits does not block the same visitor's email", code == 200 and len(body["fixes"]) == 3)
for _ in range(5):
    (code, body), _ = quiet(L.submit_lead, {"event": "route", "email": "f@s.in", "inhouse": "no"}, "9.9.9.9")
check("route answers are never rate limited", code == 200)

print("\nsites that block our reader")
for status in (401, 403, 429, 451):
    a.audit = lambda url, timeout=8, s=status: (_ for _ in ()).throw(urllib.error.HTTPError(url, s, "blocked", {}, None))
    (code, body), _ = quiet(L.run_audit, {"url": "guarded.example"}, f"blk{status}")
    check(f"HTTP {status} is 'could not read', with no score", code == 200 and body["scorable"] is False and str(status) in body["reason"])
check("the message does not blame the visitor's score", "says nothing about how it scores" in body["reason"])
a.audit = lambda url, timeout=8: (_ for _ in ()).throw(urllib.error.HTTPError(url, 404, "nf", {}, None))
(code, body), _ = quiet(L.run_audit, {"url": "gone.example"}, "nf")
check("a 404 is still an error the visitor can fix", code == 502 and body["ok"] is False)
a.audit = real_audit

print(f"\n{'all passed' if not failures else str(failures) + ' FAILED'}")
sys.exit(1 if failures else 0)
