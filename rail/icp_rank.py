#!/usr/bin/env python3
"""Rank the Stablecon shortlist against Noah's ICP. Input final_all.json; output ranked JSON + PDF + xlsx."""
import json, re, html, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
src, base = sys.argv[1], sys.argv[2]
out=json.load(open(src))
# company fit by domain: 5 core ICP (moves money cross-border, needs fiat legs), 4 banks/issuers/networks, 3 crypto infra adjacent, 2 vendors, 1 media/events/other
CAT={
5:("Cross-border payments, stablecoin rails, remittance, neobank or ramp",['bvnk.com','bridge.xyz','conduitpay.com','mesta.xyz','rain.xyz','spherepay.co','muralpay.com','blindpay.com','felixpago.com','fonbnk.com','kulipa.xyz','velafi.com','monerium.com','takenos.com','juicyway.com','nala.com','onafriq.com','yellowcard.io','kredete.io','higlobe.com','pomelo.la','photonpay.com','payoneer.com','nium.com','thunes.com','transfi.com','routefusion.com','pockyt.io','paydidas.com','paymitto.com','monato.com','s1lkpay.com','sigmaremote.com','tauripay.com','knova.finance','stablerail.com','saber.money','ubyx.xyz','zuba.com','avenia.io','tracefinance.com','coinbax.com','tesser.xyz','caliza.com','flex.one','wirexapp.com','youpay.co','empowch.com','bettermoney.com','fiatrepublic.com','levl.ch','mudrex.com','meshpay.com','corsa.finance','tala.co','netevia.com','omnia.financial','flyra.com','theflip.africa','trycoast.com','zerohash.com','m0.org','schuman.io','frankencoin.com','pfsc.io','matera.com','nubank.com.br','wio.io','mercadobitcoin.com.br','transak.com','moonpay.com','kraken.com','coinbase.com','bitpanda.com','circle.com','ripple.com','eco.com','kast.xyz','dakota.xyz','meld.io','lightspark.com','cari.com','withconvexity.com','rhythmic.io','latitude.xyz','creditcoop.xyz','firstpoint.io','kmbal.com','areta.io','lovie.co','n3xt.io','infinia.xyz','velocity.xyz','galoy.io','verapath.com','xfx.io','unigox.com','checker.finance','stablecoinblueprint.com','tempo.xyz','ramp.com','riseworks.io','mandalagroup.xyz','monay.com','syntex.pro','augustus.com','crxfx.com','fuze.finance','securitize.io','tetradg.com','findgroup.io']),
4:("Bank, credit union, card issuer or payment network",['column.com','lithic.com','episodesix.com','moderntreasury.com','crossriver.com','pathward.com','ccbank.com','austincapitalbank.com','americanpridebank.com','bibank.com','republicebank.com','fnboxford.com','fsbsandiego.com','svb.com','hsbcinnovationbanking.com','usbank.com','citi.com','jpmorganchase.com','bny.com','sumup.com','fiserv.com','visa.com','mastercard.com','paypal.com','swift.com','jcbusa.com','ascu.org','avadiancu.com','bvscu.org','catalystcorp.org','citadelbanking.com','clearviewfcu.org','cutx.org','glcu.org','kfcu.org','partnercoloradocu.org','peopleschoicecreditunion.com','primewayfcu.com','r1cu.org','statewidefcu.org','origence.com','shieldbanking.com','banksocial.io','akoya.com','earlywarning.com','brico.ai','airlegit.com','kuratek.com','thirdwayv.com','strativgroup.com']),
3:("Crypto infrastructure, custody, chains or wallets",['fireblocks.com','bitgo.com','turnkey.com','dfns.co','utila.io','privy.io','crossmint.com','polygon.technology','solana.org','monad.xyz','aleo.org','stellar.org','tron.network','inco.org','allium.so','predicate.io','aquanow.com','enigma-securities.io','coinlist.co','truemarkets.co','yieldclub.io','zenotta.net','57blocks.com','inherencelabs.com','infinite.dev','roe-ai.com','cordant.ai','archontech.ai','boardy.ai','zero-knowledge.com','tassat.com','appliedblockchain.com','bambooblock.io','solo.one','input.global','finavator.com','webacy.com','valinordigital.com']),
2:("Compliance, identity, analytics or security vendor",['bitstudiocoin.com','chainalysis.com','trmlabs.com','elliptic.co','sumsub.com','socure.com','prove.com','sardine.ai','sentilink.com','unit21.ai','notabene.id','merklescience.com','gbg.com','vouched.id','aiprise.com','cryptio.co','lukka.global','lukka.tech','inca.digital','blockaid.io','chainpatrol.io','coincover.com','halborn.com','verifyvasp.com','witheisen.com','metrika.co','circuitsecurity.com','equifax.com','concorderesearch.com']),
1:("Media, events, research, advisory",['stablecon.com','thisweekinfintech.com','hlth.com','slateevents.com','ignitetalks.io','fxcintel.com','washingtonpost.com','calibercorporate.com','noveldc.com','patomak.com','caphillcrypto.com','pentagroup.com','financialprofessionals.org','cryptoforinnovation.org','departmentofxyz.com']),
}
dom2={d:(k,lbl) for k,(lbl,ds) in CAT.items() for d in ds}
KNOWN=set('bvnk.com conduitpay.com mesta.xyz circle.com nala.com nium.com thunes.com payoneer.com nubank.com.br kraken.com coinbase.com bitpanda.com moonpay.com transak.com ripple.com bridge.xyz rain.xyz spherepay.co muralpay.com lightspark.com zerohash.com onafriq.com higlobe.com pomelo.la photonpay.com transfi.com fiatrepublic.com monerium.com wirexapp.com wio.io mercadobitcoin.com.br meld.io kast.xyz dakota.xyz tala.co routefusion.com felixpago.com fonbnk.com juicyway.com kredete.io avenia.io takenos.com levl.ch mudrex.com flex.one ramp.com riseworks.io securitize.io blindpay.com kulipa.xyz velafi.com m0.org eco.com paypal.com visa.com mastercard.com fiserv.com crossriver.com column.com lithic.com moderntreasury.com svb.com usbank.com citi.com jpmorganchase.com bny.com sumup.com swift.com fireblocks.com bitgo.com privy.io polygon.technology solana.org stellar.org tron.network'.split())
PARTNER={'attrus.com':'Apollo account tagged ZZZ-PARTNER, do not SME-outreach','tracefinance.com':'Apollo account tagged ZZZ-PARTNER, do not SME-outreach'}
INVEST=re.compile(r'ventures|capital|partners\b|investor|\bvc\b|fund\b|asset management|securities|temasek|gic\b|blackrock|northwestern mutual|federated hermes|gtcr|summit|norwest|quona|haun|4dx|a100x|mirana|flourish|commerce\.vc|light node|wellesley|tdsecurities|245park|architect',re.I)
def company_fit(o):
    d=o['domain']
    if d in dom2: return dom2[d]
    c=o['company']+' '+d
    if INVEST.search(c): return (0,'Investor / fund')
    if re.search(r'pay|remit|money|cash|wallet|bank|fx|treasur|stable|coin|crypto|settle',c,re.I): return (4,'Payments-shaped (unclassified)')
    return (2,'Other')
def role_fit(t):
    t=t or ''
    if re.search(r'\b(founder|co-founder|ceo|chief executive|owner|managing partner)\b',t,re.I) or re.search(r'(?<!vice )(?<!senior vice )(?<!executive vice )\bpresident\b',t,re.I): return 3,'Decision maker'
    if re.search(r'payment|treasur|partnership|banking|stablecoin|crypto|digital asset|issuance|cards?\b|remit|cross.?border|\bfx\b|business development|\bbd\b',t,re.I) and re.search(r'head|vp|vice president|chief|director|lead|manager|gm\b|general manager|officer|svp|evp',t,re.I): return 3,'Buyer of rails'
    if re.search(r'chief|\bc[a-z]o\b|head|vp|vice president|svp|evp|director|general manager|gm\b',t,re.I): return 2,'Senior, not payments-specific'
    return 1,'Other role'
ranked=[]
for o in out:
    if not o['email'] or o['tier'][0] in 'EFX': continue
    cf,clbl=company_fit(o); rf,rlbl=role_fit(o['title'])
    inv = o['tier']=='B Investor' or cf==0
    if inv: continue
    if o['customer']: continue
    if o['domain'] in PARTNER: continue
    hsb = 1 if o['hsk']=='new' else (0 if o['hsk']=='company' else -1)
    score=cf*3+rf+hsb
    if o['hsk']=='contact': action='Coordinate with owner first'
    elif o['hsk']=='company': action='Company known, person new'
    else: action='Cold, nobody at Noah has touched'
    ranked.append({**o,'cf':cf,'clbl':clbl,'rf':rf,'rlbl':rlbl,'score':score,'action':action,'known':int(o['domain'] in KNOWN)})
ranked.sort(key=lambda r:(-r['score'],-r['known'],-r['rf'],-r['cf'],r['company'].lower(),r['name'].lower()))
for i,r in enumerate(ranked,1): r['rank']=i
investors=[o for o in out if o['email'] and (o['tier']=='B Investor' or company_fit(o)[0]==0)]
investors.sort(key=lambda o:(o['hsk']!='new',o['company'].lower()))
customers=[o for o in out if o['email'] and o['customer']]
partners=[o for o in out if o['email'] and o['domain'] in PARTNER]
json.dump({'ranked':ranked,'investors':investors,'customers':customers},open(base+'.json','w'),indent=0)
# ---- xlsx
F=lambda **k: Font(name='Arial', size=10, **k); hdrfill=PatternFill('solid',fgColor='1F3864'); thin=Side(style='thin',color='D9D9D9')
wb=Workbook(); wb.remove(wb.active)
def sheet(name,rows,hdr,widths,note,fn):
    ws=wb.create_sheet(name); ws['A1']=note; ws['A1'].font=F(italic=True); ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(hdr)); ws['A1'].alignment=Alignment(wrap_text=True,vertical='top'); ws.row_dimensions[1].height=30
    for i,h in enumerate(hdr,1):
        c=ws.cell(row=2,column=i,value=h); c.font=Font(name='Arial',size=10,bold=True,color='FFFFFF'); c.fill=hdrfill
    for j,o in enumerate(rows,3):
        for i,v in enumerate(fn(o),1):
            c=ws.cell(row=j,column=i,value=v); c.font=F(); c.border=Border(bottom=thin)
        if o.get('hsk')=='contact': ws.cell(row=j,column=len(hdr)-1).fill=PatternFill('solid',fgColor='FFF2CC')
    for i,w in enumerate(widths,1): ws.column_dimensions[chr(64+i)].width=w
    ws.freeze_panes='C3'; ws.auto_filter.ref=f"A2:{chr(64+len(hdr))}{len(rows)+2}"
sheet('RANKED',ranked,['Rank','Score','Name','Title','Company','What they are','Why them','Email','HubSpot','Action'],[6,6,24,34,28,40,26,32,34,30],
 f'Stablecon shortlist ranked against Noah ICP, 16 Sep 2026. {len(ranked)} people. Score = company fit x3 (5 cross-border payments/stablecoin rails, 4 banks and networks, 3 crypto infra, 2 vendors, 1 media) + role fit (3 decision maker or rails buyer, 2 senior, 1 other) + HubSpot (+1 new, 0 company known, -1 person already owned). Customers and investors are on their own tabs.',
 lambda r:[r['rank'],r['score'],r['name'],r['title'],r['company'],r['clbl'],r['rlbl'],r['email'],r['hubspot'],r['action']])
sheet('INVESTORS',investors,['#','Name','Title','Company','Email','HubSpot','LinkedIn'],[5,24,32,30,34,34,40],'Investors and funds on the badge wall with a verified email. Not for the product pitch; Shah decides who to approach.',lambda o:[investors.index(o)+1,o['name'],o['title'],o['company'],o['email'],o['hubspot'],o['linkedin']])
sheet('CUSTOMERS',customers,['#','Name','Title','Company','Email','HubSpot'],[5,24,32,30,34,40],'Attendees from companies that are already Noah customers. Relationship, not outreach.',lambda o:[customers.index(o)+1,o['name'],o['title'],o['company'],o['email'],o['hubspot']])
wb.save(base+'.xlsx')
# ---- PDF
esc=html.escape
CSS='''<style>body{font-family:Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.35;color:#111;margin:0}
h1{font-size:20pt;margin:0 0 2px;color:#1F3864} h2{font-size:12.5pt;margin:14px 0 6px;border-bottom:2px solid #1F3864;padding-bottom:3px;color:#1F3864}
.sub{color:#555;margin:0 0 10px} table{border-collapse:collapse;width:100%;margin:4px 0 10px;font-size:8.8pt}
th{background:#1F3864;color:#fff;text-align:left;padding:3px 5px} td{border-bottom:1px solid #ddd;padding:3px 5px;vertical-align:top}
.kpi{display:flex;gap:8px;margin:10px 0 14px;flex-wrap:wrap} .kpi div{flex:1;min-width:105px;background:#f4f6fb;border:1px solid #cfd6e6;padding:8px 10px;border-radius:4px;font-size:9.5pt}
.kpi b{font-size:20pt;display:block;color:#1F3864} .a{background:#FFF2CC} .g{background:#E2F0D9} .pb{page-break-before:always} p{margin:0 0 6px} .icp td{font-size:9.5pt}</style>'''
def tbl(rows):
    h='<table><tr><th>#</th><th>Name</th><th>Title</th><th>Company</th><th>What they are</th><th>Email</th><th>HubSpot</th></tr>'
    for r in rows:
        cls='a' if r['hsk']=='contact' else ('g' if r['hsk']=='new' else '')
        h+=f"<tr><td>{r['rank']}</td><td>{esc(r['name'])}</td><td>{esc(r['title'])}</td><td>{esc(r['company'])}</td><td>{esc(r['clbl'])}</td><td>{esc(r['email'])}</td><td class='{cls}'>{esc(r['hubspot'])}</td></tr>"
    return h+'</table>'
top=[r for r in ranked if r['score']>=17]; mid=[r for r in ranked if 13<=r['score']<17]; rest=[r for r in ranked if r['score']<13]
h=f'''<!doctype html><html><head><meta charset="utf-8"><title>Stablecon, ranked against Noah ICP</title>{CSS}</head><body>
<h1>Stablecon attendees, ranked for outreach</h1>
<p class="sub">16 Sep 2026. Every attendee with a verified work email, scored against Noah's ICP and ordered. Customers and investors are separate lists at the back.</p>
<div class="kpi"><div><b>{len(ranked)}</b>people ranked</div><div><b>{len(top)}</b>write first</div><div><b>{len(mid)}</b>write second</div><div><b>{sum(1 for r in ranked if r['hsk']=='new')}</b>nobody at Noah has touched</div><div><b>{len(investors)}</b>investors, separate list</div><div><b>{len(customers)}</b>already customers</div></div>
<h2>How the ranking works</h2>
<table class="icp"><tr><th>Company fit (counts three times)</th><th>Role fit</th><th>HubSpot</th></tr>
<tr><td>5 &nbsp; Moves money across borders and needs fiat legs: stablecoin payment rails, remittance, payouts, neobanks, ramps and exchanges<br>4 &nbsp; Bank, credit union, card issuer or payment network<br>3 &nbsp; Crypto infrastructure, custody, chains, wallets<br>2 &nbsp; Compliance, identity, analytics or security vendor<br>1 &nbsp; Media, events, research, advisory</td>
<td>3 &nbsp; Decision maker: founder, CEO, president, owner<br>3 &nbsp; Buyer of rails: head, VP, director or chief of payments, treasury, partnerships, banking, stablecoins<br>2 &nbsp; Senior but not payments-specific<br>1 &nbsp; Other role</td>
<td>+1 &nbsp; New: nobody at Noah has this person or company (green)<br>0 &nbsp; Company known, this person is new<br>-1 &nbsp; Person already owned by someone at Noah (amber): coordinate first</td></tr></table>
<p>Score = company fit x 3 + role fit + HubSpot. Maximum 19. Ties are broken in favour of established names, then decision makers. "Write first" is 17 and above: a decision maker or rails buyer at a company that needs exactly what Noah sells.</p>
<h2>Write first ({len(top)})</h2>{tbl(top)}
<h2 class="pb">Write second ({len(mid)})</h2>{tbl(mid)}
<h2 class="pb">The rest, in order ({len(rest)})</h2>{tbl(rest)}
<h2 class="pb">Investors and funds ({len(investors)}), Shah's call</h2>
<table><tr><th>Name</th><th>Title</th><th>Company</th><th>Email</th><th>HubSpot</th></tr>{''.join(f"<tr><td>{esc(o['name'])}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td>{esc(o['hubspot'])}</td></tr>" for o in investors)}</table>
<h2>Partners flagged in Apollo, do not cold-email ({len(partners)})</h2>
<table><tr><th>Name</th><th>Title</th><th>Company</th><th>Email</th><th>Why</th></tr>{''.join(f"<tr><td>{esc(o['name'])}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td>{esc(PARTNER[o['domain']])}</td></tr>" for o in partners)}</table>
<h2>Already customers ({len(customers)}), relationship not outreach</h2>
<table><tr><th>Name</th><th>Title</th><th>Company</th><th>Email</th><th>HubSpot</th></tr>{''.join(f"<tr><td>{esc(o['name'])}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td>{esc(o['hubspot'])}</td></tr>" for o in customers)}</table>
</body></html>'''
open(base+'.html','w').write(h)
print('ranked',len(ranked),'top',len(top),'mid',len(mid),'rest',len(rest),'investors',len(investors),'customers',len(customers))
print('TOP 25:'); [print(f"  {r['rank']:>3} {r['score']:>2} {r['name'][:22]:<22} {r['title'][:28]:<28} {r['company'][:22]:<22} {r['hubspot'][:30]}") for r in top[:25]]
