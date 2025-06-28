import streamlit as st
import altair as alt
from vega_datasets import data
import pandas as pd
import numpy as np

st.title("Nashville Airbnb Exploration")
df = pd.read_csv("listings.csv")

df_subset = df
df_subset['price'] = df_subset['price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
df_subset['price'] = df_subset['price'].astype(float)
df_subset['numeric_dist'] = [int(i.split(' ')[-1]) for i in df_subset.neighbourhood_cleansed]

click = alt.selection_point(fields=['room_type'])
conditional = alt.when(click).then(alt.value(1.0)).otherwise(alt.value(0.4))

measure_options = {"Rental Type": "room_type",
                   "Superhost": "host_is_superhost"}
selected_measure = st.selectbox(
    "Select Measure:", list(measure_options.keys()))



pie_chart1 = alt.Chart(df_subset).transform_aggregate(
    count='count()', groupby=[measure_options[selected_measure]]
).mark_arc().encode(
    theta=alt.Theta(field='count', type='quantitative'),
    color=alt.Color(field=measure_options[selected_measure]).scale(scheme="blues"),
    tooltip=[measure_options[selected_measure]]
)

bar_chart = alt.Chart(df_subset).transform_aggregate(
  avg_size = "mean(['accommodates'])",
  groupby=["room_type"]
).transform_window(
    rank="rank(avg_size)",
    sort=[alt.SortField("room_type", order="ascending")]
).mark_bar().encode(
    y=alt.Y('room_type:N', title="Rental Type"),
    x=alt.X('avg_size:Q', title="Avg Size of Accommodation"),
    color=alt.condition(click, alt.Color(field='room_type').scale(scheme="blues"), alt.value('lightgray')) 
).add_params(
    click  # Add interactive selection to the chart
)

stacked_chart = alt.Chart(df_subset).mark_bar().encode(
    x='room_type',
    y='count(room_type)',
    color='host_is_superhost',
    tooltip="count(room_type)"
).transform_filter(
    click  
)


both = alt.vconcat(pie_chart1, bar_chart, stacked_chart
                   ).resolve_scale(
                       color='independent'
                   )

st.altair_chart(both, use_container_width=True)