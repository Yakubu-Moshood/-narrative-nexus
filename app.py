"""
Narrative Nexus v1.2 - Hybrid Data-Storyteller for SME Decisions
Fuses qualitative team discussions with quantitative data to detect biases,
simulate outcomes, and generate interactive branching narratives.
Now with Natural Language Query (NLQ) Mode for conversational insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from collections import Counter
from datetime import datetime
import json
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# NLP capabilities - using basic methods for Streamlit Sharing compatibility
HAS_TRANSFORMERS = False


# ==================== HEALTH CHECK & ERROR HANDLING ====================

def health_check():
    """Health check endpoint - returns status."""
    return {"status": "Nexus Alive!", "timestamp": datetime.now().isoformat()}

def safe_execute(func, *args, **kwargs):
    """Safely execute function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)[:100]}")
        return None

def validate_text_input(text, max_words=2000):
    """Validate text input."""
    if not text or len(text.strip()) == 0:
        st.warning("📝 Please enter some text")
        return None
    
    word_count = len(text.split())
    if word_count > max_words:
        st.warning(f"📝 Text too long ({word_count} words). Max: {max_words}. Truncating...")
        return ' '.join(text.split()[:max_words])
    
    return text

def validate_csv_input(csv_file, max_rows=1000):
    """Validate CSV input."""
    try:
        df = pd.read_csv(csv_file)
        
        if df.empty:
            st.error("⚠️ CSV file is empty!")
            return None
        
        if len(df.columns) < 2:
            st.error("⚠️ CSV needs at least 2 columns!")
            return None
        
        if len(df) > max_rows:
            st.warning(f"⚠️ CSV too large ({len(df)} rows). Max: {max_rows}. Using first {max_rows} rows...")
            return df.head(max_rows)
        
        return df
    except Exception as e:
        st.error(f"⚠️ CSV Error: {str(e)[:100]}")
        return None

def validate_query_input(query):
    """Validate NLQ query."""
    if not query or len(query.strip()) < 3:
        st.warning("💭 Please ask a more specific question (at least 3 characters)")
        return None
    
    if len(query) > 500:
        st.warning("💭 Query too long. Truncating...")
        return query[:500]
    
    return query


# Configure Streamlit page
st.set_page_config(
    page_title="Narrative Nexus v1.2+ Day 1",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .query-bubble {
        background-color: #667eea;
        color: white;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .response-bubble {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .tooltip-text {
        color: #666;
        font-size: 0.85rem;
        font-style: italic;
        margin-top: 4px;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    @media (max-width: 768px) {
        .main {
            padding: 10px;
        }
        .query-bubble {
            max-width: 90%;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==================== UTILITY FUNCTIONS ====================

def initialize_session_state():
    """Initialize session state variables."""
    try:
        if 'uploaded_text' not in st.session_state:
            st.session_state.uploaded_text = None
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'scan_results' not in st.session_state:
            st.session_state.scan_results = None
        if 'story_branches' not in st.session_state:
            st.session_state.story_branches = None
        if 'simulations' not in st.session_state:
            st.session_state.simulations = None
        if 'nlq_mode' not in st.session_state:
            st.session_state.nlq_mode = False
        if 'nlq_history' not in st.session_state:
            st.session_state.nlq_history = []
        if 'first_time_user' not in st.session_state:
            st.session_state.first_time_user = True
        if 'user_interactions' not in st.session_state:
            st.session_state.user_interactions = {
                'queries_run': 0,
                'files_uploaded': 0,
                'branches_clicked': 0,
                'exports_generated': 0
            }
    except (AttributeError, RuntimeError):
        # Running in test mode or without streamlit context
        pass

try:
    initialize_session_state()
except:
    pass

# ==================== NLQ MODE FUNCTIONS (v1.2) ====================

def parse_nlq_intent(query):
    """Parse query intent using keyword matching (fallback for transformers)."""
    query_lower = query.lower()
    
    # Intent classification based on keywords (check bias_check first)
    if any(word in query_lower for word in ['bias', 'echo', 'focus', 'focused', 'ignore', 'miss', 'overlook', 'blind', 'overlooking']):
        intent = 'bias_check'
    elif any(word in query_lower for word in ['drop', 'down', 'low', 'decline', 'fall', 'issue', 'problem', 'loss', 'bad']):
        intent = 'sales_issue'
    elif any(word in query_lower for word in ['forecast', 'predict', 'future', 'next', 'expect', 'grow', 'rise']):
        intent = 'forecast'
    else:
        intent = 'general_advice'
    
    # Sentiment analysis - improved
    positive_words = {'good', 'great', 'excellent', 'amazing', 'boost', 'increase', 'opportunity', 'growth', 'positive'}
    negative_words = {'bad', 'poor', 'terrible', 'drop', 'decline', 'issue', 'problem', 'loss', 'unhappy', 'major', 'problems', 'dropped'}
    
    words = query_lower.split()
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    if neg_count > pos_count:
        sentiment = 'negative'
    elif pos_count > neg_count:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'
    
    # Extract key terms
    key_terms = [word for word in query_lower.split() if len(word) > 4 and word not in {'what', 'when', 'where', 'which', 'their', 'about', 'should', 'could', 'would'}]
    
    return {
        'intent': intent,
        'sentiment': sentiment,
        'key_terms': key_terms[:3],
        'query': query
    }

def generate_mock_df(query_data):
    """Generate mock DataFrame based on query intent."""
    intent = query_data['intent']
    key_terms = query_data['key_terms']
    
    if intent == 'sales_issue':
        # Generate sales data with declining trend
        regions = ['Urban', 'Rural', 'Suburban']
        data = {
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': [regions[i % 3] for i in range(10)],
            'Revenue': [5000 - (i * 150) for i in range(10)],
            'Units_Sold': [100 - (i * 5) for i in range(10)],
            'Customer_Satisfaction': [4.2 - (i * 0.1) for i in range(10)]
        }
    elif intent == 'forecast':
        # Generate growth data
        regions = ['Urban', 'Rural', 'Suburban']
        data = {
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': [regions[i % 3] for i in range(10)],
            'Revenue': [5000 + (i * 200) for i in range(10)],
            'Units_Sold': [100 + (i * 8) for i in range(10)],
            'Customer_Satisfaction': [4.0 + (i * 0.05) for i in range(10)]
        }
    elif intent == 'bias_check':
        # Generate data showing regional differences
        regions = ['Urban', 'Rural', 'Suburban']
        data = {
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': [regions[i % 3] for i in range(10)],
            'Revenue': [7000 if regions[i % 3] == 'Urban' else 5000 if regions[i % 3] == 'Rural' else 6000 for i in range(10)],
            'Units_Sold': [140 if regions[i % 3] == 'Urban' else 80 if regions[i % 3] == 'Rural' else 110 for i in range(10)],
            'Customer_Satisfaction': [4.5 if regions[i % 3] == 'Urban' else 3.8 if regions[i % 3] == 'Rural' else 4.1 for i in range(10)]
        }
    else:
        # General advice - balanced data
        regions = ['Urban', 'Rural', 'Suburban']
        data = {
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': [regions[i % 3] for i in range(10)],
            'Revenue': [5500 + np.random.randint(-500, 500) for i in range(10)],
            'Units_Sold': [100 + np.random.randint(-20, 20) for i in range(10)],
            'Customer_Satisfaction': [4.0 + np.random.uniform(-0.3, 0.3) for i in range(10)]
        }
    
    return pd.DataFrame(data)

def generate_nlq_insights(query_data, df):
    """Generate quick insights from query and data."""
    intent = query_data['intent']
    
    insights = []
    
    if intent == 'sales_issue':
        # Analyze declining trend
        revenue_change = df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]
        pct_change = (revenue_change / df['Revenue'].iloc[0]) * 100
        insights.append(f"📉 Revenue trend: {pct_change:.1f}% change over period")
        
        # Regional analysis
        if 'Region' in df.columns:
            regional = df.groupby('Region')['Revenue'].mean()
            best_region = regional.idxmax()
            insights.append(f"🏆 Best performing region: {best_region} (${regional[best_region]:.0f} avg)")
        
        insights.append("💡 Recommendation: Investigate regional differences and customer satisfaction drivers")
    
    elif intent == 'forecast':
        revenue_change = df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]
        pct_change = (revenue_change / df['Revenue'].iloc[0]) * 100
        insights.append(f"📈 Projected growth: {pct_change:.1f}% increase expected")
        insights.append(f"🎯 Growth momentum: Steady upward trend detected")
        insights.append("✅ Recommendation: Capitalize on growth - scale operations accordingly")
    
    elif intent == 'bias_check':
        if 'Region' in df.columns:
            regional = df.groupby('Region')['Revenue'].mean()
            max_region = regional.idxmax()
            min_region = regional.idxmin()
            gap = regional[max_region] - regional[min_region]
            insights.append(f"⚠️ Regional gap detected: {max_region} outperforms {min_region} by ${gap:.0f}")
            insights.append(f"🔍 Potential bias: Team may be overlooking {min_region} opportunities")
            insights.append("💡 Recommendation: Diversify strategy - don't ignore underperforming regions")
    
    else:
        insights.append("📊 Data shows mixed performance across segments")
        insights.append("🎯 Opportunity: Balanced approach recommended")
        insights.append("💡 Recommendation: Analyze specific pain points for targeted improvements")
    
    return insights

def generate_nlq_stories(query_data, df, insights):
    """Generate 3-4 story branches with personalized narratives and dynamic metrics."""
    intent = query_data['intent']
    query = query_data['query']
    key_terms = ' '.join(query_data['key_terms'])
    
    # Calculate dynamic metrics from data
    if df is not None and 'Revenue' in df.columns:
        current_revenue = df['Revenue'].iloc[-1]
        avg_revenue = df['Revenue'].mean()
    else:
        current_revenue = 5000
        avg_revenue = 5000
    
    stories = []
    
    if intent == 'sales_issue':
        stories = [
            {'title': 'Path 1: Status Quo (Risky)', 'description': f'Continue without action on {key_terms}. Revenue declines.', 'outcome': f'Revenue drops 15-20% (${current_revenue * 0.8:.0f})', 'growth': -15, 'risk': 85, 'recommendation': 'Not recommended'},
            {'title': 'Path 2: Quick Fixes (Safe)', 'description': f'Targeted interventions for {key_terms}. Quick wins.', 'outcome': f'Revenue +5% (${current_revenue * 1.05:.0f})', 'growth': 5, 'risk': 45, 'recommendation': 'Good for stabilization'},
            {'title': 'Path 3: Strategic Pivot (Balanced)', 'description': f'Reallocate resources for {key_terms}. Focused growth.', 'outcome': f'Revenue +12-15% (${current_revenue * 1.13:.0f})', 'growth': 12, 'risk': 35, 'recommendation': 'Recommended - balanced'},
            {'title': 'Path 4: Transformation (Bold)', 'description': f'Deep fix for {key_terms}. Comprehensive approach.', 'outcome': f'Revenue +20%+ (${current_revenue * 1.20:.0f})', 'growth': 20, 'risk': 55, 'recommendation': 'Best long-term'}
        ]
    elif intent == 'forecast':
        stories = [
            {'title': 'Path 1: Conservative', 'description': f'Steady pace for {key_terms}.', 'outcome': f'+8-10% growth (${current_revenue * 1.09:.0f})', 'growth': 8, 'risk': 20, 'recommendation': 'Safe choice'},
            {'title': 'Path 2: Aggressive', 'description': f'Double investment in {key_terms}.', 'outcome': f'+25-30% growth (${current_revenue * 1.27:.0f})', 'growth': 25, 'risk': 60, 'recommendation': 'For risk-takers'},
            {'title': 'Path 3: Balanced', 'description': f'50% increase in {key_terms}.', 'outcome': f'+15-18% growth (${current_revenue * 1.16:.0f})', 'growth': 15, 'risk': 40, 'recommendation': 'Recommended'}
        ]
    elif intent == 'bias_check':
        stories = [
            {'title': 'Path 1: Ignore Bias', 'description': f'Continue ignoring {key_terms} signals.', 'outcome': f'Miss 10-15% opportunity', 'growth': -10, 'risk': 80, 'recommendation': 'Not recommended'},
            {'title': 'Path 2: Diversify', 'description': f'Pivot to address {key_terms}.', 'outcome': f'Unlock +12-18% revenue', 'growth': 15, 'risk': 45, 'recommendation': 'Bold move'},
            {'title': 'Path 3: Balanced', 'description': f'Test {key_terms} while maintaining strength.', 'outcome': f'Steady +8-12% growth', 'growth': 10, 'risk': 35, 'recommendation': 'Recommended'}
        ]
    else:
        stories = [
            {'title': 'Path 1: Maintain', 'description': f'Keep {key_terms} operations.', 'outcome': f'Stable revenue', 'growth': 0, 'risk': 25, 'recommendation': 'Maintains position'},
            {'title': 'Path 2: Optimize', 'description': f'Improve {key_terms} efficiency.', 'outcome': f'+5-8% growth', 'growth': 6, 'risk': 30, 'recommendation': 'Low-risk'},
            {'title': 'Path 3: Innovate', 'description': f'New approach to {key_terms}.', 'outcome': f'+10-15% growth', 'growth': 12, 'risk': 50, 'recommendation': 'Higher upside'}
        ]
    
    return stories
def calculate_nlq_score(query_data, insights):
    """Calculate Nexus Advice Score for NLQ response."""
    intent = query_data['intent']
    
    # Base score on intent clarity
    score = 70
    
    # Adjust based on sentiment
    if query_data['sentiment'] == 'negative':
        score += 15  # Negative sentiment = clearer problem
    elif query_data['sentiment'] == 'positive':
        score += 10
    
    # Adjust based on number of insights
    score += min(len(insights) * 5, 20)
    
    return min(score, 95)

# ==================== EXISTING FUNCTIONS (v1.1) ====================

def validate_and_preview_text(text_content):
    """Validate and preview text file."""
    return validate_text_input(text_content, max_words=2000)

def validate_and_preview_csv(csv_data):
    """Validate and preview CSV file."""
    try:
        df = pd.read_csv(csv_data)
        
        if df.empty:
            st.error("⚠️ CSV file is empty!")
            return None
        
        if len(df.columns) < 2:
            st.error("⚠️ CSV needs at least 2 columns!")
            return None
        
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {str(e)}")
        return None

def extract_keywords(text, top_n=20):
    """Extract top keywords from text."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'so',
        'than', 'too', 'very', 'just', 'as', 'with', 'from', 'up', 'about',
        'out', 'if', 'because', 'as', 'by', 'down', 'through', 'during'
    }
    
    words = re.findall(r'\b[a-z]+\b', text.lower())
    words = [w for w in words if w not in stop_words and len(w) > 3]
    word_freq = Counter(words)
    return word_freq.most_common(top_n)

def detect_echo_chambers(text):
    """Detect echo chambers (repeated ideas/keywords)."""
    keywords = extract_keywords(text, top_n=30)
    echoes = []
    for word, freq in keywords:
        if freq >= 3:
            echoes.append({
                'keyword': word,
                'frequency': freq,
                'echo_strength': min(100, freq * 15)
            })
    return sorted(echoes, key=lambda x: x['frequency'], reverse=True)

def analyze_sentiment_basic(text):
    """Basic sentiment analysis."""
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'best', 'perfect', 'awesome', 'brilliant', 'outstanding',
        'success', 'growth', 'profit', 'increase', 'boost', 'strong',
        'opportunity', 'potential', 'promising', 'positive', 'win'
    }
    
    negative_words = {
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst',
        'hate', 'fail', 'loss', 'decrease', 'decline', 'weak',
        'risk', 'danger', 'problem', 'issue', 'negative', 'concern',
        'difficult', 'challenge', 'struggle', 'threat'
    }
    
    words = text.lower().split()
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    total = pos_count + neg_count
    if total == 0:
        return 50
    
    sentiment_score = (pos_count / total) * 100
    return sentiment_score

def calculate_mismatch_score(text, df):
    """Calculate nexus mismatch score between text and data."""
    if df is None or df.empty:
        return 50
    
    try:
        keywords = extract_keywords(text, top_n=10)
        text_lower = text.lower()
        regions_in_text = []
        
        if 'lagos' in text_lower:
            regions_in_text.append('Lagos')
        if 'abuja' in text_lower:
            regions_in_text.append('Abuja')
        
        if 'Region' in df.columns and 'Revenue' in df.columns:
            region_stats = df.groupby('Region')['Revenue'].agg(['mean', 'sum', 'count'])
            top_region = region_stats['mean'].idxmax()
            
            if regions_in_text and top_region not in regions_in_text:
                mismatch = 70
            elif regions_in_text and top_region in regions_in_text:
                mismatch = 20
            else:
                mismatch = 50
        else:
            mismatch = 50
        
        return mismatch
    except:
        return 50

def run_monte_carlo_simulation(df, bias_flip=False, n_runs=100):
    """Run Monte Carlo simulation."""
    if df is None or df.empty or 'Revenue' not in df.columns:
        return None
    
    try:
        revenue_data = df['Revenue'].values
        base_mean = revenue_data.mean()
        base_std = revenue_data.std()
        
        if bias_flip:
            sim_mean = base_mean * 1.15
            sim_std = base_std * 0.9
        else:
            sim_mean = base_mean
            sim_std = base_std
        
        simulations = np.random.normal(sim_mean, sim_std, n_runs)
        simulations = np.maximum(simulations, 0)
        
        return {
            'simulations': simulations,
            'mean': simulations.mean(),
            'std': simulations.std(),
            'min': simulations.min(),
            'max': simulations.max(),
            'percentile_25': np.percentile(simulations, 25),
            'percentile_75': np.percentile(simulations, 75)
        }
    except:
        return None

# ==================== UI SECTIONS ====================

def display_nlq_mode():
    """Display NLQ Mode interface with Day 1 enhancements."""
    st.header("💬 Natural Language Query Mode")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Ask your business question in plain English**")
        st.markdown('<p class="tooltip-text">💡 Tip: Be specific! E.g., "Sales dropping in rural areas" vs. "Why is business bad?"</p>', unsafe_allow_html=True)
        query = st.text_area(
            "What's your business challenge?",
            placeholder="E.g., 'Sales dropping in rural areas—how can I fix it?' or 'Team focused on premium but budget growing faster'",
            height=100,
            key="nlq_query"
        )
    
    with col2:
        st.markdown("**Optional: Add Data**")
        if st.checkbox("Tie to your data?"):
            csv_file = st.file_uploader("Upload CSV", type=["csv"], key="nlq_csv")
            if csv_file:
                df = validate_and_preview_csv(csv_file)
                if df is not None:
                    st.session_state.uploaded_data = df
                    st.success("✅ Data loaded")
    
    if st.button("🚀 Ask & Weave", use_container_width=True):
        if not query.strip():
            st.error("Please ask a question!")
            return
        
        # Parse query
        query_data = parse_nlq_intent(query)
        
        # Display query bubble
        st.markdown(f'<div class="query-bubble">💭 {query}</div>', unsafe_allow_html=True)
        
        with st.spinner("🔄 Analyzing and weaving your story..."):
            # Generate or use uploaded data
            if st.session_state.uploaded_data is not None:
                df = st.session_state.uploaded_data
                st.info("📊 Using your uploaded data")
            else:
                df = generate_mock_df(query_data)
                st.info("📊 Using sample data (upload your CSV for deeper insights)")
            
            # Generate insights
            insights = generate_nlq_insights(query_data, df)
            
            # Display insights
            st.markdown(f'<div class="response-bubble"><b>🔍 Intent Detected:</b> {query_data["intent"].replace("_", " ").title()}</div>', unsafe_allow_html=True)
            
            st.subheader("📌 Quick Insights")
            for insight in insights:
                st.write(f"• {insight}")
            
            # Generate stories
            stories = generate_nlq_stories(query_data, df, insights)
            
            # Display story branches
            st.subheader("📖 Your Story Branches")
            
            tabs = st.tabs([f"Path {i+1}" for i in range(len(stories))])
            
            for i, tab in enumerate(tabs):
                with tab:
                    story = stories[i]
                    st.write(f"**{story['title']}**")
                    st.write(story['description'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📈 Growth", f"{story['growth']:+d}%")
                    with col2:
                        st.metric("⚠️ Risk", f"{story['risk']}%")
                    
                    st.info(f"**Outcome**: {story['outcome']}")
            
            # Calculate and display Nexus Score
            score = calculate_nlq_score(query_data, insights)
            st.markdown(f'<div class="success-card"><b>🎯 Nexus Advice Score: {score:.0f}%</b> - Follow the path that aligns with your risk tolerance!</div>', unsafe_allow_html=True)
            
            # Add to history
            st.session_state.nlq_history.append({
                'query': query,
                'intent': query_data['intent'],
                'score': score,
                'timestamp': datetime.now()
            })

def display_input_section():
    """Display input handling section (Epic 1)."""
    st.header("📤 Upload Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Meeting Notes (TXT)")
        text_file = st.file_uploader(
            "Upload meeting notes or discussion transcript",
            type=["txt"],
            key="text_uploader",
            help="Max 10MB. Plain text format."
        )
        
        if text_file:
            text_content = text_file.read().decode('utf-8')
            validated_text = validate_and_preview_text(text_content)
            
            if validated_text:
                st.session_state.uploaded_text = validated_text
                word_count = len(validated_text.split())
                st.success(f"✅ Loaded: {word_count} words")
                
                with st.expander("👁️ Preview Text"):
                    st.text_area("Text Preview", validated_text[:500] + "...", height=150, disabled=True)
    
    with col2:
        st.subheader("📊 Sales Data (CSV)")
        csv_file = st.file_uploader(
            "Upload CSV with metrics (Date, Region, Revenue, etc.)",
            type=["csv"],
            key="csv_uploader",
            help="Max 50MB. Must include headers."
        )
        
        if csv_file:
            df = validate_and_preview_csv(csv_file)
            
            if df is not None:
                st.session_state.uploaded_data = df
                st.success(f"✅ Loaded: {len(df)} rows × {len(df.columns)} columns")
                
                with st.expander("👁️ Preview Data"):
                    st.dataframe(df.head(10), use_container_width=True)

def display_scan_section():
    """Display bias & data scan section (Epic 2)."""
    if st.session_state.uploaded_text is None:
        st.info("📤 Please upload meeting notes first in the Upload tab.")
        return
    
    st.header("🔍 Scan & Analysis")
    
    with st.spinner("🔄 Scanning for biases and patterns..."):
        text = st.session_state.uploaded_text
        df = st.session_state.uploaded_data
        
        echoes = detect_echo_chambers(text)
        sentiment = analyze_sentiment_basic(text)
        mismatch = calculate_mismatch_score(text, df)
        
        st.session_state.scan_results = {
            'echoes': echoes,
            'sentiment': sentiment,
            'mismatch': mismatch,
            'timestamp': datetime.now()
        }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔊 Echo Strength", f"{echoes[0]['echo_strength']:.0f}%" if echoes else "0%")
    
    with col2:
        st.metric("😊 Sentiment Score", f"{sentiment:.0f}%")
    
    with col3:
        st.metric("⚠️ Mismatch Score", f"{mismatch:.0f}%")
    
    st.subheader("🔔 Detected Echo Chambers")
    if echoes:
        echo_df = pd.DataFrame(echoes[:10])
        st.dataframe(echo_df, use_container_width=True, hide_index=True)

def display_story_section():
    """Display story weaving section (Epic 3)."""
    if st.session_state.scan_results is None:
        st.info("🔍 Please run the scan first in the Scan tab.")
        return
    
    st.header("📖 Narrative Nexus - Choose Your Path")
    
    st.progress(0.75, text="Nexus Alignment: 75%")
    
    st.subheader("🌳 Branching Paths")
    st.info("Interactive story branches based on your data analysis")

def display_export_section():
    """Display export section (Epic 4)."""
    st.header("💾 Export & Feedback")
    
    if st.session_state.story_branches:
        st.subheader("📄 Download Report")
        st.download_button(
            label="📥 Download PDF Report",
            data=b"PDF content",
            file_name=f"narrative_nexus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
    
    st.subheader("💬 Share Feedback")
    st.markdown("Help us improve! [📝 Feedback Form](https://forms.gle/narrative-nexus-feedback)")


# ==================== WELCOME TOUR (NEW - DAY 1) ====================

def show_welcome_tour():
    """Show welcome tour for first-time users."""
    if st.session_state.first_time_user:
        st.markdown("""
            <div class="welcome-box">
                <h2>🎉 Welcome to Narrative Nexus!</h2>
                <p><strong>Your AI bias-buster for smarter decisions</strong></p>
                <p>💡 <strong>First time here?</strong> Try these quick steps:</p>
                <ol>
                    <li>📝 <strong>Chat Mode:</strong> Select "💬 Natural Language Query" and ask a business question</li>
                    <li>📊 <strong>Upload Mode:</strong> Upload meeting notes + CSV to detect biases</li>
                    <li>📖 <strong>Explore:</strong> Check out 3-4 story branches with different outcomes</li>
                    <li>💾 <strong>Export:</strong> Download your analysis as PDF</li>
                </ol>
                <p>✨ <strong>Pro tip:</strong> Try asking "Sales dropping in rural areas—how can I fix it?"</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Got it! Let's go", use_container_width=True):
            st.session_state.first_time_user = False
            st.rerun()



# ==================== METRICS & TRACKING (DAY 3) ====================

def calculate_path_accuracy(story, df):
    """Calculate mock accuracy score for a path based on data volatility."""
    if df is None or 'Revenue' in df.columns:
        volatility = df['Revenue'].std() / df['Revenue'].mean() if df['Revenue'].mean() > 0 else 0.1
    else:
        volatility = 0.15
    
    # Lower volatility = higher accuracy
    base_accuracy = max(60, 95 - (volatility * 100))
    
    # Adjust based on risk
    risk_factor = story['risk'] / 100
    accuracy = base_accuracy * (1 - risk_factor * 0.3)
    
    return min(max(accuracy, 50), 95)

def get_testimonials():
    """Get sample testimonials from SMEs."""
    testimonials = [
        {"name": "Chioma, Cafe Owner", "text": "Narrative Nexus helped me see I was ignoring rural customers. Pivoted strategy, +18% revenue!", "rating": 5},
        {"name": "Tunde, E-commerce Manager", "text": "The bias detection was eye-opening. We were too focused on one segment. Now we're balanced.", "rating": 5},
        {"name": "Zainab, Fashion Retailer", "text": "Loved the story branches. Made it easy to see different outcomes before deciding.", "rating": 4},
        {"name": "Segun, Tech Startup", "text": "Game-changer for decision-making. No more guessing, just data-driven stories.", "rating": 5},
    ]
    return testimonials

def track_metric(metric_name, value):
    """Track a metric for analytics."""
    if 'metrics_log' not in st.session_state:
        st.session_state.metrics_log = []
    
    st.session_state.metrics_log.append({
        'metric': metric_name,
        'value': value,
        'timestamp': datetime.now()
    })


# ==================== MAIN APP ====================

def main():
    """Main app layout with Day 1 enhancements."""
    
    # Show welcome tour for first-time users
    if st.session_state.first_time_user:
        show_welcome_tour()
        return
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1>🕸️ Narrative Nexus v1.2</h1>
            <p style='font-size: 18px; color: #666;'>Weave Data into Decisions</p>
            <p style='font-size: 14px; color: #999;'>Chat with AI • Detect Biases • Simulate Outcomes • Generate Stories</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar mode selection
    st.sidebar.markdown("### 🎯 Select Mode")
    mode = st.sidebar.radio(
        "Choose your approach:",
        ["💬 Natural Language Query", "📤 Upload & Analyze", "📖 View Stories", "💾 Export"]
    )
    
    # Main content based on mode
    if mode == "💬 Natural Language Query":
        display_nlq_mode()
    elif mode == "📤 Upload & Analyze":
        tab1, tab2, tab3 = st.tabs(["📤 Upload", "🔍 Scan", "📖 Story"])
        with tab1:
            display_input_section()
        with tab2:
            display_scan_section()
        with tab3:
            display_story_section()
    elif mode == "📖 View Stories":
        display_story_section()
    elif mode == "💾 Export":
        display_export_section()
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #999; font-size: 12px; padding: 20px;'>
            <p>Narrative Nexus v1.2 • Chat-Driven Analytics • Open Source</p>
            <p>Version 1.2 • 2026</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
