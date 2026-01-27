# 📊 Sample Files for Testing Narrative Nexus

Use these files to test all 3 modes of the platform!

---

## 📝 meeting_notes.txt

**Purpose**: Test Hybrid and NLQ modes

**Scenario**: A company leadership team unanimously decides to focus exclusively on the Premium segment and cut the Budget segment by 30%.

**Key Features**:
- Strong echo chamber: "Premium" mentioned 20+ times
- Team consensus on one strategy
- Ignores Budget segment potential
- Perfect for demonstrating bias detection

**How to Use**:
1. **Hybrid Mode**: Upload this + sales_data.csv
2. **NLQ Mode**: Copy text and ask questions about it

---

## 📊 sales_data.csv

**Purpose**: Test all 3 modes

**Scenario**: Real sales data showing:
- Premium segment: ~2.5% monthly growth
- Budget segment: ~10% monthly growth (4x faster!)
- Mid-Market: ~3% monthly growth

**Data Includes**:
- Date (Oct-Dec 2025)
- Segment (Premium, Budget, Mid-Market)
- Region (Urban, Rural)
- Revenue, Units Sold, Customer Count
- Satisfaction scores
- Growth rates

**Key Insight**: Budget is growing 4x faster than Premium, but the meeting notes ignore this!

**How to Use**:
1. **Hybrid Mode**: Upload meeting_notes.txt + this file
2. **Solo Mode**: Upload this file alone
3. **NLQ Mode**: Ask "Why is Budget growing faster than Premium?"

---

## 🎯 Expected Results

### Hybrid Mode
- **Echo Chamber**: Detected (Premium mentioned 20+ times)
- **Text-Data Mismatch**: ~75% (team focuses on Premium, data shows Budget growing)
- **Insight**: Team is missing the Budget opportunity

### Solo Mode
- **Growth Analysis**: Budget growing 10% vs Premium 2.5%
- **Revenue Trends**: Budget revenue increasing faster
- **Customer Satisfaction**: Budget improving (3.5→4.3)

### NLQ Mode
- Ask: "Sales dropping in rural areas—how can I fix it?"
- Get: Insights about regional opportunities
- Paths: Growth, Stability, Bold strategies

---

## 💡 Discussion Points

1. **Why is the team biased?**
   - Higher Premium margins (45% vs 25%)
   - Fewer Premium customers to manage
   - Premium is "easier"

2. **What's the real opportunity?**
   - Budget growing 4x faster
   - More customers, more scale
   - Better growth trajectory

3. **What should the company do?**
   - Don't cut Budget (it's growing!)
   - Diversify strategy
   - Serve both segments

---

## 🚀 Test Workflow

1. **Start with Solo Mode**
   - Upload sales_data.csv
   - See the data trends
   - Notice Budget growth

2. **Try Hybrid Mode**
   - Upload meeting_notes.txt + sales_data.csv
   - See the mismatch
   - Understand the bias

3. **Explore NLQ Mode**
   - Ask strategic questions
   - Get instant insights
   - See story paths

---

**Enjoy testing Narrative Nexus!** 🎉
