import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

# ==================== v1.5 UI TWEAK: VIBRANT COLORS & TOP NAV BAR ====================

# Configure Streamlit page
st.set_page_config(
    page_title="Narrative Nexus",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# v1.5: Enhanced Color Palette & Top Nav Bar CSS
st.markdown("""
<style>
/* v1.5 Vibrant Color Palette */
:root {
    --primary: #4F46E5;
    --orange: #F59E0B;
    --purple: #8B5CF6;
    --green: #10B981;
    --red: #EF4444;
    --bg-light: #F0F9FF;
    --bg-warm: #FEF3C7;
}

/* v1.5: Top Navigation Bar */
.top-nav-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: linear-gradient(90deg, #2D3748 0%, #1A202C 100%);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
}

.nav-logo {
    font-size: 1.8em;
    font-weight: 700;
    color: white;
    margin-right: 40px;
}

.nav-tabs {
    display: flex;
    gap: 10px;
    flex: 1;
    justify-content: center;
}

.nav-tab {
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    color: white;
    background: rgba(255, 255, 255, 0.1);
}

.nav-tab:hover {
    transform: scale(1.05);
    background: rgba(255, 255, 255, 0.2);
}

.nav-tab.hybrid {
    border-color: #F59E0B;
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.3) 0%, rgba(245, 158, 11, 0.3) 100%);
}

.nav-tab.hybrid:hover {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.5) 0%, rgba(245, 158, 11, 0.5) 100%);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
}

.nav-tab.solo {
    border-color: #10B981;
    background: rgba(16, 185, 129, 0.2);
}

.nav-tab.solo:hover {
    background: rgba(16, 185, 129, 0.4);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
}

.nav-tab.nlq {
    border-color: #8B5CF6;
    background: rgba(139, 92, 246, 0.2);
}

.nav-tab.nlq:hover {
    background: rgba(139, 92, 246, 0.4);
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}

.nav-tab.active {
    background: linear-gradient(135deg, #F59E0B 0%, #8B5CF6 100%);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.6);
}

.nav-icons {
    display: flex;
    gap: 15px;
}

/* v1.5: Main Content Offset */
.main-content {
    margin-top: 90px;
    padding: 20px;
}

/* v1.5: Vibrant Background Gradient */
body {
    background: linear-gradient(135deg, #F0F9FF 0%, #FEF3C7 100%);
}

/* v1.5: Hero Section with Vibrant Colors */
.hero-section {
    background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 50%, #F59E0B 100%);
    padding: 40px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
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

/* v1.5: Mode Cards with Vibrant Accents */
.mode-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
    border-left: 5px solid transparent;
}

.mode-card.hybrid {
    border-left-color: #F59E0B;
}

.mode-card.solo {
    border-left-color: #10B981;
}

.mode-card.nlq {
    border-left-color: #8B5CF6;
}

.mode-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
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

/* v1.5: Vibrant Metric Badges */
.metric-badge {
    display: inline-block;
    background: linear-gradient(135deg, #F59E0B 0%, #8B5CF6 100%);
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

/* v1.5: Branch Cards with Color Accents */
.branch-card {
    background: white;
    border-left: 5px solid #4F46E5;
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
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.02) 100%);
}

.branch-card.negative {
    border-left-color: #EF4444;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%);
}

.branch-card.opportunity {
    border-left-color: #F59E0B;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(245, 158, 11, 0.02) 100%);
}

/* v1.5: Status Badge */
.status-badge {
    display: inline-block;
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9em;
}

/* v1.5: Animations */
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

@keyframes colorPulse {
    0%, 100% {
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
    }
    50% {
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
    }
}

/* v1.5: Responsive Mobile */
@media (max-width: 768px) {
    .top-nav-bar {
        height: 60px;
        padding: 0 10px;
    }
    
    .nav-logo {
        font-size: 1.4em;
        margin-right: 20px;
    }
    
    .nav-tabs {
        gap: 5px;
    }
    
    .nav-tab {
        padding: 8px 12px;
        font-size: 0.85em;
    }
    
    .main-content {
        margin-top: 80px;
        padding: 10px;
    }
    
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
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'dashboard'
if 'user_interactions' not in st.session_state:
    st.session_state.user_interactions = {
        'queries_run': 0,
        'files_uploaded': 0,
        'branches_clicked': 0,
        'exports_generated': 0
    }

# ==================== v1.5: TOP NAVIGATION BAR ====================

def render_top_nav():
    """v1.5: Render vibrant top navigation bar"""
    
    col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
    
    with col1:
        st.markdown('<div class="nav-logo">🕸️ Nexus</div>', unsafe_allow_html=True)
    
    with col2:
        # Mode tabs
        tab_col1, tab_col2, tab_col3 = st.columns(3)
        
        with tab_col1:
            if st.button("📤 Hybrid", key="nav_hybrid", use_container_width=True):
                st.session_state.current_mode = 'hybrid'
                st.rerun()
        
        with tab_col2:
            if st.button("📊 Solo", key="nav_solo", use_container_width=True):
                st.session_state.current_mode = 'solo'
                st.rerun()
        
        with tab_col3:
            if st.button("💬 NLQ", key="nav_nlq", use_container_width=True):
                st.session_state.current_mode = 'nlq'
                st.rerun()
    
    with col3:
        st.markdown('<div style="text-align: right; color: #666; font-size: 0.9em;">v1.5 Vibrant</div>', unsafe_allow_html=True)
    
    with col4:
        if st.button("🏠", key="nav_home", use_container_width=True):
            st.session_state.current_mode = 'dashboard'
            st.rerun()

# ==================== v1.5: DASHBOARD HOMEPAGE ====================

def render_dashboard_homepage():
    """v1.5: Render vibrant dashboard homepage"""
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Hero Section with Vibrant Gradient
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
    
    # Mode Selection Cards with Vibrant Colors
    st.subheader("🚀 Choose Your Path")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="mode-card hybrid">
            <h3>📤 Hybrid Mode</h3>
            <p>Upload meeting notes + sales data. Detect echoes and hidden opportunities.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="mode-card solo">
            <h3>📊 Solo Mode</h3>
            <p>Upload CSV data. Clean, analyze, and explore insights with interactive charts.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="mode-card nlq">
            <h3>💬 NLQ Mode</h3>
            <p>Ask your business question in plain English. Get instant story-driven insights.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Teaser Metrics with Vibrant Badges
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
        <p style="font-size: 0.9em;">v1.5 Vibrant Top Nav • Heroku Live • 99.9% Uptime</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN APP ====================

# Render top nav bar
render_top_nav()

# Render content based on current mode
if st.session_state.current_mode == 'dashboard':
    render_dashboard_homepage()

elif st.session_state.current_mode == 'hybrid':
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📤 Hybrid Mode (Upload & Scan)")
    st.info("🎨 v1.5: Vibrant hybrid mode with top nav - coming soon!")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_mode == 'solo':
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📊 Solo Mode (CSV Analysis)")
    st.info("🎨 v1.5: Vibrant solo mode with top nav - coming soon!")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_mode == 'nlq':
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("💬 Natural Language Query Mode")
    st.info("🎨 v1.5: Vibrant NLQ mode with top nav - coming soon!")
    st.markdown('</div>', unsafe_allow_html=True)
