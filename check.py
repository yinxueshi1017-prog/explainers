#!/usr/bin/env python3
"""Acceptance gate for the site as a whole.

The pieces check their own physics in the page (open any of them with #dev).
This checks the things no single piece can see: claims that describe another
file, links between pages, and the metadata a reader meets before the page.

Every one of these exists because it failed once.

    python3 check.py
"""
import os, re, sys, glob, html, xml.etree.ElementTree as ET
from urllib.parse import urlparse

BASE = "https://yinxueshi1017-prog.github.io/explainers/"
HERE = os.path.dirname(os.path.abspath(__file__)) or "."
fails = []
ran = []
def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    ran.append(msg)
    if not ok: fails.append(msg)

os.chdir(HERE)
pages = sorted(glob.glob("*.html"))
src = {p: open(p, encoding="utf-8").read() for p in pages}

print("\nSIZE CLAIMS  (a number about another file goes stale in silence)")
kb = os.path.getsize("hydrogen-embrittlement.html") / 1024
check(("%.1f&nbsp;KB" % kb) in src["the-bolt-that-was-fine.html"],
      "case-study rail states the live size of the piece (%.1f KB)" % kb)
check(("%.1f KB" % kb) in src["the-bolt-that-was-fine.html"],
      "case-study table states the live size of the piece")
check(("%d&nbsp;KB" % round(kb)) in src["index.html"],
      "index card states the live size of the piece (%d KB)" % round(kb))
check(kb < 500, "the piece is inside its 500 KB budget")

print("\nSTRUCTURE  (<title> lived in the BODY on two pages and grep never saw it)")
for p in pages:
    s = src[p].lower()
    check(0 <= s.find("<title>") < s.find("</head>"), "%s: <title> is inside <head>" % p)
    check(src[p].count("<title>") == 1, "%s: exactly one <title>" % p)

print("\nTHE EXTERIOR  (what a reader meets before the page)")
for p in pages:
    s = src[p]
    want = BASE if p == "index.html" else BASE + p
    def meta(n):
        m = re.search(r'<meta\s+(?:property|name)="%s"\s+content="([^"]*)"' % re.escape(n), s)
        return html.unescape(m.group(1)) if m else None
    check(bool(meta("description")), "%s: has a description" % p)
    check(meta("og:title") and meta("og:description"), "%s: has og:title and og:description" % p)
    check(meta("og:url") == want, "%s: og:url is its own canonical address" % p)
    m = re.search(r'<link rel="canonical" href="([^"]*)"', s)
    check(m and html.unescape(m.group(1)) == want, "%s: canonical is its own address" % p)
    check(meta("twitter:card") == "summary_large_image", "%s: twitter card is the large one" % p)
    # The name on the card, the name in the unfurl and the name in the tab were
    # three different strings for one piece ("Fatigue Crack Growth" / "Fatigue
    # cracks" / "Fatigue crack growth"). They are now one string, character for
    # character — the tab was moved to the card's sentence case. The index is the
    # one documented exception: its tab carries the author, its card names the
    # thing.
    title = re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip()
    if p == "index.html":
        check(meta("og:title") == "Interactive explainers for engineering failure modes",
              "%s: homepage card names the site, not the author" % p)
    else:
        check(meta("og:title") == title,
              "%s: shared name is the page's own name, exactly" % p)
    check(meta("twitter:title") == meta("og:title"), "%s: twitter title matches og" % p)
    # The alt describes the IMAGE, not the og:title — on the homepage the card
    # is drawn with the short name while the unfurl title is the long one.
    drawn = "Interactive explainers" if p == "index.html" else meta("og:title")
    check(meta("og:image:alt") and drawn in meta("og:image:alt"),
          "%s: image alt describes the card that was drawn" % p)
    img = meta("og:image")
    check(bool(img) and img.startswith(BASE) and os.path.exists(img[len(BASE):]),
          "%s: og:image is a file that exists" % p)
    check(not (img or "").endswith(".svg"), "%s: og:image is not SVG (crawlers reject it)" % p)

print("\nLINKS  (a pitch page once linked to a claim that had been cut)")
for p in pages:
    for href in re.findall(r'href="([^"#?]+)[^"]*"', src[p]):
        if href.startswith(("mailto:", "data:", "http://", "https://")): continue
        check(os.path.exists(href), "%s -> %s resolves" % (p, href))

print("\nNOTHING OFF-ORIGIN  (the whole argument of the site)")
for p in pages:
    for attr in re.findall(r'(?:src|href)="(https?://[^"]+)"', src[p]):
        check(attr.startswith(BASE), "%s: %s is our own origin" % (p, attr[:60]))

print("\nDISCLOSURE  (no engineer has reviewed any of this; every page must say so)")
for p in pages:
    if p == "index.html": continue
    check(re.search(r"has not been reviewed|no (?:\w+ )?engineer has reviewed", src[p], re.I) is not None,
          "%s: says the physics is unreviewed" % p)
    check("mailto:" in src[p], "%s: offers a way to reply" % p)

print("\nTHE DOCS DESCRIBE THIS REPOSITORY  (they said four files and cd site)")
d = open("DEPLOY.md", encoding="utf-8").read()
words = {"twelve":12, "eleven":11, "ten":10, "thirteen":13, "fourteen":14}
m = re.match(r"# Deploying this site\n\n(\w+) pages, (\w+) preview cards", d)
check(m is not None, "DEPLOY.md still opens by counting what is here")
if m:
    check(words.get(m.group(1).lower()) == len(pages),
          "DEPLOY.md's page count is the number of pages (%d)" % len(pages))
    check(words.get(m.group(2).lower()) == len(glob.glob("og/*.png")),
          "DEPLOY.md's card count is the number of cards (%d)" % len(glob.glob("og/*.png")))
check("python3 check.py" in d, "DEPLOY.md tells you to run this gate")
check("cd site" not in d, "DEPLOY.md does not tell you to cd into a folder that is not here")

print("\nSITEMAP")
root = ET.parse("sitemap.xml").getroot()
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [e.text for e in root.iterfind(".//s:loc", ns)]
listed = {(l[len(BASE):] or "index.html") for l in locs}
check(listed == set(pages), "sitemap lists exactly the pages that exist")
check(BASE + "sitemap.xml" in open("robots.txt").read(), "robots.txt points at the sitemap")

print("\n%d checks, %d failed" % (len(ran), len(fails)))
if fails: print("FAILED:\n  " + "\n  ".join(fails))
sys.exit(1 if fails else 0)
