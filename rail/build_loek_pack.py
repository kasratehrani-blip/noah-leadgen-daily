#!/usr/bin/env python3
"""Loek-format CEO outreach pack (12 Sep 2026 layout) from sweep results JSON.
Usage: build_loek_pack.py <results.json...> --name <pack> --date "18 Sep 2026" [--exclude names.txt]"""
import json, sys, argparse, html, re, csv
ap = argparse.ArgumentParser(); ap.add_argument('results', nargs='+'); ap.add_argument('--name', required=True); ap.add_argument('--date', required=True); ap.add_argument('--exclude', default=''); ap.add_argument('--rows', default='', help='comma list of live_row to include as cards'); ap.add_argument('--batch', default=''); ap.add_argument('--closeout-only', action='store_true'); ap.add_argument('--no-closeout', action='store_true')
a = ap.parse_args()
FIXED = ("Noah is the stablecoin infrastructure powering modern payments, with the ability to issue named USD, EUR and GBP virtual accounts in 160+ markets, and local payout in 70+ markets. "
         "We help move money worldwide faster and more cheaply than correspondent banking - powering the likes of Deel, Toptal, WorldRemit and Ledger.")
SIG = "[Loek's Gmail signature - per STEP 1]"
def yes(v): return str(v).strip().lower() in ('true', 'yes', '1')
rows = []
for p in a.results:
    try: rows += json.load(open(p))
    except Exception as e: print('skip', p, e)
excl = {l.strip().lower() for l in open(a.exclude)} if a.exclude else set()
def s(v): return ', '.join(map(str, v)) if isinstance(v, list) else ('' if v is None else str(v))
def short(c):
    c = re.sub(r'\s*\(.*?\)\s*', ' ', c).strip()
    return re.sub(r',?\s+(Inc\.?|LLC|Ltd\.?|Limited|Corp\.?|S\.A\.|SA|AG|GmbH|Pte\.? Ltd\.?|LLP|PBC)$', '', c, flags=re.I).strip()
def qualifies(r):
    why = []
    if (r.get('company') or r.get('input_name') or '').lower() in excl: why.append('already drafted')
    if (s(r.get('hubspot_status')) or '').upper() != 'NET_NEW': why.append('HubSpot: ' + s(r.get('hubspot_status')) + ' - ' + s(r.get('hubspot_evidence'))[:220])
    if not yes(r.get('is_ceo')): why.append('not CEO (title: ' + s(r.get('ceo_title')) + ')')
    if not yes(r.get('ceo_current')): why.append('CEO not confirmed current')
    if not r.get('ceo_email'): why.append('no verified email')
    elif not s(r.get('email_status')).lower().startswith(('verified', 'likely')): why.append('email status ' + s(r.get('email_status')))
    if r.get('ceo_email') and not yes(r.get('email_domain_matches', True)): why.append('email domain is not this company')
    if s(r.get('identity_confidence')).lower() == 'low': why.append('company identity not confirmed')
    return why
go, held = [], []
for r in sorted(rows, key=lambda r: int(r.get('live_row') or 0)):
    (held if qualifies(r) else go).append(r)
if a.rows:
    keep = {int(x) for x in a.rows.split(',')}; go = [r for r in go if int(r.get('live_row') or 0) in keep]
def subj(r):
    t = s(r.get('subject')).strip()
    if not t: t = 'Noah for ' + short(r['company'])
    return t if t.lower().startswith('noah') else 'Noah: ' + t
def body(r):
    first = r.get('ceo_first_name') or r['ceo_name'].split()[0]; hook = s(r.get('fit_hook')).strip().rstrip('.')
    return f"Hi {first},\n\n{FIXED}\n\nWe are the missing piece for {hook}, and I'd love the opportunity to explore it with {short(r['company'])}.\n\n{SIG}"
esc = html.escape
CSS = '''<style>@page{margin:14mm} body{font-family:Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.4;color:#1a1a1a;margin:0}
.top{background:#1F3864;color:#fff;padding:16px 18px;margin:-2px 0 14px;border-radius:4px} .top h1{font-size:17pt;margin:0 0 4px;letter-spacing:.2px} .top .sub{font-size:9.5pt;opacity:.92;margin:0}
h2{font-size:12pt;margin:16px 0 8px;color:#1F3864;border-bottom:2px solid #1F3864;padding-bottom:3px}
.box{border-left:4px solid #1F3864;background:#f4f6fb;padding:9px 12px;margin:8px 0 10px;font-size:9.5pt} .box b{color:#1F3864}
.card{border:1px solid #cfd6e6;border-radius:4px;margin:0 0 12px;page-break-inside:avoid;overflow:hidden}
.card .head{background:#eef2f9;padding:7px 12px;display:flex;justify-content:space-between;align-items:baseline}
.card .head .n{font-weight:bold;font-size:11pt;color:#1F3864} .card .head .d{font-size:8.5pt;color:#555}
.card table.meta{width:100%;border-collapse:collapse;font-size:9.5pt;margin:0} .card table.meta td{padding:4px 12px;border-bottom:1px solid #eef2f9;vertical-align:top} .card table.meta td.k{width:80px;color:#555;font-weight:bold}
.card pre{white-space:pre-wrap;font-family:Helvetica,Arial,sans-serif;font-size:9.8pt;margin:0;padding:10px 12px;background:#fff}
.v{font-size:8.3pt;color:#666;padding:6px 12px;border-top:1px dashed #cfd6e6;background:#fafbfd} .v b{color:#1F3864}
.pb{page-break-before:always} table.c{border-collapse:collapse;width:100%;font-size:8.6pt} table.c th{background:#1F3864;color:#fff;text-align:left;padding:4px 6px} table.c td{border-bottom:1px solid #ddd;padding:4px 6px;vertical-align:top}
.foot{font-size:8.5pt;color:#777;margin-top:14px}</style>'''
bt = f' - Batch {a.batch}' if a.batch else ''
H = f'''<!doctype html><html><head><meta charset="utf-8"><title>Noah CEO Outreach Pack - Loek{bt} - {a.date}</title>{CSS}</head><body>
<div class="top"><h1>Noah · CEO Outreach Pack · Loek de Jager{bt}</h1><p class="sub">{a.date} · {len(go)} Gmail drafts · Source: Noah lead-pool book (8 Sep 2026) · HubSpot-clean, current CEO, Apollo-verified mailbox on the company's own domain · Drafts only, nothing sends</p></div>
<div class="box"><b>How to use.</b> Open a Claude session with Loek's Gmail connector, upload this PDF and say: "Create these as Gmail drafts, follow the instructions in the file." Review in Gmail Drafts. Send only what you choose, yourself.</div>
<div class="box"><b>Instructions for the Claude session this file is uploaded to</b><br>
<b>Step 1, signature.</b> Every draft ends with Loek's real Gmail signature: the Noah logo, "Loek de Jager", "Business Development", a rule, "Mobile: +31 6 42221575", "Email: loek.dejager@noah.com", "Address: 4th Floor, 205 Regent Street, London, England, W1B 4HB", then the links "Connect on LinkedIn" and "Schedule a call". Take it from Gmail send-as settings (HTML, with the logo image); if that fails, copy the block verbatim from Loek's most recent sent email, logo included. Put it where the bracketed line is. If you cannot reproduce it with the logo, stop and report before creating drafts.<br>
<b>Step 2, HubSpot (read-only).</b> For each card search CONTACT by the To-address and by name, COMPANY by domain and by name. Any record for this person, or a deal for this company, = hold the card and report the URL.<br>
<b>Step 3, create.</b> One Gmail draft per remaining card: To, Subject, body exactly as printed, signature in place of the bracketed line. Never send. The "Verified" and "Note" lines never go in a draft.<br>
<b>Step 4, check.</b> List the drafts back: To equals the card address, the company in the body matches the recipient, the greeting matches the mailbox owner, the signature shows the logo.<br>
<b>Step 5, report.</b> Subjects created, signature source, holds with reasons, and confirm nothing was sent. Touch nothing else in the mailbox.</div>
<h2>Drafts ({len(go)})</h2>''' if not a.closeout_only else f'''<!doctype html><html><head><meta charset="utf-8"><title>Noah lead pool close-out - {a.date}</title>{CSS}</head><body><div class="top"><h1>Noah · Lead pool close-out · internal</h1><p class="sub">{a.date} · The {len(rows)} lead-pool companies not covered by the 12 Sep pack: {len(go)} went to draft cards, {len(held)} held. Why each was held, and the best person found.</p></div>'''
for i, r in enumerate(([] if a.closeout_only else go), 1):
    note = s(r.get('flags')).strip()
    H += (f'<div class="card"><div class="head"><span class="n">{i:02d} · {esc(short(r["company"]))}</span><span class="d">domain {esc(s(r.get("domain")))}</span></div>'
          f'<table class="meta"><tr><td class="k">To</td><td>{esc(r["ceo_email"])}</td></tr><tr><td class="k">Subject</td><td>{esc(subj(r))}</td></tr><tr><td class="k">Contact</td><td>{esc(r["ceo_name"])}, {esc(s(r.get("ceo_title")))}</td></tr></table>'
          f'<pre>{esc(body(r))}</pre>'
          f'<div class="v"><b>Verified {esc(a.date)}:</b> {esc(s(r.get("ceo_evidence"))[:220])} · <b>Email:</b> {esc(s(r.get("email_status")))}, Apollo · <b>HubSpot:</b> {esc(s(r.get("hubspot_evidence"))[:140])}' + (f' · <b>Note:</b> {esc(note[:220])}' if note else '') + '</div></div>')
if not a.no_closeout:
  H += (f'<h2 class="pb">Close-out: suppressed and held ({len(held)}), internal for Kasra and Loek</h2>' if not a.closeout_only else f'<h2>Suppressed and held ({len(held)}), internal for Kasra and Loek</h2>') + '<table class="c"><tr><th>#</th><th>Company</th><th>Domain</th><th>Why held</th><th>Best person found</th><th>HubSpot</th></tr>'
  for r in held:
    H += f'<tr><td>{r.get("live_row","")}</td><td>{esc(s(r.get("company") or r.get("input_name")))}</td><td>{esc(s(r.get("domain")))}</td><td>{esc("; ".join(qualifies(r)))[:300]}</td><td>{esc(s(r.get("ceo_name")))} {("(" + esc(s(r.get("ceo_title"))) + ")") if r.get("ceo_title") else ""} {esc(s(r.get("ceo_email")))}</td><td>{esc(s(r.get("hubspot_evidence")))[:200]}</td></tr>'
  H += '</table>'
H += '<p class="foot">Generated by the Noah lead-gen tooling. Sources: lead-pool book 8 Sep 2026, Apollo and HubSpot checks 18 Sep 2026.</p></body></html>'
open(f'out/{a.name}.html', 'w').write(H)
with open(f'out/{a.name}.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['#', 'company', 'domain', 'to', 'ceo', 'title', 'subject', 'hubspot', 'email_status'])
    for i, r in enumerate(go, 1): w.writerow([i, short(r['company']), s(r.get('domain')), r['ceo_email'], r['ceo_name'], s(r.get('ceo_title')), subj(r), s(r.get('hubspot_evidence'))[:120], s(r.get('email_status'))])
with open(f'out/{a.name}-held.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['row', 'company', 'domain', 'why', 'person', 'title', 'email', 'hubspot'])
    for r in held: w.writerow([r.get('live_row'), s(r.get('company') or r.get('input_name')), s(r.get('domain')), '; '.join(qualifies(r)), s(r.get('ceo_name')), s(r.get('ceo_title')), s(r.get('ceo_email')), s(r.get('hubspot_evidence'))[:200]])
print(f'{len(go)} cards, {len(held)} held -> out/{a.name}.html')
