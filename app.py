"""
Narrative Nexus v2.0 - AI-Powered Business Advisor
Features:
- GPT-powered intelligent analysis
- Plain language reports (no jargon)
- Voice input for hands-free queries
- Echo chamber detection
- Strategic story generation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from datetime import datetime
import json
import re
import os

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="Narrative Nexus v2.0",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== VIBRANT STYLING ====================

st.markdown("""
<style>
/* Base Styling */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, #f0f9ff 0%, #fef3c7 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main {
    background: transparent;
    padding: 20px;
}

/* Vibrant Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab-list"] button {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border: 2px solid #4F46E5;
    color: #4F46E5;
    font-weight: 600;
    border-radius: 10px;
    padding: 12px 24px;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #F59E0B 0%, #8B5CF6 100%);
    color: white;
    border-color: #F59E0B;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

/* Headers */
h1, h2, h3 {
    color: #4F46E5;
    font-weight: 700;
}

h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* File Uploader */
.stFileUploader {
    border: 2px dashed #4F46E5;
    border-radius: 12px;
    padding: 20px;
    background: rgba(79, 70, 229, 0.05);
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: #F59E0B;
    background: rgba(245, 158, 11, 0.05);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
}

/* Text Input */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 2px solid #4F46E5;
    border-radius: 10px;
    padding: 12px;
    font-size: 1em;
}

/* Metrics */
.stMetric {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
    border-left: 5px solid #4F46E5;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Plain Language Report Box */
.plain-report {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border-left: 5px solid #10B981;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    font-size: 1.1em;
    line-height: 1.8;
}

.plain-report h3 {
    color: #059669;
    margin-bottom: 15px;
}

/* AI Badge */
.ai-badge {
    background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}

/* Voice Button */
.voice-btn {
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    color: white;
    padding: 15px 25px;
    border-radius: 50px;
    font-size: 1.1em;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

.voice-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

/* Divider */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, #4F46E5 0%, #F59E0B 50%, #8B5CF6 100%);
    margin: 30px 0;
}

/* Responsive */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8em;
    }
}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================

if 'mode' not in st.session_state:
    st.session_state.mode = 'dashboard'
if 'interactions' not in st.session_state:
    st.session_state.interactions = {'queries': 0, 'uploads': 0, 'ai_calls': 0}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ==================== GPT AI FUNCTIONS ====================

def get_openai_client():
    """Get OpenAI client if available"""
    if OPENAI_AVAILABLE:
        try:
            return OpenAI()
        except:
            return None
    return None

def ai_analyze_query(query, context=None):
    """Use GPT to analyze business query and generate insights"""
    client = get_openai_client()
    
    if client:
        try:
            system_prompt = """You are a friendly business advisor for small and medium businesses. 
            Your job is to:
            1. Understand the business owner's question
            2. Provide clear, actionable advice in plain English
            3. Avoid jargon - explain like you're talking to a friend
            4. Be encouraging but honest
            5. Give specific, practical recommendations
            
            Format your response with:
            - A brief summary of what you understood
            - 3-4 key insights (use emojis to make it friendly)
            - A clear recommendation
            - One thing they should do TODAY"""
            
            user_message = f"Business Question: {query}"
            if context:
                user_message += f"\n\nAdditional Context: {context}"
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            st.session_state.interactions['ai_calls'] += 1
            return response.choices[0].message.content, True
        except Exception as e:
            return None, False
    
    return None, False

def ai_analyze_documents(text_content, df_summary, echo_info, mismatch_score):
    """Use GPT to analyze documents and generate plain language report"""
    client = get_openai_client()
    
    if client:
        try:
            system_prompt = """You are a friendly business advisor analyzing meeting notes and sales data.
            Your job is to:
            1. Explain what you found in PLAIN ENGLISH - no technical jargon
            2. Point out any biases or blind spots you noticed
            3. Highlight opportunities they might be missing
            4. Give specific, actionable advice
            
            Write like you're having a coffee chat with the business owner.
            Use everyday language. Be warm but direct.
            Use emojis sparingly to make key points stand out."""
            
            user_message = f"""I analyzed a business's meeting notes and sales data. Here's what I found:

MEETING NOTES SUMMARY:
{text_content[:1500]}

DATA SUMMARY:
{df_summary}

BIAS DETECTION:
- Echo Chamber Detected: {echo_info['detected']}
- Most Repeated Word: {echo_info['top_word']} (mentioned {echo_info['count']} times)
- Text-Data Mismatch Score: {mismatch_score}%

Please write a friendly, plain-language report explaining:
1. What the team seems to be focused on
2. What the data actually shows
3. What opportunity they might be missing
4. What they should do about it"""

            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            st.session_state.interactions['ai_calls'] += 1
            return response.choices[0].message.content, True
        except Exception as e:
            return None, False
    
    return None, False

def ai_generate_stories(context, intent):
    """Use GPT to generate personalized strategic paths"""
    client = get_openai_client()
    
    if client:
        try:
            system_prompt = """You are a strategic business advisor. Generate 3 different strategic paths 
            for the business owner to consider. Each path should be:
            1. Named with an emoji and clear title
            2. Described in 2-3 sentences of plain English
            3. Include a realistic outcome (with numbers if possible)
            4. Rate the risk level (Low/Medium/High)
            5. Give one specific action to take
            
            Make each path genuinely different - conservative, balanced, and bold options.
            Write like you're advising a friend, not writing a business report."""
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Business situation: {context}\nIntent: {intent}"}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            return response.choices[0].message.content, True
        except:
            return None, False
    
    return None, False

# ==================== HELPER FUNCTIONS ====================

def validate_text(text, max_words=2000):
    """Validate text input"""
    if not text or len(text.strip()) < 10:
        return None
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words])
    return text

def validate_csv(file, max_rows=1000):
    """Validate CSV file"""
    try:
        df = pd.read_csv(file)
        if df.empty or len(df.columns) < 2:
            return None
        return df.head(max_rows)
    except:
        return None

def detect_echo_chamber(text):
    """Detect echo chamber patterns in text"""
    if not text:
        return {'detected': False, 'top_word': None, 'count': 0, 'top_words': []}
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 'their', 
                  'what', 'when', 'where', 'which', 'would', 'could', 'should', 'about',
                  'into', 'more', 'some', 'than', 'them', 'then', 'there', 'these', 'will',
                  'going', 'need', 'want', 'make', 'just', 'also', 'like', 'think'}
    words = [w for w in words if w not in stop_words]
    
    word_freq = Counter(words)
    top_words = word_freq.most_common(10)
    
    if top_words:
        top_word, top_count = top_words[0]
        total_words = len(words)
        frequency_ratio = top_count / total_words if total_words > 0 else 0
        
        if top_count >= 8 or frequency_ratio > 0.04:
            return {
                'detected': True,
                'top_word': top_word,
                'count': top_count,
                'top_words': top_words[:5]
            }
    
    return {'detected': False, 'top_word': None, 'count': 0, 'top_words': top_words[:5]}

def calculate_mismatch(text, df):
    """Calculate text-data mismatch score"""
    if df is None or text is None:
        return 50
    
    text_lower = text.lower()
    mentioned = 0
    ignored = 0
    
    for col in df.columns:
        if df[col].dtype == 'object':
            for val in df[col].unique():
                val_str = str(val).lower()
                if len(val_str) > 3:
                    if val_str in text_lower:
                        mentioned += 1
                    else:
                        ignored += 1
    
    total = mentioned + ignored
    if total == 0:
        return 50
    
    return min(100, max(0, (ignored / total) * 100))

def get_df_summary(df):
    """Get a text summary of the dataframe"""
    if df is None:
        return "No data available"
    
    summary = f"Data has {len(df)} rows and {len(df.columns)} columns.\n"
    summary += f"Columns: {', '.join(df.columns.tolist())}\n"
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        for col in numeric_cols[:3]:
            summary += f"{col}: min={df[col].min():.0f}, max={df[col].max():.0f}, avg={df[col].mean():.0f}\n"
    
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        for col in cat_cols[:2]:
            unique_vals = df[col].unique()[:5]
            summary += f"{col} values: {', '.join(map(str, unique_vals))}\n"
    
    return summary

def generate_plain_report_fallback(echo_info, mismatch_score, df):
    """Generate plain language report without AI"""
    report = ""
    
    if echo_info['detected']:
        report += f"""
### 🔍 What I Found

**Your team seems really focused on "{echo_info['top_word']}"** - it came up {echo_info['count']} times in your meeting notes! 

When everyone keeps saying the same thing over and over, it might mean you're all on the same page... or it might mean you're missing something important.

"""
    
    if mismatch_score > 50:
        report += f"""
### ⚠️ Here's Something Interesting

**There's a {mismatch_score:.0f}% gap between what your team is talking about and what your data shows.**

In plain English: Your discussions might not be matching up with reality. Some parts of your business that are doing well might be getting ignored.

"""
    
    report += """
### 💡 My Advice

1. **Look at the numbers** - Sometimes the data tells a different story than our gut feeling
2. **Ask "what are we NOT talking about?"** - The things we ignore can be opportunities
3. **Get a second opinion** - Show this data to someone outside your team

### ✅ Do This Today

Pick ONE thing from your data that surprised you and discuss it with your team for 10 minutes.
"""
    
    return report

def generate_stories_fallback(context, intent):
    """Generate strategic paths without AI"""
    stories = [
        {
            'title': '🐢 The Safe Path',
            'description': 'Keep doing what works, but make small improvements. Low risk, steady progress.',
            'outcome': 'Expect 5-10% improvement over 6 months',
            'risk': 'Low',
            'action': 'Pick your best-performing area and invest 10% more there'
        },
        {
            'title': '⚖️ The Balanced Path',
            'description': 'Make moderate changes based on what the data shows. Some risk, good potential.',
            'outcome': 'Expect 15-20% improvement if it works',
            'risk': 'Medium',
            'action': 'Test a new approach with 20% of your resources for 30 days'
        },
        {
            'title': '🚀 The Bold Path',
            'description': 'Make significant changes to capture the opportunity. Higher risk, higher reward.',
            'outcome': 'Could see 30%+ improvement, but also possible setbacks',
            'risk': 'High',
            'action': 'Commit to a major shift and give it 90 days to prove itself'
        }
    ]
    return stories

# ==================== VOICE INPUT ====================

def add_voice_input():
    """Add voice input capability using browser's speech recognition"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center;">
        <h4 style="color: #92400e; margin-bottom: 10px;">🎤 Voice Input</h4>
        <p style="color: #78350f; margin-bottom: 15px;">Click the microphone and speak your question!</p>
        <p style="color: #92400e; font-size: 0.9em;">
            <strong>Try saying:</strong> "Why are my sales dropping in rural areas?"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript for voice recognition
    voice_js = """
    <script>
    function startVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                // Send to Streamlit
                const textArea = document.querySelector('textarea');
                if (textArea) {
                    textArea.value = transcript;
                    textArea.dispatchEvent(new Event('input', { bubbles: true }));
                }
                document.getElementById('voice-status').innerHTML = '✅ Got it: "' + transcript + '"';
            };
            
            recognition.onerror = function(event) {
                document.getElementById('voice-status').innerHTML = '❌ Error: ' + event.error;
            };
            
            recognition.onstart = function() {
                document.getElementById('voice-status').innerHTML = '🎤 Listening...';
            };
            
            recognition.start();
        } else {
            document.getElementById('voice-status').innerHTML = '❌ Voice input not supported in this browser. Try Chrome!';
        }
    }
    </script>
    <div style="text-align: center; margin: 10px 0;">
        <button onclick="startVoiceRecognition()" style="
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        ">
            🎤 Click to Speak
        </button>
        <p id="voice-status" style="margin-top: 15px; color: #666;"></p>
    </div>
    """
    st.components.v1.html(voice_js, height=150)

# ==================== DASHBOARD ====================

def show_dashboard():
    """Show main dashboard"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🕸️ Narrative Nexus")
        st.markdown('<span class="ai-badge">✨ AI-Powered v2.0</span>', unsafe_allow_html=True)
        st.markdown("**Your AI Business Advisor** • Detect Biases • Get Clear Advice")
    with col2:
        st.markdown("### 🟢 Live")
        st.caption("GPT-Enhanced")
    
    st.markdown("---")
    
    # What's new banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h4 style="color: #5b21b6; margin-bottom: 10px;">🆕 What's New in v2.0</h4>
        <ul style="color: #6d28d9; margin: 0; padding-left: 20px;">
            <li><strong>🧠 GPT-Powered Analysis</strong> - Real AI that understands your questions</li>
            <li><strong>📝 Plain Language Reports</strong> - No jargon, just clear advice</li>
            <li><strong>🎤 Voice Input</strong> - Just speak your question!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions Asked", st.session_state.interactions['queries'])
    with col2:
        st.metric("Files Analyzed", st.session_state.interactions['uploads'])
    with col3:
        st.metric("AI Insights", st.session_state.interactions['ai_calls'])
    with col4:
        st.metric("Status", "✅ Active")
    
    st.markdown("---")
    
    st.subheader("📊 Choose Your Analysis Mode")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%); 
                    padding: 25px; border-radius: 15px; color: white; text-align: center; min-height: 200px;">
            <h3>💬 Ask AI</h3>
            <p style="margin: 15px 0;">Ask any business question in plain English (or speak it!)</p>
            <p><strong>🎤 Voice enabled!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                    padding: 25px; border-radius: 15px; color: white; text-align: center; min-height: 200px;">
            <h3>📤 Deep Analysis</h3>
            <p style="margin: 15px 0;">Upload meeting notes + data for bias detection</p>
            <p><strong>🧠 AI-powered insights!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    padding: 25px; border-radius: 15px; color: white; text-align: center; min-height: 200px;">
            <h3>📊 Data Explorer</h3>
            <p style="margin: 15px 0;">Upload CSV data for interactive analysis</p>
            <p><strong>📈 Visual insights!</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ==================== ASK AI MODE ====================

def show_nlq_mode():
    """AI-Powered Natural Language Query Mode"""
    st.title("💬 Ask Your AI Advisor")
    st.markdown('<span class="ai-badge">🧠 GPT-Powered</span>', unsafe_allow_html=True)
    st.markdown("Ask any business question and get clear, actionable advice.")
    
    st.markdown("---")
    
    # Voice input section
    add_voice_input()
    
    st.markdown("---")
    
    # Example queries
    with st.expander("💡 Example Questions (click to expand)"):
        st.markdown("""
        - "Sales are dropping in rural areas - what should I do?"
        - "My team keeps talking about premium customers but budget is growing faster - what's going on?"
        - "How can I grow my business next quarter?"
        - "Are we missing any opportunities?"
        - "What should I focus on this month?"
        """)
    
    query = st.text_area(
        "What's on your mind?", 
        height=120, 
        placeholder="Type your question here, or use the voice button above to speak it..."
    )
    
    if st.button("🔍 Get AI Advice", use_container_width=True):
        if query and len(query) > 10:
            st.session_state.interactions['queries'] += 1
            
            with st.spinner("🧠 Your AI advisor is thinking..."):
                # Try AI analysis first
                ai_response, ai_success = ai_analyze_query(query)
                
                if ai_success and ai_response:
                    st.success("✅ Here's what I found!")
                    
                    # Display AI response in a nice box
                    st.markdown(f"""
                    <div class="plain-report">
                        <h3>🤖 AI Advisor Says:</h3>
                        {ai_response.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    # Fallback to basic analysis
                    st.info("💡 Here's my analysis based on your question:")
                    
                    # Basic intent detection
                    query_lower = query.lower()
                    if any(word in query_lower for word in ['drop', 'decline', 'down', 'fall', 'problem']):
                        st.markdown("""
                        ### 📉 Sounds Like a Sales Challenge
                        
                        Based on your question, here's my advice:
                        
                        **1. Don't panic** - Most sales dips are temporary and fixable
                        
                        **2. Look at the data** - Which specific area is dropping? When did it start?
                        
                        **3. Talk to customers** - Sometimes they'll tell you exactly what's wrong
                        
                        **4. Check your competition** - Are they doing something new?
                        
                        ### ✅ Do This Today
                        Pull up your sales data from the last 3 months and find the EXACT week things changed.
                        """)
                    else:
                        st.markdown("""
                        ### 💡 Here's My Take
                        
                        Great question! Here are some thoughts:
                        
                        **1. Start with data** - What do your numbers actually say?
                        
                        **2. Talk to your team** - They often see things you don't
                        
                        **3. Test small** - Try new ideas with 10% of your resources first
                        
                        ### ✅ Do This Today
                        Write down the ONE metric that matters most to your business right now.
                        """)
                
                # Generate strategic paths
                st.markdown("---")
                st.subheader("🎯 Your Options")
                
                ai_stories, stories_success = ai_generate_stories(query, "general")
                
                if stories_success and ai_stories:
                    st.markdown(ai_stories)
                else:
                    stories = generate_stories_fallback(query, "general")
                    for story in stories:
                        with st.expander(f"{story['title']}"):
                            st.write(f"**What it means:** {story['description']}")
                            st.write(f"**Expected outcome:** {story['outcome']}")
                            st.write(f"**Risk level:** {story['risk']}")
                            st.write(f"**👉 Action:** {story['action']}")
        else:
            st.warning("⚠️ Please ask a more specific question (at least 10 characters)")

# ==================== HYBRID MODE ====================

def show_hybrid_mode():
    """Deep Analysis Mode - Text + CSV"""
    st.title("📤 Deep Analysis")
    st.markdown('<span class="ai-badge">🧠 AI-Powered Bias Detection</span>', unsafe_allow_html=True)
    st.markdown("Upload your meeting notes and data to uncover hidden biases and opportunities.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    text_content = None
    df = None
    
    with col1:
        st.subheader("📝 Meeting Notes / Discussions")
        st.caption("Upload notes from meetings, emails, or team discussions")
        text_file = st.file_uploader("Upload TXT file", type=['txt'], key='txt_hybrid')
        
        if text_file:
            text_content = text_file.read().decode('utf-8')
            text_content = validate_text(text_content)
            if text_content:
                st.success(f"✅ Loaded {len(text_content):,} characters")
                with st.expander("Preview"):
                    st.text(text_content[:500] + "..." if len(text_content) > 500 else text_content)
    
    with col2:
        st.subheader("📊 Business Data")
        st.caption("Upload sales, revenue, or performance data")
        csv_file = st.file_uploader("Upload CSV file", type=['csv'], key='csv_hybrid')
        
        if csv_file:
            df = validate_csv(csv_file)
            if df is not None:
                st.success(f"✅ Loaded {len(df):,} rows")
                with st.expander("Preview"):
                    st.dataframe(df.head(5), use_container_width=True)
    
    st.markdown("---")
    
    if st.button("🔍 Analyze for Biases", use_container_width=True):
        if text_content and df is not None:
            st.session_state.interactions['uploads'] += 1
            
            with st.spinner("🧠 AI is analyzing your documents..."):
                # Detect echo chamber
                echo_info = detect_echo_chamber(text_content)
                
                # Calculate mismatch
                mismatch = calculate_mismatch(text_content, df)
                
                # Get data summary
                df_summary = get_df_summary(df)
                
                st.success("✅ Analysis Complete!")
                
                # Key metrics
                st.subheader("📊 Quick Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    echo_status = "🔴 Yes - Potential groupthink!" if echo_info['detected'] else "🟢 No echo chamber"
                    st.metric("Echo Chamber", echo_status)
                
                with col2:
                    if echo_info['top_word']:
                        st.metric("Most Repeated", f'"{echo_info["top_word"]}" ({echo_info["count"]}x)')
                    else:
                        st.metric("Most Repeated", "N/A")
                
                with col3:
                    mismatch_label = "🔴 High" if mismatch > 60 else "🟡 Medium" if mismatch > 40 else "🟢 Low"
                    st.metric("Talk vs Data Gap", f"{mismatch_label} ({mismatch:.0f}%)")
                
                st.markdown("---")
                
                # Plain Language Report
                st.subheader("📝 Your Report (Plain English)")
                
                ai_report, ai_success = ai_analyze_documents(
                    text_content[:2000], 
                    df_summary, 
                    echo_info, 
                    mismatch
                )
                
                if ai_success and ai_report:
                    st.markdown(f"""
                    <div class="plain-report">
                        {ai_report.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Fallback report
                    report = generate_plain_report_fallback(echo_info, mismatch, df)
                    st.markdown(f"""
                    <div class="plain-report">
                        {report}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Data visualization
                st.subheader("📈 Your Data at a Glance")
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    col = st.selectbox("Select metric to visualize", numeric_cols)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(x=df[col], nbinsx=30, marker_color='#4F46E5'))
                    fig.update_layout(
                        title=f"Distribution of {col}",
                        xaxis_title=col,
                        yaxis_title="Frequency",
                        template="plotly_white",
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Strategic paths
                st.subheader("🎯 What You Can Do")
                
                stories = generate_stories_fallback(text_content, "bias_check")
                for story in stories:
                    with st.expander(f"{story['title']}"):
                        st.write(f"**What it means:** {story['description']}")
                        st.write(f"**Expected outcome:** {story['outcome']}")
                        st.write(f"**Risk level:** {story['risk']}")
                        st.write(f"**👉 Action:** {story['action']}")
        else:
            st.warning("⚠️ Please upload both a TXT file and a CSV file")

# ==================== SOLO MODE ====================

def show_solo_mode():
    """Data Explorer Mode - CSV Only"""
    st.title("📊 Data Explorer")
    st.markdown("Upload your data and explore it with interactive visualizations.")
    
    st.markdown("---")
    
    csv_file = st.file_uploader("Upload CSV file", type=['csv'], key='csv_solo')
    
    if csv_file:
        df = validate_csv(csv_file)
        
        if df is not None:
            st.session_state.interactions['uploads'] += 1
            st.success(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
            
            st.markdown("---")
            
            # Quick stats
            st.subheader("📈 Quick Stats")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                missing = df.isnull().sum().sum()
                st.metric("Missing Values", f"{missing:,}")
            with col4:
                st.metric("Memory", f"{df.memory_usage().sum() / 1024:.1f} KB")
            
            st.markdown("---")
            
            # Data preview
            st.subheader("👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Numeric analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                st.markdown("---")
                st.subheader("📊 Numeric Analysis")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                st.markdown("---")
                st.subheader("📈 Visualize Your Data")
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_col = st.selectbox("Select column", numeric_cols)
                with col2:
                    chart_type = st.selectbox("Chart type", ["Histogram", "Box Plot", "Line Chart"])
                
                fig = go.Figure()
                
                if chart_type == "Histogram":
                    fig.add_trace(go.Histogram(x=df[selected_col], nbinsx=30, marker_color='#4F46E5'))
                elif chart_type == "Box Plot":
                    fig.add_trace(go.Box(y=df[selected_col], marker_color='#4F46E5', name=selected_col))
                else:
                    fig.add_trace(go.Scatter(y=df[selected_col], mode='lines', line=dict(color='#4F46E5')))
                
                fig.update_layout(
                    title=f"{chart_type} of {selected_col}",
                    template="plotly_white",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlation
                if len(numeric_cols) > 1:
                    st.markdown("---")
                    st.subheader("🔗 How Your Metrics Relate")
                    corr = df[numeric_cols].corr()
                    
                    fig = px.imshow(
                        corr,
                        text_auto='.2f',
                        color_continuous_scale='RdBu_r',
                        aspect='auto'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Categorical analysis
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            if cat_cols:
                st.markdown("---")
                st.subheader("📋 Category Breakdown")
                
                selected_cat = st.selectbox("Select category", cat_cols)
                value_counts = df[selected_cat].value_counts().head(10)
                
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    color=value_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    title=f"Top values in {selected_cat}",
                    xaxis_title=selected_cat,
                    yaxis_title="Count",
                    template="plotly_white",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Upload a CSV file to explore your data")

# ==================== MAIN APP ====================

# Navigation
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.mode = 'dashboard'
        st.rerun()

with col2:
    if st.button("💬 Ask AI", use_container_width=True):
        st.session_state.mode = 'nlq'
        st.rerun()

with col3:
    if st.button("📤 Deep Analysis", use_container_width=True):
        st.session_state.mode = 'hybrid'
        st.rerun()

with col4:
    if st.button("📊 Data Explorer", use_container_width=True):
        st.session_state.mode = 'solo'
        st.rerun()

st.markdown("---")

# Show selected mode
if st.session_state.mode == 'dashboard':
    show_dashboard()
elif st.session_state.mode == 'nlq':
    show_nlq_mode()
elif st.session_state.mode == 'hybrid':
    show_hybrid_mode()
elif st.session_state.mode == 'solo':
    show_solo_mode()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>🕸️ Narrative Nexus v2.0</strong> • AI-Powered Business Advisor</p>
    <p>Turn Data into Stories • Detect Biases • Get Clear Advice</p>
    <p style="font-size: 0.85em; margin-top: 10px;">Built with ❤️ for Business Owners</p>
</div>
""", unsafe_allow_html=True)
