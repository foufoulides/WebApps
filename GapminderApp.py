# To run the app, the the same directory/folder as the .py file: 
# Enter command: streamlit run "app-name.py"

import streamlit as st
import altair as alt 
import pandas as pd 
from vega_datasets import data

# INTRO AND SETUP

st.title("Gapminder Web App with Streamlit")

expander = st.expander(label="Intro to Gapminder")
# expander.header("Intro")

expander.write('''
* This demo is inspired by the **Trendalyzer** software developed by **Hans Rolzing**.
* His goal was to bring to  light many insights from datasets available from world 
organizations, such as the WHO and the UN, that showed how the world progressed in development
areas such as Life Expecancy, GDP Per Capita, andFertility Rate, etc. 
* The tool became famous in Hans Rolsing 2007 TED Talk: 
''')

expander.video("https://www.youtube.com/watch?v=hVimVzgtD6w&t=320s")

# READ THE DATA AND CACHE IT SO THAT IT DOESN'T LOAD EVERY TIME THE APP REFRESHES
@st.cache() # Decorator
def read_excel_data(workbook, worksheet): 
    return pd.read_excel(workbook, worksheet)

gapminder = read_excel_data("gapminder.xlsx", "gapminder" )

# The timple way of reading the data would be 
# gapminder = pd.read_excel("gapminder.xlsx", sheet_name="gapminder")

expander.write("**Here is a quick look at the Gapminder sample data we will use.**")
expander.dataframe(data=gapminder, width=800, height=200)

# DASHBOARD 

# Create a year slider that returns a the selected year as a variable that is in 
# turn used to filter our data frame.
year_slider = st.slider(label="Select Year", 
                        min_value=gapminder["Year"].min(), 
                        max_value=gapminder["Year"].max(), 
                        step=5)

gapminder_sel = gapminder[(gapminder["Year"]==year_slider) ]

# GDP PER CAPITA VS LIFE EXPECTANCY BUBBLE CHART (TRENDALIZER) 
st.header("GDP Per Capita vs Life Expectancy")

bubble_chart = alt.Chart(gapminder_sel).mark_point(filled=True, clip=True).encode(
    x=alt.X("GDPPC:Q", title="GDP Per Capita", scale=alt.Scale(domain=(0, 50000))),
    y=alt.Y("LifeExp:Q", scale=alt.Scale(domain=(0, 90)), title="Life Expectancy"), 
    color=alt.Color("Continent:N"),
    size="Population:Q",
    tooltip=[alt.Tooltip("Country:N"), 
            alt.Tooltip("Year:Q"), 
            alt.Tooltip("GDPPC:Q", title = "GDP Per Capita", format="$,.0f"), 
            alt.Tooltip("LifeExp:Q", title="Life Expectancy", format=".0f")]
).properties(width=780, height=300)

watermark = alt.Chart(gapminder_sel).mark_text(
    align='center', dx=0, dy=18, fontSize=64, fontWeight=200, color="lightgrey"
).encode(text="Year:Q")

bubble_graph = bubble_chart + watermark
bubble_graph

# LIFE EXPECTANCY SECTION AND GRAPHS 
st.header("Life Expectancy")

#BAR CHARTS 
LifeExpVal = alt.Chart(gapminder_sel).mark_bar().encode(
    alt.X("LifeExp:Q", bin=alt.Bin(extent=[25, 85], step=5), title="Life Expectancy"),
    alt.Y("count()", scale=alt.Scale(domain=(0, 40)), title="Count"),
    alt.Color("Continent:N")
).properties(width=300, height=225)

LifeExpPct = alt.Chart(gapminder_sel).transform_joinaggregate(
    Total ='count(*)'
).transform_calculate(
    Percent = "1 / datum.Total"
).mark_bar().encode(
    alt.X("LifeExp:Q", bin=alt.Bin(extent=[25, 85], step=5), title="Life Expectancy"),
    alt.Y("sum(Percent):Q", axis=alt.Axis(format='.0%'), scale=alt.Scale(domain=(0, 0.3)), title="Percent"),
    alt.Color("Continent:N")
).properties(width=300, height=225)

LifeExp = alt.hconcat(LifeExpVal, LifeExpPct)

LifeExp

# CHOLOPLETH MAP

# Set up background map for Chloropleth Wolrd Map
# Data source for world land area
countries = alt.topo_feature(data.world_110m.url, "countries")
# Background map to "attach" data to
background = alt.Chart(countries).mark_geoshape(fill="lightgrey", stroke="white").project(type="equirectangular").properties(width=800, height=350)

LifeExpMap = alt.Chart(countries).mark_geoshape(stroke="white").encode(
    color=alt.Color("LifeExp:Q", scale=alt.Scale(scheme='blues')), 
    tooltip=[alt.Tooltip("Country:N"), 
            alt.Tooltip("Year:Q"), 
            alt.Tooltip("LifeExp:Q", format=".0f", title="Life Expectancy")]
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(gapminder_sel, "ISOCode", ["Country", "Year", "LifeExp"])
).project(type="equirectangular").properties(width=500, height=350)

LifeMap = alt.layer(background, LifeExpMap)
LifeMap

# GROSS DOMESTIC PRODUCT SECTION AND GRAPHS

st.header("Gross Domestic Product")

# BAR CHARTS 
GDPPC = alt.Chart(gapminder_sel).mark_bar().encode(
    alt.X("GDPPC:Q", bin=alt.Bin(extent=[0, 60000], step=5000), title="GDP Per Capita"),
    alt.Y("count()", scale=alt.Scale(domain=(0, 120)), title="Count"),
    alt.Color("Continent:N")
).properties(width=300, height=225)

GDPPCPct = alt.Chart(gapminder_sel).transform_joinaggregate(
    Total ='count(*)'
).transform_calculate(
    Percent = "1 / datum.Total"
).mark_bar().encode(
    alt.X("GDPPC:Q", bin=alt.Bin(extent=[0, 60000], step=5000), title="GDP Per Capita"),
    alt.Y("sum(Percent):Q", axis=alt.Axis(format='.0%'), scale=alt.Scale(domain=(0, .85)), title="Percent"),
    alt.Color("Continent:N")
).properties(width=300, height=225)

GDP = alt.hconcat(GDPPC, GDPPCPct)
GDP

# CHLOROPLETH MAP
GDPPCMap = alt.Chart(countries).mark_geoshape(stroke="white").encode(
    color=alt.Color("GDPPC:Q", scale=alt.Scale(scheme='greens')), 
    tooltip=[alt.Tooltip("Country:N"), 
            alt.Tooltip("Year:Q"), 
            alt.Tooltip("GDPPC:Q", format="$,.0f", title="GDP Per Capita")]
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(gapminder, "ISOCode", ["Country", "Year", "GDPPC"])
).project(type="equirectangular").properties(width=750, height=350)

GDPMap = alt.layer(background, GDPPCMap)
GDPMap