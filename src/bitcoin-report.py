import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import snowflake.connector
from dotenv import load_dotenv
import os

def load_env():
    """
    Load environment variables from a .env file
    """
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(dotenv_path)

def get_snowflake_connection():
    """
    Set up and return a Snowflake connection using environment variables
    """
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

def add_border(fig):
    """
    Add a border to a Plotly figure
    """
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
    """
    Load data from Snowflake and preprocess it
    """
    conn = get_snowflake_connection()

    query = """
    SELECT * FROM btc_daily
    ORDER BY TIMESTAMP
    """

    df = pd.read_sql(query, conn)
    df['t'] = pd.to_datetime(df['TIMESTAMP'])
    conn.close()
    return df

def plot_interactive_chart(df, start_date, end_date):
    """
    Plot an interactive chart using Plotly and Streamlit
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)]
    numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    selected_column = st.selectbox("Select a column to display", numeric_columns)

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

def plot_bottom_left(df, start_date, end_date):
    """
    Plot bottom left chart comparing Target Hash Rate and Observed Rate
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)]
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    df_to_plot = df_filtered.melt(id_vars=['t'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(
        df_to_plot,
        x="t",
        y="Hash Rate",
        color='Rate Type',
        title="Comparison of Target Hash Rate and Observed Rate Over Time",
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

def plot_bottom_right(df):
    """
    Plot bottom right chart for 2024 data
    """
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

def main():
    """
    Main function to run the Streamlit app
    """
    load_env()
    st.set_page_config(page_title="Bitcoin Dashboard", page_icon=":bar_chart:", layout="wide")
    st.title("Bitcoin Dashboard")
    st.markdown("_Prototype v0.0.1_")
    
    df = load_data()
    
    with st.expander("Data Preview"):
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect("Select columns to display", all_columns, default=["TIMESTAMP", "PRICE_USD_CLOSE", "HASH_RATE_MEAN"])
        if selected_columns:
            st.dataframe(df[selected_columns], column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")})
        else:
            st.warning("Please select at least one column to display.")
    
    top_left_column, top_right_column = st.columns((2, 1))
    bottom_left_column, bottom_right_column = st.columns(2)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", pd.to_datetime('2024-01-01'))
    with col2:
        end_date = st.date_input("End date", pd.to_datetime('2024-12-31'))
    
    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
    else:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        df_filtered = df[(df['t'] >= start_datetime) & (df['t'] <= end_datetime)]
        
        col_select, col_expander = st.columns([1, 3])
        with col_select:
            all_columns = df_filtered.columns.tolist()
            selected_columns = st.multiselect("Select columns", all_columns, default=["TIMESTAMP", "PRICE_USD_CLOSE", "HASH_RATE_MEAN"])
        
        with col_expander:
            with st.expander("Data Preview", expanded=True):
                if selected_columns:
                    st.dataframe(df_filtered[selected_columns], column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")})
                else:
                    st.warning("Please select at least one column to display.")
        
        plot_bottom_left(df_filtered, start_datetime, end_datetime)
        
        with st.expander("Interactive Chart", expanded=True):
            plot_interactive_chart(df_filtered, start_datetime, end_datetime)

if __name__ == "__main__":
    main()
