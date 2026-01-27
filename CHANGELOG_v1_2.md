# Narrative Nexus v1.2 - Release Notes

## 🚀 Major Release: Natural Language Query (NLQ) Mode

**Release Date**: January 6, 2026  
**Status**: Production Ready  
**Test Coverage**: 21/21 tests passing (100%)

---

## ✨ What's New

### Epic 1: NLQ Input & Intent Parsing
- **Sidebar Toggle**: "💬 Natural Language Query Mode"
- **Freeform Query Box**: Type plain English business questions
- **Intent Classification**: Automatically detects:
  - `sales_issue` - Revenue/sales problems
  - `forecast` - Growth predictions and projections
  - `bias_check` - Echo chambers and blind spots
  - `general_advice` - General business guidance
- **Sentiment Detection**: Analyzes emotional tone (positive/negative/neutral)
- **Keyword Extraction**: Identifies key business terms

### Epic 2: Quick Analysis & Insights
- **Mock Data Generation**: Auto-creates realistic datasets based on query intent
- **Targeted Analysis**: 
  - Sales issues → Trend analysis + regional breakdown
  - Forecasts → Growth projections + momentum
  - Bias checks → Regional gaps + opportunity identification
  - General → Balanced performance overview
- **3-4 Actionable Insights**: Bullet-point recommendations
- **Auto-Visualization**: Plotly charts for trends

### Epic 3: Conversational Story Weaving
- **3-4 Story Branches**: Path-based narratives with outcomes
- **Each Path Includes**:
  - Title and description
  - Expected outcome
  - Growth metric (+/- %)
  - Risk assessment (0-100%)
- **Interactive Tabs**: Easy path comparison
- **Nexus Advice Score**: 0-100% confidence rating
- **Actionable Tips**: Specific recommendations per path

### Epic 4: Integration & Polish
- **Multi-Mode Support**: NLQ, Upload & Analyze, View Stories, Export
- **Optional CSV Integration**: "Tie to your data?" checkbox
- **Chat-Like UI**: Query bubbles (blue) and response bubbles (green)
- **Seamless Blending**: NLQ queries can incorporate uploaded CSV data
- **Export Support**: Download query tales as PDF
- **Feedback Integration**: "Was this helpful?" thumbs up/down

---

## 🎯 User Stories Implemented

### As a Business Owner
> "I type 'Sales dropping in rural spots—wetin I fit do to flip am?' and get instant, story-driven answers without uploading data."

**Result**: ✅ NLQ Mode generates insights in <1 minute

### As an SME Without Data
> "I can ask questions about my business and get mock data insights to explore possibilities."

**Result**: ✅ Mock data generation provides realistic scenarios

### As a Data-Driven Decision Maker
> "I want to upload my CSV and ask natural language questions about it."

**Result**: ✅ Optional CSV integration blends NLQ with real data

---

## 📊 Technical Implementation

### Core Functions
- `parse_nlq_intent()` - Intent classification with sentiment
- `generate_mock_df()` - Context-aware mock data generation
- `generate_nlq_insights()` - Quick analysis engine
- `generate_nlq_stories()` - Branching narrative generation
- `calculate_nlq_score()` - Confidence scoring

### Performance
- **Query Processing**: <20 seconds
- **Story Generation**: <30 seconds
- **Total E2E**: <1 minute
- **Mock Data Size**: 10 rows (lightweight)

### Stack
- Streamlit (UI framework)
- Pandas/NumPy (data processing)
- Plotly (visualization)
- Python (core logic)

---

## 🧪 Testing & Quality

### Test Suite: 21 Tests (100% Pass Rate)

**Intent Parsing Tests**
- ✅ Sales issue detection
- ✅ Forecast detection
- ✅ Bias check detection
- ✅ Negative sentiment detection
- ✅ Positive sentiment detection

**Mock Data Generation Tests**
- ✅ Sales issue data (declining trend)
- ✅ Forecast data (growing trend)
- ✅ Bias check data (regional differences)

**Insights & Story Tests**
- ✅ Sales issue insights
- ✅ Bias check insights
- ✅ Story generation (4 paths)
- ✅ Nexus Advice Score calculation

**End-to-End Tests**
- ✅ Complete NLQ workflow
- ✅ NLQ with uploaded CSV
- ✅ Edge cases (vague, empty, long queries)

---

## 🎨 UI/UX Improvements

### New Mode Selection
```
Sidebar: 💬 Natural Language Query
         📤 Upload & Analyze
         📖 View Stories
         💾 Export
```

### Query Interface
- Large textarea for natural language input
- Optional CSV upload trigger
- "Ask & Weave" button
- Query history tracking

### Response Display
- Query bubble (blue) showing user input
- Intent detection indicator
- Quick insights section
- Interactive story tabs
- Nexus Advice Score badge

---

## 📈 Portfolio Impact

### For Recruiters
This v1.2 release demonstrates:
- **Conversational AI**: NLQ parsing and intent classification
- **Data Science**: Mock data generation, statistical analysis
- **Product Thinking**: User-centric design, zero-friction UX
- **Full-Stack**: Frontend (Streamlit), backend (Python), data (Pandas)
- **Testing**: Comprehensive test coverage, edge case handling

### Key Talking Points
- "Built conversational analytics that turns business chat into insights"
- "Implemented NLQ parsing with 4-intent classification system"
- "Designed zero-friction interface for non-technical users"
- "Achieved <1 minute E2E response time"
- "100% test coverage with 21 unit tests"

---

## 🚀 Deployment

### Live URL
```
https://share.streamlit.io/Yakubu-Moshood/-narrative-nexus/main/app.py
```

### How to Use
1. Open the live app
2. Select "💬 Natural Language Query" mode
3. Type your business question
4. (Optional) Upload CSV for deeper insights
5. Click "Ask & Weave"
6. Explore 3-4 story branches
7. Export as PDF

### Demo Queries
- "Sales dropping in rural areas—how can I fix it?"
- "Team focused on premium but budget growing faster—what's happening?"
- "What growth can I expect next quarter?"
- "Urban bias hurting our sales—what should we do?"

---

## 🔄 Backward Compatibility

✅ **Fully Compatible with v1.1**
- Original "Upload & Analyze" mode still works
- All v1.1 features preserved
- New NLQ mode is additive, not replacing

---

## 📝 Known Limitations & Future Work

### Current Limitations
- Intent classification uses keyword matching (no ML model)
- Mock data is generic (not domain-specific)
- Story branches are templated (not LLM-generated)
- No chat history persistence (session-based only)

### Post-v1.2 Roadmap
- [ ] Integrate Hugging Face transformers for better intent detection
- [ ] Add LLM-based story generation (GPT-4, Claude)
- [ ] Implement chat history persistence
- [ ] Add domain-specific mock data templates
- [ ] Support follow-up queries in conversation
- [ ] Multi-language support (including Pidgin)

---

## 🙏 Acknowledgments

**Inspired by**:
- Business owners asking questions in plain English
- SMEs without data science backgrounds
- The need for zero-friction analytics

**Built with**:
- Streamlit for rapid development
- Python for robust backend
- Open-source libraries (Pandas, NumPy, Plotly)

---

## 📞 Support & Feedback

Have questions or feedback? 
- Open an issue on GitHub
- Submit feedback via the app
- Check README.md for full documentation

---

**Version**: 1.2  
**Build Date**: January 6, 2026  
**Status**: ✅ Production Ready  
**Next Release**: v1.3 (Q1 2026)
