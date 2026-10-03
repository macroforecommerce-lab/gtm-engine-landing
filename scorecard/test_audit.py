#!/usr/bin/env python3
"""
Fixture tests for audit_proto.

Every page here is synthetic and belongs to nobody. That is deliberate: the
analyser must never be pointed at a client's site, and its test record must
never carry a client's score. See CLAUDE.md.

Run: python3 test_audit.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "api"))
import _audit_proto as a

REAL_FETCH = a.fetch   # positioning() swaps a.fetch for a stub; keep the real one

FILLER = " ".join(["the system delivers revenue for your sales team and we build it with you"] * 12)
IT_FILLER = " ".join(["il sistema di vendita per la tua azienda con il quale non si perde tempo"] * 12)


def page(body, lang='lang="en"'):
    return f"<html {lang}><body>{body}<p>{FILLER}</p></body></html>"


# name -> (html, expected positioning score or None when not scorable)
CASES = [
    ("no h1 - nothing claims the page",
     page("<h2>Something</h2>"), 0),
    ("h1 cut off on a function word",
     page("<h1>The same technology used by</h1>"), 2),
    ("h1 is a two-word slogan",
     page("<h1>Grow faster</h1>"), 2),
    ("h1 well formed but names nobody",
     page("<h1>Build marketing systems that actually deliver</h1>"), 4),
    ("h1 names a number and a buyer",
     page("<h1>Add 30 qualified founder calls to your pipeline each month</h1>"), 5),
    ("h1 over sixteen words",
     page("<h1>" + " ".join(["word"] * 20) + "</h1>"), 2),
    ("buzzword inside the h1",
     page("<h1>Leveraging the same platform used by leaders</h1>"), 2),
    ("buzzword storm",
     page("<h1>Innovative seamless synergy for your business</h1>"
          "<p>We leverage robust holistic cutting-edge disruption.</p>"), 1),
]

GATES = [
    ("thin page is refused, not scored",
     '<html lang="en"><body><div id="root"></div></body></html>', "visible words"),
    ("non-English page is refused, not scored",
     f'<html lang="it-IT"><body><h1>Il sistema per il tuo studio</h1><p>{IT_FILLER}</p></body></html>',
     "not in English"),
    ("non-English detected without a lang attribute",
     f"<html><body><h1>Il sistema per il tuo studio</h1><p>{IT_FILLER}</p></body></html>",
     "not in English"),
    ("English accepted without a lang attribute",
     f"<html><body><h1>Book more qualified calls with founders</h1><p>{FILLER}</p></body></html>",
     None),
]


def positioning(html):
    a.fetch = lambda u, timeout=25: (html, "https://fixture")
    r = a.audit("fixture")
    if not r["scorable"]:
        return None, r
    return [d for d in r["dimensions"] if d["dimension"] == "Positioning"][0]["score"], r


def main():
    failures = 0

    print("positioning")
    for name, html, want in CASES:
        got, _ = positioning(html)
        ok = got == want
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name:42} want {want}  got {got}")

    print("\nrefusal gates")
    for name, html, want in GATES:
        got, r = positioning(html)
        if want is None:
            ok = r.get("scorable") is True
            detail = "scored" if ok else f"refused: {r.get('reason', '')[:40]}"
        else:
            ok = r.get("scorable") is False and want in r.get("reason", "")
            detail = r.get("reason", "scored")[:52]
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name:42} {detail}")

    print("\nbuzzword stems")
    import re
    stems = [("leverage", True), ("Leveraging", True), ("leveraged", True),
             ("seamlessly", True), ("innovation", True), ("empowering", True),
             ("synergistic", True), ("robustness", True), ("next-generation", True),
             ("game-changing", True), ("disruptive", True),
             ("level", False), ("sales", False), ("deliver", False)]
    for word, want in stems:
        got = bool(re.search(a.BUZZWORDS, word, flags=re.I))
        ok = got == want
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {word:18} {'match' if got else 'no match':9} expected "
              f"{'match' if want else 'no match'}")

    print("\nunsafe addresses are refused (no network needed)")
    refused = [
        ("loopback", "http://127.0.0.1/"),
        ("localhost", "http://localhost/"),
        ("cloud metadata", "http://169.254.169.254/latest/meta-data/"),
        ("private 10/8", "http://10.0.0.5/"),
        ("private 192.168/16", "http://192.168.1.1/"),
        ("unspecified 0.0.0.0", "http://0.0.0.0/"),
        ("ipv6 loopback", "http://[::1]/"),
        ("decimal-encoded loopback", "http://2130706433/"),
        ("file scheme", "file:///etc/passwd"),
        ("ftp scheme", "ftp://example.com/"),
        ("embedded credentials", "https://user:pw@example.com/"),
        ("non-standard port", "https://example.com:8080/"),
        ("no dot in name", "http://intranet/"),
    ]
    for name, url in refused:
        try:
            a.check_public_url(url)
            ok, detail = False, "ACCEPTED"
        except a.UnsafeURL as e:
            ok, detail = True, str(e)[:44]
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name:26} {detail}")

    ok = a.check_public_url("http://93.184.216.34/") == "93.184.216.34"
    failures += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {'public address is accepted':26}")

    try:
        a._CheckedRedirects().redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/admin")
        ok, detail = False, "FOLLOWED"
    except a.UnsafeURL:
        ok, detail = True, "redirect to loopback refused"
    failures += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {'redirect to an unsafe host':26} {detail}")

    try:
        REAL_FETCH("x" * 400)
        ok = False
    except a.UnsafeURL:
        ok = True
    failures += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {'over-long address':26}")

    print(f"\n{'all passed' if not failures else str(failures) + ' FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
