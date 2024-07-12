import streamlit as st
from data import load_env
from layout import render_dashboard

def main():
    load_env()
    st.set_page_config(page_title="Bitcoin Dashboard", page_icon=":bar_chart:", layout="wide")
    render_dashboard()

if __name__ == "__main__":
    main()
