import streamlit as st
import pandas as pd
from plots import plot_comparison_chart, plot_interactive_chart, plot_daily_btc_fees, plot_daily_btc_ex_fees, plot_difficulty_growth_rate, plot_daily_spot_hash
from data import load_data
import numpy as np

def load_css():
    with open('./style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_title():
    st.markdown("<h1 style='text-align: center;'>Bitcoin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>_Prototype v1.0.0_</p>", unsafe_allow_html=True)

def get_date_inputs():
    st.markdown('<div class="date-input-container">', unsafe_allow_html=True)
    start_date = st.date_input("Start date", pd.to_datetime('2024-05-01'))
    end_date = st.date_input("End date", pd.to_datetime('2024-12-01'))
    st.markdown('</div>', unsafe_allow_html=True)
    return start_date, end_date

def filter_data_by_date(df, start_date, end_date):
    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return pd.DataFrame()
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    return df[(df['Time'] >= start_datetime) & (df['Time'] <= end_datetime)]
    

def render_charts(df_filtered, start_datetime, end_datetime):
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="title-box">Hash Rate Comparison</div>', unsafe_allow_html=True)
        fig1 = plot_comparison_chart(df_filtered, start_datetime, end_datetime)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.markdown('<div class="title-box">BTC Price</div>', unsafe_allow_html=True)
        fig2 = plot_interactive_chart(df_filtered, start_datetime, end_datetime)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})


def render_data_table(df_filtered):
    st.markdown("<h3 style='text-align: center;'>Data Table</h3>", unsafe_allow_html=True)
    col_select = st.container()
    with col_select:
        all_columns = df_filtered.columns.tolist()
        selected_columns = st.multiselect("Select columns", all_columns, default=["PRICE_USD_CLOSE", "HASH_RATE_MEAN", "Time", "DIFFICULTY_LATEST"])

    # Convert hash rate to petahashes (PH)
    if "HASH_RATE_MEAN" in df_filtered.columns:
        df_filtered["HASH_RATE_MEAN_PH"] = df_filtered["HASH_RATE_MEAN"] / 10**15

    # Convert difficulty to terahashes (TH)
    if "DIFFICULTY_LATEST" in df_filtered.columns:
        df_filtered["DIFFICULTY_LATEST_TH"] = df_filtered["DIFFICULTY_LATEST"] / 10**12

    st.markdown('<div class="title-box">Data Table</div>', unsafe_allow_html=True)
    if selected_columns:
        # Replace HASH_RATE_MEAN with HASH_RATE_MEAN_PH and DIFFICULTY_LATEST with DIFFICULTY_LATEST_TH in the selected columns
        selected_columns = ["HASH_RATE_MEAN_PH" if col == "HASH_RATE_MEAN" else col for col in selected_columns]
        selected_columns = ["DIFFICULTY_LATEST_TH" if col == "DIFFICULTY_LATEST" else col for col in selected_columns]
        st.dataframe(df_filtered[selected_columns].style.set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center')]},
             {'selector': 'td', 'props': [('text-align', 'center')]}]
        ), use_container_width=True, hide_index=True)
    else:
        st.warning("Please select at least one column to display.")


def render_dashboard():
    load_css()
    render_title()

    df = load_data()
    start_date, end_date = get_date_inputs()

    df_filtered = filter_data_by_date(df, start_date, end_date)
    if not df_filtered.empty:
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        render_charts(df_filtered, start_date, end_date)
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        col3, col4 = st.columns([1, 1])
        with col3:
            st.markdown('<div class="title-box">BTC ex Fees</div>', unsafe_allow_html=True)
            fig4 = plot_daily_btc_ex_fees(df_filtered, start_date, end_date)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        with col4:
            st.markdown('<div class="title-box">Spot Hash Price</div>', unsafe_allow_html=True)
            fig6 = plot_daily_spot_hash(df_filtered, start_date, end_date)
            st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

        
        col1, col2 = st.columns([1, 1])
        with col2:
            st.markdown('<div class="title-box">BTC Fees %</div>', unsafe_allow_html=True)
            fig3 = plot_daily_btc_fees(df_filtered, start_date, end_date)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        with col1:
            st.markdown('<div class="title-box">Difficulty Growth Rate</div>', unsafe_allow_html=True)
            fig5 = plot_difficulty_growth_rate(df_filtered, start_date, end_date)
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

        # col3, col4 = st.columns([1, 1])
        # with col3:
        
        

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        render_data_table(df_filtered)

    html_code = """
    <script>
    document.addEventListener("DOMContentLoaded", function(event) { 
        console.log("Full app JavaScript - injected and running");
        setTimeout(function() {
            console.log("Full app JavaScript - refreshing page");
            location.reload();
        }, 60000); // Refresh every 6 minutes 
    });
    </script>
    """
    st.components.v1.html(html_code)

if __name__ == "__main__":
    render_dashboard()
