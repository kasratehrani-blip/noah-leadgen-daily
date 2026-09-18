#!/usr/bin/env python3
"""Stablecon attendees as a lead-gen workbook, one tab per Noah vertical, v24 columns in plain words.
Usage: build_v24_stablecon.py <ranked.json> <hs_desc.json> <apollo_org.json> <out.xlsx>"""
import json, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
src, hsd, apd, out = sys.argv[1:5]
J = json.load(open(src)); HS = json.load(open(hsd)); AP = json.load(open(apd))
DATE = '18 Sep 2026'
FIXED = ("Noah is the stablecoin infrastructure powering modern payments, with the ability to issue named USD, EUR and GBP virtual accounts in 160+ markets, and local payout in 70+ markets. "
         "We help move money worldwide faster and more cheaply than correspondent banking - powering the likes of Deel, Toptal, WorldRemit and Ledger.")
INTRO = ("I hope you are doing well. My name is Thijn Lamers, co-founder of Noah and before that part of the founding team at Adyen. "
         "It would be great if we could schedule a call, even 15 minutes, to explore how we could work together and help each other.")
OUTRO = "Looking forward to hearing from you.\n\nMany thanks,\n\nThijn"

def nm(s): return ' '.join(w.capitalize() if len(w) > 1 else w for w in s.split()) if (s.islower() or s.isupper()) else s
def short(c):
    c = re.sub(r'\s*\(.*?\)\s*', ' ', c).strip()
    return re.sub(r',?\s+(Inc\.?|LLC|Ltd\.?|Limited|Corp\.?|S\.A\.|SA|AG|GmbH|Pte\.? Ltd\.?|LLP)$', '', c, flags=re.I).strip()
def is_cu(c): return bool(re.search(r'credit union|\bFCU\b|\bCU\b', c, re.I))
def band(e):
    try: e = int(e)
    except: return ''
    return '1-10' if e <= 10 else '11-50' if e <= 50 else '51-200' if e <= 200 else '201-1,000' if e <= 1000 else '1,000+'
SEG = {5:'RAILS', 4:'BANKS', 3:'CRYPTO', 2:'VENDORS', 1:'MEDIA'}
VLBL = {'RAILS':'Rails (cross-border, stablecoin, remittance)', 'BANKS':'Bank, credit union or network', 'CRYPTO':'Crypto infrastructure', 'PAYMENTS':'Payments (check first)', 'VENDORS':'Compliance / identity vendor', 'MEDIA':'Media / advisory', 'OTHER':'Not classified'}
def seg_of(r):
    if r['clbl'].startswith('Payments-shaped'): return 'PAYMENTS'
    if r['clbl'] == 'Other': return 'OTHER'
    return SEG[r['cf']]
def owner_of(h):
    m = re.search(r'\(([^)]*)\)', h); inner = m.group(1) if m else ''
    return next((p.strip() for p in inner.split(',') if re.match(r'^[A-Z][a-z]+ [A-Z]', p.strip())), ''), inner
def in_hubspot(r):
    h = r['hubspot']
    if h == 'New': return 'No, new to Noah'
    owner, inner = owner_of(h)
    stage = 'deal open' if 'deal' in inner else ('opportunity' if 'opportunity' in inner else 'lead')
    if h.startswith('Contact'): return f"Yes, this person is owned by {owner}" if owner else 'Yes, this person is already a contact'
    return f"Company only ({stage}" + (f", {owner}" if owner else '') + "), this person is new"
def action(r, seg):
    if seg == 'VENDORS': return 'Partner chat only, no pitch'
    if seg == 'MEDIA': return 'Say hello, no pitch'
    if seg == 'OTHER': return 'Check what they do first'
    if r['hsk'] == 'contact':
        owner, _ = owner_of(r['hubspot']); return f"Go through {owner}" if owner else 'Go through the record owner'
    if seg == 'PAYMENTS': return 'Check what they do, then write'
    if r['rf'] == 3: return '1. Write first'
    if r['rf'] == 2: return '2. Write second'
    return '3. Ask them who owns payments'
def deal_size(seg, emp, cu):
    try: e = int(emp or 0)
    except: e = 0
    if seg == 'RAILS': return '$3-10k a month' if e and e <= 50 else '$10-30k a month' if e and e <= 250 else '$30k+ a month, partnership' if e else '$5-20k a month (size unknown)'
    if seg == 'BANKS': return '$3-10k a month (member remittance)' if cu else '$5-20k a month, volume-led'
    if seg == 'CRYPTO': return 'Referral first; $5-15k a month if embedded'
    if seg == 'PAYMENTS': return 'Unknown until classified'
    return 'None, not a buyer'
def copy_for(r, seg):
    C = short(r['company']); cu = is_cu(r['company']); who = 'members' if cu else 'customers'
    if seg in ('RAILS', 'PAYMENTS'):
        return dict(fit=f"{C} moves money across borders and needs fiat legs. Noah gives them named USD, EUR and GBP accounts in 160+ markets to collect, stablecoin settlement in the middle, and local payout in 70+ markets, so they stop stitching bank partners per corridor." + (" Segment guessed from the name; read 'What they do' first." if seg == 'PAYMENTS' else ''),
                    flow="USD/EUR/GBP in via named accounts (ACH, Fedwire, SWIFT, SEPA, FPS) -> stablecoin settlement -> local payout in 70+ markets. Business and individual payouts.",
                    pain="Every new corridor is a new bank partner or licence. Correspondent banking is slow and holds float. No named accounts outside the home market. Reconciliation across several providers.",
                    incumbent="Own bank partners plus " + ' or '.join(x for x in ('Bridge', 'BVNK', 'Circle') if x.lower() not in C.lower()) + " for the stablecoin leg, SWIFT correspondents for the rest. Noah replaces the fiat legs, not their product.",
                    model="Partner-licensed or own licence. Standard KYB for business flows.",
                    hook=f"named USD, EUR and GBP accounts and local payout behind {C}'s cross-border flows", subject="Noah for your fiat legs")
    if seg == 'BANKS':
        return dict(fit=f"{C}'s {who} send money abroad through correspondent wires. Noah gives a bank or credit union local payout in 70+ markets and named USD, EUR and GBP accounts without building corridors. A complement to the core, not a replacement.",
                    flow=f"{who.capitalize()} USD out -> stablecoin settlement -> local payout in 70+ markets. Individuals and SME suppliers.",
                    pain=f"International wires are slow, expensive and opaque. {who.capitalize()} leave for Wise or Remitly. Correspondent and FX fees erode margin.",
                    incumbent="Correspondent banks over SWIFT, sometimes a white-label remittance partner. Typically 0.5-1% plus a fixed fee, against Noah in basis points.",
                    model="Regulated institution. Bank runs its own KYC, Noah is the rail.",
                    hook=f"local payout in 70+ markets when {C}'s {who} send money abroad", subject=f"Noah for your {who} abroad")
    if seg == 'CRYPTO':
        return dict(fit=f"{C} sells custody, wallets or chain infrastructure. Their clients still need fiat on and off legs. Noah is the fiat layer under their stack: named USD, EUR and GBP accounts plus local payout. Partner as much as customer.",
                    flow="Client fiat in via named account -> stablecoin on their rails -> fiat out via local payout in 70+ markets.",
                    pain="Fiat legs are the gap. Bank partners per market, consumer ramps are patchy, clients ask them for a business-grade fiat rail.",
                    incumbent="Consumer ramps (MoonPay, Transak) or nothing. Noah is the business fiat layer they can embed or refer.",
                    model="Partner rail. They onboard the client, Noah settles.",
                    hook=f"the fiat legs under {C}'s stablecoin stack", subject="Noah under your stack")
    if seg == 'VENDORS':
        return dict(fit=f"{C} sells compliance, identity or analytics to the same fintechs Noah sells to. Referral partner, not a buyer.", flow="Not applicable, channel partner.", pain="Their clients ask who runs the fiat rails.", incumbent="Not applicable.", model="Not applicable.", hook=f"the fiat legs {C}'s clients keep asking about", subject="Noah alongside " + C)
    if seg == 'MEDIA':
        return dict(fit=f"{C} is media, events, research or advisory. Relationship value only.", flow="", pain="", incumbent="", model="", hook="", subject="")
    return dict(fit="Not classified. Read 'What they do' before any outreach.", flow="", pain="", incumbent="", model="", hook="", subject="")
def how_to_open(r, seg):
    C = short(r['company'])
    if seg in ('MEDIA', 'OTHER'): return 'No cold pitch. Thijn personalises only if he knows them.'
    if seg == 'VENDORS': return 'Partner note: we both sell to stablecoin fintechs, offer a referral loop.'
    if r['rlbl'] == 'Decision maker': return f"Founder or CEO decides. Open with the corridor they cannot cover today and the Stablecon meet. One 15-minute call."
    if r['rlbl'] == 'Buyer of rails': return f"Owns payments or partnerships at {C}. Open with a coverage map: which of their markets Noah already pays out to."
    if r['rlbl'].startswith('Senior'): return f"Senior but not payments. Ask for the intro to whoever owns payments at {C}."
    return f"Junior or unclear role. Ask who owns payments at {C}. Do not pitch."
def draft(r, seg, c):
    if not c['hook']: return '', ''
    first = nm(r['name']).split()[0]; C = short(r['company'])
    return 'Re: ' + c['subject'], f"Hi {first},\n\n{INTRO}\n\nAbout Noah\n{FIXED}\n\nWe are the missing piece for {c['hook']}, and I'd love the opportunity to explore it with {C}.\n\n{OUTRO}"
def company_info(dom):
    h = HS.get(dom, {}); a = AP.get(dom, {})
    desc = h.get('desc') or a.get('desc') or 'No description found. Check the website before writing.'
    src = 'HubSpot' if h.get('desc') else ('Apollo' if a.get('desc') else '')
    city = h.get('city') or a.get('city') or ''; country = h.get('country') or a.get('country') or ''
    emp = h.get('emp') or a.get('emp') or ''
    extra = ', '.join(x for x in ([f"founded {a['founded']}" if a.get('founded') else ''] + [f"raised {a['funding']}" if a.get('funding') else ''] + [a['stage'] if a.get('stage') and a['stage'] != 'Other' else '']) if x)
    return desc, src, ', '.join(x for x in (city, country) if x) or 'unknown', emp, extra

HDR = ['Action','Name','Title','Company','Email','LinkedIn','In HubSpot?','Vertical','What they do','HQ','Size (staff)','Founded / funding','Why Noah fits','Money flow','Their pain today','Deal size (estimate)','How to open','Who they use today','Compliance model','Draft subject','Draft body','Score','Rank','Source','Checked']
W = [26,22,30,24,30,16,32,26,60,20,10,24,58,48,44,22,46,44,30,26,80,7,7,26,11]
WRAP = {8,12,13,14,16,17,18,20}
def row_for(r):
    seg = seg_of(r); c = copy_for(r, seg); desc, dsrc, hq, emp, extra = company_info(r['domain'])
    subj, body = draft(r, seg, c)
    return [action(r, seg), nm(r['name']), r['title'], r['company'], r['email'], r['linkedin'], in_hubspot(r), VLBL[seg], desc, hq, band(emp), extra, c['fit'], c['flow'], c['pain'], deal_size(seg, emp, is_cu(r['company'])), how_to_open(r, seg), c['incumbent'], c['model'], subj, body, r.get('score',''), r.get('rank',''), f"Badge wall (Faris, 9 Sep); Apollo 16-18 Sep; HubSpot 16 Sep; description from {dsrc or 'n/a'}", DATE], seg, r

F = lambda **k: Font(name='Arial', **{'size': 10, **k})
LINK = Font(name='Arial', size=10, color='0563C1', underline='single')
GREEN = PatternFill('solid', fgColor='E2F0D9'); AMBER = PatternFill('solid', fgColor='FFF2CC'); BLUE = PatternFill('solid', fgColor='DDEBF7'); GREY = PatternFill('solid', fgColor='EDEDED')
wb = Workbook(); wb.remove(wb.active)
def sheet(name, note, rows, hdr=HDR, widths=W, wrap=WRAP, freeze='E3', link_cols=(5, 6), colour=True):
    ws = wb.create_sheet(name)
    ws['A1'] = note; ws['A1'].font = F(italic=True); ws['A1'].alignment = Alignment(wrap_text=True, vertical='top')
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=min(len(hdr), 10)); ws.row_dimensions[1].height = 34
    for i, h in enumerate(hdr, 1): ws.cell(row=2, column=i, value=h)
    for j, (vals, seg, r) in enumerate(rows, 3):
        for i, v in enumerate(vals, 1):
            c = ws.cell(row=j, column=i, value=v); c.font = F(); c.alignment = Alignment(wrap_text=(i - 1) in wrap, vertical='top')
            if i in link_cols and v:
                if i == 5 and '@' in str(v): c.hyperlink = f"mailto:{v}"; c.font = LINK
                elif i == 6: c.hyperlink = str(v); c.value = 'LinkedIn'; c.font = LINK
        if colour and r is not None:
            a = ws.cell(row=j, column=1); h = ws.cell(row=j, column=7)
            if r.get('hsk') == 'contact': h.fill = AMBER; a.fill = AMBER
            elif r.get('hsk') == 'new': h.fill = GREEN
            if str(vals[0]).startswith('1.'): a.fill = BLUE
            elif str(vals[0]).startswith(('Partner', 'Say hello', 'Check')): a.fill = GREY
        ws.row_dimensions[j].height = 64
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ref = f"A2:{get_column_letter(len(hdr))}{max(len(rows), 1) + 2}"
    t = Table(displayName=re.sub(r'[^A-Za-z0-9]', '', name) + 'Tbl', ref=ref)
    t.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True); ws.add_table(t)
    ws.freeze_panes = freeze
    return ws

ranked = J['ranked']; inv = J['investors']; cust = J['customers']
rows = [row_for(r) for r in ranked]
by = {}
for x in rows: by.setdefault(x[1], []).append(x)
TABS = [('RAILS', 'Companies that move money across borders: stablecoin rails, remittance, payouts, neobanks, ramps, exchanges. Noah core customer. Sorted best first.'),
        ('BANKS', 'Banks, credit unions, card issuers and payment networks. Angle: local payout in 70+ markets for their customers or members. Sorted best first.'),
        ('CRYPTO', 'Custody, wallets and chains. Their clients need fiat legs, Noah is the fiat layer under the stack. Sorted best first.'),
        ('PAYMENTS', 'Looks like payments from the name but not classified. Read "What they do" before writing.'),
        ('VENDORS', 'Compliance, identity, analytics and security vendors. Referral partners, not buyers.'),
        ('MEDIA', 'Media, events, research and advisory. Relationship only.'),
        ('OTHER', 'Not classified. Check before any outreach.')]
def kpi(seg): xs = by.get(seg, []); return len(xs), sum(1 for x in xs if x[2]['hsk'] == 'new'), sum(1 for x in xs if str(x[0][0]).startswith('1.'))
ws = wb.create_sheet('START HERE')
L = [('Noah lead gen: Stablecon attendees by vertical, ' + DATE, 13, True),
     ('', 10, False),
     ('What this is', 11, True),
     ('All 1,041 Stablecon badges (Faris, 9 Sep 2026) run through Apollo for current company and a verified work email, checked against HubSpot, scored against Noah ICP and split by vertical. One row per person. Click an email to write, click LinkedIn to open the profile.', 10, False),
     ('', 10, False), ('Tabs', 11, True)]
for seg, note in TABS:
    n, new, first = kpi(seg); L.append((f"{seg}: {n} people, {new} new to Noah, {first} to write first. {note}", 10, False))
L += [(f"INVESTORS: {len(inv)} people. Shah decides. No pitch.", 10, False), (f"CUSTOMERS: {len(cust)} people at companies already live with Noah. Say hello only.", 10, False), (f"ALL RANKED: all {len(rows)} people in one list.", 10, False), ('', 10, False),
      ('The first column, Action, tells you what to do', 11, True),
      ('1. Write first = founder, CEO or the person who buys payment rails, at a company nobody at Noah owns. Blue.', 10, False),
      ('2. Write second = senior but not in payments. Worth a note.', 10, False),
      ('3. Ask them who owns payments = junior or unclear role. Use them for the intro, do not pitch.', 10, False),
      ('Go through <name> = someone at Noah already owns this contact. Amber. Talk to that person first.', 10, False),
      ('Partner chat only / Say hello / Check first = grey. Not a sales target.', 10, False), ('', 10, False),
      ('In HubSpot? column', 11, True),
      ('Green = No, new to Noah. White = the company is in HubSpot but this person is not. Amber = this person is already owned by someone at Noah.', 10, False), ('', 10, False),
      ('Other columns', 11, True),
      ('What they do = HubSpot description where we have one, otherwise Apollo (18 Sep). Why Noah fits, Money flow, Their pain, Who they use today = written per vertical with the company name dropped in; personalise with What they do before sending. Deal size = rough estimate by vertical and size. Draft subject and body = Thijn standard, ready to paste. Score = company fit x3 + role fit + HubSpot, max 19.', 10, False), ('', 10, False),
      ('Rules', 11, True), ('Nothing sends from this book. HubSpot is read-only. Confirm the title on the web before drafting. Amber rows go through the owner.', 10, False)]
for i, (t, sz, b) in enumerate(L, 1):
    c = ws.cell(row=i, column=1, value=t); c.font = F(bold=b, size=sz); c.alignment = Alignment(wrap_text=True, vertical='top')
ws.column_dimensions['A'].width = 150
for seg, note in TABS:
    if by.get(seg): sheet(seg, note, by[seg])
IH = ['Action','Name','Title','Company','Email','LinkedIn','In HubSpot?','What they do','HQ','Size (staff)','How to open','Source','Checked']
IW = [26,22,30,26,30,12,32,60,20,10,44,26,11]
def inv_row(o):
    desc, dsrc, hq, emp, extra = company_info(o['domain'])
    return ['Shah decides', nm(o['name']), o['title'], o['company'], o['email'], o['linkedin'], in_hubspot(o), desc, hq, band(emp), 'Intro path only. Thijn or Shah personalises if the relationship is real. No product pitch.', f"Badge wall; Apollo; HubSpot; description from {dsrc or 'n/a'}", DATE], 'INV', o
sheet('INVESTORS', 'Investors and funds on the badge wall with a verified email. Shah decides who to approach. No product pitch.', [inv_row(o) for o in inv], IH, IW, {7,10}, freeze='E3')
def cust_row(o):
    desc, dsrc, hq, emp, extra = company_info(o['domain'])
    return ['Say hello, no pitch', nm(o['name']), o['title'], o['company'], o['email'], o['linkedin'], 'Yes, customer', desc, hq, band(emp), 'Route through the account owner.', f"Badge wall; Apollo; HubSpot; description from {dsrc or 'n/a'}", DATE], 'CUST', o
sheet('CUSTOMERS', 'Attendees from companies already live with Noah. Relationship, not outreach.', [cust_row(o) for o in cust], IH, IW, {7,10}, freeze='E3', colour=False)
sheet('ALL RANKED', f'All {len(rows)} ranked people in one list, best first. Same columns as the vertical tabs.', rows)
wn = wb.create_sheet('NOTES')
for i, t in enumerate(['Column standard follows Noah Quick-Sign v24 (Jul 2026), renamed in plain words: HubSpot status, company, region, what they do, why Noah fit, payment flow, likely pain, expected MMC, buyer and contact, outreach angle, incumbent vs Noah, compliance model, draft, source, date checked.',
                       'One row per person, not per company, because the source is a badge wall. Role fit, Rank and Score added.',
                       'Company descriptions: HubSpot for 119 companies, Apollo organisation enrichment (18 Sep 2026, 168 companies) for the rest. 10 small companies had no record anywhere.',
                       'Partners excluded: ATTRUS and Trace Finance (Apollo account tagged ZZZ-PARTNER).',
                       'Segment map lives in rail/icp_rank.py. A company in the wrong tab = fix the map and rebuild with rail/build_v24_stablecon.py.'], 1):
    c = wn.cell(row=i, column=1, value=t); c.font = F(); c.alignment = Alignment(wrap_text=True, vertical='top')
wn.column_dimensions['A'].width = 150
wb.save(out)
print({s: len(by.get(s, [])) for s, _ in TABS}, 'inv', len(inv), 'cust', len(cust), 'total', len(rows))
