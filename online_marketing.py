import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import datetime
import altair as alt
import re
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import requests
import base64

load_dotenv()
psw= os.environ.get("token")
url = "https://connection.north-europe.azure.keboola.com/"
headers = {
    "x-storageapi-token": psw
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Process the response data
    pass
else:
    print("error to connect")


# Now you can use the client instance to make API calls
from my_package.style import css_style
from my_package.html import html_code, html_footer, title, logo_html


# Configure Streamlit layout
st.set_page_config(layout="wide")

# Load data from CSV file
file_path = "/data/in/tables/online_marketing.csv"
df_data = pd.read_csv(file_path)

# Create date-related columns
df_data["date_format"] = pd.to_datetime(df_data["date"]).dt.date
df_data["datetime_format"] = pd.to_datetime(df_data["date"])
df_data["month_year"] = df_data["datetime_format"].dt.to_period("M").apply(lambda x: x.strftime("%Y-%m"))

# Set up Streamlit container with title and logo
with st.container():
    secret_name = st.secrets["name"]
    st.markdown(f"{logo_html}", unsafe_allow_html=True)
    st.title(secret_name)


# Create a Streamlit container to hold filter controls and layout
with st.container():
    st.markdown(title["filter"], unsafe_allow_html=True)
    
    # Extract unique values for campaigns and domains
    distinct_campaigns = df_data['campaign'].unique()
    distinct_domain = df_data['source'].unique()
    
    # Create two columns for filter controls
    col1, col3 = st.columns((1.5, 1.5))
    
    # Get current month and year
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    
    # Create filter controls for date range in the first column
    with col1:
        since_date = st.date_input("Select a start date:", datetime.date(current_year - 1, current_month, 1), key="since_date")
        until_date = st.date_input("Select an end date:", datetime.date(current_year, current_month, 1), key="until_date")
    
    # Create filter controls for source and campaign selection in the second column
    with col3:
        selected_sources = st.multiselect('Select a source:', distinct_domain, default=None, placeholder="All sources", key="source")
        selected_campaigns = st.multiselect('Select a campaign:', distinct_campaigns, default=None, placeholder="All campaigns", key="campaign")

# Define default filter values
default = {
    'since_date': datetime.date(current_year - 1, current_month, 1),
    'until_date': datetime.date(current_year, current_month, 1),
    'source': [],
    'campaign': []
}

# Convert into same format to compare
since_date = pd.Timestamp(st.session_state.since_date)
until_date = pd.Timestamp(st.session_state.until_date)
df_data['date'] = pd.to_datetime(df_data['date'])

# Apply filters to the DataFrame based on user selections

filtered_df = df_data[
    (df_data['date'] >= since_date) &
    (df_data['date'] <= until_date)
    ]

if len(st.session_state.source) != 0:
    filtered_df = filtered_df[filtered_df['source'].isin(st.session_state.source)]

if len(st.session_state.campaign) != 0:
    filtered_df = filtered_df[filtered_df['campaign'].isin(st.session_state.campaign)]

# Display statistics title and apply CSS style
st.markdown(title["statistic"], unsafe_allow_html=True)
st.markdown(css_style, unsafe_allow_html=True)

# Create columns for layout
col0 = st.columns(3)
col1, col2, col3 = st.columns(3)

# Define metrics and associated icons
metrics = [
    ("Clicks:", filtered_df[['clicks']].sum()),
    ("Impressions:", filtered_df[['impressions']].sum()),
    ("AVG Cost:", filtered_df[['costs_cpc']].mean().fillna(0.0))
]

my_dict = {
    "Clicks": "click.png",
    "Impressions": "impression.png",
    "AVG Cost": "money.png"
}

# Iterate over the metrics and display icons and values
for i, metric in enumerate(metrics):
    column_index = i % 3
    metric_label, metric_value = metric
    number = re.sub(r"[^\d.]", "", metric_value.to_string())
    
    col = col1 if column_index == 0 else col2 if column_index == 1 else col3
    
    # Retrieve the icon for the metric label
    for key in my_dict.keys():
        if key in metric_label:
            icon_path = my_dict[key]
    

    with col:
        icon_image = os.path.abspath(f"/home/appuser/app/static/{icon_path}")
        st.markdown(f'''
        <div style="margin: 10px auto; width: 70%">
            <div class="div-container" style="display:flex; margin:10px">
                <div class="div-icon" style="flex-basis:2">
                    <img class="icon-img"  src="data:image/png;base64,{base64.b64encode(open(icon_image, "rb").read()).decode()}">
                </div>
                <div style="flex-shrink:1; margin-left: 8%">
                    <h2 class="header">{metric_label}</h2>
                    <p class="text">{number}</p>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Display charts title
st.markdown(title["charts"], unsafe_allow_html=True)

# Create tabs for visualizations and raw data
tab1, tab2 = st.tabs(["Visualizations", "Raw data"])

with tab1:
    # Display title for the "Campaigns" section
    st.markdown(title["campaigns"], unsafe_allow_html=True)

    # Create a bar chart using Plotly Express for campaign clicks analysis
    fig = px.bar(filtered_df, x="date_format", y="clicks", color="campaign", title="Campaign Clicks Analysis")

    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    # Display title for the "Impressions" section
    st.markdown(title["impressions"], unsafe_allow_html=True)

    # Create a line chart using Altair to visualize impressions over time
    line_chart = (
        alt.Chart(filtered_df)
        .mark_line()
        .encode(x="date_format", y="impressions", color="campaign")
    )

    # Display the line chart for impressions
    st.altair_chart(line_chart, use_container_width=True)

    # Display title for the "top 10 campaigns" section
    st.markdown(title["campaignsPerClick"], unsafe_allow_html=True)

    # Create columns for layout
    c10, c11, c1010, c12, c13 = st.columns((0.5, 2.5, 0.5, 2.5, 0.5))

    # Create a plot to display top 10 campaigns per clicks
    with c11:
        # Group the data by campaign and calculate the sum of clicks
        campaign_clicks = filtered_df.groupby('campaign')['clicks'].sum()

        # Get the top 10 campaigns with the highest sum of clicks
        top_10_campaigns = campaign_clicks.nlargest(10).sort_values(ascending=True)

        # Create the horizontal bar plot using Plotly Express
        fig1 = go.Figure(go.Bar(
            x=top_10_campaigns.values,
            y=top_10_campaigns.index,
            orientation='h',
            marker_color='lightskyblue'
        ))

        # Customize the plot layout
        fig1.update_layout(
            title='Top 10 Campaigns by Clicks',
            xaxis_title='Clicks',
            yaxis_title='Campaigns',
            margin=dict(l=150),
        )

        # Display the plot
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)


    # Create a plot to display top 10 campaigns by impressions
    with c12:
        # Convert 'impressions' column to numeric
        filtered_df['impressions'] = pd.to_numeric(filtered_df['impressions'])

        # Group the data by campaign and calculate the sum of impressions
        campaign_impressions = filtered_df.groupby('campaign')['impressions'].sum()

        # Get the top 10 campaigns with the highest sum of impressions
        top_10_campaigns = campaign_impressions.nlargest(10).sort_values(ascending=True)

        # Create the horizontal bar plot using Plotly Graph Objects
        fig2 = go.Figure(go.Bar(
            x=top_10_campaigns.values,
            y=top_10_campaigns.index,
            orientation='h',
            marker_color='lightskyblue'
        ))

        # Customize the plot layout
        fig2.update_layout(
            title='Top 10 Campaigns by Impressions',
            xaxis_title='Impressions',
            yaxis_title='Campaign',
            margin=dict(l=150),
        )

        # Display the plot
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

# Create tab to display raw data
with tab2:
    # Display raw data section
    st.markdown(title["rawData"], unsafe_allow_html=True)
    # Display the DataFrame with adjustable width
    st.dataframe(df_data, use_container_width=True)

# Display description title
st.markdown(title["description"], unsafe_allow_html=True)

# Display HTML code 
st.write(html_code, unsafe_allow_html=True)

# Display HTML footer
st.markdown(html_footer, unsafe_allow_html=True)

