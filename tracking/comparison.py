import streamlit as st
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

def main():
    st.set_page_config(page_title="FPL Predictor Dashboard", layout="wide")
    st.title("FPL Team Predictor — Weekly Performance")

    log_path = os.path.join(DATA_DIR, 'weekly_comparison_2026-27.csv')

    try:
        data = pd.read_csv(log_path)
    except FileNotFoundError:
        st.error(f"Couldn't find {log_path}. Log at least one gameweek first.")
        return

    if data.empty:
        st.warning("No gameweeks logged yet.")
        return

    st.subheader("Score comparison across the season")
    chart_data = data.set_index('gw')[
        ['my_best11_points', 'p_1', 'fpl_average', 'highest_score_may_include_chips']
    ]
    chart_data.columns = ['Predicted (best 11)', 'My actual squad', 'FPL average', 'Highest score (may include chips)']
    st.line_chart(chart_data)

    st.subheader("Season summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg predicted best-11", f"{data['my_best11_points'].mean():.1f}")
    col2.metric("Avg actual squad", f"{data['p_1'].mean():.1f}")
    col3.metric("Avg FPL average", f"{data['fpl_average'].mean():.1f}")
    col4.metric("GWs beating FPL average", f"{(data['p_1'] > data['fpl_average']).sum()} / {len(data)}")

    st.subheader("Raw data")
    st.dataframe(data, use_container_width=True)

if __name__ == '__main__':
    main()