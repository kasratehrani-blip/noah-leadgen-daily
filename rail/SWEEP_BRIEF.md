# Brief: sweep Rail "LIVE" clients -> net-new to Noah's HubSpot -> current CEO + verified email

Context. Noah (noah.com) is a stablecoin-powered payment rail: named USD/EUR/GBP virtual accounts in 160+
markets and local payout in 70+ markets. Noah is approaching the LIVE clients of Rail, a competitor that is
shutting down. You get a list of Rail's live clients (company name + rough region hint from Rail's CRM).
For EACH company produce one JSON record. This is READ-ONLY research: nothing is sent, nothing is
written to HubSpot, Apollo or Gmail. Today is 2026-09-15.

## Tools (load each with ToolSearch "select:<name>" before first use)
- HubSpot (Noah's CRM, portal 145864360), READ ONLY: mcp__HubSpot__search_crm_objects and
  mcp__HubSpot__query_crm_data only. NEVER call manage_crm_objects or any write tool.
- Apollo: mcp__Apollo_io__apollo_mixed_people_api_search (free; finds people; emails masked) and
  mcp__Apollo_io__apollo_people_match (1 lead credit per matched person; reveals the work email).
  Use _conversation_ref "rail2batch9x". Do NOT use apollo_mixed_companies_search,
  apollo_organizations_enrich, reveal_phone_number, reveal_personal_emails, run_waterfall_email or
  run_waterfall_phone. Never create or update Apollo contacts, accounts, sequences, tasks or labels.
- WebSearch / WebFetch to identify the company and to confirm the CEO is current.

## Steps per company
1. IDENTIFY. Find the real company behind the name: primary domain, one-line description of what it
   actually does (product, customers, corridors), HQ country. Use the region hint to disambiguate. These
   are Rail clients, so they move money cross-border (fintech / payments / crypto / banking / FX).
   If you cannot identify it with reasonable confidence, set identity_confidence "low" and say why.
2. HUBSPOT SWEEP (net-new test; strict). In Noah's HubSpot run ALL of:
   (a) COMPANY search with query = company name (properties: name, domain, lifecyclestage,
       hs_lead_status, num_associated_deals, num_associated_contacts, notes_last_contacted,
       hs_last_sales_activity_timestamp, hubspot_owner_id, createdate);
   (b) COMPANY search with filter domain CONTAINS_TOKEN the bare domain (e.g. "abra.com");
   (c) CONTACT search with query = the bare domain (properties: email, firstname, lastname, jobtitle,
       lifecyclestage, hubspot_owner_id, notes_last_contacted, hs_last_sales_activity_timestamp);
   (d) once you know the CEO's email (step 4), CONTACT search with query = that exact email.
   Classify hubspot_status:
     - "NET_NEW": nothing found in (a)-(d) that is plausibly this company or this person.
     - "IN_HUBSPOT": ANY company or contact record that is this company (any lifecycle stage, owner or
       not, deal or not). Record everything you saw: record URL(s) built from urlTemplate, lifecycle
       stage, owner id, deal count, contact count, last contacted / last activity dates.
     - "AMBIGUOUS": a name match that may be a different company (different domain / business).
   Always fill hubspot_evidence with the URLs and facts, or "no record (searched name 'X', domain
   'Y', email 'Z')".
3. CURRENT CEO (do this for every company; spend Apollo credits only on NET_NEW ones).
   apollo_mixed_people_api_search with q_organization_domains_list=[domain], person_titles
   ["CEO","Chief Executive Officer","Co-Founder & CEO","Founder & CEO","Founder","Managing Director"],
   per_page 10. Pick the person whose CURRENT title is CEO (or Co-founder & CEO / Group CEO). Then
   CONFIRM with a web check (company site team/about page, LinkedIn, 2026 press or registry) that this
   person is still CEO of THIS company as of 2026. Record ceo_evidence: the URL(s) and how recent.
   If Apollo shows no CEO, find one via web and note "email not in Apollo". If the top person is a
   Founder / Managing Director / President with no CEO title, record them with is_ceo=false and the
   exact title. If there is evidence the person LEFT or changed role (new company, "former CEO", title
   now different), set ceo_current "no", do not use them, and look for the successor.
4. EMAIL (NET_NEW only). apollo_people_match with the Apollo id from step 3 (plus first_name,
   last_name, domain). Record ceo_email, email_status (verified / likely to engage / unverified /
   unavailable), and credits used. The email domain must belong to THIS company (or its confirmed
   group domain); if it belongs to another company, set email_domain_matches false and explain.
   NEVER guess or pattern-build an email. Do not reveal personal emails.
5. FIT HOOK. From what the company does, write one specific clause (max 18 words) that completes
   "We are the missing piece for ..." for Noah's offer (named USD/EUR/GBP collection accounts,
   local payout in 70+ markets, stablecoin settlement). Ground it in step 1 facts, no invented claims.
   Example: "named USD, EUR and GBP collection behind the ramp in every new geography you switch on".
6. FLAGS. Note anything risky: dormant company, dead website, sanctions / restricted geo (e.g.
   Nigeria, Pakistan, Russia, Iran), scam or clone markers, name collision, regulator action.

## Output
Write a JSON array to the results file path given in your task, one object per company, keys exactly:
live_row, input_name, region_hint, company, domain, description, hq_country, identity_confidence,
hubspot_status, hubspot_evidence, ceo_name, ceo_first_name, ceo_title, is_ceo, ceo_current,
ceo_evidence, ceo_linkedin, ceo_email, email_status, email_domain_matches, apollo_credits_used,
fit_hook, flags.
Then reply with a compact markdown table (row | company | domain | hubspot_status | ceo | is_ceo |
ceo_current | email | email_status) and the total Apollo credits you consumed. Be exact and cite;
never invent. Write the JSON file even if some companies could not be resolved (fill nulls + flags).
