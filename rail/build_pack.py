#!/usr/bin/env python3
"""Build a Noah CEO outreach pack (HTML + PDF + CSV) from the sweep results.

Input : one or more JSON files produced by the sweep (see rail/SWEEP_BRIEF.md).
Output: out/<pack-name>.html, out/<pack-name>.pdf, out/<pack-name>.csv

A company makes the pack only if ALL of these hold:
  - hubspot_status == NET_NEW            (nothing in Noah's HubSpot, company or contact)
  - is_ceo and ceo_current == yes        (the person is the CEO of this company today)
  - ceo_email present, email_domain_matches, email_status verified or likely to engage
  - not excluded by name (already drafted in an earlier pack)
Everything else lands in the "held" list at the end of the pack with the reason.
"""
import csv, glob, html, json, os, re, sys, datetime

FIXED_PARA = ("Noah is the stablecoin infrastructure powering modern payments, with the ability to issue named USD, EUR "
              "and GBP virtual accounts in 160+ markets, and local payout in 70+ markets. We help move "
              "money worldwide faster and more cheaply than correspondent banking - powering the likes of "
              "Deel, Toptal, WorldRemit and Ledger.")
INTRO = "<<Thijn will insert intro here>>"
OUTRO = "<<Thijn will insert outro here>>"


def load(paths):
    rows = []
    for p in paths:
        with open(p) as f:
            rows.extend(json.load(f))
    return rows


def yes(v):
    return str(v).strip().lower() in ("yes", "true", "1", "y")


def qualifies(r, excluded):
    reasons = []
    if (r.get("company") or r.get("input_name") or "").strip().lower() in excluded:
        reasons.append("already drafted in an earlier pack")
    if (r.get("hubspot_status") or "").upper() != "NET_NEW":
        reasons.append(f"HubSpot: {r.get('hubspot_status')} - {r.get('hubspot_evidence')}")
    if not yes(r.get("is_ceo")):
        reasons.append(f"contact is not CEO (title: {r.get('ceo_title')})")
    if not yes(r.get("ceo_current")):
        reasons.append("CEO not confirmed current at this company")
    if not r.get("ceo_email"):
        reasons.append("no verified email")
    elif (r.get("email_status") or "").lower() not in ("verified", "likely to engage"):
        reasons.append(f"email status {r.get('email_status')}")
    if r.get("ceo_email") and not yes(r.get("email_domain_matches", True)):
        reasons.append("email domain does not belong to this company")
    if (r.get("identity_confidence") or "").lower() == "low":
        reasons.append("company identity not confirmed")
    return reasons


def subject_for(r):
    s = (r.get("subject") or "").strip()
    if s:
        return s if "noah" in s.lower() else f"Noah opportunity: {s}"
    return f"Noah opportunity for {r['company']}"


def body_for(r):
    first = r.get("ceo_first_name") or r["ceo_name"].split()[0]
    hook = r["fit_hook"].strip().rstrip(".")
    short = r.get("short_name") or r["company"]
    return (f"Hi {first},\n{INTRO}\n{FIXED_PARA}\nWe are the missing piece for {hook}, and I'd love the "
            f"opportunity to explore it with {short}.\n{OUTRO}")


def build(paths, pack_name, title, excluded_names, mission_md):
    rows = sorted(load(paths), key=lambda r: int(r.get("live_row") or 0))
    excluded = {n.strip().lower() for n in excluded_names}
    go, held = [], []
    for r in rows:
        why = qualifies(r, excluded)
        (held if why else go).append((r, why))
    today = datetime.date.today().strftime("%d %b %Y")
    esc = html.escape
    cards = []
    for i, (r, _) in enumerate(go, 1):
        subj = subject_for(r)
        body = body_for(r)
        cards.append(f"""
<section class="card">
<h2>{i:02d} {esc(r['company'])}</h2>
<p class="meta"><b>To:</b> {esc(r['ceo_email'])} &nbsp;·&nbsp; <b>pre-check domain:</b> {esc(r['domain'])}<br>
<b>Subject:</b> {esc(subj)}<br>
<b>Contact:</b> {esc(r['ceo_name'])}, {esc(r['ceo_title'])} (CEO title verified {today}: {esc(str(r.get('ceo_evidence') or ''))})<br>
<b>CRM STATUS:</b> NET-NEW &nbsp;·&nbsp; <b>HUBSPOT (verified {today}):</b> {esc(str(r.get('hubspot_evidence') or 'no record'))}<br>
<b>Source:</b> Rail LIVE client list row {esc(str(r.get('live_row')))} &nbsp;·&nbsp; <b>Company:</b> {esc(str(r.get('description') or ''))}
{('<br><b>Flags:</b> ' + esc(str(r.get('flags')))) if r.get('flags') else ''}</p>
<p class="lbl">DRAFT BODY (verbatim, nothing above this line goes in the email):</p>
<pre>{esc(body)}</pre>
</section>""")
    held_html = "".join(
        f"<li><b>{esc(r.get('company') or r.get('input_name'))}</b> (row {esc(str(r.get('live_row')))}): "
        f"{esc('; '.join(w))}</li>" for r, w in held)
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title>
<style>
body{{font-family:Helvetica,Arial,sans-serif;font-size:10.5pt;line-height:1.35;color:#111;margin:0}}
h1{{font-size:15pt;margin:0 0 4px}} h2{{font-size:12.5pt;margin:0 0 4px;border-bottom:1px solid #999;padding-bottom:2px}}
.sub{{color:#444;margin:0 0 10px}} .mission{{background:#f4f4f4;border:1px solid #ccc;padding:8px 10px;margin:8px 0 14px;white-space:pre-wrap;font-size:9.5pt}}
.card{{page-break-inside:avoid;margin:0 0 14px}} .meta{{margin:0 0 4px;font-size:9.5pt}} .lbl{{margin:4px 0 2px;font-weight:bold;font-size:9.5pt}}
pre{{white-space:pre-wrap;font-family:Helvetica,Arial,sans-serif;font-size:10.5pt;background:#fafafa;border:1px solid #ddd;padding:8px;margin:0}}
.held{{page-break-before:always}} li{{margin-bottom:4px;font-size:9.5pt}}
</style></head><body>
<h1>{esc(title)}</h1>
<p class="sub">Generated {today} from Rail's LIVE client list, swept live: Noah HubSpot (company by name and domain, contact by domain and by email), CEO title (Apollo + web, per person), email (Apollo). Sender: Thijn Lamers. CEOs only. Net-new only.</p>
<div class="mission">{esc(mission_md)}</div>
{''.join(cards)}
<section class="held"><h2>NOT IN THIS PACK - swept out, for Kasra to confirm (do not draft any of these)</h2><ul>{held_html}</ul></section>
</body></html>"""
    os.makedirs("out", exist_ok=True)
    hp = f"out/{pack_name}.html"
    with open(hp, "w") as f:
        f.write(doc)
    with open(f"out/{pack_name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "company", "domain", "ceo_name", "ceo_title", "to_email", "email_status", "subject",
                    "hubspot_evidence", "ceo_evidence", "live_row", "flags"])
        for i, (r, _) in enumerate(go, 1):
            w.writerow([i, r["company"], r["domain"], r["ceo_name"], r["ceo_title"], r["ceo_email"],
                        r.get("email_status"), subject_for(r), r.get("hubspot_evidence"), r.get("ceo_evidence"),
                        r.get("live_row"), r.get("flags")])
    with open(f"out/{pack_name}-held.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["company", "live_row", "reasons", "hubspot_evidence", "ceo_name", "ceo_title"])
        for r, why in held:
            w.writerow([r.get("company") or r.get("input_name"), r.get("live_row"), "; ".join(why),
                        r.get("hubspot_evidence"), r.get("ceo_name"), r.get("ceo_title")])
    print(f"{len(go)} cards, {len(held)} held -> {hp}")
    return hp


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--name", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--mission", required=True, help="markdown/text file with the MISSION FOR CLAUDE block")
    ap.add_argument("--exclude", default="", help="file with one already-drafted company name per line")
    a = ap.parse_args()
    ex = [l for l in open(a.exclude).read().splitlines() if l.strip()] if a.exclude else []
    build(a.results, a.name, a.title, ex, open(a.mission).read())

# Render to PDF (Chromium via the globally installed Playwright):
#   NODE_PATH=$(npm root -g) node rail/topdf.js "$PWD/out/<pack>.html" "$PWD/out/<pack>.pdf"
