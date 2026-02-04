# GSC Audit Analysis Instructions

Use these instructions to analyze Google Search Console audit data exported by the GSC Audit Tool.

**GitHub Repository:** https://github.com/Jaicenberg/GSC-Audits.git

---

## How to Use

1. Share the current month's audit folder with Claude (contains `Top Links/` and `Pages/` subfolders)
2. Share the previous month's audit folder for comparison (optional but recommended)
3. Ask Claude to run these instructions

**Example prompt:**
```
Please run instructions.md for the PATH: [paste current month folder path]
Previous month for comparison: [paste previous month folder path]
```

---

## Analysis Tasks

### Task 1: Top Links Analysis Report

Analyze all CSV files in the `Top Links/` subfolder and generate a comprehensive report.

**Input:** All `*-Top linking sites-*.csv` files in the Top Links folder

**Output:** Generate `TopLinks_Analysis_Report.md` with the following sections:

#### Report Structure:

```markdown
# Google Search Console Top Linking Sites Analysis Report
## [Month Year] Data - Complete Analysis

---

## Overview Statistics

| Metric | Value |
|--------|-------|
| **Total Domains Analyzed** | [count] |
| **Total Unique Linking Sites** | [count] |
| **Total Link Occurrences** | [count] |
| **Average Links per Domain** | [calculated] |

---

## Top 10 Most Common Linking Sites

These sites appear most frequently across all client domains:

| Rank | Linking Site | Appearances | % of Domains |
|------|-------------|-------------|--------------|
| 1 | **[site]** | [count] | [%] |
...

### Key Insight
[Analysis of what the top linking sites indicate about the backlink profile]

---

## Month-over-Month Trend Analysis

### Overall Trends (Based on [X] Domains)

| Trend | Count | Percentage |
|-------|-------|------------|
| **Improvement** (gained links) | [count] | [%] |
| **Stable** (same or minor changes) | [count] | [%] |
| **Decrease** (lost links) | [count] | [%] |
| **New domains** | [count] | [%] |

### Biggest Improvements

| Domain | Prev Links | Current Links | Change | Notable New Links |
|--------|------------|---------------|--------|-------------------|
...

### Biggest Decreases

| Domain | Prev Links | Current Links | Change | Notable Lost Links |
|--------|------------|---------------|--------|-------------------|
...

---

## Clients with MOST Linking Sites

### Top 10 Domains by Number of Unique Backlinks:

| Rank | Domain | Unique Links | Total Linking Pages | Quality Score |
|------|--------|--------------|---------------------|---------------|
...

### Notable High-Quality Link Profiles:
- [domain] - [notable high-authority links]
...

---

## Clients with FEWEST Linking Sites

### Bottom 10 Domains - Need Attention:

| Rank | Domain | Unique Links | Status |
|------|--------|--------------|--------|
...

---

## Link Quality Categories

### High-Authority Editorial Sites (Highest Value):
- [list of high-authority domains and which clients have them]

### Quality Podcast/Media Platforms:
- [list]

### Quality Business/Professional Sites:
- [list]

### Profile/Directory Sites (Common, Low-Value):
- [list with counts]

---

## Domains No Longer in Network

[List any domains from previous month not in current data]

---

## New Domains This Month

| Domain | Links | Notes |
|--------|-------|-------|
...

---

## Summary of Changes

### Links Commonly Added:
1. [site] - [context]
...

### Links Commonly Lost:
1. [site] - [context]
...

### Quality Observations:
- [insights about link quality trends]

---

## Recommendations

### Immediate Attention Needed:
1. [domains with issues]
...

### Growth Opportunities:
1. [actionable recommendations]
...

---

*Report generated: [Date]*
*Data source: Google Search Console Top Linking Sites exports*
*Comparison: [Previous Month] → [Current Month]*
```

---

### Task 2: Indexing Analysis Report

Analyze the `Pages/` subfolder containing Coverage/Indexing data exports.

**Input:** All `*-Coverage-*.zip` or `*-Coverage-*.csv` files in the Pages folder

**Output:** Generate `Indexing_Analysis_Report.md` with the following sections:

#### Report Structure:

```markdown
# Google Search Console Page Indexing Analysis Report
## [Month Year] Data

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Properties Analyzed** | [count] |
| **Export Date** | [date] |

---

## Indexing Status Summary

[If ZIP files can be extracted and analyzed, provide detailed stats]

### Properties by Indexing Health:

| Status | Count | Percentage |
|--------|-------|------------|
| **Healthy** (mostly indexed) | [count] | [%] |
| **Needs Attention** (issues detected) | [count] | [%] |
| **Critical** (major problems) | [count] | [%] |

---

## Month-over-Month Comparison

[Compare with previous month if available]

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Total indexed pages | [count] | [count] | [+/-] |
| Pages with errors | [count] | [count] | [+/-] |
| Pages excluded | [count] | [count] | [+/-] |

---

## Properties Needing Attention

| Domain | Issue | Recommendation |
|--------|-------|----------------|
...

---

## Common Indexing Issues

1. **[Issue type]** - Affects [X] properties
   - [Explanation and fix]

---

## Recommendations

### Immediate Actions:
1. [actionable items]

### Monitoring:
1. [what to watch]

---

*Report generated: [Date]*
*Data source: Google Search Console Page Indexing exports*
```

---

## Notes

- The CSV files in `Top Links/` have format: `Site,Linking pages,Target pages`
- The ZIP/CSV files in `Pages/` contain Google's Coverage report export
- Compare current data with previous month(s) to identify trends
- Focus on actionable insights and recommendations

---

## After Analysis: Save Reports & Push to GitHub

After generating both analysis reports:

### 1. Save Reports
Save the generated reports to the `Reports/` subfolder inside the audit folder:
- `[Audit Folder]/Reports/TopLinks_Analysis_Report.md`
- `[Audit Folder]/Reports/Indexing_Analysis_Report.md`

### 2. Push to GitHub
Commit and push the reports to the GitHub repository:

```bash
cd "C:\Users\franb\OneDrive\Escritorio\Code\Google Search Console"
git add "[Audit Folder Name]"
git commit -m "Add [Month Year] analysis reports"
git push
```

**Repository:** https://github.com/Jaicenberg/GSC-Audits.git
