import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION (Futuristic Look) ---
st.set_page_config(
    page_title="DORA Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "GLASSMORPHISM" UI ---
st.markdown("""
<style>
    /* Gradient Background for Metrics */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    /* Hover effect */
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 136, 0.5);
        transform: translateY(-2px);
        transition: all 0.3s ease;
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
    # Fetch Runs
    runs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
    runs_data = []
    page = 1
    # Fetch last 100 runs
    params = {"per_page": 100, "page": page}
    r = requests.get(runs_url, headers=HEADERS, params=params)
    if r.status_code == 200:
        runs_data = r.json()['workflow_runs']
    
    # Fetch PRs
    prs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    prs_params = {"state": "closed", "base": "main", "per_page": 100}
    p = requests.get(prs_url, headers=HEADERS, params=prs_params)
    prs_data = p.json() if p.status_code == 200 else []
    
    return runs_data, prs_data

runs, prs = get_data()

if not runs:
    st.warning("No data found. Check repository permissions.")
    st.stop()

# --- PRE-PROCESSING ---
df_runs = pd.DataFrame(runs)
df_runs['created_at'] = pd.to_datetime(df_runs['created_at'])
df_runs['date'] = df_runs['created_at'].dt.date

# Sidebar Filters
st.sidebar.header("⚙️ Settings")
days_filter = st.sidebar.slider("Time Range (Days)", 1, 90, 30)
cutoff_date = pd.to_datetime(datetime.now(df_runs['created_at'].dt.tz) - timedelta(days=days_filter))

# Filter Data
df_filtered = df_runs[df_runs['created_at'] > cutoff_date].copy()
st.sidebar.write(f"Analyzing {len(df_filtered)} deployments")

# --- METRIC CALCULATIONS ---

# 1. Deployment Frequency
deploy_freq = len(df_filtered)
deploy_freq_daily = deploy_freq / days_filter

# 2. Change Failure Rate
failures = df_filtered[df_filtered['conclusion'] == 'failure']
failure_rate = (len(failures) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0

# 3. Lead Time for Changes
lead_times = []
for pr in prs:
    if pr['merged_at']:
        merged = pd.to_datetime(pr['merged_at'])
        created = pd.to_datetime(pr['created_at'])
        if merged > cutoff_date:
            diff_mins = (merged - created).total_seconds() / 60
            lead_times.append(diff_mins)
avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

# 4. MTTR (Mean Time To Restore) logic
# Sort by time ascending
df_sorted = df_runs.sort_values(by='created_at', ascending=True)
incident_start = None
restore_times = []

for _, row in df_sorted.iterrows():
    if row['conclusion'] == 'failure' and incident_start is None:
        incident_start = row['created_at']
    elif row['conclusion'] == 'success' and incident_start is not None:
        restore_time = (row['created_at'] - incident_start).total_seconds() / 60
        restore_times.append(restore_time)
        incident_start = None # Incident resolved

avg_mttr = sum(restore_times) / len(restore_times) if restore_times else 0

# --- DASHBOARD LAYOUT ---

st.title("🚀 DevOps Command Center")
st.markdown(f"**Repository:** `{OWNER}/{REPO}` | **Window:** Last {days_filter} Days")

# 4 Big Cards
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    label="Deployment Frequency", 
    value=f"{deploy_freq_daily:.2f}/day", 
    delta=f"{deploy_freq} Total"
)
c2.metric(
    label="Lead Time (Avg)", 
    value=f"{avg_lead_time:.0f} min", 
    delta="Target: < 60m", 
    delta_color="inverse"
)
c3.metric(
    label="Change Failure Rate", 
    value=f"{failure_rate:.1f}%", 
    delta="Target: < 15%", 
    delta_color="inverse"
)
c4.metric(
    label="MTTR (Avg Restore)", 
    value=f"{avg_mttr:.0f} min", 
    delta="Target: < 30m", 
    delta_color="inverse"
)

# --- VISUALIZATIONS ---

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Velocity & Performance")
    
    # Timeline of deployments
    daily_counts = df_filtered.groupby('date').size().reset_index(name='Deployments')
    fig_line = px.bar(
        daily_counts, x='date', y='Deployments',
        title="Deployments per Day",
        template="plotly_dark",
        color='Deployments',
        color_continuous_scale=['#00ff88', '#00ccff']
    )
    fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("🛡️ Stability Index")
    
    # Donut Chart for Success/Failure
    status_counts = df_filtered['conclusion'].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=status_counts.index, 
        values=status_counts.values, 
        hole=.5,
        marker=dict(colors=['#00ff88', '#ff4d4d', '#ffaa00']) # Green, Red, Orange
    )])
    fig_pie.update_layout(
        title_text="Success vs Failure",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Raw Data Expander
with st.expander("📝 View Raw Pipeline Data"):
    st.dataframe(df_filtered[['name', 'conclusion', 'created_at', 'actor', 'head_branch']], use_container_width=True)
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "dora_metrics_full.csv", "text/csv")