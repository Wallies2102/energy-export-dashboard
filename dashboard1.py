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
df['date'] = df['time'].dt.date
df['export_kwh'] = df['export_kwh']
df['export_per_interval'] = df['export_kwh'].diff().fillna(0)

# Preprocessing: Remove intervals with no change in export for > 24 hours (48 intervals assuming 30-min data)
df['constant_group'] = (df['export_kwh'] != df['export_kwh'].shift()).cumsum()
group_sizes = df.groupby('constant_group').size()
long_constant_groups = group_sizes[group_sizes > 48].index
df = df[~df['constant_group'].isin(long_constant_groups)].copy()
df.drop(columns='constant_group', inplace=True)


# Step: Remove months with suspiciously low average export (e.g., < 50% of median)
monthly_avg = df.groupby(df['time'].dt.month)['export_per_interval'].mean()
threshold = monthly_avg.median() * 0.5
valid_months = monthly_avg[monthly_avg > threshold].index
df = df[df['month'].isin(valid_months)].copy()

# Sidebar filters
st.sidebar.header("Filter Options")
selected_plot = st.sidebar.selectbox("Select plot type", ["Heatmap", "Box Plot", "Cumulative Export", "Hourly Export", "Daily Export"])
start_date = st.sidebar.date_input("Start Date", df['time'].min().date())
end_date = st.sidebar.date_input("End Date", df['time'].max().date())

# Filter data by date
mask = (df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask].copy()

st.title("Energy Export Dashboard")

# Heatmap
if selected_plot == "Heatmap":
    if 'eport_kwh' in df_filtered.columns:
        pivot = df_filtered.pivot_table(index='day', columns='hour', values='export_kwh', aggfunc='mean')
        fig, ax = plt.subplots()
        sns.heatmap(pivot, ax=ax, cmap='YlGnBu')
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Day of Week (0=Monday)")
        st.pyplot(fig)
    else:
        st.warning("Column 'eport_kwh' not found in the dataset.")

# Box Plot
elif selected_plot == "Box Plot":
    fig = px.box(df_filtered, x='month', y='export_kwh', points='all',
                 title="Monthly Export Distribution",
                 labels={'month': 'Month', 'eport_kwh': 'Export (kWh)'})
    st.plotly_chart(fig)

# Cumulative Plot
elif selected_plot == "Cumulative Export":
    df_filtered['cumulative_export_kwh'] = df_filtered['export_kwh'].cumsum()
    fig = px.line(df_filtered, x='time', y='cumulative_export_kwh',
                  title='Cumulative Energy Export (kWh)',
                  labels={'cumulative_export_kwh': 'Energy Export (kWh)'})
    st.plotly_chart(fig)

# Hourly trend
elif selected_plot == "Hourly Export":
    hourly_export = df_filtered.groupby('hour')['export_per_interval'].mean()
    st.subheader("Average Energy Export by Hour of Day")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(hourly_export.index, hourly_export.values, color='darkorange')
    ax2.set_xlabel("Hour")
    ax2.set_ylabel("Average Export (kWh)")
    ax2.set_title("Hourly Export Pattern")
    ax2.grid(True)
    st.pyplot(fig2)

# Daily Export trend
elif selected_plot == "Daily Export":
    daily_export = df_filtered.groupby('date')['export_per_interval'].sum()
    st.subheader("Total Daily Energy Export")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(daily_export.index, daily_export.values, marker='o')
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Total Export (kWh)")
    ax3.set_title("Daily Energy Export Trend")
    ax3.grid(True)
    st.pyplot(fig3)