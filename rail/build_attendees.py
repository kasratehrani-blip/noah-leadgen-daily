#!/usr/bin/env python3
"""Build the Stablecon attendee workbook + PDF from final_all.json (tiered, HubSpot-checked)."""
import json, html, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
src, base = sys.argv[1], sys.argv[2]
out=json.load(open(src))
order={'A Founder / CEO':0,'B Investor':1,'C Buyer title':2,'D Other attendee':3,'E Association':4,'F Consultancy / rating':5,'F Legal':6,'F Regulator / public':7,'F Press':8,'X Noah':9}
out.sort(key=lambda o:(order.get(o['tier'],9), 0 if o['email'] else 1, o['hsk']!='new', o['name'].lower()))
F=lambda **k: Font(name='Arial', size=10, **k)
hdrfill=PatternFill('solid',fgColor='1F3864'); thin=Side(style='thin',color='D9D9D9')
tf={'A Founder / CEO':'E2F0D9','B Investor':'DDEBF7','C Buyer title':'FFF2CC'}
def note_for(o):
    if o['moved']: return 'Moved: '+(o['notes'] or '')
    if o['email_raw'] and not o['email']: return 'Email '+o['email_status']
    if not o['email_raw']: return o['notes'] or ('Not in Apollo' if not o['matched'] else 'No email in Apollo')
    return ''
def sheet(wb,name,rows,hdr,widths,note):
    ws=wb.create_sheet(name)
    ws['A1']=note; ws['A1'].font=F(italic=True); ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(hdr)); ws['A1'].alignment=Alignment(wrap_text=True,vertical='top'); ws.row_dimensions[1].height=30
    for i,h in enumerate(hdr,1):
        c=ws.cell(row=2,column=i,value=h); c.font=Font(name='Arial',size=10,bold=True,color='FFFFFF'); c.fill=hdrfill
    for j,o in enumerate(rows,3):
        vals=[j-2,o['tier'],o['name'],o['title'],o['company'],o['email'],o['hubspot'],o['linkedin'],note_for(o)]
        for i,v in enumerate(vals,1):
            c=ws.cell(row=j,column=i,value=v); c.font=F(); c.border=Border(bottom=thin)
        if o['tier'] in tf: ws.cell(row=j,column=2).fill=PatternFill('solid',fgColor=tf[o['tier']])
        if o['customer']: ws.cell(row=j,column=7).fill=PatternFill('solid',fgColor='F8D7DA')
        elif o['hsk']=='contact': ws.cell(row=j,column=7).fill=PatternFill('solid',fgColor='FFF2CC')
    for i,w in enumerate(widths,1): ws.column_dimensions[chr(64+i)].width=w
    ws.freeze_panes='D3'; ws.auto_filter.ref=f"A2:{chr(64+len(hdr))}{len(rows)+2}"
hdr=['#','Tier','Name','Title','Company','Email','HubSpot','LinkedIn','Note']; widths=[5,18,24,36,30,34,34,40,40]
wb=Workbook(); wb.remove(wb.active)
short=[o for o in out if o['email'] and o['tier'][0] in 'ABC']; noem=[o for o in out if not o['email']]
sheet(wb,'SHORTLIST',short,hdr,widths,f'Stablecon attendees for Shah, 16 Sep 2026. {len(short)} people with a verified work email in the three tiers that matter: A founders and CEOs, B investors, C buyer titles. HubSpot: New = nobody at Noah has touched them; Company in CRM = the company exists but not this person; Contact in CRM = someone at Noah owns this person (name in brackets); CUSTOMER = live client.')
sheet(wb,'ALL 1041',out,hdr,widths,'Every badge scanned (1,041), tiered, with the Apollo result and HubSpot status.')
sheet(wb,'NO EMAIL',noem,hdr,widths,f'{len(noem)} attendees with no verified email: not in Apollo, no email on file, or moved company.')
wb.save(base+'.xlsx')
esc=html.escape
CSS='''<style>body{font-family:Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.35;color:#111;margin:0}
h1{font-size:20pt;margin:0 0 2px;color:#1F3864} h2{font-size:12.5pt;margin:14px 0 6px;border-bottom:2px solid #1F3864;padding-bottom:3px;color:#1F3864}
.sub{color:#555;margin:0 0 10px} table{border-collapse:collapse;width:100%;margin:4px 0 10px;font-size:8.8pt}
th{background:#1F3864;color:#fff;text-align:left;padding:3px 5px} td{border-bottom:1px solid #ddd;padding:3px 5px;vertical-align:top}
.kpi{display:flex;gap:8px;margin:10px 0 14px;flex-wrap:wrap} .kpi div{flex:1;min-width:105px;background:#f4f6fb;border:1px solid #cfd6e6;padding:8px 10px;border-radius:4px;font-size:9.5pt}
.kpi b{font-size:20pt;display:block;color:#1F3864} .a{background:#FFF2CC}.r{background:#F8D7DA} .pb{page-break-before:always} p{margin:0 0 6px}</style>'''
def tbl(rows):
    h='<table><tr><th>Name</th><th>Title</th><th>Company</th><th>Email</th><th>HubSpot</th></tr>'
    for o in rows:
        cls='r' if o['customer'] else ('a' if o['hsk']=='contact' else '')
        h+=f"<tr><td>{esc(o['name'])}</td><td>{esc(o['title'])}</td><td>{esc(o['company'])}</td><td>{esc(o['email'])}</td><td class='{cls}'>{esc(o['hubspot'])}</td></tr>"
    return h+'</table>'
T=lambda t:[o for o in out if o['tier']==t and o['email']]
A,B,C,D=T('A Founder / CEO'),T('B Investor'),T('C Buyer title'),T('D Other attendee'); E=[o for o in out if o['tier'][0] in 'EF' and o['email']]
warm=sum(1 for o in short if o['hsk']!='new')
h=f'''<!doctype html><html><head><meta charset="utf-8"><title>Stablecon attendees for Shah</title>{CSS}</head><body>
<h1>Stablecon attendees, the full list for Shah</h1>
<p class="sub">Source: Faris's badge-wall videos, 9 Sep 2026 (1,041 badges). Every name was run through Apollo on 15 and 16 Sep for current employer, title and verified work email, then checked against Noah's HubSpot by email and by company domain. Read-only; nothing was written to HubSpot.</p>
<div class="kpi"><div><b>1,041</b>badges</div><div><b>{sum(1 for o in out if o['matched'])}</b>found in Apollo</div><div><b>{sum(1 for o in out if o['email'])}</b>verified work emails</div><div><b>{len(A)}</b>founders and CEOs with email</div><div><b>{len(B)}</b>investors with email</div><div><b>{len(C)}</b>buyer titles with email</div><div><b>{warm}</b>of the shortlist already known in HubSpot</div></div>
<h2>How to read it</h2>
<p><b>Tiers.</b> A: founder, CEO, president or owner. B: investor or fund. C: a buyer title (payments, treasury, partnerships, banking, stablecoins, crypto, or a VP, director or head role). D: other attendees with an email. E and F: associations, consultancies, law firms, regulators and press, at the back for completeness.</p>
<p><b>HubSpot column.</b> New: nobody at Noah has this person or company. Company in CRM: the company exists, this person does not; stage and owner shown. Contact in CRM (amber): someone at Noah already owns this person; check with them before writing. CUSTOMER (red): live client.</p>
<p><b>What is not here.</b> {len(noem)} attendees have no verified email: Apollo does not index them or has no email on file. They are listed by name in the workbook so they can be found on LinkedIn.</p>
<h2>Tier A. Founders and CEOs ({len(A)})</h2>{tbl(A)}
<h2 class="pb">Tier B. Investors and funds ({len(B)})</h2>{tbl(B)}
<h2 class="pb">Tier C. Buyer titles ({len(C)})</h2>{tbl(C)}
<h2 class="pb">Tier D. Other attendees with an email ({len(D)})</h2>{tbl(D)}
<h2 class="pb">Tiers E and F. Associations, consultancies, legal, regulators, press ({len(E)})</h2>{tbl(E)}
</body></html>'''
open(base+'.html','w').write(h); print('shortlist',len(short),'| A',len(A),'B',len(B),'C',len(C),'D',len(D),'EF',len(E),'| no email',len(noem))
