import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DORA Intelligence Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark theme with gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        background-attachment: fixed;
    }
    
    /* Animated gradient border for metrics */
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(0, 255, 136, 0.5); }
        50% { border-color: rgba(0, 204, 255, 0.7); }
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 255, 136, 0.1) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(0.8); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 136, 0.8);
        transform: translateY(-4px) scale(1.02);
        box-shadow: 
            0 12px 48px rgba(0, 255, 136, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        animation: borderGlow 2s ease-in-out infinite;
    }
    
    /* Metric labels */
    div[data-testid="stMetric"] label {
        color: #00ff88 !important;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric values */
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
    }
    
    h1 {
        font-size: 3rem !important;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleShimmer 3s ease-in-out infinite;
    }
    
    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95) 0%, rgba(15, 20, 25, 0.98) 100%);
        border-right: 1px solid rgba(0, 255, 136, 0.2);
        backdrop-filter: blur(10px);
    }
    
    section[data-testid="stSidebar"] h2 {
        color: #00ff88 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 204, 255, 0.1) 100%);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 136, 0.3);
        color: #00ff88 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(0, 255, 136, 0.6);
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 204, 255, 0.15) 100%);
    }
    
    /* Dataframe */
    .dataframe {
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
        border-radius: 10px;
    }
    
    /* Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        color: #0a0e27;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 255, 136, 0.4);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        border: 1px solid #00ff88;
    }
    
    .status-failure {
        background: rgba(255, 77, 77, 0.2);
        color: #ff4d4d;
        border: 1px solid #ff4d4d;
    }
    
    /* Loading animation */
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(0, 204, 255, 0.1) 0%, rgba(0, 255, 136, 0.05) 100%);
        border-left: 4px solid #00ccff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
OWNER = "OUCHAALI"
REPO = "dora-metrics-tp"
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
except FileNotFoundError:
    st.error("❌ Secrets file not found. Please create .streamlit/secrets.toml")
    st.stop()

HEADERS = {"Authorization": f"token {TOKEN}"}

# --- DATA FETCHING ---
@st.cache_data(ttl=60)
def get_data():
    runs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
    runs_data = []
    params = {"per_page": 100, "page": 1}
    r = requests.get(runs_url, headers=HEADERS, params=params)
    if r.status_code == 200:
        runs_data = r.json()['workflow_runs']
    
    prs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    prs_params = {"state": "closed", "base": "main", "per_page": 100}
    p = requests.get(prs_url, headers=HEADERS, params=prs_params)
    prs_data = p.json() if p.status_code == 200 else []
    
    return runs_data, prs_data

# --- HEADER ---
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("🚀 DORA Intelligence Hub")
    st.markdown(f"<div class='info-box'>📡 Monitoring <b>{OWNER}/{REPO}</b> • Real-time DevOps Analytics</div>", unsafe_allow_html=True)

with col_status:
    with st.spinner(""):
        runs, prs = get_data()

if not runs:
    st.warning("⚠️ No data available. Please check repository permissions.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("---")

days_filter = st.sidebar.slider("📅 Time Window (Days)", 1, 90, 30, help="Adjust the analysis time range")
refresh_rate = st.sidebar.selectbox("🔄 Refresh Rate", ["1 min", "5 min", "15 min", "Manual"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Metrics Overview")

# --- DATA PROCESSING ---
df_runs = pd.DataFrame(runs)
df_runs['created_at'] = pd.to_datetime(df_runs['created_at'])
df_runs['date'] = df_runs['created_at'].dt.date

cutoff_date = pd.to_datetime(datetime.now(df_runs['created_at'].dt.tz) - timedelta(days=days_filter))
df_filtered = df_runs[df_runs['created_at'] > cutoff_date].copy()

st.sidebar.info(f"📈 Analyzing **{len(df_filtered)}** deployments")
st.sidebar.success(f"✅ Success Rate: **{(df_filtered['conclusion'] == 'success').sum() / len(df_filtered) * 100:.1f}%**")

# --- METRIC CALCULATIONS ---
deploy_freq = len(df_filtered)
deploy_freq_daily = deploy_freq / days_filter if days_filter > 0 else 0

failures = df_filtered[df_filtered['conclusion'] == 'failure']
failure_rate = (len(failures) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0

lead_times = []
for pr in prs:
    if pr['merged_at']:
        merged = pd.to_datetime(pr['merged_at'])
        created = pd.to_datetime(pr['created_at'])
        if merged > cutoff_date:
            diff_mins = (merged - created).total_seconds() / 60
            lead_times.append(diff_mins)
avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

df_sorted = df_runs.sort_values(by='created_at', ascending=True)
incident_start = None
restore_times = []

for _, row in df_sorted.iterrows():
    if row['conclusion'] == 'failure' and incident_start is None:
        incident_start = row['created_at']
    elif row['conclusion'] == 'success' and incident_start is not None:
        restore_time = (row['created_at'] - incident_start).total_seconds() / 60
        restore_times.append(restore_time)
        incident_start = None

avg_mttr = sum(restore_times) / len(restore_times) if restore_times else 0

# --- DORA PERFORMANCE RATING ---
def get_dora_rating(deploy_freq_daily, lead_time, failure_rate, mttr):
    score = 0
    # Deployment Frequency (Elite: >1/day, High: 1/week-1/day, Medium: 1/month-1/week, Low: <1/month)
    if deploy_freq_daily > 1: score += 25
    elif deploy_freq_daily > 0.14: score += 20
    elif deploy_freq_daily > 0.03: score += 15
    else: score += 10
    
    # Lead Time (Elite: <1h, High: <1day, Medium: <1week, Low: >1month)
    if lead_time < 60: score += 25
    elif lead_time < 1440: score += 20
    elif lead_time < 10080: score += 15
    else: score += 10
    
    # Failure Rate (Elite: <5%, High: 5-15%, Medium: 16-30%, Low: >30%)
    if failure_rate < 5: score += 25
    elif failure_rate < 15: score += 20
    elif failure_rate < 30: score += 15
    else: score += 10
    
    # MTTR (Elite: <1h, High: <1day, Medium: <1week, Low: >1week)
    if mttr < 60: score += 25
    elif mttr < 1440: score += 20
    elif mttr < 10080: score += 15
    else: score += 10
    
    if score >= 90: return "🏆 Elite", score, "#00ff88"
    elif score >= 75: return "⭐ High", score, "#00ccff"
    elif score >= 60: return "📈 Medium", score, "#ffaa00"
    else: return "⚠️ Low", score, "#ff4d4d"

rating, score, color = get_dora_rating(deploy_freq_daily, avg_lead_time, failure_rate, avg_mttr)

# --- MAIN METRICS ---
st.markdown("### 📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Deployment Freq", 
        value=f"{deploy_freq_daily:.2f}/day", 
        delta=f"{deploy_freq} total"
    )

with col2:
    st.metric(
        label="Lead Time", 
        value=f"{avg_lead_time:.0f} min", 
        delta="Elite < 60m",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Failure Rate", 
        value=f"{failure_rate:.1f}%", 
        delta="Elite < 5%",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="MTTR", 
        value=f"{avg_mttr:.0f} min", 
        delta="Elite < 60m",
        delta_color="inverse"
    )

with col5:
    st.metric(
        label="DORA Score", 
        value=f"{score}/100",
        delta=rating
    )

st.markdown("---")

# --- VISUALIZATIONS ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🎯 Performance", "🔥 Heatmap", "📋 Details"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Deployment Velocity")
        daily_counts = df_filtered.groupby('date').size().reset_index(name='Deployments')
        
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=daily_counts['date'],
            y=daily_counts['Deployments'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#00ff88', width=3),
            fillcolor='rgba(0, 255, 136, 0.2)',
            name='Deployments'
        ))
        
        fig_area.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.3)",
            font=dict(color="#ffffff"),
            hovermode='x unified',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    with col_right:
        st.subheader("🛡️ Stability Index")
        status_counts = df_filtered['conclusion'].value_counts()
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.6,
            marker=dict(colors=['#00ff88', '#ff4d4d', '#ffaa00']),
            textfont=dict(size=14, color='#ffffff')
        )])
        
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            height=400,
            annotations=[dict(text=f"{(status_counts.get('success', 0) / status_counts.sum() * 100):.1f}%",
                             x=0.5, y=0.5, font_size=24, showarrow=False, font=dict(color='#00ff88'))]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("🎯 DORA Metrics Performance")
    
    metrics_data = {
        'Metric': ['Deploy Freq', 'Lead Time', 'Failure Rate', 'MTTR'],
        'Current': [deploy_freq_daily, avg_lead_time / 60, failure_rate, avg_mttr / 60],
        'Elite Target': [1, 1, 5, 1],
        'Unit': ['/day', 'hours', '%', 'hours']
    }
    
    col_perf1, col_perf2 = st.columns(2)
    
    with col_perf1:
        fig_radar = go.Figure()
        
        categories = ['Deploy\nFrequency', 'Lead\nTime', 'Failure\nRate', 'MTTR']
        
        # Normalize values for radar (0-100 scale)
        current_normalized = [
            min(deploy_freq_daily * 50, 100),
            max(100 - avg_lead_time / 10, 0),
            max(100 - failure_rate * 5, 0),
            max(100 - avg_mttr / 10, 0)
        ]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=current_normalized,
            theta=categories,
            fill='toself',
            name='Current',
            line=dict(color='#00ff88', width=2),
            fillcolor='rgba(0, 255, 136, 0.3)'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[100, 100, 100, 100],
            theta=categories,
            fill='toself',
            name='Elite Target',
            line=dict(color='#00ccff', width=2, dash='dash'),
            fillcolor='rgba(0, 204, 255, 0.1)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col_perf2:
        # Performance gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall DORA Score", 'font': {'color': '#ffffff'}},
            delta={'reference': 90, 'increasing': {'color': "#00ff88"}},
            gauge={
                'axis': {'range': [None, 100], 'tickcolor': "#ffffff"},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(255, 77, 77, 0.3)'},
                    {'range': [60, 75], 'color': 'rgba(255, 170, 0, 0.3)'},
                    {'range': [75, 90], 'color': 'rgba(0, 204, 255, 0.3)'},
                    {'range': [90, 100], 'color': 'rgba(0, 255, 136, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#ffffff"},
            height=400
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab3:
    st.subheader("🔥 Deployment Heatmap")
    
    df_filtered['hour'] = df_filtered['created_at'].dt.hour
    df_filtered['dayofweek'] = df_filtered['created_at'].dt.dayofweek
    
    heatmap_data = df_filtered.groupby(['dayofweek', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='dayofweek', columns='hour', values='count').fillna(0)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=[[0, '#0a0e27'], [0.5, '#00ccff'], [1, '#00ff88']],
        showscale=True,
        hovertemplate='Day: %{y}<br>Hour: %{x}<br>Deployments: %{z}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.info("💡 **Insight:** Identify peak deployment times to optimize CI/CD resource allocation")

with tab4:
    st.subheader("📋 Recent Deployments")
    
    display_df = df_filtered[['name', 'conclusion', 'created_at', 'actor', 'head_branch']].copy()
    display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df = display_df.sort_values('created_at', ascending=False).head(50)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv,
        file_name=f"dora_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# --- FOOTER ---
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.caption("🔄 Last Updated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
with col_footer2:
    st.caption(f"📊 Data Source: GitHub Actions API")
with col_footer3:
    st.caption("⚡ Powered by Streamlit & Plotly")