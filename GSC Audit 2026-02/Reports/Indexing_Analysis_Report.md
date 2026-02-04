# Google Search Console Page Indexing Analysis Report
## February 2026 Data

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Properties Analyzed** | 68 |
| **Export Date** | February 3, 2026 |
| **Data Period** | November 4, 2025 - January 30, 2026 |

---

## Indexing Status Summary

### Overall Network Statistics

| Metric | Total |
|--------|-------|
| **Total Indexed Pages** | 1,199 |
| **Total Not Indexed Pages** | 30,704 |
| **Average Indexed per Domain** | 17.6 |
| **Average Not Indexed per Domain** | 451.5* |

*Note: aymanalabdullah.com has 28,404 not-indexed pages, significantly skewing the average.

### Excluding Outlier (aymanalabdullah.com):

| Metric | Total |
|--------|-------|
| **Total Indexed Pages** | 1,168 |
| **Total Not Indexed Pages** | 2,300 |
| **Average Indexed per Domain** | 17.4 |
| **Average Not Indexed per Domain** | 34.3 |

---

### Properties by Indexing Health

| Status | Count | Percentage |
|--------|-------|------------|
| **Healthy** (>50% indexed) | 38 | 55.9% |
| **Needs Attention** (25-50% indexed) | 19 | 27.9% |
| **Critical** (<25% indexed) | 11 | 16.2% |

---

## Top 10 Best Indexed Properties

| Domain | Indexed | Not Indexed | Index Rate | Impressions |
|--------|---------|-------------|------------|-------------|
| skylarromines.com | 4 | 0 | 100% | 0 |
| taylorjacobson.org | 9 | 4 | 69.2% | 8 |
| alexlieberman.com | 38 | 26 | 59.4% | 251 |
| johnarrow.com | 21 | 16 | 56.8% | 15 |
| gregcook.me | 13 | 5 | 72.2% | 1 |
| geneseidman.com | 12 | 8 | 60.0% | 5 |
| theadamrobinson.com | 17 | 12 | 58.6% | 844 |
| collinwmartin.com | 20 | 14 | 58.8% | 188 |
| tjlarkin.com | 14 | 8 | 63.6% | 12 |
| adamrozan.com | 21 | 4 | 84.0% | 0 |

---

## Properties Needing Critical Attention

### Critical Indexing Issues (>100 Not Indexed Pages):

| Domain | Indexed | Not Indexed | Index Rate | Primary Issue |
|--------|---------|-------------|------------|---------------|
| **aymanalabdullah.com** | 31 | 28,404 | 0.1% | Massive crawling issues, duplicate content |
| **michaelgalpert.com** | 24 | 603 | 3.8% | 302 404s, 142 server errors (5xx) |
| **mikesmith.me** | 97 | 296 | 24.7% | 86 noindex pages, 78 not indexed by Google |

### Properties with Server Errors (5xx):

| Domain | 5xx Errors | Status |
|--------|------------|--------|
| michaelgalpert.com | 142 | Started validation |
| aymanalabdullah.com | 4 | Not Started |
| sorenarnsbo.com | 1 | Not Started |
| austinrief.com | 0 | N/A (previously had issues) |
| danlerman.com | 1 | Not Started |

---

## Common Indexing Issues Across Network

### Issue Breakdown (All 68 Properties):

| Issue Type | Affected Properties | Total Pages | Priority |
|------------|---------------------|-------------|----------|
| **Crawled - currently not indexed** | 56 | 16,631* | High |
| **Not found (404)** | 58 | 9,606* | High |
| **Page with redirect** | 62 | 372 | Medium |
| **Blocked by robots.txt** | 61 | 284 | Medium |
| **Discovered - currently not indexed** | 42 | 156 | Medium |
| **Alternate page with proper canonical** | 19 | 131 | Low |
| **Excluded by 'noindex' tag** | 19 | 118 | Low |
| **Duplicate without user-selected canonical** | 17 | 34 | Low |
| **Duplicate, Google chose different canonical** | 2 | 3,161* | Medium |
| **Blocked due to other 4xx issue** | 8 | 6 | Low |
| **Blocked due to access forbidden (403)** | 2 | 0 | N/A |
| **Server error (5xx)** | 5 | 148 | Critical |
| **Soft 404** | 4 | 0 | N/A |
| **Redirect error** | 1 | 1 | Low |

*Note: aymanalabdullah.com accounts for most of these high numbers.

---

## Detailed Issue Analysis

### 1. Crawled - Currently Not Indexed (HIGH PRIORITY)

Google has crawled these pages but chosen not to index them. This often indicates:
- Thin content
- Low-quality or duplicate content
- Insufficient internal linking

**Most Affected:**
- aymanalabdullah.com: 16,203 pages
- michaelgalpert.com: 94 pages
- mikesmith.me: 78 pages
- noahberkson.com: 19 pages
- randlarsen.com: 16 pages

**Recommendation:** Audit content quality, add unique value, improve internal linking.

### 2. Not Found (404) Errors (HIGH PRIORITY)

Broken pages that need to be fixed or redirected:

**Most Affected:**
- aymanalabdullah.com: 8,890 pages
- michaelgalpert.com: 302 pages
- mikesmith.me: 30 pages
- ryanbed.org: 21 pages
- sorenarnsbo.com: 11 pages

**Recommendation:** Set up proper 301 redirects or restore content. Large numbers indicate site restructuring or migration issues.

### 3. Server Errors (5xx) (CRITICAL)

Server errors prevent Google from crawling:

| Domain | Pages | Action Needed |
|--------|-------|---------------|
| michaelgalpert.com | 142 | Check server stability, hosting resources |
| aymanalabdullah.com | 4 | Investigate specific URLs |
| sorenarnsbo.com | 1 | Single page fix |
| danlerman.com | 1 | Single page fix |

**Recommendation:** Immediate server/hosting review for michaelgalpert.com.

### 4. Blocked by robots.txt (MEDIUM)

Pages intentionally or accidentally blocked:

**Most Affected:**
- randlarsen.com: 18 pages
- monicalim.co: 13 pages
- aniawysocka.com: 13 pages
- michaelgalpert.com: 9 pages
- mikesmith.me: 9 pages
- peterknox.com: 9 pages
- barbruhis.com: 9 pages
- noahberkson.com: 9 pages

**Recommendation:** Review robots.txt files. Ensure important pages are not accidentally blocked.

### 5. Page with Redirect (MEDIUM)

Redirect chains or unnecessary redirects:

**Most Affected:**
- aymanalabdullah.com: 87 pages
- mikesmith.me: 46 pages
- michaelgalpert.com: 32 pages
- jasonyoong.com: 8 pages
- adambuice.com: 7 pages

**Recommendation:** Clean up redirect chains. Ensure single-hop 301 redirects.

---

## Month-over-Month Comparison

### Indexing Trends (November 2025 to January 2026):

| Trend | Count | Description |
|-------|-------|-------------|
| **Improving** | 31 | Indexed pages increased |
| **Stable** | 22 | Minor fluctuations |
| **Declining** | 15 | Indexed pages decreased |

### Notable Improvements:
- **mikesmith.me**: 80 → 97 indexed pages (+21%)
- **alexlieberman.com**: 26 → 38 indexed pages (+46%)
- **collinwmartin.com**: 14 → 20 indexed pages (+43%)
- **chrispetkas.com**: 35 → 45 indexed pages (+29%)
- **noahberkson.com**: 26 → 43 indexed pages (+65%)

### Notable Declines:
- **adambuice.com**: 38 → 37 indexed (stable after initial drop from 42)
- **andrewkanderson.com**: 17 → 13 indexed (-24%)
- **randlarsen.com**: 35 → 30 indexed (-14%)
- **braelinnfrank.com**: 20 → 16 indexed (-20%)
- **ryanbed.org**: 10 → 6 indexed (-40%)

---

## Properties by Validation Status

### Validations in Progress:

| Domain | Issue | Status | Pages |
|--------|-------|--------|-------|
| michaelgalpert.com | Server error (5xx) | Started | 142 |
| aniawysocka.com | Crawled - not indexed | Started | 9 |
| aniawysocka.com | Discovered - not indexed | Started | 3 |
| jasonyoong.com | Crawled - not indexed | Started | 12 |
| jasonyoong.com | Discovered - not indexed | Started | 3 |
| danlerman.com | Crawled - not indexed | Started | 8 |
| danlerman.com | Discovered - not indexed | Started | 12 |

### Failed Validations:

| Domain | Issue | Pages |
|--------|-------|-------|
| adambuice.com | Crawled - not indexed | 12 |
| alexlieberman.com | Crawled - not indexed | 10 |
| andysommer.com | Page with redirect | 3 |
| andysommer.com | Crawled - not indexed | 6 |
| courtneyjohnsonnews.com | Crawled - not indexed | 4 |
| davidlkirkpatrick.com | Crawled - not indexed | 6 |
| johnwbrandes.com | Crawled - not indexed | 1 |
| mikesmith.me | Crawled - not indexed | 78 |
| noahberkson.com | Crawled - not indexed | 19 |
| randlarsen.com | Crawled - not indexed | 16 |

---

## Top Performers by Impressions

Sites with highest search visibility:

| Domain | Indexed | Impressions (Jan 30) | Avg Daily Impressions |
|--------|---------|---------------------|----------------------|
| theadamrobinson.com | 17 | 844 | ~10-50 |
| alexlieberman.com | 38 | 251 | ~150-350 |
| collinwmartin.com | 20 | 188 | ~100-250 |
| mikesmith.me | 97 | 148 | ~75-200 |
| aymanalabdullah.com | 31 | 93 | ~50-100 |
| ryanbed.org | 6 | 49 | ~20-150 |
| noahberkson.com | 43 | 46 | ~25-75 |
| chrispetkas.com | 45 | 39 | ~30-50 |
| danlerman.com | 30 | 39 | ~30-50 |
| jasonyoong.com | 32 | 28 | ~10-30 |

---

## Recommendations

### Immediate Actions:

1. **aymanalabdullah.com** - CRITICAL
   - 28,404 not-indexed pages needs immediate audit
   - Likely has duplicate content, crawl budget, or site structure issues
   - Review server capacity and crawl efficiency
   - Consider implementing proper canonicalization

2. **michaelgalpert.com** - HIGH PRIORITY
   - Fix 142 server errors (5xx) immediately
   - Clean up 302 404 pages with redirects
   - Review hosting performance

3. **mikesmith.me** - MEDIUM PRIORITY
   - Review 86 noindex pages - ensure intentional
   - Address 78 "crawled but not indexed" pages with content improvements

4. **ryanbed.org** - MEDIUM PRIORITY
   - Investigate 21 404 errors
   - Index rate declining (40% drop) needs attention

5. **randlarsen.com** - MEDIUM PRIORITY
   - Review 18 pages blocked by robots.txt
   - Address 16 "crawled but not indexed" pages

### Monitoring:

1. **Track validation progress** for sites with started validations (michaelgalpert.com, aniawysocka.com, jasonyoong.com, danlerman.com)

2. **Watch declining sites**: andrewkanderson.com, braelinnfrank.com, ryanbed.org

3. **Celebrate wins**: alexlieberman.com, noahberkson.com, chrispetkas.com showing strong improvement

### General Recommendations:

1. **Robots.txt Audit**: 61 properties have pages blocked - verify these are intentional

2. **404 Cleanup**: Implement monitoring for broken links across all properties

3. **Content Quality**: For "crawled but not indexed" issues, improve content depth and uniqueness

4. **Server Monitoring**: Set up uptime monitoring for sites with 5xx errors

5. **Redirect Cleanup**: Audit redirect chains, ensure single-hop 301s

---

*Report generated: February 3, 2026*
*Data source: Google Search Console Page Indexing exports*
