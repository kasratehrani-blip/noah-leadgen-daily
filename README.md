# Noah Daily SME Leadgen

A self-contained repo that generates **30 net-new, humanized Gmail drafts** of
Noah-fit SME prospects every weekday. Your coworker clones it, drops in four files,
and pastes one prompt into Cursor each morning. Nothing sends automatically — the run
stops at drafts, and a human reviews and clicks send.

This README is the whole manual. Read it once end to end before the first run.

---

## What this is (and what it is not)

**It is** an agent-driven daily prospecting loop. Given Noah's product positioning, its
ICP, and a HubSpot export of existing clients, it discovers fresh SME targets, screens
them so you never touch an existing or excluded account, finds the right contact, and
writes 30 outreach emails in Noah's own voice — left as Gmail drafts.

**It is not** an autosender, a mass-mail tool, or a scraper. It never sends. It never
targets a live or onboarding client. It never invents facts about a company. Every claim
in every draft traces back to a real, dated signal or to one of your input PDFs.

Why drafts and not autosend: cold outreach rides on your banking partners' reputation and
on your domain's deliverability. A human eyeballing 30 drafts for 10 minutes is the cheap
insurance that keeps both intact. The automation is everything up to the send button; the
human is the send button.

---

## The daily flow, step by step

Each run walks these seven stages in order. This is exactly what `MISSION.md` instructs
the agent to do — the summary here is so you understand what you are approving.

1. **Discover** — Search for at least 60 candidate companies throwing off a Noah-fit
   signal. Candidates are prioritised strongest-first:
   1. Using a Noah **competitor** and signalling expansion (competitor usage proves the
      product fits, so these convert best).
   2. Just **applied for or announced banking rails or a licence**.
   3. Announced **expansion** into a market Noah serves.
   4. Hiring **compliance or treasury** leadership.
   No dated signal, no candidate.

2. **Geo filter** — Drop any company headquartered in a restricted geo (full list in
   `inputs/icp.pdf`). **Nigeria and Pakistan are excluded right now** even though they sit
   inside Noah's dedicated geos, because Noah's banking partners will not accept those
   corridors at the moment. This is a live commercial block, not a permanent ICP rule.

3. **Size filter** — Keep companies with **11 to 500 employees**. Drop micro/solo (no
   budget for banking rails yet) and drop anything past lower mid-market (too slow to
   close for a daily SME motion).

4. **Screen against HubSpot** — This is the source-of-truth gate. Match every survivor
   against `inputs/hubspot-screener.csv`, by domain first then by name. Drop anyone who
   is a client, onboarding, or already in the CRM at any stage. **Net-new only.** An
   ambiguous match is dropped, not kept, and the reason is logged.

5. **Rank** — Score the survivors on fit (signal strength, corridor match, product match)
   and keep the best 30.

6. **Find the contact** — For each of the 30, identify the right point of contact and
   their email. Anything the agent cannot confirm directly, it resolves through the
   **Apollo connector**. It never guesses an address. If Apollo also can't resolve one,
   it swaps in the next-best ranked candidate so you still end with a full 30.

7. **Draft, then stop** — Write 30 Gmail drafts in Noah's voice (see the voice rules
   below), save a summary table to `out/`, and stop. All 30 sit in your Gmail Drafts
   folder for review.

---

## One-time setup (about 5 minutes)

1. **Clone and open in Cursor**
   ```bash
   git clone <this-repo-url> noah-leadgen-daily
   cursor noah-leadgen-daily
   ```

2. **Add the three input files** to `inputs/` (details and CSV format in
   `inputs/README.md`). These are gitignored, so they never land on GitHub — Kasra sends
   them to you privately.
   - `product-positioning.pdf` — what Noah sells, the capabilities, the proof points.
   - `icp.pdf` — the ideal customer profile plus the full restricted-geo list.
   - `hubspot-screener.csv` — existing clients, the net-new source of truth.

3. **Add the voice** — copy `voice/EXAMPLE-past-emails.md` to `voice/past-emails.md` and
   replace the samples with 5 to 10 real emails that landed well. This single file is what
   makes the drafts sound human instead of robotic. Do not skip it and do not stuff it with
   generic filler (see "Why voice is the whole game" below).

4. **Connect the tools in Cursor / Claude**: the **Apollo** connector (resolves emails)
   and **Gmail** (creates the drafts). If Gmail is not connected the run still produces the
   table and the email text, it just cannot place the drafts for you.

   The **Artlist** MCP server (AI image, video, and voiceover generation) is already
   configured at the project level — `.mcp.json` for Claude Code and `.cursor/mcp.json`
   for Cursor point at `https://mcp.artlist.io/mcp`. On first use the editor will prompt
   you to approve the server and complete its sign-in.

---

## Running it

Weekdays. Open Cursor in the repo, paste the entire contents of `MISSION.md`, press enter.
When it finishes:
- 30 drafts are in your Gmail **Drafts** folder.
- A summary table is in `out/` (company, domain, employee count, contact, email, the dated
  signal, priority tier, draft location) plus any companies dropped at screening and why.

Review the drafts, fix anything that reads off, send the good ones. That is the loop.

---

## The voice rules (why this matters most)

The drafts must read like a person typed them quickly, not like AI. Enforced in every
draft:
- **No em-dashes.** Do not join clauses with a hyphen either.
- Open with the specific **dated signal** that qualified the company.
- One reason Noah fits, tied to a **real capability**, not a vague benefit.
- One low-friction ask. **Under 90 words.** First name only. Warm and informal.
- **No invented facts.** Every claim traces to a PDF or a signal found this run.

**Why voice is the whole game:** the mission file can *say* "sound human," but the only
real teacher is the examples in `voice/past-emails.md`. Thin or generic examples there and
the drafts drift straight back to corporate-AI phrasing. That file is the highest-leverage
input in the entire repo. Spend more time on it than on anything else.

---

## Configuration

Every knob lives in `config.yaml` — change it there, never in the prompt:
- `target_drafts` (30) and `discovery_pool_min` (60)
- `size_band` (11 to 500 employees)
- `excluded_geos` (Nigeria, Pakistan, plus the `icp.pdf` list)
- `priority_signals` (the discovery ordering)
- `send: false` — the hard safety switch. **Never flip this to true.**

---

## Hard rules (do not break)

1. **Nothing sends without a human.** The run stops at drafts, always.
2. **Net-new only.** HubSpot CSV is the source of truth. Screen before drafting.
3. **No invented facts** in any email. Dated signal or nothing.
4. **Respect the geo blocks**, including the current Nigeria/Pakistan exclusion.
5. **Never write into HubSpot.** The screener is read-only.

---

## Troubleshooting

- **Fewer than 30 drafts came out** — discovery or Apollo could not fill the pool. Rerun;
  if it persists, the signals may be thin that day or `hubspot-screener.csv` is dropping
  too much. Check the "dropped at screening" notes in the `out/` table.
- **Drafts sound robotic** — your `voice/past-emails.md` is too thin or too generic. Add
  more real, specific examples.
- **No drafts in Gmail, only text** — the Gmail connector is not linked in Cursor.
- **A known client slipped through** — the CSV was missing that company's domain. Add it;
  domain match is more reliable than name match.
- **Emails look wrong for a company** — check the dated signal in the `out/` table; if the
  signal is weak, the draft will be too.

---

## Repo layout

```
noah-leadgen-daily/
  README.md                    this file
  .mcp.json                    project MCP servers for Claude Code (Artlist)
  .cursor/mcp.json             project MCP servers for Cursor (Artlist)
  MISSION.md                   the prompt pasted into Cursor each morning
  config.yaml                  all tunable settings
  inputs/
    README.md                  what to drop here + CSV format
    product-positioning.pdf    (you add, gitignored)
    icp.pdf                    (you add, gitignored)
    hubspot-screener.csv       (you add, gitignored)
  voice/
    EXAMPLE-past-emails.md     template
    past-emails.md             (you add, gitignored) the real voice anchor
  out/                         daily lead tables land here
```
