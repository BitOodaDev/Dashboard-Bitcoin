import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import snowflake.connector
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

# Load the .env file
load_dotenv(dotenv_path)



# Set up Snowflake connection parameters
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")


#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Bitcoin Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Bitcoin Dashboard")
st.markdown("_Prototype v0.0.1_")

#######################################
# DATA LOADING
#######################################
def add_border(fig):
    fig.update_layout(
        shapes=[
            go.layout.Shape(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="black", width=2),
            )
        ]
    )
    return fig

@st.cache_data
def load_data():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    query = """
    SELECT * FROM btc_daily
    ORDER BY TIMESTAMP
    """

    df = pd.read_sql(query, conn)
    print(df.head())
    df['t'] = pd.to_datetime(df['TIMESTAMP'])
    conn.close()
    return df

df = load_data()
all_months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

with st.expander("Data Preview"):
    # Get all column names
    all_columns = df.columns.tolist()
    
    # Create a multi-select widget for column selection
    selected_columns = st.multiselect("Select columns to display", all_columns, default=["TIMESTAMP", "PRICE_USD_CLOSE", "HASH_RATE_MEAN"])
    
    # Display the selected columns
    if selected_columns:
        st.dataframe(
            df[selected_columns],
            column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")},
        )
    else:
        st.warning("Please select at least one column to display.")
def plot_interactive_chart(df, start_date, end_date):
    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter data based on the selected date range
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)]
    
    # Get numeric columns for selection
    numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    
    # Create a selectbox for column selection
    selected_column = st.selectbox("Select a column to display", numeric_columns)
    
    # Create the line chart
    fig = px.line(
        df_filtered,
        x="t",
        y=selected_column,
        title=f"{selected_column} Over Time",
        markers=True
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=6),
        opacity=0.8
    )

    fig = add_border(fig)  
    st.plotly_chart(fig, use_container_width=True)

#######################################
# VISUALIZATION METHODS
#######################################

# Keep your existing visualization methods (plot_metric, plot_gauge) as they are

def plot_bottom_left(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter data based on the selected date range
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)]
    
    # Calculate Target Hash Rate
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    # Prepare the DataFrame for plotting
    df_to_plot = df_filtered.melt(id_vars=['t'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                         var_name='Rate Type', value_name='Hash Rate')
    
    # Create a line plot using Plotly
    fig = px.line(
        df_to_plot,
        x="t",
        y="Hash Rate",
        color='Rate Type',
        title="Comparison of Target Hash Rate and Observed Rate Over Time",
        markers=True,
        color_discrete_map={'Target Hash Rate': 'blue', 'HASH_RATE_MEAN': 'red'}
    )
    
    # Update traces for better visibility
    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=8),
        opacity=0.8
    )
    
    fig.update_traces(
        selector=dict(name='Target Hash Rate'),
        line=dict(width=6),
        marker=dict(size=10, symbol='circle')
    )
    
    fig.update_traces(
        selector=dict(name='HASH_RATE_MEAN'),
        opacity=0.5
    )
    fig = add_border(fig)  
    st.plotly_chart(fig, use_container_width=True)

def plot_bottom_right():
    df_2024 = df[df['t'].dt.year == 2024]
    df_2024['HASH_RATE_MEAN'] = pd.to_numeric(df_2024['HASH_RATE_MEAN'], errors='coerce')
    df_2024['Target Hash Rate'] = df_2024['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    df_to_plot = df_2024.melt(id_vars=['t'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                         var_name='Rate Type', value_name='Hash Rate')
    
    fig = px.line(
        df_to_plot,
        x="t",
        y="Hash Rate",
        color='Rate Type',
        title="Comparison of Target Hash Rate and Observed Rate in 2024",
        markers=True,
        color_discrete_map={'Target Hash Rate': 'blue', 'HASH_RATE_MEAN': 'red'}
    )
    
    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=8),
        opacity=0.8
    )
    
    fig.update_traces(
        selector=dict(name='Target Hash Rate'),
        line=dict(width=6),
        marker=dict(size=10, symbol='circle')
    )
    
    fig.update_traces(
        selector=dict(name='HASH_RATE_MEAN'),
        opacity=0.5
    )
    fig = add_border(fig)  
    st.plotly_chart(fig, use_container_width=True)

#######################################
# STREAMLIT LAYOUT
#######################################

top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)


# Add date range input for filtering data
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", pd.to_datetime('2024-01-01'))
with col2:
    end_date = st.date_input("End date", pd.to_datetime('2024-12-31'))

if start_date > end_date:
    st.error("Error: End date must fall after start date.")
else:
    # Convert date to datetime for consistency
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    
    # Filter the dataframe based on the selected date range
    df_filtered = df[(df['t'] >= start_datetime) & (df['t'] <= end_datetime)]
    
    # Create two columns for side-by-side layout
    col_select, col_expander = st.columns([1, 3])
    
    with col_select:
        # Get all column names
        all_columns = df_filtered.columns.tolist()
        
        # Create a multi-select widget for column selection
        selected_columns = st.multiselect("Select columns", all_columns, default=["TIMESTAMP", "PRICE_USD_CLOSE", "HASH_RATE_MEAN"])
    
    with col_expander:
        with st.expander("Data Preview", expanded=True):
            # Display the selected columns
            if selected_columns:
                st.dataframe(
                    df_filtered[selected_columns],
                    column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")},
                )
            else:
                st.warning("Please select at least one column to display.")

    plot_bottom_left(start_datetime, end_datetime)

    # Add the new interactive chart
    with st.expander("Interactive Chart", expanded=True):
        plot_interactive_chart(df_filtered, start_datetime, end_datetime)
