import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

st.markdown(
    "<h1 style='text-align: center; font-size: 36px;'>📊 Sample SuperStore EDA</h1>",
    unsafe_allow_html=True
)


fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    df = pd.read_csv("superstore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))

try:
    df["Order Date"] = pd.to_datetime(df["Order Date"])
except Exception as e:
    st.error(f"Error in parsing Order Date column: {e}")

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
df2 = df if not region else df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
df3 = df2 if not state else df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())
filtered_df = df3 if not city else df3[df3["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_sales.style.background_gradient(cmap="Oranges"))
        csv = region_sales.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

filtered_df["month_year"] = filtered_df["Order Date"].dt.strftime("%Y-%b")

st.subheader('Time Series Analysis')
linechart = filtered_df.groupby("month_year")["Sales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sub-Category")
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head()
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", title="Sales vs. Profit Scatter Plot")
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
