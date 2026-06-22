"""Vysta Google Ads analysis prompt resources.

Pre-built analysis prompts that users can add to their Claude conversation.
Each prompt instructs Claude to pull data via MCP tools and run the analysis.
"""

from ads_mcp.coordinator import mcp


@mcp.resource(
    uri="resource://prompt/wasted-spend-audit",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def wasted_spend_audit() -> str:
    """Wasted Spend Audit — Find search terms burning budget with zero conversions.

    Identifies irrelevant, low-intent, and duplicate search terms
    wasting ad spend. Outputs a negative keyword list sorted by spend.
    """
    return """# Wasted Spend Audit

You are a senior Google Ads analyst specializing in waste reduction. Use the connected Google Ads MCP tools to run this analysis.

## Steps
1. Ask the user for their **Customer ID** and **date range** (default: last 30 days).
2. Use the `search` tool to pull search terms data:
   - Resource: `search_term_view`
   - Fields: `search_term_view.search_term`, `search_term_view.status`, `campaign.name`, `ad_group.name`, `metrics.impressions`, `metrics.clicks`, `metrics.cost_micros`, `metrics.conversions`, `metrics.ctr`
   - First use `get_resource_metadata` for `search_term_view` to confirm exact field names.
3. Analyze the data and identify:
   - Search terms with $25+ spend and zero conversions
   - Search terms with CTR below 1% and 100+ impressions
   - Search terms that appear irrelevant to the advertiser's business
   - Duplicate/overlapping search terms cannibalizing each other

## Output Format
For each flagged term, provide a table with:
| Search Term | Campaign | Spend | Impressions | Clicks | CTR | Conversions | Why Flag | Neg Match Type |

Sort by spend (highest first).

End with:
- **Total recoverable spend/month**
- **Ready-to-import negative keyword list** (grouped by match type)
"""


@mcp.resource(
    uri="resource://prompt/cpa-spike-diagnosis",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def cpa_spike_diagnosis() -> str:
    """CPA Spike Diagnosis — Diagnose why your cost-per-acquisition suddenly increased.

    Checks bid strategy changes, search term drift, Quality Score drops,
    impression share changes, and conversion rate shifts.
    """
    return """# CPA Spike Diagnosis

You are a PPC diagnostician. Use the connected Google Ads MCP tools to diagnose a CPA spike.

## Steps
1. Ask the user for: **Customer ID**, **time period of the spike**, and **which campaign(s)** are affected.
2. Pull data using the `search` tool (use `get_resource_metadata` first to confirm fields):
   - **Campaign metrics** (resource: `campaign`): cost, conversions, CPA, impression share — compare spike period vs. prior period
   - **Search terms** (resource: `search_term_view`): look for new irrelevant queries entering during the spike
   - **Keyword Quality Scores** (resource: `keyword_view`): check for QS drops — `metrics.historical_quality_score`
   - **Device/geo breakdown** (resource: `campaign`, segmented by `segments.device` and `segments.geo_target_region`): conversion rate shifts
   - **Ad group performance** (resource: `ad_group`): identify which ad groups drove the CPA increase

## Diagnosis Checklist
Check each cause and provide evidence:
1. **Search term drift** — new irrelevant queries entering?
2. **Quality Score drops** — which keywords lost QS and why?
3. **Impression share changes** — competitors entering the auction?
4. **Conversion rate decline** — landing page or audience issues?
5. **Device/geo shifts** — traffic mix changing?
6. **Budget/bid changes** — spending pattern shifts?

## Output Format
Ranked diagnosis table:
| Rank | Cause | Severity | Evidence | Fix | Expected CPA Impact | Timeline |

Most likely cause first. End with a specific action plan.
"""


@mcp.resource(
    uri="resource://prompt/quality-score-analysis",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def quality_score_analysis() -> str:
    """Quality Score Analysis — Find keywords with low QS and estimate savings from improving them.

    Analyzes QS distribution, identifies components dragging scores down,
    and prioritizes fixes by potential cost savings.
    """
    return """# Quality Score Analysis

You are a Quality Score optimization specialist. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID**.
2. Use `get_resource_metadata` for `keyword_view` to find QS-related fields.
3. Pull data using the `search` tool:
   - Resource: `keyword_view`
   - Fields: keyword text, QS, QS components (expected CTR, ad relevance, landing page experience), campaign name, ad group name, impressions, clicks, cost, CPC, conversions
   - Condition: `campaign.status = ENABLED` and `ad_group.status = ENABLED`
4. Analyze the data.

## Analysis
1. **QS Distribution**: count keywords at QS 1-3 (poor), 4-6 (average), 7-10 (good)
2. **Revenue Impact**: estimate cost savings if QS 1-6 keywords reached QS 7 (roughly 15-50% CPC reduction)
3. **Component Breakdown**: for each low-QS keyword, which component is "Below Average"?
4. **Priority Fixes**: top 10 keywords where QS improvement saves the most money
5. **Ad Group Restructuring**: suggest tighter themes where keyword-to-ad relevance is weak

## Output Format
| Keyword | Campaign | Ad Group | QS | Exp CTR | Ad Rel | LP Exp | Monthly Spend | CPC | Fix | Est. CPC Savings |

Sort by potential monthly savings (highest first).
"""


@mcp.resource(
    uri="resource://prompt/search-term-leakage",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def search_term_leakage() -> str:
    """Search Term Leakage Scan — Find systematic patterns of irrelevant search terms.

    Groups irrelevant terms into themes, identifies missing negatives,
    and detects cross-campaign bleed.
    """
    return """# Search Term Leakage Scan

You are a search term analyst. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID** and **date range** (default: last 30 days).
2. Use `get_resource_metadata` for `search_term_view` to confirm fields.
3. Pull search terms data:
   - Resource: `search_term_view`
   - Fields: search term, campaign name, ad group name, impressions, clicks, cost, conversions, status
   - Order by cost descending
4. Analyze for leakage patterns.

## Analysis
1. **Theme clusters**: group irrelevant terms into themes (e.g., "free", "jobs", "DIY", "how to", competitor names)
2. **Missing negatives**: for each theme, list specific negative keywords to block the entire cluster
3. **Match type gaps**: broad match keywords triggering distant semantic matches
4. **Cross-campaign bleed**: same search terms appearing in multiple campaigns
5. **Brand term contamination**: non-brand campaigns capturing branded searches

## Output Format
For each leakage pattern:
| Theme | Example Terms (top 5) | Total Spend (30d) | Campaigns Affected | Recommended Negatives | Match Type |

End with a **negative keyword implementation plan** sorted by spend impact.
"""


@mcp.resource(
    uri="resource://prompt/impression-share-gap",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def impression_share_gap() -> str:
    """Impression Share Gap Finder — Find where you're losing impressions and how to capture them.

    Identifies IS lost to budget vs. rank, estimates revenue opportunity,
    and recommends budget or optimization changes.
    """
    return """# Impression Share Gap Finder

You are an impression share strategist. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID**.
2. Use `get_resource_metadata` for `campaign` to find impression share fields.
3. Pull campaign data:
   - Resource: `campaign`
   - Fields: campaign name, status, impressions, clicks, conversions, cost, CPA, `metrics.search_impression_share`, `metrics.search_budget_lost_impression_share`, `metrics.search_rank_lost_impression_share`, `metrics.search_absolute_top_impression_share`
   - Condition: `campaign.status = ENABLED`, `segments.date DURING LAST_30_DAYS`

## Analysis
1. **Budget-limited campaigns**: IS lost to budget > 10%
2. **Rank-limited campaigns**: IS lost to rank > 20%
3. **Revenue opportunity**: estimate additional conversions if IS reached 90%
4. **Budget needed**: calculate incremental daily budget to capture lost budget-based IS
5. **Rank fixes**: identify whether rank loss is bid level, QS, or ad relevance

## Output Format
| Campaign | Current IS | IS Lost (Budget) | IS Lost (Rank) | Est. Additional Conv | Fix Type | Action |

Categorize into:
- **Quick wins**: small budget increase captures significant IS
- **Optimization targets**: QS/ad improvements recover IS without more spend
- **Deprioritize**: IS gap not worth closing (low conversion rate)
"""


@mcp.resource(
    uri="resource://prompt/negative-keyword-mining",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def negative_keyword_mining() -> str:
    """Negative Keyword Mining — Generate a comprehensive negative keyword list from your data.

    Mines search terms for irrelevant queries and generates categorized
    negatives with match types, ready for import.
    """
    return """# Negative Keyword Mining

You are a negative keyword specialist. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID**, **what they sell**, and **who their target customer is**.
2. Pull search terms data:
   - Resource: `search_term_view`
   - Fields: search term, campaign, ad group, impressions, clicks, cost, conversions
   - Condition: last 30 days, order by cost descending
3. Also pull current keywords:
   - Resource: `keyword_view`
   - Fields: keyword text, match type, campaign, ad group
4. Generate comprehensive negatives.

## Generate Negatives From
1. **Search terms data**: actual irrelevant queries (zero conversions, high spend)
2. **Industry negatives**: common non-buyer intent terms ("free", "jobs", "salary", "how to become", "DIY", "reddit", "tutorial")
3. **Semantic negatives**: terms close to keywords but wrong intent
4. **Geographic negatives**: location terms outside service area (ask user)

## Output Format
Group by category:
| Category | Negative Keyword | Match Type | Apply To | Reason |

End with a **Google Ads Editor-ready import list**:
```
Keyword, Match Type, Campaign
[negative keyword], Exact, All campaigns
```
"""


@mcp.resource(
    uri="resource://prompt/bid-strategy-selector",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def bid_strategy_selector() -> str:
    """Bid Strategy Selector — Get the optimal bidding strategy for each campaign.

    Evaluates conversion volume, value variation, and budget headroom
    to recommend Manual CPC, Max Conversions, tCPA, tROAS, or Max Value.
    """
    return """# Bid Strategy Selector

You are a Google Ads bidding strategist. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID**.
2. Pull campaign data:
   - Resource: `campaign`
   - Fields: campaign name, bidding strategy type, status, impressions, clicks, conversions, cost, conversion value, CPA, ROAS, `metrics.search_impression_share`, `metrics.search_budget_lost_impression_share`
   - Condition: `campaign.status = ENABLED`, `segments.date DURING LAST_30_DAYS`
3. For deeper analysis, pull daily conversion data to assess volume consistency.

## Evaluate Each Campaign
1. **Current bid strategy** and performance trend
2. **Conversion volume**: 30+/month (needed for tCPA) or 50+/month (ideal for tROAS)?
3. **Conversion value variation**: consistent or highly variable?
4. **Budget headroom**: is the campaign budget-constrained?

## Recommendation Matrix
- **< 15 conversions/month** → Manual CPC or Maximize Clicks
- **15-30 conversions/month** → Maximize Conversions
- **30+ conversions/month, consistent CPA goal** → Target CPA
- **50+ conversions/month, value tracking** → Target ROAS
- **Ecommerce, variable order values** → Maximize Conversion Value

## Output Format
| Campaign | Current Strategy | Monthly Conv | Recommended Strategy | Target (tCPA/tROAS) | Transition Plan | Expected Impact | Risk |
"""


@mcp.resource(
    uri="resource://prompt/budget-reallocation",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def budget_reallocation() -> str:
    """Budget Reallocation Model — Optimize how your budget is distributed across campaigns.

    Ranks campaigns by efficiency, identifies donors and recipients,
    and models Conservative/Moderate/Aggressive reallocation scenarios.
    """
    return """# Budget Reallocation Model

You are a budget optimization analyst. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID** and **total monthly Google Ads budget**.
2. Pull campaign data:
   - Resource: `campaign`
   - Fields: campaign name, cost, conversions, CPA, conversion value, ROAS, `metrics.search_budget_lost_impression_share`, `metrics.search_impression_share`
   - Condition: `campaign.status = ENABLED`, `segments.date DURING LAST_30_DAYS`

## Build Reallocation Model
1. **Current state**: rank all campaigns by efficiency (conversions per dollar)
2. **Identify donors**: campaigns with high CPA, low ROAS, or declining conversion rates
3. **Identify recipients**: campaigns with low CPA, high ROAS, and IS lost to budget
4. **Model 3 scenarios**:
   - Conservative: shift 10% of total budget
   - Moderate: shift 20% of total budget
   - Aggressive: shift 35% of total budget

## Output Format
For each scenario:
| Campaign | Current Spend | New Spend | Change | Projected Conv | Projected CPA | Projected ROAS |

Summary table:
| Scenario | Total Conv (Before → After) | Blended CPA | Blended ROAS | Risk Level |

Recommend which scenario to implement and why.
"""


@mcp.resource(
    uri="resource://prompt/ad-copy-ab-generator",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def ad_copy_ab_generator() -> str:
    """Ad Copy A/B Generator — Generate two RSA variations for testing.

    Creates Version A (rational/direct) and Version B (emotional/aspirational)
    with 15 headlines and 4 descriptions each, plus pinning recommendations.
    """
    return """# Ad Copy A/B Generator

You are an expert Google Ads copywriter. Use the connected Google Ads MCP tools for context.

## Steps
1. Ask the user for:
   - **Customer ID**
   - **Which campaign/ad group** to write ads for
   - **Product/service description**
   - **Target audience**
   - **Key differentiators**
2. Pull current ad data for context:
   - Resource: `ad_group_ad`
   - Fields: ad group name, ad headlines, descriptions, performance metrics
   - Use `get_resource_metadata` first to find the exact headline/description fields
3. Pull keyword data for the ad group:
   - Resource: `keyword_view`
   - Fields: keyword text, impressions, clicks, conversions

## Generate 2 RSA Variations
**Version A** (Direct/Rational) and **Version B** (Emotional/Aspirational)

Each needs:
- **15 headlines (≤30 chars each)**:
  - 3 with primary keyword insertion
  - 3 with unique value propositions
  - 3 with social proof / numbers
  - 3 with urgency / CTA
  - 3 with benefit-focused messaging
- **4 descriptions (≤90 chars each)**:
  - 1 feature-focused
  - 1 benefit-focused
  - 1 social-proof focused
  - 1 CTA-focused

## Output Format
For each version:
| # | Headline (≤30 chars) | Char Count | Category | Pin Position |

Descriptions:
| # | Description (≤90 chars) | Char Count | Focus |

Include: pinning recommendations, test hypothesis, suggested test duration.
"""


@mcp.resource(
    uri="resource://prompt/landing-page-scorer",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def landing_page_scorer() -> str:
    """Landing Page Match Scorer — Score how well your landing pages match your ads.

    Scores message match, keyword presence, intent alignment, CTA clarity,
    and trust signals on a 1-10 scale.
    """
    return """# Landing Page Match Scorer

You are a landing page optimization specialist. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID** and **which campaign(s)** to analyze.
2. Pull ad and keyword data:
   - Resource: `ad_group_ad` — get current ad copy (headlines, descriptions, final URLs)
   - Resource: `keyword_view` — get target keywords per ad group
   - Resource: `landing_page_view` — get landing page URLs and metrics
   - Use `get_resource_metadata` first to confirm available fields.
3. For each landing page URL, ask the user to paste the page content (or fetch if accessible).

## Score Each Landing Page (1-10 scale)
1. **Message match**: does the headline echo the ad and keyword intent?
2. **Keyword presence**: are target keywords in H1, subheads, body?
3. **Intent alignment**: does the page satisfy the searcher's intent?
4. **CTA clarity**: clear next step above the fold?
5. **Trust signals**: reviews, testimonials, guarantees?
6. **Mobile experience**: responsive, fast loading?
7. **Form friction**: number of fields, required info?

**Overall score** = weighted average (message match and intent = 2x weight)

## Output Format
| Landing Page | Campaign | Keywords | Message Match | Intent | CTA | Trust | Overall | Priority |

For pages scoring below 7: specific changes, expected QS impact, expected conversion rate impact.
"""


@mcp.resource(
    uri="resource://prompt/weekly-performance-digest",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def weekly_performance_digest() -> str:
    """Weekly Performance Digest — Auto-generate a stakeholder-ready weekly report.

    Pulls this week vs. last week vs. same week last month,
    highlights top/bottom campaigns, flags anomalies, and lists action items.
    """
    return """# Weekly Performance Digest

You are a performance marketing analyst writing a weekly report. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID**.
2. Pull data for 3 periods using the `search` tool:
   - **This week** (last 7 days)
   - **Last week** (8-14 days ago)
   - **Same week last month** (28-34 days ago)
   - Resource: `campaign`
   - Fields: campaign name, impressions, clicks, CTR, CPC, cost, conversions, conversion rate, CPA, conversion value, ROAS
   - Condition: filter by date ranges, `campaign.status = ENABLED`

## Generate Report Sections

### 1. EXECUTIVE SUMMARY (3 sentences max)
Overall spend, conversions, CPA, ROAS this week. Biggest win and biggest concern.

### 2. KEY METRICS TABLE
| Metric | This Week | Last Week | WoW Change | Same Week Last Month | MoM Change |
Rows: Spend, Impressions, Clicks, CTR, CPC, Conversions, CPA, Conv. Rate, Revenue, ROAS

### 3. CAMPAIGN HIGHLIGHTS
Top 3 performers and bottom 3. What changed and why (data-backed).

### 4. ANOMALIES & FLAGS
- Any metric that moved >15% WoW
- Any campaign that spent >20% of its budget with zero conversions

### 5. NEXT WEEK ACTION ITEMS (3-5 specific tasks)
Each: what to do, expected impact, who should own it.

Keep language clear and non-technical. Use actual numbers.
"""


@mcp.resource(
    uri="resource://prompt/anomaly-detection",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def anomaly_detection() -> str:
    """Anomaly Detection Alert — Statistical anomaly detection across your campaigns.

    Calculates rolling averages and flags metrics that deviate >2 standard
    deviations from the norm.
    """
    return """# Anomaly Detection Alert

You are a statistical anomaly detector for Google Ads. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for their **Customer ID**.
2. Pull daily campaign data for the last 60 days:
   - Resource: `campaign`
   - Fields: campaign name, date, impressions, clicks, cost, CPC, CTR, conversions, conversion rate, CPA, `metrics.search_impression_share`
   - Segment by: `segments.date`
   - Condition: `campaign.status = ENABLED`

## For Each Campaign and Metric (CPC, CTR, CPA, Conv Rate, IS, Spend)
1. Calculate the **30-day rolling average** and **standard deviation**
2. Flag any day in the **last 7 days** where metric is >2 SD from the mean
3. Identify **trends**: metric gradually shifting (>5% drift over 30 days)?

## Output Format — Alert Dashboard
| Severity | Campaign | Metric | Current Value | 30-Day Avg | Std Devs | Direction | Likely Cause | Action |

Severity levels:
- **Critical** (>3 SD)
- **Warning** (>2 SD)
- **Watch** (trend drift)

Sort by severity (Critical first).
For campaigns within normal bounds: "No anomalies detected."
"""


@mcp.resource(
    uri="resource://prompt/executive-summary",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def executive_summary() -> str:
    """Executive Summary Generator — Create a C-suite ready monthly summary.

    One-page summary with headline stat, performance dashboard,
    what worked, what needs attention, and next month's plan.
    """
    return """# Executive Summary Generator

You are writing a Google Ads executive summary for a C-suite audience. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID** and **business context** (what the business sells, main goals).
2. Pull monthly data:
   - Resource: `campaign`
   - Fields: campaign name, cost, impressions, clicks, conversions, conversion value, CPA, ROAS
   - Pull **this month** and **last month** for comparison
   - Segment by `segments.month` or use date conditions

## Generate 1-Page Executive Summary

### 1. HEADLINE STAT (one sentence)
Example: "Google Ads generated $127K in revenue at 4.2x ROAS this month — up 18% from last month."

### 2. PERFORMANCE DASHBOARD (4 metrics only)
| Metric | This Month | Last Month | Change |
Revenue, Conversions, CPA, ROAS — with trend arrows.

### 3. WHAT WORKED (2-3 bullets, plain language)
Translate PPC metrics into business outcomes.
- GOOD: "More qualified prospects are clicking our ads"
- BAD: "CTR improved 0.3 points"

### 4. WHAT NEEDS ATTENTION (1-2 bullets)
Business impact framing. Include estimated dollar impact of inaction.

### 5. NEXT MONTH'S PLAN (2-3 bullets)
What you'll change and expected business outcome.

**Keep under 400 words. No jargon. Write like you're emailing the CEO.**
"""


@mcp.resource(
    uri="resource://prompt/competitor-benchmark",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def competitor_benchmark() -> str:
    """Competitor Benchmark Report — Analyze your competitive position in the auction.

    Uses impression share and available competitive metrics to benchmark
    your performance and identify strategic gaps.
    """
    return """# Competitor Benchmark Report

You are a competitive intelligence analyst. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID** and **industry**.
2. Pull campaign performance data:
   - Resource: `campaign`
   - Fields: campaign name, cost, impressions, clicks, CTR, CPC, conversions, conversion rate, CPA, ROAS, `metrics.search_impression_share`, `metrics.search_absolute_top_impression_share`, `metrics.search_budget_lost_impression_share`, `metrics.search_rank_lost_impression_share`, `metrics.search_top_impression_share`
   - Condition: `campaign.status = ENABLED`, last 30 days

## Analysis

### 1. COMPETITIVE POSITION
- Overall impression share across campaigns
- Absolute top impression share (position #1)
- Where you're losing: budget vs. rank
- Top of page rate vs. absolute top rate

### 2. PERFORMANCE BENCHMARKING
Compare the user's metrics against known industry averages:
- CPC vs. industry average
- CTR vs. industry average
- Conversion rate vs. industry average
- Verdict: above, at, or below benchmark

### 3. COMPETITIVE GAPS
- Campaigns where rank IS loss is highest (competitors outranking)
- Device or time-of-day segments where position drops

### 4. STRATEGIC RECOMMENDATIONS
- **Increase aggression**: where you're close to winning (IS > 60%, low rank loss)
- **Defend**: where competitors are gaining share
- **Retreat**: where it's not cost-effective to compete

Note: Per-competitor domain breakdown (auction insights) requires Standard Access API token. If unavailable, use impression share metrics for competitive analysis.
"""


@mcp.resource(
    uri="resource://prompt/roas-forecasting",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def roas_forecasting() -> str:
    """ROAS Forecasting Model — Forecast ROAS under different spend scenarios.

    Analyzes historical trends, models spend increase/decrease scenarios,
    and identifies the diminishing returns threshold.
    """
    return """# ROAS Forecasting Model

You are a performance forecasting analyst. Use the connected Google Ads MCP tools.

## Steps
1. Ask the user for: **Customer ID** and **any planned changes** (budget increases, new campaigns, seasonal events).
2. Pull daily data for the last 90 days:
   - Resource: `campaign`
   - Fields: campaign name, date, cost, conversions, conversion value, ROAS, CPA, impressions
   - Segment by: `segments.date`
   - Condition: `campaign.status = ENABLED`

## Build Forecast Model

### 1. HISTORICAL ANALYSIS
- Monthly ROAS trend (last 3 months)
- Seasonality patterns (day-of-week, month effects)
- ROAS decay curve: how does ROAS change as spend increases?

### 2. BASELINE FORECAST (no changes)
| Period | Projected Spend | Projected Conv | Projected Revenue | Projected ROAS |
For next 30, 60, 90 days at current spend.
Include confidence interval (optimistic, expected, pessimistic).

### 3. SCENARIO MODELING
- **Scenario A**: +15% spend — projected ROAS and incremental conversions
- **Scenario B**: +25% spend — projected ROAS and incremental conversions
- **Scenario C**: -10% spend, reallocate to top performers — projected ROAS

### 4. RISK FACTORS
- Seasonal risks
- Diminishing returns threshold: at what spend level does ROAS drop below target?
- Signs of increasing competition

## Output
| Scenario | Spend | Conversions | Revenue | CPA | ROAS |

Recommend optimal scenario with justification.
"""
