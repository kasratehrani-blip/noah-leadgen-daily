# Inputs

Drop these three files here before the first run. They are gitignored, so they never get
committed to GitHub. Share them privately (AirDrop, Drive, Slack DM), not through the repo.

| File | What it is | Who provides it |
|------|------------|-----------------|
| `product-positioning.pdf` | What Noah sells, the capabilities, the proof points | Kasra |
| `icp.pdf` | Ideal customer profile + the full restricted-geo list | Kasra |
| `hubspot-screener.csv` | Source of truth for net-new. One row per company. | Kasra |

## hubspot-screener.csv format

Minimum columns for the net-new screen to work by exact match:

```csv
company_name,domain,lifecycle_stage
Acme Pay,acmepay.com,Customer
Beta Remit,betaremit.io,Onboarding
Gamma FX,gammafx.co,Lead
```

The run drops any company that appears here at any stage. Domain is matched first, then
name, so include the domain wherever you have it. A name-only row still works but is
fuzzier.
