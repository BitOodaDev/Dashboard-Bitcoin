import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
def load_env():
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(dotenv_path)

# Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

# Add border and background to plots
def add_border(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,30,1)",  # Set a distinct background color for the plot area
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        showlegend=True
    )
    return fig

# Load data
@st.cache_data
def load_data():
    conn = get_snowflake_connection()
    query = "SELECT * FROM btc_daily ORDER BY TIMESTAMP"
    df = pd.read_sql(query, conn)
    df['t'] = pd.to_datetime(df['TIMESTAMP'])
    conn.close()
    return df

# Plot comparison chart
def plot_comparison_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)].copy()
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    df_to_plot = df_filtered.melt(id_vars=['t'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(df_to_plot, x="t", y="Hash Rate", color='Rate Type', markers=True,
                  color_discrete_map={'Target Hash Rate': 'blue', 'HASH_RATE_MEAN': 'red'})

    fig.update_traces(line=dict(width=2), marker=dict(size=8), opacity=0.8)  # Reduced line width
    fig.update_traces(selector=dict(name='Target Hash Rate'), line=dict(width=3), marker=dict(size=10, symbol='circle'))
    fig.update_traces(selector=dict(name='HASH_RATE_MEAN'), opacity=0.5)
    fig = add_border(fig)
    fig.update_layout(
        height=535,
        width=700,  # Adjusted width
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

# Plot interactive chart
def plot_interactive_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)].copy()
    numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    selected_column = st.selectbox("Select a column to display", numeric_columns)

    fig = px.line(df_filtered, x="t", y=selected_column, markers=True)
    fig.update_traces(line=dict(width=3), marker=dict(size=6), opacity=0.8)
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=500,  # Adjusted width
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

# Main function
def main():
    load_env()
    st.set_page_config(page_title="Bitcoin Dashboard", page_icon=":bar_chart:", layout="wide")
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .plot-container {
        padding: 10px;
        margin: 0;
        border-radius: 10px;
        height: 500px;
    }
    .separator {
        margin: 20px 0;
    }
    .title-box {
        background-color: #111111;
        color: white;
        border: 1px solid white;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        font-size: 24px;
        margin-bottom: 10px;
    }
    .boundary {
        border: 2px solid white;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Bitcoin Dashboard")
    st.markdown("_Prototype v0.0.1_")
    
    df = load_data()
    
    col1, col2 = st.columns([2, 1])  # Allocate more width to the first column
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
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Create two columns for the charts and their headings
        col1, col2 = st.columns([3, 2])  # Adjusted proportions
        
        # Adding containers for the plots with outer border and headings
        with col1:
            st.markdown('<div class="title-box">Hash Rate Comparison</div>', unsafe_allow_html=True)
            fig1 = plot_comparison_chart(df_filtered, start_datetime, end_datetime)
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        with col2:
            st.markdown('<div class="title-box">Price Analysis</div>', unsafe_allow_html=True)
            fig2 = plot_interactive_chart(df_filtered, start_datetime, end_datetime)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Display the dataframe below the charts
        with st.container():
            st.markdown('<div class="title-box">Data Table</div>', unsafe_allow_html=True)
            if selected_columns:
                st.dataframe(df_filtered[selected_columns], column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")})
            else:
                st.warning("Please select at least one column to display.")

if __name__ == "__main__":
    main()
