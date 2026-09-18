#!/usr/bin/env python3
"""Shah-ready PDF of the Stablecon ranking. Input: the ranked JSON from icp_rank.py. Output: HTML (render with topdf.js landscape)."""
import json, html, re, sys
src, out = sys.argv[1], sys.argv[2]
j = json.load(open(src)); ranked, investors, customers = j['ranked'], j['investors'], j['customers']
esc = html.escape
def nm(s):
    return ' '.join(w.capitalize() if (w.islower() or w.isupper()) and len(w) > 1 else w for w in s.split()) if (s.islower() or s.isupper()) else s
SHORT = {5: 'Rails', 4: 'Bank / network', 3: 'Crypto infra', 2: 'Vendor', 1: 'Media', 0: 'Investor'}
def what(r):
    if r['clbl'].startswith('Payments-shaped'): return 'Payments (unclassified)'
    if r['clbl'] == 'Other': return 'Other'
    return SHORT.get(r['cf'], r['clbl'])
def hs(r):
    h = r['hubspot']
    if h == 'New': return 'New to Noah'
    m = re.search(r'\(([^)]*)\)', h); inner = m.group(1) if m else ''
    owner = next((p.strip() for p in inner.split(',') if re.match(r'^[A-Z][a-z]+ [A-Z]', p.strip())), '')
    stage = 'deal' if 'deal' in inner else ('opportunity' if 'opportunity' in inner else 'lead')
    if h.startswith('Contact'): return f'Owned by {owner}' if owner else 'Contact already in CRM'
    return f'Company known ({stage}' + (f', {owner}' if owner else '') + ')'
def tbl(rows, first=True):
    h = '<table><tr><th style="width:3%">#</th><th style="width:15%">Name</th><th style="width:22%">Title</th><th style="width:14%">Company</th><th style="width:9%">Segment</th><th style="width:10%">Role fit</th><th style="width:15%">Email</th><th style="width:12%">HubSpot</th></tr>'
    for r in rows:
        cls = 'a' if r['hsk'] == 'contact' else ('g' if r['hsk'] == 'new' else '')
        h += (f"<tr><td>{r['rank']}</td><td>{esc(nm(r['name']))}</td><td>{esc(r['title'])}</td><td>{esc(r['company'])}</td>"
              f"<td>{what(r)}</td><td>{esc(r['rlbl'])}</td><td>{esc(r['email'])}</td><td class='{cls}'>{esc(hs(r))}</td></tr>")
    return h + '</table>'
top = [r for r in ranked if r['score'] >= 17]; mid = [r for r in ranked if 13 <= r['score'] < 17]; rest = [r for r in ranked if r['score'] < 13]
new = sum(1 for r in ranked if r['hsk'] == 'new'); owned = sum(1 for r in ranked if r['hsk'] == 'contact')
top_new = sum(1 for r in top if r['hsk'] == 'new'); top_dm = sum(1 for r in top if r['rlbl'] == 'Decision maker')
CSS = '''<style>body{font-family:Helvetica,Arial,sans-serif;font-size:9.5pt;line-height:1.35;color:#111;margin:0}
h1{font-size:22pt;margin:0 0 4px;color:#1F3864} h2{font-size:12.5pt;margin:14px 0 6px;border-bottom:2px solid #1F3864;padding-bottom:3px;color:#1F3864}
h3{font-size:10.5pt;margin:12px 0 4px;color:#1F3864} .sub{color:#555;margin:0 0 12px;font-size:10.5pt}
table{border-collapse:collapse;width:100%;margin:4px 0 10px;font-size:8.6pt;table-layout:fixed}
th{background:#1F3864;color:#fff;text-align:left;padding:3px 5px;font-size:8.6pt} td{border-bottom:1px solid #ddd;padding:3px 5px;vertical-align:top;word-wrap:break-word}
tr{page-break-inside:avoid} .kpi{display:flex;gap:10px;margin:10px 0 12px} .kpi div{flex:1;background:#f4f6fb;border:1px solid #cfd6e6;padding:10px 12px;border-radius:4px;font-size:9.5pt}
.kpi b{font-size:19pt;display:block;color:#1F3864} .a{background:#FFF2CC} .g{background:#E2F0D9} .pb{page-break-before:always} p{margin:0 0 7px}
.cover{font-size:10pt} .cover p{margin:0 0 7px} .cover li{margin:0 0 5px} .method td{font-size:8.6pt;background:#fafbfd} .meta{color:#555;font-size:9.5pt;margin-bottom:14px}
.legend span{display:inline-block;padding:1px 8px;margin-right:8px;border:1px solid #ccc}</style>'''
h = f'''<!doctype html><html><head><meta charset="utf-8"><title>Stablecon attendees ranked for Noah</title>{CSS}</head><body>
<div class="cover">
<h1>Stablecon attendees, ranked for Noah outreach</h1>
<p class="meta">Prepared for Shah Ramezani by Kasra Tehrani, 18 Sep 2026. Source: the Stablecon attendee list Faris captured on 9 Sep 2026 (1,041 badges).</p>
<div class="kpi"><div><b>1,041</b>attendees on the badge wall</div><div><b>{len(ranked)}</b>with a verified work email, ranked</div><div><b>{len(top)}</b>write first</div><div><b>{new}</b>new to Noah, nobody has touched them</div><div><b>{len(investors)}</b>investors, separate list</div><div><b>{len(customers)}</b>already customers</div></div>
<h2>What this is</h2>
<p>Every attendee was run through Apollo to confirm their current company and get a verified work email, then checked against HubSpot so we know who Noah already talks to. The {len(ranked)} people with a verified email are scored against Noah's ideal customer profile and listed in order. Investors, existing customers and two partner accounts are separated out at the back so they are not cold-emailed by mistake.</p>
<h2>What we suggest</h2>
<ul>
<li><b>Write first, {len(top)} people.</b> Decision makers or buyers of payment rails at companies that move money across borders and need fiat legs. {top_new} of them are new to Noah and {top_dm} are founders or CEOs. This is the list for Thijn's outreach.</li>
<li><b>Write second, {len(mid)} people.</b> Same kind of company with a less senior title, or a bank, network or crypto infrastructure company with a strong title.</li>
<li><b>Investors, {len(investors)}.</b> Your call on who to approach. No product pitch.</li>
<li><b>Amber rows, {owned} people.</b> Someone at Noah already owns the contact. The owner is named; coordinate before writing.</li>
</ul>
<p class="legend">Row colours: <span class="g">green, new to Noah</span><span class="a">amber, owned by someone at Noah</span><span>white, company known, person new</span></p>
<h2>How the ranking works</h2>
<table class="method"><tr><th style="width:40%">Company fit (counts three times)</th><th style="width:33%">Role fit</th><th style="width:27%">HubSpot</th></tr>
<tr><td>5 &nbsp; Rails: moves money across borders and needs fiat legs (stablecoin payment rails, remittance, payouts, neobanks, ramps, exchanges)<br>4 &nbsp; Bank, credit union, card issuer or payment network<br>3 &nbsp; Crypto infrastructure, custody, chains, wallets<br>2 &nbsp; Compliance, identity, analytics or security vendor<br>1 &nbsp; Media, events, research, advisory</td>
<td>3 &nbsp; Decision maker: founder, CEO, president, owner<br>3 &nbsp; Buyer of rails: head, VP, director or chief of payments, treasury, partnerships, banking or stablecoins<br>2 &nbsp; Senior but not payments-specific<br>1 &nbsp; Other role</td>
<td>+1 &nbsp; New to Noah: nobody has this person or company (green)<br>0 &nbsp; Company known, this person is new<br>-1 &nbsp; Person already owned by someone at Noah (amber)</td></tr></table>
<p>Score = company fit x 3 + role fit + HubSpot, maximum 19. Ties go to established names, then to decision makers. Write first is a score of 17 or more. Emails are Apollo-verified as of 16 Sep 2026; titles come from Apollo and were not individually checked on the web, so confirm before sending.</p>
</div>
<h2 class="pb">Write first ({len(top)})</h2>{tbl(top)}
<h2 class="pb">Write second ({len(mid)})</h2>{tbl(mid)}
<h2 class="pb">The rest, in order ({len(rest)})</h2>{tbl(rest)}
<h2 class="pb">Investors and funds ({len(investors)})</h2>
<table><tr><th style="width:4%">#</th><th style="width:18%">Name</th><th style="width:22%">Title</th><th style="width:20%">Company</th><th style="width:20%">Email</th><th style="width:16%">HubSpot</th></tr>{''.join(f"<tr><td>{i}</td><td>{esc(nm(o['name']))}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td class='{'a' if o['hsk']=='contact' else ('g' if o['hsk']=='new' else '')}'>{esc(hs(o))}</td></tr>" for i,o in enumerate(investors,1))}</table>
<h2>Already customers ({len(customers)}), relationship not outreach</h2>
<table><tr><th style="width:4%">#</th><th style="width:18%">Name</th><th style="width:22%">Title</th><th style="width:20%">Company</th><th style="width:20%">Email</th><th style="width:16%">HubSpot</th></tr>{''.join(f"<tr><td>{i}</td><td>{esc(nm(o['name']))}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td>Customer</td></tr>" for i,o in enumerate(customers,1))}</table>
<h2>Partners, do not cold-email (2)</h2>
<p>ATTRUS and Trace Finance are tagged as partner accounts in Apollo. Attendees from those two companies are left out of the ranking.</p>
</body></html>'''
open(out, 'w').write(h)
print('top', len(top), 'mid', len(mid), 'rest', len(rest), 'inv', len(investors), 'cust', len(customers), 'new', new, 'owned', owned)
