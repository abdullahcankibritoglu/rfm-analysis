# 🛒 RFM Customer Segmentation Analysis
### End-to-End Customer Analytics Pipeline | Python · Plotly · Pandas

> A production-grade RFM analysis project built on the UCI Online Retail dataset.  
> From raw transactional data to actionable customer segments — with full data cleaning, exploratory analysis, behavioral scoring, cohort retention tracking, and business recommendations.

---

## 📌 What is This Project?

Every business has customers — but not all customers are equal. Some buy every week and spend thousands. Others bought once two years ago and never came back. Treating them all the same is a waste of marketing budget.

**RFM analysis** solves this by scoring every customer on three dimensions:

| Dimension | Question | Insight |
|---|---|---|
| **R**ecency | When did they last buy? | Are they still engaged? |
| **F**requency | How often do they buy? | Are they habitual customers? |
| **M**onetary | How much do they spend? | What is their revenue contribution? |

This project applies RFM to a real UK e-commerce dataset, segments ~4,300 customers into behavioral groups, and translates each group into concrete business actions.

---

## 📂 Dataset

**Source:** [UCI Online Retail Dataset via Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data)  
**Business:** UK-based online gift and homeware retailer  
**Period:** December 2010 – December 2011 (13 months)  
**Raw Records:** 541,909 transactions  

| Column | Type | Description |
|---|---|---|
| `InvoiceNo` | object | Invoice number. Prefix "C" = cancellation |
| `StockCode` | object | Unique product code |
| `Description` | object | Product name |
| `Quantity` | int | Units per transaction (negative = return) |
| `InvoiceDate` | datetime | Transaction timestamp |
| `UnitPrice` | float | Price per unit in GBP (£) |
| `CustomerID` | float | Unique customer identifier (nullable = guest) |
| `Country` | object | Customer's country |

---

## 🧹 Data Cleaning Pipeline

| Step | Rows Removed | Remaining | Reason |
|---|---|---|---|
| Raw data | — | 541,909 | |
| Missing CustomerID | 135,080 | 406,829 | Guest purchases — no identity |
| Cancelled invoices (C prefix) | 8,905 | 397,924 | Returns and cancellations |
| Invalid quantity / price | 40 | 397,884 | Data entry errors |
| **Final dataset** | **144,025 (26.6%)** | **397,884** | |

---

## 📊 Exploratory Data Analysis

### 1️⃣ Top 10 Countries by Revenue

**UK generates £7.3M** — roughly **25x** the next largest market (Netherlands at £290K). High market concentration = revenue risk.

**Business Implication:** The company is heavily dependent on a single market. International expansion would reduce revenue concentration risk.

---

### 2️⃣ Daily Sales Trend + 30-Day Rolling Average

Sales show a **clear upward trend** starting September 2011, peaking in November 2011.

**Key Findings:**
- **Flat period (Jan–Aug 2011):** ~£20k–£30k daily average
- **Growth phase (Sep 2011):** Gradual increase begins
- **Peak (Nov 2011):** ~£50k daily average — **Noel hediye alışveriş sezonu**
- **Strong Q4 Seasonality:** Business depends heavily on holiday season

**Business Implication:** 
- Strong seasonality driven by holiday gifting
- If you can achieve Nov 2011 levels year-round, revenue could be **2–3x higher**
- Plan inventory and marketing aggressively for Q4 (Sep–Dec)

---

### 3️⃣ Order Density Heatmap (Hour × Day of Week)

Key findings:
- **Peak hour: 12:00** — lunchtime orders dominate across all weekdays
- **No Saturday data** — the business does not operate on weekends
- **Thursday at noon** is consistently the busiest slot

**Business implication:** Email campaigns and promotions should be scheduled for **Tuesday–Thursday mornings** to catch customers before peak browsing time.

---

### 4️⃣ Top 10 Products by Quantity

The best-selling products are **low-cost, high-volume** decorative and household items:
1. PAPER CRAFT, LITTLE BIRDIE (~82K units)
2. MEDIUM CERAMIC TOP STORAGE JAR (~74K units)
3. WORLD WAR 2 GLIDERS ASST DESIGNS (~55K units)

**Business implication:** These products drive volume but may not drive margin. **Cross-selling strategy:** Use high-volume items as traffic drivers, then upsell higher-margin products to frequent buyers.

---

## 🧮 RFM Scoring Methodology

### Metrics

| Metric | Definition | Calculation |
|---|---|---|
| **Recency** | Days since last purchase | `(reference_date - last_invoice_date).days` |
| **Frequency** | Number of unique invoices | `nunique()` — not `count()` |
| **Monetary** | Total spend | `sum(TotalPrice)` |

### Scoring Logic

Each metric scored 1–5 using quintile binning (`pd.qcut`):

```python
# Recency: lower days = better → reverse labels
rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5,4,3,2,1])

# Frequency: rank() first to handle duplicate values
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5])

# Monetary: higher = better
rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1,2,3,4,5])
```

**Combined score:** `RFM_Score = str(R) + str(F) + str(M)` → e.g. `"555"` = best customer

---

## 👥 Customer Segments & Business Actions

### Segment Distribution

| Segment | Count | % of Base | Rule | Priority |
|---|---|---|---|---|
| Loyal Customers | 998 | 23.0% | R≥3, F≥3 | 🔴 High |
| Champions | 962 | 22.2% | R≥4, F≥4, M≥4 | 🔴 Critical |
| Lost | 824 | 19.0% | R≤2, F≤2, M≤2 | 🟢 Low |
| Hibernating | 781 | 18.0% | All others | 🟡 Medium |
| At Risk | 454 | 10.5% | R≤2, F≥3, M≥3 | 🔴 Urgent |
| New Customers | 319 | 7.3% | R≥4, F≤2 | 🔴 High |
| Cannot Lose Them | — | — | R≤2, F≥4, M≥4 | 🔴 Critical |

---

### 🏆 Champions
**Who they are:** Best customers. Bought recently, buy often, spend the most.  
**Revenue impact:** ~22% of customers, ~50%+ of revenue  
**Risk:** High revenue dependency — loss of Champions has outsized business impact.

**Actions:**
- VIP loyalty program with exclusive early access
- Personalized thank-you communications
- Referral incentives — Champions are the best word-of-mouth channel
- Immediate intervention at first sign of activity drop

---

### 💚 Loyal Customers
**Who they are:** Regular buyers who consistently return. One good campaign away from becoming Champions.  
**Revenue impact:** ~23% of customers, ~25%+ of revenue

**Actions:**
- Points-based rewards system
- Personalized product recommendations based on purchase history
- Bundle deals to increase average order value
- Members-only events or product previews

---

### 🆕 New Customers
**Who they are:** Purchased recently but only once or twice. The second purchase is the most important predictor of long-term retention.  
**Revenue impact:** ~7% of customers, modest revenue  
**Retention risk:** ~70% churn within 30 days (industry average)

**Actions:**
- Automated welcome email series (3–5 emails over 30 days)
- **Discount on second purchase within 30 days** — critical retention lever
- Highlight bestsellers to build confidence in the brand
- Gather feedback — what brought them, what would bring them back?

---

### ⚠️ At Risk
**Who they are:** Previously good customers who are becoming inactive. The window to save them is closing.  
**Revenue impact:** ~11% of customers, once high-value  
**Urgency:** Save NOW or lose them forever

**Actions:**
- "We miss you" personalized email with a time-limited offer
- Win-back discount (15–25%)
- Survey to understand why they stopped — product, price, service?
- Move to Lost protocol after 2–3 failed campaigns

---

### 🚨 Cannot Lose Them
**Who they are:** Former high-value customers who have gone quiet. Every day without action increases churn probability.  
**Revenue impact:** Recovering these saves significant revenue  
**Urgency:** CRITICAL — require immediate personal outreach

**Actions:**
- Direct personal outreach — not automated
- Premium win-back offer: free shipping, exclusive product, or large discount
- Escalate immediately — do not rely on standard campaigns

---

### 😴 Hibernating
**Who they are:** Low activity across all metrics. Not actively engaged but not fully lost.  
**Revenue impact:** Minimal current, but could be reactivated  
**Potential:** Seasonal triggers could wake them up

**Actions:**
- Seasonal reactivation campaigns ("New arrivals this season")
- "What's new" product update emails — low cost, low pressure
- Test with small offers before investing heavily

---

### ❌ Lost
**Who they are:** Haven't purchased in a long time, rarely bought, spent very little. Marketing spend here has poor ROI.  
**Revenue impact:** None — already churned  
**Strategy:** Accept churn, learn why, prevent future losses

**Actions:**
- One final win-back attempt — if no response, accept churn
- Remove from regular marketing lists to reduce cost
- Analyze this segment to understand **why** they churned — fix root causes for future customers

---

## 📈 Cohort Retention Analysis

### What is Cohort Analysis?

Customers grouped by **first purchase month**. We track what percentage returns each subsequent month.

*"Of customers who first purchased in January 2011, how many came back in February? In June?"*

### Key Findings

| Cohort | Month 0 (First Purchase) | Month 1 After | Month 2 After | Months 3+ | Insight |
|---|---|---|---|---|---|
| **Jan 2011** | 100% | ~30% | ~22% | ~15–20% | **Best long-term retention** — early adopters most loyal |
| **Mar 2011** | 100% | ~25% | ~18% | ~12–15% | Consistent mid-year performance |
| **May 2011** | 100% | ~20% | ~15% | ~10–12% | Slight decline |
| **Jul 2011** | 100% | ~18% | ~13% | ~8–10% | Continued trend |
| **Nov 2011** | 100% | ~15% | N/A | N/A | Too recent to measure long-term |

### Critical Insights

🔴 **Sharp retention drop after month 1:** ~70% customer loss within 30 days — typical for e-commerce but improvable

🟡 **Jan 2011 cohort is an outlier:** Better long-term retention suggests early customers have stronger brand affinity

💡 **The diagonal blank space:** Future months don't exist yet — expected pattern

### Business Implications

**The biggest retention challenge** is converting one-time buyers into repeat customers.

**Strategic Opportunity:** A strong 30-day post-purchase onboarding sequence would have the **highest ROI impact** on overall retention rates.

**Recommended Actions:**
- Welcome email series (Day 1, 3, 7, 14, 21)
- Second-purchase incentive (15–25% off, valid 30 days)
- Personalized product recommendations
- Proactive customer support reach-out

**Potential Impact:** If you can move Month 1 retention from 15–20% to 25–30%, you'd increase customer lifetime value by 50%+

---

## 🔍 RFM Scatter Plot

**X-Axis:** Recency (days since last purchase)  
**Y-Axis:** Monetary (total spend in £)  
**Bubble Size:** Frequency (purchase count)  
**Color:** Segment classification

### Visual Patterns

- **Top-left cluster (Champions, red):** Low Recency (recently bought), High Monetary (big spenders), Large bubbles (frequent buyers) — These are your superstars
- **Mid-left (Loyal Customers, cyan):** Moderate recency, moderate spend, consistent size — Steady revenue generators
- **Right side (At Risk, Lost, Hibernating):** High Recency (haven't bought in ages), low spend — Dormant or churned
- **Bottom-left (New Customers):** Recent but low spend, small bubbles — Young relationship, high potential

### Strategic Insight

**The concentration of large, red bubbles in the top-left** = your business model works for high-value repeat customers. **The sparse coverage on the left-bottom** = you need better conversion from new to loyal.

---

## 🎯 Strategic Summary

### Revenue Concentration
- 🇬🇧 **92% from UK** — reduce single-market risk through expansion
- **22% of customers (Champions + high-tier Loyal) generate 50%+ of revenue**

### Seasonality Opportunity
- **Nov peak = 2–3x baseline** — with year-round Nov performance, revenue could triple
- **Q4 planning is critical** — inventory, marketing, staffing

### Retention Crisis
- **70% month-1 churn** — standard but fixable
- **30-day onboarding could move needle 5–10%** — massive ROI

### Product Strategy
- **Low-margin volume items drive traffic** — use cross-selling to upsell
- **Top 10 products are decorative/gifts** — leverage seasonality here

---

## 🔁 Reusable Pipeline

The entire analysis is encapsulated in a single callable function:

```python
df_raw = pd.read_csv("online_retail.csv", encoding="latin1")
rfm = run_rfm_pipeline(df_raw.copy())
```

**Why `.copy()`?** Prevents the function from modifying the original dataframe — good practice for reproducible analysis.

This enables:
- **Reproducibility** — identical results every run
- **Modularity** — easy to swap datasets or adjust parameters
- **Production readiness** — can be scheduled or integrated into a larger pipeline

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `pandas>=1.5.0` | Data manipulation and aggregation |
| `plotly>=5.0.0` | Interactive visualizations (HTML export) |
| `kaleido>=0.2.1` | Static image export support |
| `datetime` | Date arithmetic for Recency calculation |

---

## ⚙️ Setup & Usage

```bash
# 1. Clone the repository
git clone https://github.com/abdullahcankibritoglu/rfm-analysis.git
cd rfm-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create visualizations directory
mkdir visualizations

# 4. Add the dataset
# Download online_retail.csv from Kaggle and place in project root
# https://www.kaggle.com/datasets/carrie1/ecommerce-data

# 5. Run the analysis
python rfm.py
```

All visualizations will be saved to `visualizations/` as interactive HTML files.

---

## 📁 Project Structure

```
rfm-analysis/
│
├── rfm.py                      # Main analysis script
├── online_retail.csv           # Dataset (download from Kaggle)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Excludes dataset and cache
├── README.md                   # Project documentation
│
└── visualizations/             # Auto-generated (create with mkdir)
    ├── top_countries.html
    ├── daily_sales.html
    ├── heatmap.html
    ├── top_products.html
    ├── treemap.html
    ├── scatter.html
    └── cohort.html
```

---

## 🔮 Potential Extensions

- [ ] **Streamlit dashboard** — interactive segment explorer with real-time filters
- [ ] **ML-based segmentation** — K-Means clustering as alternative to rule-based approach
- [ ] **CLV prediction** — predict future customer lifetime value using RFM scores
- [ ] **Automated reporting** — scheduled pipeline with email summary output
- [ ] **A/B testing framework** — test win-back campaigns on At Risk segment
- [ ] **Churn prediction model** — identify who will churn next month, intervene early

---

## 📚 Key Learnings

✅ **RFM is not a one-time analysis** — run monthly to track segment migrations and campaign impact  
✅ **Segment-based actions beat generic marketing** — Champions need different strategy than New Customers  
✅ **Retention > Acquisition** — keeping a $100 customer is cheaper than finding a new one  
✅ **Data tells a story** — seasonality + cohort patterns reveal business dynamics  
✅ **Actionability > Complexity** — 7 segments beats 100 micro-segments you can't act on  

---

## 👤 Author

**Abdullah Can Kibritoglu**  
[GitHub](https://github.com/abdullahcankibritoglu) · [Email](mailto:abdullahcankibritoglukjadsjdk@gmail.com)

---

## 📄 License

This project is open source and available under the MIT License.

---

*Dataset Source: Dr. Daqing Chen, School of Engineering, London South Bank University*  
*Data Period: December 2010 – December 2011 | Records: 541,909 transactions*
