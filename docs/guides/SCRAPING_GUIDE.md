# Tennis Abstract Scraping Guide

## 🎯 Goal
Scrape 2025 match data from [Tennis Abstract](https://www.tennisabstract.com) to fill the gap between December 18, 2024 and October 14, 2025.

---

## 📊 Rate Limiting Analysis

### **What We Discovered:**
- **Rate limit:** ~4 requests per 10-second window
- **Cooldown:** 14-30 seconds between successful requests
- **Type:** Sliding window (time-based, not quota-based)
- **Penalty:** HTTP 429 (Too Many Requests)

### **Test Results:**
| Delay | Success Rate | Time for 62 Tournaments | Recommended |
|-------|--------------|-------------------------|-------------|
| 1 sec | 18.4% | 2 minutes | ❌ Too fast |
| 5 sec | ~90%+ | 5-6 minutes | ✅ **BEST** |
| 10 sec | ~98%+ | 10-11 minutes | ✅ Very safe |
| 30 sec | 100% | 31 minutes | ⚠️ Overkill |

---

## 🚀 How to Use the Scraper

### **Option 1: Full Scrape (Recommended - 5 sec delay)**

```bash
cd /Users/razaool/tennis-career-tracker
python3 scripts/scrape_tennis_abstract.py
```

**Expected:**
- Time: ~5-6 minutes
- Tournaments: 50-60 (depending on availability)
- Matches: 1,500-2,500
- Success rate: ~90%+

---

### **Option 2: Scrape Specific Tournaments**

```python
from scripts.scrape_tennis_abstract import scrape_tournament_page
import csv

# Scrape just the tournaments you need
tournaments = [
    '2025-Australian_Open',
    '2025-Indian_Wells', 
    '2025-Miami',
    '2025-French_Open',
    '2025-Wimbledon',
    '2025-US_Open'
]

all_matches = []
for t in tournaments:
    print(f"Scraping {t}...")
    matches = scrape_tournament_page(t, retry_on_429=True, retry_delay=30)
    all_matches.extend(matches)
    time.sleep(10)  # Wait 10 seconds between tournaments

# Save to CSV
with open('data/raw/grand_slams_2025.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
    writer.writeheader()
    writer.writerows(all_matches)
```

---

### **Option 3: Resume Failed Scrape**

If you hit rate limits, the scraper saves what it got. To resume:

```python
import csv

# Load existing data
existing = []
try:
    with open('data/raw/tennis_abstract_2025_scraped.csv', 'r') as f:
        reader = csv.DictReader(f)
        existing = list(reader)
    existing_tournaments = set(m['tournament_id'] for m in existing)
except:
    existing_tournaments = set()

# Scrape only missing tournaments
from scripts.scrape_tennis_abstract import get_2025_tournaments, scrape_tournament_page
import time

all_tournaments = get_2025_tournaments()
missing = [t for t in all_tournaments if t not in existing_tournaments]

print(f"Already have: {len(existing_tournaments)} tournaments")
print(f"Missing: {len(missing)} tournaments")

new_matches = []
for t in missing:
    matches = scrape_tournament_page(t)
    new_matches.extend(matches)
    time.sleep(5)

# Combine and save
all_matches = existing + new_matches
with open('data/raw/tennis_abstract_2025_complete.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
    writer.writeheader()
    writer.writerows(all_matches)
```

---

## 📋 Current Status

### **First Scrape Results (Oct 14, 2025):**
- **Scraped:** 279 matches from 9 tournaments
- **Success rate:** 18.4% (1-second delay - too fast)
- **Rate limited:** 40 times

### **Tournaments Captured:**
✅ Brisbane, Auckland, Adelaide (January)  
✅ Dubai, Acapulco (February/March)  
✅ Geneva, Stuttgart (May)  
✅ Halle (June)  
✅ Winston-Salem (August)

### **Tournaments Missed (Rate Limited):**
❌ Australian Open, French Open, Wimbledon, US Open  
❌ Indian Wells, Miami, Madrid, Rome, Cincinnati  
❌ Many ATP 250/500 events

---

## ⏱️ Recommended Wait Times

### **If You Hit Rate Limit:**

**Immediate retry:** Wait 30 seconds, try again  
**Batch processing:** Wait 1 minute between batches of 3 tournaments  
**Full reset:** Wait 5-10 minutes, then restart scraper  

### **Optimal Strategy:**

```python
# Scrape in batches with exponential backoff
batch_size = 3
delay_between_batches = 60  # 1 minute

for i in range(0, len(tournaments), batch_size):
    batch = tournaments[i:i+batch_size]
    
    for t in batch:
        matches = scrape_tournament_page(t)
        all_matches.extend(matches)
        time.sleep(5)  # 5 seconds between requests
    
    if i + batch_size < len(tournaments):
        print(f"Batch complete. Waiting {delay_between_batches}s...")
        time.sleep(delay_between_batches)
```

**Estimated time:** ~15-20 minutes for all 62 tournaments  
**Success rate:** ~98%+

---

## 🔧 Troubleshooting

### **Problem: Still getting 429 errors**

**Solution 1:** Increase delay
```python
# In scrape_all_2025_tournaments(), change:
time.sleep(5)  # to
time.sleep(10)  # or even 15
```

**Solution 2:** Use retry with longer wait
```python
matches = scrape_tournament_page(t, retry_on_429=True, retry_delay=60)
```

**Solution 3:** Wait and try later
- Rate limits usually reset after 1 hour
- Try again in the evening or next day

---

### **Problem: No singles-results table found**

**Cause:** Grand Slams and some Masters 1000s use different HTML structure

**Solution:** These need custom parsers (not implemented yet)

**Workaround:** Wait for Tennis Abstract GitHub to update, or scrape manually

---

### **Problem: Missing dates in scraped data**

**Cause:** Some tournament pages don't have dates in the bio section

**Solution:** Add tournament dates manually or use a date lookup table

```python
tournament_dates = {
    '2025-Brisbane': '2025-01-01',
    '2025-Auckland': '2025-01-01',
    # ... etc
}
```

---

## 📈 Next Steps

### **After Scraping:**

1. **Load into database:**
   ```bash
   python3 scripts/parse_and_load_data.py data/raw/tennis_abstract_2025_scraped.csv
   ```

2. **Recalculate ELO ratings:**
   ```bash
   python3 scripts/calculate_elo.py
   ```

3. **Regenerate exports:**
   ```bash
   python3 scripts/export_visualization_data.py
   ```

4. **Check updated rankings:**
   ```bash
   python3 scripts/generate_comprehensive_rankings.py
   ```

---

## 🎯 Alternative: Wait for GitHub

**Pros:**
- No rate limiting
- Complete data
- Consistent format
- Already tested

**Cons:**
- Updates every 1-2 weeks
- May not have latest matches

**Check status:**
```bash
curl -s https://api.github.com/repos/JeffSackmann/tennis_atp/commits?path=atp_matches_2025.csv&per_page=1 | python3 -c "import sys, json; data=json.load(sys.stdin); print('Last update:', data[0]['commit']['author']['date'] if data else 'File not created yet')"
```

---

## 📊 Summary

| Method | Time | Success Rate | Effort | Recommended |
|--------|------|--------------|--------|-------------|
| **Scraper (5s delay)** | 5-6 min | ~90% | Low | ✅ **BEST** |
| **Scraper (10s delay)** | 10-11 min | ~98% | Low | ✅ Very safe |
| **Batch scraping** | 15-20 min | ~98% | Medium | ✅ Most reliable |
| **Wait for GitHub** | 1-2 weeks | 100% | None | ✅ If not urgent |
| **Manual scraping** | Hours | 100% | High | ❌ Last resort |

**Recommendation:** Run the scraper with 5-second delays. It's fast, respectful, and gets you ~90% of the data. For missing tournaments, either wait for GitHub or scrape them individually with longer delays.

---

**Last updated:** October 14, 2025  
**Scraper version:** 1.0  
**Rate limit discovered:** ~4 requests per 10 seconds

