# DesigXner Content Engine

A pillar-and-cluster content production system targeting **118 articles** for
DesigXner.com, built on **11ty** with **Claude Code** as the production engine.

Audience: SMBs in Tier-1 countries (US, CA, UK, AU, NZ, DE, FR).

---

## What's in this repo

```
desigxner-content-engine/
├── content-plan.yaml          ← The strategic map of all 118 articles
├── package.json               ← 11ty + minimal dependencies
├── .eleventy.js               ← 11ty config (collections, permalinks, schema)
├── src/
│   ├── _includes/
│   │   ├── base.njk           ← Outer HTML shell
│   │   ├── article.njk        ← Cluster-piece layout
│   │   └── pillar.njk         ← Pillar-page layout
│   ├── content/
│   │   └── {cluster}/         ← Markdown articles live here, one folder per cluster
│   ├── sitemap.njk            ← Auto-generated sitemap
│   └── index.njk              ← Home (link here from main DesigXner site)
└── .claude/
    └── commands/              ← Custom Claude Code slash commands
        ├── brief.md           ← /brief <slug>  → research + outline
        ├── draft.md           ← /draft <slug>  → write first draft
        ├── teardown.md        ← /teardown <industry> → site teardown
        ├── audit.md           ← /audit         → full repo audit
        └── refresh.md         ← /refresh <slug> → update existing article
```

---

## The 10 authority plays (your moat)

Generic AI content gets deranked. Original data and frameworks get cited.
Pick at minimum 3-4 of these to weave through your content. Build the rest
as you grow.

1. **Teardowns** — Audit 20-30 public SMB sites per industry, publish findings.
   Each industry article should reference its own teardown.
2. **Named frameworks** — Own terminology like *The 7-Second Trust Test*,
   *The SMB Homepage Hierarchy*, *The Minimum Viable Brand System*. Repeat
   them across articles so they become DesigXner-associated entities.
3. **Free tools** — Cost calculator, audit widget, brief generator. Build
   as HTML+JS, embed in articles, link from anywhere.
4. **Mini-surveys** — 20-30 SMB owners polled via Reddit/LinkedIn. The
   stats become evergreen citations.
5. **Annual State-of report** — *State of SMB Web Design 2026* aggregates
   everything above into a flagship PDF + web report. Pitch to industry press.
6. **Public datasets** — Release the raw teardown data as downloadable CSV.
   LLMs and journalists love linkable data.
7. **Original glossary** — Define web design terms with your interpretation.
   Page per term, all interlinked. Strong for entity SEO.
8. **Downloadable templates** — RFPs, briefs, launch checklists. Gate or
   ungate — gated grows email list, ungated grows backlinks.
9. **Comparison matrices** — Side-by-side feature/price grids in HTML tables
   with semantic markup. AI engines cite these verbatim.
10. **Open-source mini-tools** — Small utilities on GitHub (image optimizer,
    schema generator, etc.) linking back to DesigXner.

---

## The content production loop

```
1.  Pick next article from content-plan.yaml (lowest write_order, P0 first)
2.  Run /brief <slug>      → outputs src/content/{cluster}/{slug}.brief.md
3.  Human review            → 5 min to add angle, examples, opinions
4.  Run /draft <slug>       → outputs src/content/{cluster}/{slug}.md
5.  Human edit              → 15-20 min: opening, examples, one strong claim
6.  Commit, push, deploy
7.  After 4-6 weeks: /refresh <slug> based on Search Console data
```

**Skip the human steps and your content will look like everyone else's
AI slop. Don't skip them.**

---

## Setup

```bash
cd desigxner-content-engine
npm install
npx @11ty/eleventy --serve
```

Open http://localhost:8080.

For Claude Code slash commands to work, this repo must be the working
directory when you run `claude` — the `.claude/commands/` folder is
auto-detected.

---

## Cadence

| Weeks | Activity | Output |
|-------|----------|--------|
| 1-3   | Write all 10 pillar pages (write_order 1-10) | 10 pillars live |
| 4-6   | Industry pages + key cost pages              | 25-30 articles live |
| 7-12  | Cluster fill: conversion, SEO, performance   | 50-60 articles live |
| 13-20 | Remaining clusters + frameworks + flagship   | 100+ articles live |
| 21+   | Audit, refresh, expand winning topics        | 118+ and growing    |

**Realistic pace**: 3-4 finished articles/week with one person + Claude Code.
Aggressive but achievable pace: 5-6/week.

---

## How to think about each article

Every piece should answer one specific buyer question that an SMB owner
in your target geographies is actually typing into Google, ChatGPT, or
Perplexity. If you can't picture the person typing it, kill the article.

Every piece should include at least one of:
- An original data point or stat (from your surveys/teardowns)
- A named framework (yours)
- A linkable asset (template, checklist, tool)
- A strong opinionated claim other agencies won't make

If a piece has none of those, it's filler. Filler hurts rankings now.

---

## Schema markup (built into templates)

- **All articles**: `Article` + `BreadcrumbList`
- **Pillars**: + `FAQPage`
- **Comparison pieces**: + `Table` markup
- **The flagship report**: `Report` + `Dataset` (links to CSV)
- **Industry pages**: + `Service` markup (you offer this service)

The `article.njk` and `pillar.njk` templates emit all of this automatically
from frontmatter.

---

## Geographic targeting note

Most articles are written for English-speaking Tier-1 markets generically.
A few are split by region (US cost vs UK/CA/AU cost) where local pricing
differs meaningfully. For German/French expansion later:
- Don't translate — rewrite for each market
- Use hreflang in `<head>` (template-ready)
- Separate URL structure: `/de/`, `/fr/`

---

## Measuring success

Track these monthly in a simple dashboard:

| Metric | Tool | Target by month 6 |
|--------|------|-------------------|
| Indexed pages | Search Console | 100+ |
| Organic clicks | Search Console | 2,000+/mo |
| Avg position (top 20 keywords) | Search Console | < 15 |
| LLM citations | Manual checks on ChatGPT/Perplexity | 5+ tracked |
| Demo/contact form submissions from content | GA4 | Set baseline by month 2 |
| Backlinks earned | Ahrefs Webmaster Tools (free) | 50+ |

---

## What to do today

1. `npm install` and verify 11ty runs locally
2. Read `content-plan.yaml` end-to-end (~15 min)
3. Pick which 3-4 authority plays you'll commit to this quarter
4. Run `/brief small-business-website-cost-2026` to start your first pillar
5. Block 4 hours tomorrow to draft and ship pillar #1
