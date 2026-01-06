"""
Narrative Nexus MVP - Hybrid Data-Storyteller for SME Decisions
Fuses qualitative team discussions with quantitative data to detect biases,
simulate outcomes, and generate interactive branching narratives.
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

# Configure Streamlit page
st.set_page_config(
    page_title="Narrative Nexus",
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
    </style>
""", unsafe_allow_html=True)

# ==================== UTILITY FUNCTIONS ====================

def initialize_session_state():
    """Initialize session state variables."""
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

initialize_session_state()

# ==================== EPIC 1: INPUT HANDLING ====================

def validate_and_preview_text(text_content):
    """Validate and preview text file."""
    if not text_content or len(text_content.strip()) == 0:
        st.error("⚠️ Text file is empty!")
        return None
    
    word_count = len(text_content.split())
    if word_count > 10000:
        st.warning(f"📝 Text is long ({word_count} words). Truncating to 1000 words for analysis.")
        text_content = ' '.join(text_content.split()[:1000])
    
    return text_content

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
        
        # Auto-detect numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {str(e)}")
        return None

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
                    st.write(f"**Columns**: {', '.join(df.columns.tolist())}")
                    st.write(f"**Data Types**: {dict(df.dtypes)}")

# ==================== EPIC 2: BIAS & DATA SCAN ====================

def extract_keywords(text, top_n=20):
    """Extract top keywords from text."""
    # Remove common words
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
    
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    words = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count frequencies
    word_freq = Counter(words)
    return word_freq.most_common(top_n)

def detect_echo_chambers(text):
    """Detect echo chambers (repeated ideas/keywords)."""
    keywords = extract_keywords(text, top_n=30)
    
    echoes = []
    for word, freq in keywords:
        if freq >= 3:  # Echo threshold
            echoes.append({
                'keyword': word,
                'frequency': freq,
                'echo_strength': min(100, freq * 15)  # Normalize to 0-100
            })
    
    return sorted(echoes, key=lambda x: x['frequency'], reverse=True)

def analyze_sentiment_basic(text):
    """Basic sentiment analysis without transformers."""
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
        return 50  # Neutral
    
    sentiment_score = (pos_count / total) * 100
    return sentiment_score

def analyze_sentiment_transformers(text):
    """Sentiment analysis - using basic method for compatibility."""
    return analyze_sentiment_basic(text)

def calculate_mismatch_score(text, df):
    """Calculate nexus mismatch score between text and data."""
    if df is None or df.empty:
        return 50
    
    try:
        # Extract keywords from text
        keywords = extract_keywords(text, top_n=10)
        keyword_list = [kw[0] for kw in keywords]
        
        # Check for region mentions in text
        text_lower = text.lower()
        regions_in_text = []
        
        if 'lagos' in text_lower:
            regions_in_text.append('Lagos')
        if 'abuja' in text_lower:
            regions_in_text.append('Abuja')
        if 'kano' in text_lower:
            regions_in_text.append('Kano')
        
        # Analyze data by region
        if 'Region' in df.columns and 'Revenue' in df.columns:
            region_stats = df.groupby('Region')['Revenue'].agg(['mean', 'sum', 'count'])
            top_region = region_stats['mean'].idxmax()
            
            # Check if text emphasizes the top-performing region
            if regions_in_text and top_region not in regions_in_text:
                # Text ignores top performer - high mismatch
                mismatch = 70
            elif regions_in_text and top_region in regions_in_text:
                # Text aligns with data - low mismatch
                mismatch = 20
            else:
                # Neutral
                mismatch = 50
        else:
            mismatch = 50
        
        return mismatch
    except Exception as e:
        return 50

def create_echo_graph(echoes):
    """Create a network graph visualization of echo chambers."""
    G = nx.Graph()
    
    # Add nodes for top echoes
    for echo in echoes[:5]:
        G.add_node(echo['keyword'], size=echo['frequency'] * 10)
    
    # Add edges between related echoes (simple co-occurrence)
    if len(echoes) > 1:
        for i in range(len(echoes) - 1):
            G.add_edge(echoes[i]['keyword'], echoes[i+1]['keyword'], weight=0.5)
    
    # Create Plotly visualization
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_size.append(G.nodes[node].get('size', 20))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=node_size,
            color='#667eea',
            line_width=2,
            line_color='white'
        ),
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="🕸️ Echo Chamber Network",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    return fig

def create_mismatch_gauge(mismatch_score):
    """Create a gauge chart for mismatch score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=mismatch_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Text-Data Mismatch Score"},
        delta={'reference': 50, 'suffix': " from neutral"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "#11998e"},
                {'range': [25, 50], 'color': "#f5af19"},
                {'range': [50, 75], 'color': "#f5576c"},
                {'range': [75, 100], 'color': "#d32f2f"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=70, b=20))
    return fig

def display_scan_section():
    """Display bias & data scan section (Epic 2)."""
    if st.session_state.uploaded_text is None:
        st.info("📤 Please upload meeting notes first in the section above.")
        return
    
    st.header("🔍 Scan & Analysis")
    
    # Perform scan
    with st.spinner("🔄 Scanning for biases and patterns..."):
        text = st.session_state.uploaded_text
        df = st.session_state.uploaded_data
        
        # Detect echoes
        echoes = detect_echo_chambers(text)
        
        # Sentiment analysis
        sentiment = analyze_sentiment_basic(text)
        
        # Mismatch score
        mismatch = calculate_mismatch_score(text, df)
        
        # Store results
        st.session_state.scan_results = {
            'echoes': echoes,
            'sentiment': sentiment,
            'mismatch': mismatch,
            'timestamp': datetime.now()
        }
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔊 Echo Strength", f"{echoes[0]['echo_strength']:.0f}%" if echoes else "0%", 
                  help="How strongly repeated ideas dominate the discussion")
    
    with col2:
        st.metric("😊 Sentiment Score", f"{sentiment:.0f}%", 
                  help="Overall positivity/negativity of discussion")
    
    with col3:
        st.metric("⚠️ Mismatch Score", f"{mismatch:.0f}%", 
                  help="How much text contradicts data trends")
    
    # Display visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        if echoes:
            fig = create_echo_graph(echoes)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No significant echoes detected.")
    
    with col2:
        fig = create_mismatch_gauge(mismatch)
        st.plotly_chart(fig, use_container_width=True)
    
    # Display echo details
    st.subheader("🔔 Detected Echo Chambers")
    if echoes:
        echo_df = pd.DataFrame(echoes[:10])
        st.dataframe(echo_df, use_container_width=True, hide_index=True)
        
        # Interpretation
        if echoes[0]['frequency'] >= 5:
            st.warning(f"⚠️ **Strong Echo Detected**: '{echoes[0]['keyword']}' repeated {echoes[0]['frequency']} times. This may indicate groupthink.")
    else:
        st.success("✅ No significant echo chambers detected. Discussion is balanced.")
    
    # Data insights
    if df is not None and not df.empty:
        st.subheader("📊 Data Insights")
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Numeric Summary**")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            
            with col2:
                # Regional analysis if available
                if 'Region' in df.columns and 'Revenue' in df.columns:
                    region_stats = df.groupby('Region')['Revenue'].agg(['mean', 'sum', 'count']).round(2)
                    st.write("**Revenue by Region**")
                    st.dataframe(region_stats, use_container_width=True)

# ==================== EPIC 3: STORY WEAVING & SIMULATIONS ====================

def run_monte_carlo_simulation(df, bias_flip=False, n_runs=100):
    """Run Monte Carlo simulation for what-if scenarios."""
    if df is None or df.empty or 'Revenue' not in df.columns:
        return None
    
    try:
        revenue_data = df['Revenue'].values
        base_mean = revenue_data.mean()
        base_std = revenue_data.std()
        
        # Simulate with and without bias
        if bias_flip:
            # Simulate positive outcome from removing bias
            sim_mean = base_mean * 1.15  # +15% improvement
            sim_std = base_std * 0.9  # Reduced variance
        else:
            sim_mean = base_mean
            sim_std = base_std
        
        simulations = np.random.normal(sim_mean, sim_std, n_runs)
        simulations = np.maximum(simulations, 0)  # No negative revenue
        
        return {
            'simulations': simulations,
            'mean': simulations.mean(),
            'std': simulations.std(),
            'min': simulations.min(),
            'max': simulations.max(),
            'percentile_25': np.percentile(simulations, 25),
            'percentile_75': np.percentile(simulations, 75)
        }
    except Exception as e:
        st.warning(f"Simulation error: {str(e)}")
        return None

def generate_branch_narrative(branch_num, text, df, echoes, sim_results):
    """Generate a narrative branch with story and metrics."""
    
    # Extract key echo for narrative
    top_echo = echoes[0]['keyword'] if echoes else "market bias"
    
    # Branch templates
    branches = [
        {
            'title': f"Path 1: The Echo Trap",
            'description': f"Your team's obsession with '{top_echo}' blinds you to emerging opportunities. Sticking to this bias leads to stagnation.",
            'outcome': "Revenue plateaus. Market share erodes.",
            'metrics': {'growth': -5, 'risk': 75}
        },
        {
            'title': f"Path 2: The Bold Pivot",
            'description': f"Challenge the '{top_echo}' narrative. Diversify into overlooked markets. Your data whispers of untapped potential.",
            'outcome': "Revenue surges +15%. New customer segments unlock.",
            'metrics': {'growth': 15, 'risk': 35}
        },
        {
            'title': f"Path 3: The Hybrid Strategy",
            'description': f"Keep '{top_echo}' as your anchor, but allocate 30% resources to test alternatives. Balanced risk, steady growth.",
            'outcome': "Revenue grows +8%. Reduces single-market dependency.",
            'metrics': {'growth': 8, 'risk': 45}
        },
        {
            'title': f"Path 4: The Data-Driven Pivot",
            'description': f"Ignore '{top_echo}' sentiment. Follow the data. Your metrics show clear winners in overlooked regions.",
            'outcome': "Revenue grows +20%. Establishes market leadership.",
            'metrics': {'growth': 20, 'risk': 50}
        },
        {
            'title': f"Path 5: The Gradual Shift",
            'description': f"Slowly reduce '{top_echo}' focus. Build parallel operations in high-potential regions. Minimize disruption.",
            'outcome': "Revenue grows +10%. Smooth transition, low churn.",
            'metrics': {'growth': 10, 'risk': 30}
        },
        {
            'title': f"Path 6: The Contrarian Play",
            'description': f"Your team's '{top_echo}' is a competitive advantage—but only if you exploit it strategically. Double down selectively.",
            'outcome': "Revenue grows +12%. Dominates current market.",
            'metrics': {'growth': 12, 'risk': 40}
        }
    ]
    
    if branch_num < len(branches):
        branch = branches[branch_num].copy()
    else:
        branch = branches[-1].copy()
    
    # Add simulation data
    if sim_results:
        branch['sim_mean'] = sim_results['mean']
        branch['sim_range'] = (sim_results['percentile_25'], sim_results['percentile_75'])
    
    return branch

def create_branch_chart(branch_num, sim_results):
    """Create a visualization for a branch outcome."""
    if not sim_results:
        return None
    
    simulations = sim_results['simulations']
    
    fig = go.Figure()
    
    # Add histogram
    fig.add_trace(go.Histogram(
        x=simulations,
        nbinsx=30,
        name='Simulated Revenue',
        marker_color='#667eea',
        opacity=0.7
    ))
    
    # Add mean line
    fig.add_vline(
        x=sim_results['mean'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${sim_results['mean']:.0f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title=f"Revenue Distribution - Path {branch_num + 1}",
        xaxis_title="Revenue ($)",
        yaxis_title="Frequency",
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def calculate_nexus_score(text, df, echoes):
    """Calculate overall nexus score (0-100%)."""
    if not echoes:
        return 85  # Good score if no echoes
    
    # Score based on echo strength
    max_echo_freq = echoes[0]['frequency'] if echoes else 0
    echo_penalty = min(50, max_echo_freq * 5)
    
    # Score based on data alignment
    mismatch = calculate_mismatch_score(text, df)
    alignment_penalty = mismatch * 0.3
    
    nexus_score = 100 - echo_penalty - alignment_penalty
    return max(0, min(100, nexus_score))

def display_story_section():
    """Display story weaving & simulations section (Epic 3)."""
    if st.session_state.scan_results is None:
        st.info("🔍 Please run the scan first in the section above.")
        return
    
    st.header("📖 Narrative Nexus - Choose Your Path")
    
    # Calculate nexus score
    nexus_score = calculate_nexus_score(
        st.session_state.uploaded_text,
        st.session_state.uploaded_data,
        st.session_state.scan_results['echoes']
    )
    
    # Display progress bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(nexus_score / 100, text=f"Nexus Alignment: {nexus_score:.0f}%")
    
    with col2:
        if nexus_score >= 80:
            st.success("✅ Strong Sync")
        elif nexus_score >= 60:
            st.warning("⚠️ Moderate Sync")
        else:
            st.error("❌ Low Sync")
    
    # Generate branches
    st.subheader("🌳 Branching Paths")
    
    # Run simulations
    sim_results = run_monte_carlo_simulation(st.session_state.uploaded_data, bias_flip=True)
    
    # Create tabs for each branch
    tabs = st.tabs([f"Path {i+1}" for i in range(6)])
    
    for i, tab in enumerate(tabs):
        with tab:
            branch = generate_branch_narrative(
                i,
                st.session_state.uploaded_text,
                st.session_state.uploaded_data,
                st.session_state.scan_results['echoes'],
                sim_results
            )
            
            # Display branch content
            st.subheader(branch['title'])
            st.write(branch['description'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📈 Growth Potential", f"{branch['metrics']['growth']:+d}%")
                st.metric("⚠️ Risk Level", f"{branch['metrics']['risk']}%")
            
            with col2:
                st.write("**Outcome**")
                st.info(branch['outcome'])
            
            # Display simulation chart
            if sim_results:
                fig = create_branch_chart(i, sim_results)
                st.plotly_chart(fig, use_container_width=True)
    
    # Store story branches for export
    st.session_state.story_branches = [
        generate_branch_narrative(
            i,
            st.session_state.uploaded_text,
            st.session_state.uploaded_data,
            st.session_state.scan_results['echoes'],
            sim_results
        )
        for i in range(6)
    ]
    st.session_state.simulations = sim_results

# ==================== EPIC 4: POLISH & USABILITY ====================

def generate_pdf_report(text, df, scan_results, story_branches, nexus_score):
    """Generate PDF report with narrative and visualizations."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("🕸️ Narrative Nexus Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_text = f"""
    This report analyzes your team's meeting notes against quantitative data to identify decision biases,
    detect echo chambers, and simulate alternative strategic paths. Your Nexus Alignment Score is <b>{nexus_score:.0f}%</b>,
    indicating how well your qualitative discussions align with data-driven insights.
    """
    story.append(Paragraph(summary_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Scan Results
    story.append(Paragraph("Scan Results", heading_style))
    
    scan_table_data = [
        ['Metric', 'Value', 'Interpretation'],
        ['Echo Strength', f"{scan_results['echoes'][0]['echo_strength']:.0f}%" if scan_results['echoes'] else "0%", 
         'Strength of repeated ideas in discussion'],
        ['Sentiment Score', f"{scan_results['sentiment']:.0f}%", 'Overall positivity of discussion'],
        ['Text-Data Mismatch', f"{scan_results['mismatch']:.0f}%", 'Alignment between discussion and data']
    ]
    
    scan_table = Table(scan_table_data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
    scan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(scan_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Top Echoes
    if scan_results['echoes']:
        story.append(Paragraph("Detected Echo Chambers", heading_style))
        echo_text = "The following ideas were repeated frequently in your discussion:<br/>"
        for i, echo in enumerate(scan_results['echoes'][:5], 1):
            echo_text += f"<br/>{i}. <b>'{echo['keyword']}'</b> (mentioned {echo['frequency']} times)"
        story.append(Paragraph(echo_text, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
    
    # Strategic Paths
    story.append(Paragraph("Strategic Paths", heading_style))
    story.append(Paragraph(
        "Based on your analysis, here are 6 strategic paths to consider:",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    for i, branch in enumerate(story_branches[:3], 1):  # Include top 3 paths in PDF
        story.append(Paragraph(f"<b>Path {i}: {branch['title']}</b>", styles['Heading3']))
        story.append(Paragraph(branch['description'], styles['BodyText']))
        story.append(Paragraph(f"<i>Outcome: {branch['outcome']}</i>", styles['Italic']))
        story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "For detailed analysis and interactive exploration of all 6 paths, use the Narrative Nexus web app.",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def display_export_section():
    """Display export and feedback section (Epic 4)."""
    st.header("💾 Export & Feedback")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.story_branches and st.session_state.scan_results:
            st.subheader("📄 Download Report")
            
            nexus_score = calculate_nexus_score(
                st.session_state.uploaded_text,
                st.session_state.uploaded_data,
                st.session_state.scan_results['echoes']
            )
            
            pdf_buffer = generate_pdf_report(
                st.session_state.uploaded_text,
                st.session_state.uploaded_data,
                st.session_state.scan_results,
                st.session_state.story_branches,
                nexus_score
            )
            
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name=f"narrative_nexus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                help="Download your complete analysis and strategic paths as PDF"
            )
        else:
            st.info("⚠️ Complete the analysis above to enable PDF export.")
    
    with col2:
        st.subheader("💬 Share Feedback")
        st.markdown("""
        Help us improve Narrative Nexus! Share your feedback:
        
        [📝 Feedback Form](https://forms.gle/narrative-nexus-feedback)
        
        Tell us:
        - What worked well?
        - What could be improved?
        - Feature requests?
        """)

# ==================== MAIN APP ====================

def main():
    """Main app layout."""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1>🕸️ Narrative Nexus</h1>
            <p style='font-size: 18px; color: #666;'>Weave Data into Decisions</p>
            <p style='font-size: 14px; color: #999;'>Detect biases • Simulate outcomes • Generate interactive stories</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "🔍 Scan", "📖 Story", "💾 Export"])
    
    with tab1:
        display_input_section()
    
    with tab2:
        display_scan_section()
    
    with tab3:
        display_story_section()
    
    with tab4:
        display_export_section()
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #999; font-size: 12px; padding: 20px;'>
            <p>Narrative Nexus MVP • Built for SME Decision-Making • Open Source</p>
            <p>Version 1.0 • 2025</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
