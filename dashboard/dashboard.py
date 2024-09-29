import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='white')

def create_holiday_df(df):
    holiday_df = df.groupby(by=["holiday"]).agg({
        "cnt": "mean"
    }).reset_index()

    holiday_df["holiday"] = holiday_df['holiday'].map({0: 'Non-Holiday', 1: 'Holiday'})
    return holiday_df

def create_proportioned_holiday_df(df):
    proportioned_holiday_df = df.groupby(by=["holiday"]).agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()

    proportioned_holiday_df["holiday"] = proportioned_holiday_df['holiday'].map({0: 'Non-Holiday', 1: 'Holiday'})
    proportioned_holiday_df[["casual", "registered"]] = proportioned_holiday_df[['casual', 'registered']].div(proportioned_holiday_df['cnt'], axis=0)
    proportioned_holiday_df.drop('cnt', axis=1, inplace=True)
    return proportioned_holiday_df

def create_workingday_df(df):
    workingday_df = df.groupby(by=["workingday"]).agg({
        "cnt": "mean"
    }).reset_index()

    workingday_df["workingday"] = workingday_df['workingday'].map({0: 'Non-Workingday', 1: 'Workingday'})
    return workingday_df

def create_proportioned_workingday_df(df):
    proportioned_workingday_df = df.groupby(by=["workingday"]).agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()

    proportioned_workingday_df["workingday"] = proportioned_workingday_df['workingday'].map({0: 'Non-Workingday', 1: 'Workingday'})
    proportioned_workingday_df[["casual", "registered"]] = proportioned_workingday_df[['casual', 'registered']].div(proportioned_workingday_df['cnt'], axis=0)
    proportioned_workingday_df.drop('cnt', axis=1, inplace=True)
    return proportioned_workingday_df

def create_peak_df(df):
    peak_df = df.groupby(by=["hr", "workingday"]).agg({
        "cnt": "mean"
    }).reset_index()
    return peak_df

def create_user_peak_df(df):
    user_peak_df = df.groupby(by=["hr", "workingday"]).agg({
        "casual": "mean",
        "registered": "mean"
    }).reset_index()
    return user_peak_df

def create_day_weathersit_df(df):
    day_weathersit_df = df.groupby(by=["weathersit"]).agg({
        "cnt": "mean"
    }).reset_index()

    day_weathersit_df["weathersit"] = day_weathersit_df["weathersit"].map({1: 'Clear or Partly Cloudy', 
                                                                        2: 'Mist or Cloudy', 
                                                                        3: 'Light Snow or Rain'})
    return day_weathersit_df

def create_hour_weathersit_df(df):
    hour_weathersit_df = df.groupby(by=["weathersit"]).agg({
        "cnt": "mean"
    }).reset_index()

    # Mapping dilakukan untuk keperluan visualisasi data
    hour_weathersit_df["weathersit"] = hour_weathersit_df["weathersit"].map({1: 'Clear or Partly Cloudy', 
                                                                        2: 'Mist or Cloudy', 
                                                                        3: 'Light Snow or Rain',
                                                                        4: 'Severe Weather'})
    return hour_weathersit_df

def create_atemp_df(df):
    atemp_df = df.groupby(by=["atemp"]).agg({
        "cnt": "mean"
    }).reset_index()

    order = ["Safe", "Caution", "Extreme Caution", "Danger", "Extreme Danger"]
    atemp_df["atemp"] = pd.Categorical(atemp_df["atemp"], categories=order, ordered=True)
    return atemp_df


dirname = os.path.dirname(__file__)

day_df = pd.read_csv(os.path.join(dirname, "day_processed.csv"))
hour_df = pd.read_csv(os.path.join(dirname, "hour_processed.csv"))
cluster_df = pd.read_csv(os.path.join(dirname, "clustered_atemp.csv"))

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
cluster_df["dteday"] = pd.to_datetime(cluster_df["dteday"])


min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]
main_cluster_df = cluster_df[(cluster_df["dteday"] >= str(start_date)) & (cluster_df["dteday"] <= str(end_date))]

holiday_df = create_holiday_df(main_day_df)
proportioned_holiday_df = create_proportioned_holiday_df(main_day_df)
workingday_df = create_workingday_df(main_day_df)
proportioned_workingday_df = create_proportioned_workingday_df(main_day_df)
peak_df = create_peak_df(main_hour_df)
user_peak_df = create_user_peak_df(main_hour_df)
day_weathersit_df = create_day_weathersit_df(main_day_df)
hour_weathersit_df = create_hour_weathersit_df(main_hour_df)
atemp_df = create_atemp_df(main_cluster_df)


st.header("Bike Rental Dashboard")

st.subheader("Total Rent by User")
col1, col2 = st.columns(2)

with col1:
    casual_user = main_day_df.casual.sum()
    st.metric("Casual User", value=casual_user)

with col2:
    registered_user = main_day_df.registered.sum()
    st.metric("Registered", value=registered_user)

st.subheader("Holiday Effect on Bike Rent")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    sns.barplot(y="cnt",
            x="holiday",
            data=holiday_df,
            color="#15B392",
            ax=ax)

    ax.set_title("Average Bike Rent based on Holiday", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    proportioned_holiday_df.set_index('holiday').plot(kind='bar', stacked=True, color=['#D2FF72', '#15B392'], ax=ax)

    ax.set_title("User Proportion based on Holiday Rent", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    ax.legend(fontsize=30)
    st.pyplot(fig)

st.subheader("Workingday Effect on Bike Rent")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    sns.barplot(y="cnt",
            x="workingday",
            data=workingday_df,
            color="#15B392",
            ax=ax)

    ax.set_title("Average Bike Rent based on Workingday", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    proportioned_workingday_df.set_index('workingday').plot(kind='bar', stacked=True, color=['#D2FF72', '#15B392'], ax=ax)

    ax.set_title("User Proportion based on Workingday Rent", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    ax.legend(fontsize=30)
    st.pyplot(fig)

st.subheader("Peak Hours")
workingday_peak = peak_df[peak_df["workingday"] == 1]
non_workingday_peak = peak_df[peak_df["workingday"] == 0]

working_peak_hour = workingday_peak.loc[workingday_peak["cnt"].idxmax(), "hr"]
non_working_peak_hour = non_workingday_peak.loc[non_workingday_peak["cnt"].idxmax(), "hr"]

fig, ax = plt.subplots(figsize=(16,8))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.plot(workingday_peak["hr"], workingday_peak["cnt"], marker="o", linewidth=2, color="#15B392")
ax.plot(non_workingday_peak["hr"], non_workingday_peak["cnt"], marker="o", linewidth=2, color="#D2FF72")

ax.axvline(x=working_peak_hour, color='#15B392', linestyle='--', label=f"Working Day Peak at {working_peak_hour}:00")
ax.axvline(x=non_working_peak_hour, color='#D2FF72', linestyle='--', label=f"Non Working Day Peak at {non_working_peak_hour}:00")

ax.set_title("Average Bike Rent by Hour", loc="center", fontsize=50)
ax.set_xticks(peak_df["hr"])
ax.tick_params(axis='x', labelsize=15, rotation=0)
ax.tick_params(axis='y', labelsize=15)
ax.legend(fontsize=15)
st.pyplot(fig)


st.subheader("Peak Hours by User")
workingday_peak = user_peak_df[user_peak_df["workingday"] == 1]
non_workingday_peak = user_peak_df[user_peak_df["workingday"] == 0]

workingday_peak_casual = workingday_peak.loc[workingday_peak["casual"].idxmax(), "hr"]
workingday_peak_registered = workingday_peak.loc[workingday_peak["registered"].idxmax(), "hr"]

non_workingday_peak_casual = non_workingday_peak.loc[non_workingday_peak["casual"].idxmax(), "hr"]
non_workingday_peak_registered = non_workingday_peak.loc[non_workingday_peak["registered"].idxmax(), "hr"]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30,6))
fig.patch.set_facecolor('white')
ax[0].set_facecolor('white')
ax[1].set_facecolor('white')

# WORKING DAY
ax[0].plot(workingday_peak["hr"], workingday_peak["casual"], marker="o", linewidth=2, color="#D2FF72", label="Casual User")
ax[0].plot(workingday_peak["hr"], workingday_peak["registered"], marker="o", linewidth=2, color="#15B392", label="Registered User")

ax[0].axvline(x=workingday_peak_casual, color='#D2FF72', linestyle='--', label=f"Peak at {workingday_peak_casual}:00")
ax[0].axvline(x=workingday_peak_registered, color='#15B392', linestyle='--', label=f"Peak at {workingday_peak_registered}:00")

ax[0].set_title("Working Day", loc="center", fontsize=30)
ax[0].set_xticks(peak_df["hr"].unique())
ax[0].set_xticklabels(peak_df["hr"].unique(), fontsize=15)
ax[0].set_yticklabels(ax[0].get_yticks(), fontsize=15)
ax[0].legend(fontsize=15)

# NON WORKING DAY
ax[1].plot(non_workingday_peak["hr"], non_workingday_peak["casual"], marker="o", linewidth=2, color="#D2FF72", label="Casual User")
ax[1].plot(non_workingday_peak["hr"], non_workingday_peak["registered"], marker="o", linewidth=2, color="#15B392", label="Registered User")

ax[1].axvline(x=non_workingday_peak_casual, color='#D2FF72', linestyle='--', label=f"Peak at {non_workingday_peak_casual}:00")
ax[1].axvline(x=non_workingday_peak_registered, color='#15B392', linestyle='--', label=f"Peak at {non_workingday_peak_registered}:00")

ax[1].set_title("Non Working Day", loc="center", fontsize=30)
ax[1].set_xticks(peak_df["hr"].unique())
ax[1].set_xticklabels(peak_df["hr"].unique(), fontsize=15)
ax[1].set_yticklabels(ax[1].get_yticks(), fontsize=15)
ax[1].legend(fontsize=15)

plt.suptitle("Average Bike Rent by Hour and User", fontsize=30)
st.pyplot(fig)

st.subheader("Weather Condition Effect on Bike Rent")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    colors_ = ["#15B392", "#73EC8B", "#D2FF72"]
    sns.barplot(x="cnt",
            y="weathersit",
            data=day_weathersit_df.sort_values(by="cnt", ascending=False),
            palette=colors_,
            orient="h",
            ax=ax)

    ax.set_title("Daily Average Bike Rent on Different Weather Situation", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    colors_ = ["#15B392", "#73EC8B", "#73EC8B", "#D2FF72"]
    sns.barplot(x="cnt",
            y="weathersit",
            data=hour_weathersit_df.sort_values(by="cnt", ascending=False),
            palette=colors_,
            orient="h",
            ax=ax)

    ax.set_title("Hourly Average Bike Rent on Different Weather Situation", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, rotation=0)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.subheader("Feeling Temperature Effect on Bike Rent")
order = ["Safe", "Caution", "Extreme Caution", "Danger", "Extreme Danger"]
atemp_df["atemp"] = pd.Categorical(atemp_df["atemp"], categories=order, ordered=True)


fig, ax = plt.subplots(figsize=(16,8))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

colors_ = ["#15B392", "#FFEB3B", "#FF9800", "#F44336", "#D32F2F"]
sns.barplot(x="cnt",
           y="atemp",
           data=atemp_df,
           palette=colors_,
           orient="h",
           ax=ax)

ax.set_title("Daily Average Bike Rent on Different Feeling Temperature", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35, rotation=0)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)
 
st.caption('Copyright (c) Pramodia 2024')