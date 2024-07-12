import streamlit as st
import pandas as pd
from plots import plot_comparison_chart, plot_interactive_chart
from data import load_data
import numpy as np

def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_dashboard():
    load_css()

    # Center align the main title
    st.markdown("<h1 style='text-align: center;'>Bitcoin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>_Prototype v0.0.1_</p>", unsafe_allow_html=True)

    df = load_data()

    # Create a single column for the date inputs, stacked on top of each other
    col_date = st.container()
    with col_date:
        start_date = st.date_input("Start date", pd.to_datetime('2024-01-01'))
        end_date = st.date_input("End date", pd.to_datetime('2024-12-31'))

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
    else:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        df_filtered = df[(df['t'] >= start_datetime) & (df['t'] <= end_datetime)]

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown('<div class="title-box">Hash Rate Comparison</div>', unsafe_allow_html=True)
            fig1 = plot_comparison_chart(df_filtered, start_datetime, end_datetime)
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        with col2:
            st.markdown('<div class="title-box">Price Analysis</div>', unsafe_allow_html=True)
            numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
            numeric_columns = [col for col in numeric_columns if col != 'TIMESTAMP']  # Exclude TIMESTAMP
            selected_column = st.selectbox("Select a column to display", numeric_columns)  # Use numeric_columns here
            fig2 = plot_interactive_chart(df_filtered, start_datetime, end_datetime, selected_column)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        # Move the multiselect column selection below the charts
        st.markdown("<h3 style='text-align: center;'>Data Table</h3>", unsafe_allow_html=True)
        col_select = st.container()
        with col_select:
            all_columns = df_filtered.columns.tolist()
            selected_columns = st.multiselect("Select columns", all_columns, default=["PRICE_USD_CLOSE", "HASH_RATE_MEAN"])

        # Display the dataframe below the charts and centered
        with st.container():
            st.markdown('<div class="title-box">Data Table</div>', unsafe_allow_html=True)
            if selected_columns:
                st.dataframe(df_filtered[selected_columns].style.set_table_styles(
                    [{'selector': 'th', 'props': [('text-align', 'center')]},
                     {'selector': 'td', 'props': [('text-align', 'center')]}]
                ), column_config={"TIMESTAMP": st.column_config.DatetimeColumn(format="YYYY-MM-DD")})
            else:
                st.warning("Please select at least one column to display.")
