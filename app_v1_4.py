import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

# ==================== v1.4 UI GLOW-UP: VISUAL & INTERACTIVE OVERHAUL ====================

# Configure Streamlit page
st.set_page_config(
    page_title="Narrative Nexus",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# v1.4: Custom CSS for stunning UI
st.markdown("""
<style>
/* v1.4 Theme Colors */
:root {
    --primary: #4F46E5;
    --accent: #10B981;
    --danger: #EF4444;
    --bg-light: #F8FAFC;
    --bg-dark: #E2E8F0;
}

/* v1.4: Global Styling */
* {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
}

/* v1.4: Hero Section */
.hero-section {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    padding: 40px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);
    animation: fadeIn 0.8s ease-in;
}

.hero-section h1 {
    font-size: 2.5em;
    margin: 0;
    font-weight: 700;
    letter-spacing: -1px;
}

.hero-section p {
    font-size: 1.1em;
    margin: 10px 0 0 0;
    opacity: 0.95;
}

/* v1.4: Mode Cards */
.mode-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
}

.mode-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(79, 70, 229, 0.15);
    border-color: #4F46E5;
}

.mode-card h3 {
    color: #4F46E5;
    margin-top: 0;
    font-size: 1.3em;
}

.mode-card p {
    color: #666;
    font-size: 0.95em;
    margin: 10px 0 0 0;
}

/* v1.4: Animations */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* v1.4: Story Branch Cards */
.branch-card {
    background: white;
    border-left: 4px solid #4F46E5;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
    animation: slideIn 0.5s ease-out;
}

.branch-card:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
    transform: translateX(4px);
}

.branch-card.positive {
    border-left-color: #10B981;
}

.branch-card.negative {
    border-left-color: #EF4444;
}

/* v1.4: Metric Badges */
.metric-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 600;
    margin: 4px;
}

.metric-badge.success {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}

.metric-badge.danger {
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
}

/* v1.4: Status Badge */
.status-badge {
    display: inline-block;
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9em;
}

/* v1.4: Responsive */
@media (max-width: 768px) {
    .hero-section h1 {
        font-size: 1.8em;
    }
    
    .mode-card {
        margin: 8px 0;
    }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'user_interactions' not in st.session_state:
    st.session_state.user_interactions = {
        'queries_run': 0,
        'files_uploaded': 0,
        'branches_clicked': 0,
        'exports_generated': 0
    }

# ==================== v1.4: DASHBOARD HOMEPAGE ====================

def render_dashboard_homepage():
    """v1.4: Render beautiful dashboard homepage"""
    
    # Hero Section
    st.markdown('''
    <div class="hero-section">
        <h1>🕸️ Narrative Nexus</h1>
        <p>Weave Your Business Story • Detect Biases • Generate Insights</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Status Badge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('''
        <div style="text-align: center;">
            <span class="status-badge">✅ Live & Stable | 99.9% Uptime</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode Selection Cards
    st.subheader("🚀 Choose Your Path")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="mode-card">
            <h3>💬 Chat & Weave</h3>
            <p>Ask your business question in plain English. Get instant story-driven insights.</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Start NLQ Mode", key="btn_nlq", use_container_width=True):
            st.session_state.mode = "nlq"
            st.rerun()
    
    with col2:
        st.markdown('''
        <div class="mode-card">
            <h3>📤 Upload & Scan</h3>
            <p>Upload meeting notes + sales data. Detect echoes, mismatches, and hidden opportunities.</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Start Hybrid Mode", key="btn_hybrid", use_container_width=True):
            st.session_state.mode = "hybrid"
            st.rerun()
    
    with col3:
        st.markdown('''
        <div class="mode-card">
            <h3>📊 Clean & Analyze</h3>
            <p>Upload CSV data. Clean, analyze, and explore insights with interactive charts.</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Start Solo Mode", key="btn_solo", use_container_width=True):
            st.session_state.mode = "solo"
            st.rerun()
    
    st.markdown("---")
    
    # Teaser Metrics
    st.subheader("📊 Quick Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Queries Run", st.session_state.user_interactions['queries_run'])
    with col2:
        st.metric("Files Uploaded", st.session_state.user_interactions['files_uploaded'])
    with col3:
        st.metric("Branches Explored", st.session_state.user_interactions['branches_clicked'])
    with col4:
        st.metric("Reports Generated", st.session_state.user_interactions['exports_generated'])
    
    st.markdown("---")
    
    # Footer
    st.markdown('''
    <div style="text-align: center; color: #666; margin-top: 40px; padding: 20px;">
        <p><strong>Built for Hustlers</strong> • Turn Data into Stories • Make Better Decisions</p>
        <p style="font-size: 0.9em;">v1.4 UI Glow-Up • Heroku Live • 99.9% Uptime</p>
    </div>
    ''', unsafe_allow_html=True)

# ==================== MAIN APP ====================

# If no mode selected, show dashboard
if st.session_state.mode is None:
    render_dashboard_homepage()
else:
    # Show mode selector in sidebar
    st.sidebar.markdown("### 🕸️ Narrative Nexus")
    
    if st.sidebar.button("← Back to Dashboard"):
        st.session_state.mode = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Mode-specific content (placeholder - will integrate existing logic)
    if st.session_state.mode == "nlq":
        st.title("💬 Natural Language Query Mode")
        st.info("NLQ mode content here - coming in full integration")
    
    elif st.session_state.mode == "hybrid":
        st.title("📤 Hybrid Mode (Upload & Scan)")
        st.info("Hybrid mode content here - coming in full integration")
    
    elif st.session_state.mode == "solo":
        st.title("📊 Solo Mode (CSV Analysis)")
        st.info("Solo mode content here - coming in full integration")
