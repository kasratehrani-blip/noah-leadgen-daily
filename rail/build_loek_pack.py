#!/usr/bin/env python3
"""Loek-format CEO outreach pack (12 Sep 2026 layout) from sweep results JSON.
Usage: build_loek_pack.py <results.json...> --name <pack> --date "18 Sep 2026" [--exclude names.txt]"""
import json, sys, argparse, html, re, csv
ap = argparse.ArgumentParser(); ap.add_argument('results', nargs='+'); ap.add_argument('--name', required=True); ap.add_argument('--date', required=True); ap.add_argument('--exclude', default='')
a = ap.parse_args()
FIXED = ("Noah is the stablecoin infrastructure powering modern payments, with the ability to issue named USD, EUR and GBP virtual accounts in 160+ markets, and local payout in 70+ markets. "
         "We help move money worldwide faster and more cheaply than correspondent banking - powering the likes of Deel, Toptal, WorldRemit and Ledger.")
SIG = "[Loek's Gmail signature - per STEP 1; fallback: Loek de Jager]"
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
def subj(r):
    t = s(r.get('subject')).strip()
    if not t: t = 'Noah for ' + short(r['company'])
    return t if t.lower().startswith('noah') else 'Noah: ' + t
def body(r):
    first = r.get('ceo_first_name') or r['ceo_name'].split()[0]; hook = s(r.get('fit_hook')).strip().rstrip('.')
    return f"Hi {first},\n\n{FIXED}\n\nWe are the missing piece for {hook}, and I'd love the opportunity to explore it with {short(r['company'])}.\n\n{SIG}"
esc = html.escape
CSS = '''<style>body{font-family:Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.35;color:#111;margin:0}
h1{font-size:15pt;margin:0 0 4px} h2{font-size:12pt;margin:14px 0 6px;border-bottom:2px solid #1F3864;padding-bottom:3px;color:#1F3864}
.hdr{font-size:9.5pt;color:#333;margin-bottom:8px} .box{border:1px solid #1F3864;padding:8px 10px;margin:8px 0;background:#f4f6fb;font-size:9.5pt}
.card{border:1px solid #bbb;padding:8px 10px;margin:0 0 10px;page-break-inside:avoid} .card .t{font-weight:bold;font-size:10.5pt}
.card .m{font-size:9pt;color:#333;margin:2px 0} .v{font-size:8.6pt;color:#1F3864;margin:3px 0 6px} .card pre{white-space:pre-wrap;font-family:Helvetica,Arial,sans-serif;font-size:9.6pt;margin:4px 0 0;background:#fafafa;padding:6px;border-left:3px solid #1F3864}
.pb{page-break-before:always} table{border-collapse:collapse;width:100%;font-size:8.6pt} th{background:#1F3864;color:#fff;text-align:left;padding:3px 5px} td{border-bottom:1px solid #ddd;padding:3px 5px;vertical-align:top}</style>'''
H = f'''<!doctype html><html><head><meta charset="utf-8"><title>Noah CEO Outreach Pack - Loek - {a.date}</title>{CSS}</head><body>
<h1>NOAH · OUTREACH OPERATIONS · DRAFTS-ONLY PROTOCOL · HUBSPOT-CLEAN</h1>
<div class="hdr">CEO Outreach Pack - Loek de Jager - {len(go)} Gmail Drafts · Generated {a.date} · sender: Loek de Jager, Noah · Source: Noah lead-pool book (Kasra, 8 Sep 2026), the {len(rows)} companies not covered by the 12 Sep pack. Every card passed: HubSpot sweep (company by name and domain, contact by domain and by email; any record = suppressed), current-CEO check, Apollo-verified mailbox on the company's own domain. Suppressed and held cards are listed on the close-out page.</div>
<div class="box"><b>HOW TO USE (Loek, or whoever runs it)</b><br>1. Open a Claude session with the Gmail connector. 2. Upload this PDF: "Create these as Gmail drafts - follow the instructions in the file." 3. Review in Gmail Drafts. 4. Send only what you choose, yourself. Nothing sends automatically, ever.</div>
<div class="box"><b>INSTRUCTIONS FOR THE CLAUDE SESSION THIS FILE IS UPLOADED TO</b><br>
STEP 1 - SIGNATURE: retrieve Loek's Gmail signature (send-as settings, else copy verbatim from a recent SENT email) and use it in place of the bracketed signature line in every draft. If none is found, use the plain name "Loek de Jager" and report it.<br>
STEP 2 - HUBSPOT: for each card, search HubSpot CONTACT by the To-address and by the person's name, and COMPANY by the domain and the name. Any record for THIS PERSON, or a deal for THIS COMPANY, = HOLD that card and report the record URL. HubSpot is read-only.<br>
STEP 3 - CREATE: one Gmail DRAFT per remaining card, To / Subject / Body exactly as printed (with the Step-1 signature). Never send.<br>
STEP 4 - MATCH CHECK: list the drafts back; confirm each To equals the card address, the body company matches the recipient, the greeting matches the mailbox owner.<br>
STEP 5 - REPORT: subjects created, signature source, holds with reasons, and confirm nothing was sent. Touch nothing else in the mailbox. The VERIFIED line never goes in a draft.</div>
<h2>Cards ({len(go)})</h2>'''
for i, r in enumerate(go, 1):
    H += (f'<div class="card"><div class="t">{i:02d} {esc(short(r["company"]))} - to {esc(r["ceo_email"])} · pre-check domain {esc(s(r.get("domain")))}</div>'
          f'<div class="m">Subject: {esc(subj(r))} · Contact: {esc(r["ceo_name"])}, {esc(s(r.get("ceo_title")))}</div>'
          f'<div class="v">VERIFIED {esc(a.date)} - {esc(s(r.get("ceo_evidence"))[:260])} · Email: {esc(s(r.get("email_status")))} (Apollo) · HubSpot: {esc(s(r.get("hubspot_evidence"))[:160])}</div>'
          f'<pre>{esc(body(r))}</pre>' + (f'<div class="m">Note: {esc(s(r.get("flags"))[:240])}</div>' if s(r.get('flags')).strip() else '') + '</div>')
H += f'<h2 class="pb">Close-out: suppressed and held ({len(held)}), internal for Kasra and Loek</h2><table><tr><th>#</th><th>Company</th><th>Domain</th><th>Why held</th><th>Best person found</th><th>HubSpot</th></tr>'
for r in held:
    H += f'<tr><td>{r.get("live_row","")}</td><td>{esc(s(r.get("company") or r.get("input_name")))}</td><td>{esc(s(r.get("domain")))}</td><td>{esc("; ".join(qualifies(r)))[:300]}</td><td>{esc(s(r.get("ceo_name")))} {("(" + esc(s(r.get("ceo_title"))) + ")") if r.get("ceo_title") else ""} {esc(s(r.get("ceo_email")))}</td><td>{esc(s(r.get("hubspot_evidence")))[:200]}</td></tr>'
H += '</table></body></html>'
open(f'out/{a.name}.html', 'w').write(H)
with open(f'out/{a.name}.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['#', 'company', 'domain', 'to', 'ceo', 'title', 'subject', 'hubspot', 'email_status'])
    for i, r in enumerate(go, 1): w.writerow([i, short(r['company']), s(r.get('domain')), r['ceo_email'], r['ceo_name'], s(r.get('ceo_title')), subj(r), s(r.get('hubspot_evidence'))[:120], s(r.get('email_status'))])
with open(f'out/{a.name}-held.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['row', 'company', 'domain', 'why', 'person', 'title', 'email', 'hubspot'])
    for r in held: w.writerow([r.get('live_row'), s(r.get('company') or r.get('input_name')), s(r.get('domain')), '; '.join(qualifies(r)), s(r.get('ceo_name')), s(r.get('ceo_title')), s(r.get('ceo_email')), s(r.get('hubspot_evidence'))[:200]])
print(f'{len(go)} cards, {len(held)} held -> out/{a.name}.html')
