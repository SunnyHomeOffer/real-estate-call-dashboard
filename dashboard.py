# Real Estate Call Dashboard - Google Sheet Sync Version
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqX2UIjXuKu7noH2QLT8k-YfNbWtJgmPbYuaunoOdy51UVtT4IQqvl-fhT0XtxTbe66FE1savHnNVv/pub?gid=286064860&single=true&output=csv"
    df = pd.read_csv(sheet_url)

    df = df.rename(columns={"Total Deep Prospects ": "Leads"})

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['DayOfWeek'] = df['Date'].dt.day_name()

    cols_to_num = ['Total Dials', 'Conversations', 'Leads', 'Offer Made', 'Total Correct Numbers',
                   'Dead Number', 'Correct Initial Call', 'Correct Follow Up 1',
                   'Correct Follow Up 2', 'Correct Follow Up 3', 'Not Interested',
                   'Wrong Number', 'OFFER SIGNED', 'CONTRACT SIGNED']
    for col in cols_to_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0  # default to 0 if missing

    df['Connection Rate'] = df['Conversations'] / df['Total Dials']
    df['Offers per Convo'] = df.apply(lambda row: row['Offer Made'] / row['Conversations']
                                       if row['Conversations'] and row['Conversations'] > 0 else None, axis=1)
    df['Acceptance Rate'] = df['OFFER SIGNED'] / df['Offer Made']
    df['Contract Rate'] = df['CONTRACT SIGNED'] / df['Offer Made']
    df['Success Rate'] = df['CONTRACT SIGNED'] / df['Total Dials']
    return df

df = load_data()
st.title("📞 Real Estate Call Performance Dashboard")

st.sidebar.header("Filter Data")
selected_day = st.sidebar.multiselect("Filter by Day", options=df['DayOfWeek'].unique(), default=df['DayOfWeek'].unique())
selected_agent = st.sidebar.selectbox("Select Caller", options=["All"] + sorted(df['Caller'].dropna().unique().tolist()))
if selected_agent != "All":
    df = df[df['Caller'] == selected_agent]
df = df[df['DayOfWeek'].isin(selected_day)]

st.header("📌 Key Metrics")
avg_metrics = df[['Total Dials', 'Conversations', 'Leads', 'Offer Made', 'Total Correct Numbers']].mean().round(2)
offer_efficiency = df['Offers per Convo'].dropna().mean().round(2) if not df['Offers per Convo'].dropna().empty else 0
acceptance_rate = df['Acceptance Rate'].dropna().mean().round(2) if not df['Acceptance Rate'].dropna().empty else 0
contract_rate = df['Contract Rate'].dropna().mean().round(2) if not df['Contract Rate'].dropna().empty else 0
success_rate = df['Success Rate'].dropna().mean().round(2) if not df['Success Rate'].dropna().empty else 0

col1, col2, col3 = st.columns(3)
col1.metric("Avg. Conversations", f"{avg_metrics['Conversations']:.2f}")
col1.metric("Avg. Correct Numbers", f"{avg_metrics['Total Correct Numbers']:.2f}")
col2.metric("Offer Efficiency", f"{offer_efficiency:.2%}")
col2.metric("Acceptance Rate", f"{acceptance_rate:.2%}")
col3.metric("Contract Rate", f"{contract_rate:.2%}")
col3.metric("Success Rate", f"{success_rate:.2%}")
