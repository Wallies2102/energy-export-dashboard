import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load data
df = pd.read_csv("LGZ58952193-ReadLoadProfile1.1.csv")
df['time'] = pd.to_datetime(df['time'])
df['hour'] = df['time'].dt.hour
df['day'] = df['time'].dt.dayofweek
df['month'] = df['time'].dt.month

# Sidebar filters
st.sidebar.header("Filter Options")
selected_plot = st.sidebar.selectbox("Select plot type", ["Heatmap", "Box Plot", "Cumulative Export"])
start_date = st.sidebar.date_input("Start Date", df['time'].min().date())
end_date = st.sidebar.date_input("End Date", df['time'].max().date())

# Filter data by date
mask = (df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask].copy()

st.title("Energy Export Dashboard")

# Heatmap
if selected_plot == "Heatmap":
    pivot = df_filtered.pivot_table(index='day', columns='hour', values='eport_kwh', aggfunc='mean')
    fig, ax = plt.subplots()
    sns.heatmap(pivot, ax=ax, cmap='YlGnBu')
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week (0=Monday)")
    st.pyplot(fig)

# Box Plot
elif selected_plot == "Box Plot":
    fig = px.box(df_filtered, x='month', y='eport_kwh', points='all',
                 title="Monthly Export Distribution",
                 labels={'month': 'Month', 'eport_kwh': 'Export (kWh)'})
    st.plotly_chart(fig)

# Cumulative Plot
elif selected_plot == "Cumulative Export":
    df_filtered['cumulative_export_kwh'] = df_filtered['eport_kwh'].cumsum()
    fig = px.line(df_filtered, x='time', y='cumulative_export_kwh',
                  title='Cumulative Energy Export (kWh)',
                  labels={'cumulative_export_kwh': 'Energy Export (kWh)'})
    st.plotly_chart(fig)