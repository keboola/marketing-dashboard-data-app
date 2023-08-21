import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import datetime
import altair as alt
import re
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import base64

# Now you can use the client instance to make API calls
from my_package.style import css_style
from my_package.html import html_code, html_footer, title, logo_html


# Configure Streamlit layout
st.set_page_config(layout="wide")

# Load data from CSV file
file_path = os.path.abspath("./app/data/in/tables/online_marketing.csv")
df_data = pd.read_csv(file_path)
# Create date-related columns
df_data["Date"] = pd.to_datetime(df_data["date"]).dt.date
df_data["datetime_format"] = pd.to_datetime(df_data["date"])
df_data["month_year"] = df_data["datetime_format"].dt.to_period("M").apply(lambda x: x.strftime("%Y-%m"))
df_data.rename(columns={'clicks': 'Clicks'}, inplace=True)

# Set up Streamlit container with title and logo
with st.container():
    st.markdown(f"{logo_html}", unsafe_allow_html=True)
    st.title("Online Marketing Analysis")


# Create a Streamlit container to hold filter controls and layout
with st.container():
    st.markdown(title["filter"], unsafe_allow_html=True)
    # Extract unique values for campaigns and domains
    distinct_campaigns = df_data['campaign'].unique()
    distinct_domain = df_data['domain'].unique()
    distinct_source = df_data["source"].unique()
    
    # Create two columns for filter controls
    col1, col2 = st.columns((1.5, 1.5))
    col11,col12,col13 = st.columns((1,1,1))
    
    # Get current month and year
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    
    # Create filter controls for date range in the first column
    with col1:
        since_date = st.date_input("Select a start date:", datetime.date(current_year, current_month-1, 1), key="since_date")
   
    # Create filter controls for source and campaign selection in the second column
    with col2:
        until_date = st.date_input("Select an end date:", datetime.date(current_year, current_month, 1), key="until_date")
        
    with col11:
        selected_sources = st.multiselect('Select a source:', distinct_source, default=None, placeholder="All sources", key="source")
    
    with col12:
        selected_campaigns = st.multiselect('Select a campaign:', distinct_campaigns, default=None, placeholder="All campaigns", key="campaign")
    
    with col13:
        selected_domain = st.multiselect('Select a domain:', distinct_domain, default=None, placeholder="All campaigns", key="domain")

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

if len(st.session_state.domain) != 0:
    filtered_df = filtered_df[filtered_df['domain'].isin(st.session_state.domain)]

# Display statistics title and apply CSS style
st.markdown(title["statistic"], unsafe_allow_html=True)
st.markdown(css_style, unsafe_allow_html=True)

# Create columns for layout
col0 = st.columns(3)
col1, col2, col3 = st.columns(3)

# Define metrics and associated icons
# prepare data
total_clicks = filtered_df['Clicks'].sum()
total_impressions = filtered_df['impressions'].sum()
total_cpc = filtered_df[['costs_cpc']].sum()
total_cpa = filtered_df[['costs_conversion']].sum()
def format_data(data):
    if isinstance(data, np.float64):
        formatted_data = format_float(data)
    elif isinstance(data, pd.Series):
        formatted_data = format_series(data)
    else:
        formatted_data = format_float(data)
    return formatted_data

def format_float(value):
    if value.is_integer():
        return '{:,.0f}'.format(value).replace(',', ' ')
    else:
        formatted_value = '{:,.1f}'.format(value).replace(',', ' ')
        return formatted_value


def format_series(series):
    formatted_series = series.apply(format_float)
    return '\n'.join(formatted_series)

metrics = [
    ("Impressions:", total_impressions),
    ("Clicks:", total_clicks),
    ("Click-Through Rate:", (total_clicks/total_impressions)*100),
    ("Cost per Clicks:", total_cpc),
    ("Cost per Conversions:",total_cpa ),
    ("Average Cost per Click:", total_cpc/total_clicks),
]

my_dict = {
    "Clicks": "click.png",
    "Impressions": "impression.png",
    "AVG Cost": "money.png",
    "Cost per Click":"money.png",
    "Cost Conversion":"money.png",
    "AVG Cost per Click":"money.png"
}

# Iterate over the metrics and display icons and values
for i, metric in enumerate(metrics):
    column_index = i % 3
    metric_label, metric_value = metric
    number =  format_data(metric_value)
    col = col1 if column_index == 0 else col2 if column_index == 1 else col3
    
    # Retrieve the icon for the metric label
    for key in my_dict.keys():
        if key in metric_label:
            icon_path = my_dict[key]

    formated_number = number
    if('cost' in metric_label.lower()):
        formated_number = f'{number} €'
    if('rate' in metric_label.lower()):
        formated_number = f'{number} %'
    
    number_with_percent = f'{number} %' if 'rate:' in metric_label.lower() else number

    with col:
        # icon_image = os.path.abspath(f"/home/appuser/app/static/{icon_path}")
        icon_image = os.path.abspath(f"./app/static/{icon_path}")
        st.markdown(f'''
        <div style="margin: 10px auto; width: 70%">
            <div class="div-container" style="display:flex; margin:10px">
                <div class="div-icon" style="flex-basis:2">
                    <img class="icon-img"  src="data:image/png;base64,{base64.b64encode(open(icon_image, "rb").read()).decode()}">
                </div>
                <div style="flex-shrink:1; margin-left: 8%">
                    <h2 class="header">{metric_label}</h2>
                    <p class="text">{formated_number}</p>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Display charts title
st.markdown(title["charts"], unsafe_allow_html=True)

# Create tabs for visualizations and raw data
tab1, tab2, tab3 = st.tabs(["Visualizations per Sources","Visualizations per Campaigns", "Raw data"])
grouped = filtered_df.groupby(['campaign', 'Date']).agg({'Clicks': 'sum', 'impressions': 'sum'}).reset_index()
grouped['ctr'] = (grouped['Clicks'] / grouped['impressions']) * 100
campaings_df = grouped.copy()

grouped = filtered_df.groupby(['source', 'Date']).agg({'Clicks': 'sum', 'impressions': 'sum'}).reset_index()
grouped['ctr'] = (grouped['Clicks'] / grouped['impressions']) * 100
# Vytvoření nového DataFrame
sources_df = grouped.copy()
max_source = sources_df["ctr"].max()
max_campaign = campaings_df["ctr"].max()
with tab1:
    st.markdown(title["impressions"], unsafe_allow_html=True)
    fig = px.bar(sources_df, x="Date", y="impressions", color="source")
    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Impressions',
    )
    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    # Display title for the "Campaigns" section
    st.markdown(title["campaigns"], unsafe_allow_html=True)
    # Create a bar chart using Plotly Express for campaign clicks analysis

    fig = px.bar(sources_df, x="Date", y="Clicks", color="source")
    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Clicks',
    )
 

    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(title["clicktr"], unsafe_allow_html=True)
    fig = px.line(sources_df, x="Date", y="ctr", color="source")

    # Update layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Click-Through Rate %',
    )
    fig.update_yaxes(range = [0,max_source+5])

    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)

    # Display title for the "top 10 campaigns" section
    st.markdown(title["sourcesPerClick"], unsafe_allow_html=True)

    # Create columns for layout
    c10, c11, c1010, c12, c13 = st.columns((0.5, 2.5, 0.5, 2.5, 0.5))

    # Create a plot to display top 10 campaigns per clicks
    with c11:
        # Group the data by campaign and calculate the sum of clicks
        sources_clicks = filtered_df.groupby('source')['Clicks'].sum()

        # Get the top 10 campaigns with the highest sum of clicks
        top_10_sources = sources_clicks.nlargest(10).sort_values(ascending=True)

        # Create the horizontal bar plot using Plotly Express
        fig1 = go.Figure(go.Bar(
            x=top_10_sources.values,
            y=top_10_sources.index,
            orientation='h',
            marker_color='lightskyblue'
        ))

        # Customize the plot layout
        fig1.update_layout(
            title='Top 10 Sources by Clicks',
            xaxis_title='Clicks',
            yaxis_title='Sources',
            margin=dict(l=150),
        )

        # Display the plot
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)


    # Create a plot to display top 10 campaigns by impressions
    with c12:
        # Convert 'impressions' column to numeric
        filtered_df['impressions'] = pd.to_numeric(filtered_df['impressions'])

        # Group the data by campaign and calculate the sum of impressions
        source_impressions = filtered_df.groupby('source')['impressions'].sum()

        # Get the top 10 campaigns with the highest sum of impressions
        top_10_sources = source_impressions.nlargest(10).sort_values(ascending=True)

        # Create the horizontal bar plot using Plotly Graph Objects
        fig2 = go.Figure(go.Bar(
            x=top_10_sources.values,
            y=top_10_sources.index,
            orientation='h',
            marker_color='lightskyblue'
        ))

        # Customize the plot layout
        fig2.update_layout(
            title='Top 10 Sources by Impressions',
            xaxis_title='Impressions',
            yaxis_title='Sources',
            margin=dict(l=150),
        )

        # Display the plot
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

with tab2:
    st.markdown(title["impressions"], unsafe_allow_html=True)
    fig = px.bar(campaings_df, x="Date", y="impressions", color="campaign")
    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Impressions',
    )
       # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

     # Display title for the "Campaigns" section
    st.markdown(title["campaigns"], unsafe_allow_html=True)
    # Create a bar chart using Plotly Express for campaign clicks analysis

    fig = px.bar(campaings_df, x="Date", y="Clicks", color="campaign")
    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Clicks',
    )
 

    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(title["clicktr"], unsafe_allow_html=True)
    fig = px.line(campaings_df, x="Date", y="ctr", color="campaign")

    # Update layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Click-Through Rate %',
    )
    fig.update_yaxes(range = [0,max_campaign+5])

    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)

    # Display title for the "top 10 campaigns" section
    st.markdown(title["campaignsPerClick"], unsafe_allow_html=True)

    # Create columns for layout
    c10, c11, c1010, c12, c13 = st.columns((0.5, 2.5, 0.5, 2.5, 0.5))

    # Create a plot to display top 10 campaigns per clicks
    with c11:
        # Group the data by campaign and calculate the sum of clicks
        campaign_clicks = filtered_df.groupby('campaign')['Clicks'].sum()

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

with tab3:
    # Display raw data section
    st.markdown(title["rawData"], unsafe_allow_html=True)
    # Display the DataFrame with adjustable width
    st.dataframe(filtered_df, use_container_width=True)

# Display description title
st.markdown(title["description"], unsafe_allow_html=True)

# Display HTML code 
st.write(html_code, unsafe_allow_html=True)

# Display HTML footer
st.markdown(html_footer, unsafe_allow_html=True)

