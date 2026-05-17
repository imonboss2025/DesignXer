---
# ============================================================================
# Article frontmatter template — copy this for every new article
# ============================================================================
# Required fields are marked REQUIRED. Optional fields can be omitted.

# REQUIRED
layout: article.njk              # or pillar.njk for pillar pages
title: "Your Article Title"      # H1 + <title>
date: 2026-05-17                 # publish date (yyyy-mm-dd)
cluster: cost                    # MUST match a cluster key in content-plan.yaml

# REQUIRED for cluster pieces (omit on pillar pages)
parent_pillar: small-business-website-cost-2026

# REQUIRED for pillars (set to true)
pillar: false

# === SEO ===
description: >
  150-160 character meta description. Lead with the answer, include the
  target keyword, end with a benefit.

target_keyword: "small business website cost"
secondary_keywords:
  - how much does a small business website cost
  - small business web design pricing

# === Angle / production metadata (used by /brief and /draft commands) ===
angle: >
  One-sentence statement of what makes this article unique.
  This is what makes the piece worth reading vs the top 10.
authority_play: original_survey_of_30_smbs

# === Optional ===
subtitle: "Optional subtitle below H1"
author: "DesigXner Team"
updated: 2026-05-17               # set when you /refresh

og_image: /images/og/small-business-website-cost.png

# === FAQ section (emits FAQPage schema automatically) ===
faqs:
  - q: "How much does a small business website cost in 2026?"
    a: "For a small business, expect $1,500-$8,000 with a freelancer, $8,000-$40,000 with an agency."
  - q: "Can I build a small business website for under $500?"
    a: "Yes, using DIY platforms like Squarespace or Wix. But factor in time cost and conversion limitations."

# === Table of contents (pillars only) ===
toc:
  - { id: "what-affects-cost", label: "What affects the cost" }
  - { id: "tier-1-diy", label: "Tier 1: DIY ($0–500)" }
  - { id: "tier-2-freelance", label: "Tier 2: Freelance ($1.5k–8k)" }
  - { id: "tier-3-agency", label: "Tier 3: Agency ($8k–40k)" }

---

# This is where the article body starts

Lead with the answer in the first 100 words. AI engines cite the opening
paragraph more than any other section.

## Use H2s for section headers

H2s become the table-of-contents anchors. They also get indexed separately
by Google's passage indexing.

### H3 for sub-sections

Keep the hierarchy clean.

> Use blockquotes for stat callouts. "73% of SMBs we surveyed said X."

- Bullet points work for lists, but don't overuse
- Three or more items justify a list
- Two items belong in prose

**Bold for emphasis on key claims.** Don't bold whole paragraphs.

End the article with a clear next step: link to the parent pillar, or
to a related cluster sibling, or to your services page if commercial intent.
