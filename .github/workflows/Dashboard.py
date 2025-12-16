import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# REPLACE THESE WITH YOUR DETAILS
OWNER = "OUCHAALI"       # e.g., OUCHAALI
REPO = "dora-metrics-tp"      # Your repo name
# Remove the hardcoded TOKEN line and replace with:
TOKEN = st.secrets["GITHUB_TOKEN"]   # Paste your token starting with ghp_...

HEADERS = {"Authorization": f"token {TOKEN}"}
# --- 1. FETCH DATA FROM GITHUB API ---
@st.cache_data(ttl=60) # Cache data for 60 seconds to avoid spamming API
def get_workflow_runs():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
    params = {"per_page": 100} 
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()['workflow_runs']
    return []

def get_pull_requests():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    params = {"state": "closed", "base": "main", "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    return []

# --- 2. PROCESS DATA ---
st.title(f"🚀 DORA Metrics Dashboard: {REPO}")
st.write("Live data fetched from GitHub API")

# Fetch Raw Data
runs = get_workflow_runs()
prs = get_pull_requests()

if not runs:
    st.error("No workflow runs found. Check your Token/Repo name.")
    st.stop()

# Convert to DataFrame
df_runs = pd.DataFrame(runs)
df_runs['created_at'] = pd.to_datetime(df_runs['created_at'])
df_runs['date'] = df_runs['created_at'].dt.date

# --- 3. CALCULATE METRICS ---

# A. Deployment Frequency (Successes per day)
success_runs = df_runs[df_runs['conclusion'] == 'success']
daily_deployments = success_runs.groupby('date').size()
total_deployments_7days = len(success_runs[success_runs['created_at'] > pd.to_datetime(datetime.now() - timedelta(days=7), utc=True)])

# B. Change Failure Rate
total_runs_count = len(df_runs)
failed_runs_count = len(df_runs[df_runs['conclusion'] == 'failure'])
failure_rate = (failed_runs_count / total_runs_count * 100) if total_runs_count > 0 else 0

# C. Lead Time (PR Merge Time)
lead_times = []
for pr in prs:
    if pr['merged_at']:
        merged = pd.to_datetime(pr['merged_at'])
        created = pd.to_datetime(pr['created_at'])
        diff_minutes = (merged - created).total_seconds() / 60
        lead_times.append(diff_minutes)
avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

# --- 4. VISUALIZATION ---

# Top Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Deployment Frequency (7d)", f"{total_deployments_7days}", "Runs")
col2.metric("Change Failure Rate", f"{failure_rate:.1f}%", "-Low is better")
col3.metric("Avg Lead Time", f"{avg_lead_time:.1f} min", "-Fast is better")

# Charts
st.subheader("📊 Deployments over Time")
st.bar_chart(daily_deployments)

st.subheader("📉 Pipeline Health (Success vs Failure)")
labels = ['Success', 'Failure', 'Other']
sizes = [
    len(df_runs[df_runs['conclusion'] == 'success']),
    len(df_runs[df_runs['conclusion'] == 'failure']),
    len(df_runs) - len(df_runs[df_runs['conclusion'].isin(['success', 'failure'])])
]
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#4CAF50', '#F44336', '#FFC107'])
st.pyplot(fig)

# Show Raw Data (Bonus Requirement: CSV Export)
st.subheader("📝 Raw Data Export")
csv = df_runs[['name', 'status', 'conclusion', 'created_at']].to_csv(index=False).encode('utf-8')
st.download_button("Download Data as CSV", data=csv, file_name="dora_metrics.csv", mime="text/csv")