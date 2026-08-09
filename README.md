# Noah Daily SME Leadgen

Clone this, drop in four files, paste one prompt into Cursor. It produces **30 net-new,
humanized Gmail drafts** of Noah-fit SMEs every weekday. Nothing sends automatically —
you review the drafts and click send.

## One-time setup (5 minutes)

1. **Clone and open in Cursor**
   ```bash
   git clone <this-repo-url> noah-leadgen-daily
   cursor noah-leadgen-daily
   ```

2. **Drop in the inputs** (see `inputs/README.md` for exactly what each is):
   - `inputs/product-positioning.pdf` — what Noah sells and why
   - `inputs/icp.pdf` — the ideal customer profile + the restricted-geo list
   - `inputs/hubspot-screener.csv` — the source of truth for net-new (company, domain, stage)

3. **Add the voice** — paste 5 to 10 real sent emails into `voice/past-emails.md`.
   This is what makes the drafts sound like Loek and not like a robot. Do not skip it.

4. **Connect the tools** in Cursor / Claude: the **Apollo** connector (to resolve emails)
   and **Gmail** (to create drafts). If Gmail is not connected, the run still produces the
   table and email text, just not the drafts.

## Daily run

Open Cursor in the repo, paste the contents of `MISSION.md`, hit enter. Weekdays only.
When it finishes, the 30 drafts are in your Gmail Drafts folder and a summary table is in
`out/`.

## What it will and will not do

- **Will:** discover, filter by geo and size, screen against HubSpot, rank, find contacts,
  draft 30 emails in your voice.
- **Will not:** send anything, target a live/onboarding client, target an excluded geo
  (Nigeria and Pakistan are excluded right now), or invent facts about a company.

## Tuning

All the knobs (size band, target count, excluded geos, priority signals) live in
`config.yaml`. Change them there, not in the prompt.
