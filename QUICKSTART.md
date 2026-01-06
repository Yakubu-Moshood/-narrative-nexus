# Quick Start Guide - Narrative Nexus

Get up and running in 5 minutes!

## 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

## 2. Run the App (30 seconds)

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 3. Try the Demo (3 minutes)

### Option A: Use Sample Data (Fastest)
1. Go to **Upload** tab
2. Upload `sample_data/notes.txt`
3. Upload `sample_data/sales.csv`
4. Go to **Scan** tab - see analysis
5. Go to **Story** tab - explore 6 paths
6. Go to **Export** tab - download PDF

### Option B: Use Your Own Data
1. Prepare a TXT file with meeting notes
2. Prepare a CSV file with sales/business data
3. Follow steps 2-6 above

## Expected Results (Sample Data)

**Scan Results:**
- Echo Strength: ~95% (strong "Lagos" bias)
- Sentiment: ~60% (positive but biased)
- Mismatch: ~70% (text contradicts data)

**Key Insight:**
Team discussion emphasizes Lagos, but data shows Abuja outperforming by 60%!

**Story Paths:**
- Path 1: Continue bias → Revenue plateaus (-5%)
- Path 2: Bold pivot → Revenue surges (+15%)
- Path 3: Hybrid strategy → Steady growth (+8%)
- Path 4: Data-driven → Market leadership (+20%)
- Path 5: Gradual shift → Smooth transition (+10%)
- Path 6: Strategic focus → Competitive advantage (+12%)

## File Formats

### TXT (Meeting Notes)
```
Plain text file with discussion transcript
Max 10MB
Any encoding (UTF-8 recommended)
```

### CSV (Business Data)
```
Must include headers
Date, Region, Revenue columns recommended
Max 50MB
Standard CSV format
```

## Troubleshooting

**App won't start?**
```bash
pip install -r requirements.txt --upgrade
streamlit run app.py --logger.level=debug
```

**Sentiment analysis slow?**
- First run downloads model (~300MB)
- Subsequent runs are instant (cached)

**PDF export fails?**
```bash
pip install reportlab --upgrade
```

## Next Steps

1. **Try with your data**: Upload your own meeting notes and sales data
2. **Share the PDF**: Export and share insights with team
3. **Deploy online**: See DEPLOYMENT.md for free hosting options
4. **Record demo**: 2-minute video for portfolio

## Need Help?

- See **README.md** for detailed documentation
- See **DEPLOYMENT.md** for hosting options
- See **BUILD_LOG.md** for technical details

---

**That's it!** You now have a working decision-support tool. 🚀
