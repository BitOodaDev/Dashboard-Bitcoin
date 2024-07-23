import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def add_border(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        showlegend=True
    )
    return fig

def add_pointer_text(fig, x, y, text):
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=10, color='yellow', symbol='star', line=dict(width=2, color='black')),
            hoverinfo='skip',
            showlegend=False
        )
    )
    fig.add_annotation(
        x=x,
        y=y,
        text=text,
        showarrow=False,
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=10, color="black"),
        xshift=10,
        yshift=10
    )

def add_stats_box(fig, df, column_name):
    stats = df[column_name].agg(['mean', 'max', 'min'])
    stats_text = (f"Mean: {stats['mean']:.3f}<br>"
                  f"Max: {stats['max']:.3f}<br>"
                  f"Min: {stats['min']:.3f}")
    
    fig.add_annotation(
        x=0.00,
        y=0.99,
        xref="paper",
        yref="paper",
        text=stats_text,
        showarrow=False,
        font=dict(size=11, color="black"),  # Increased font size and changed color to black
        align="left",
        bgcolor="rgba(255, 255, 255, 0.9)",  # Increased opacity for better contrast
        bordercolor="black",
        borderwidth=1,
        width=90,  # Increased width of the box
        height=50   # Increased height of the box
    )
    return fig

def plot_comparison_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    df_filtered.rename(columns={'HASH_RATE_MEAN': 'Observed Hash Rate'}, inplace=True)
    
    df_to_plot = df_filtered.melt(id_vars=['Time'], value_vars=['Target Hash Rate', 'Observed Hash Rate'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(df_to_plot, x="Time", y="Hash Rate", color='Rate Type', markers=True,
                  color_discrete_map={'Target Hash Rate': 'blue', 'Observed Hash Rate': 'red'})

    fig.update_traces(line=dict(width=2), marker=dict(size=6), opacity=0.8)
    fig.update_traces(selector=dict(name='Target Hash Rate'), line=dict(width=3), marker=dict(size=7, symbol='circle'))
    fig.update_traces(selector=dict(name='Observed Hash Rate'), opacity=0.5)
    
    for rate_type in ['Target Hash Rate', 'Observed Hash Rate']:
        latest_data = df_to_plot[df_to_plot['Rate Type'] == rate_type].iloc[-1]
        add_pointer_text(fig, latest_data['Time'], latest_data['Hash Rate'], f"Latest Value<br>{latest_data['Hash Rate']:.2e}")
    
    #fig = add_stats_box(fig, df_to_plot, 'Hash Rate')
    
    fig.update_layout(
        height=450,
        width=700,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            tickangle=0,
            tickformat='%b %d\n%Y',
        ),
        yaxis=dict(title="Hash Rate"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    fig = add_border(fig)
    return fig

def plot_interactive_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    fig = px.line(df_filtered, x="Time", y="PRICE_USD_CLOSE", markers=True, 
                  labels={"PRICE_USD_CLOSE": "Price (USD)"})
    fig.update_traces(
        line=dict(width=3), 
        marker=dict(size=6), 
        opacity=0.8,
        hovertemplate='Time=%{x}<br>Price (USD)=%{y:.2f}<extra></extra>'
    )

    latest_data = df_filtered.iloc[-1]
    add_pointer_text(fig, latest_data['Time'], latest_data['PRICE_USD_CLOSE'], f"Latest Value<br>${latest_data['PRICE_USD_CLOSE']:.2f}")
    
    fig = add_stats_box(fig, df_filtered, 'PRICE_USD_CLOSE')
    
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=500,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Price (USD)"
    )
    return fig

def plot_daily_btc_ex_fees(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    fig = px.line(df_filtered, x="Time", y="VOLUME_MINED_SUM", title="", markers=True,
                  labels={"VOLUME_MINED_SUM": "Volume Mined Sum"})
    fig.update_traces(
        line=dict(width=2, color='coral'),
        marker=dict(size=5, color='coral'),
        opacity=0.8,
        hovertemplate='Time=%{x}<br>Volume Mined Sum=%{y:.2f}<extra></extra>'
    )
    
    latest_data = df_filtered.iloc[-1]
    add_pointer_text(fig, latest_data['Time'], latest_data['VOLUME_MINED_SUM'], f"Latest Value<br>{latest_data['VOLUME_MINED_SUM']:.2f}")
    
    fig = add_stats_box(fig, df_filtered, 'VOLUME_MINED_SUM')
    
    fig = add_border(fig)
    fig.update_layout(
        height=500,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Volume Mined Sum"
    )
    return fig

def plot_daily_spot_hash(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    
    df_filtered['SPOT_HASH_PRICE'] = ((df_filtered['VOLUME_MINED_SUM'] * df_filtered['REVENUE_FROM_FEES'] / (1 - df_filtered['REVENUE_FROM_FEES'])+ df_filtered['VOLUME_MINED_SUM'])\
                                       * df_filtered['PRICE_USD_CLOSE'] * (10**15)) / df_filtered['HASH_RATE_MEAN']

    fig = px.line(df_filtered, x="Time", y="SPOT_HASH_PRICE", title="", markers=True,
                  labels={"SPOT_HASH_PRICE": "Spot Hash Price"})
    fig.update_traces(
        line=dict(width=2, color='Goldenrod'),
        marker=dict(size=5, color='Goldenrod'),
        opacity=0.8,
        hovertemplate='Time=%{x}<br>Spot Hash Price=%{y:.2f}<extra></extra>'
    )

    latest_data = df_filtered.iloc[-1]
    add_pointer_text(fig, latest_data['Time'], latest_data['SPOT_HASH_PRICE'], f"Latest Value<br>{latest_data['SPOT_HASH_PRICE']:.2f}")
    
    fig = add_stats_box(fig, df_filtered, 'SPOT_HASH_PRICE')
    
    fig = add_border(fig)
    fig.update_layout(
        height=500,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Spot Hash Price"
    )
    return fig

def plot_difficulty_growth_rate(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    df_filtered = df_filtered.sort_values('Time')
    
    df_filtered['DIFFICULTY_GROWTH_RATE'] = df_filtered['DIFFICULTY_LATEST'].pct_change(periods=14) * 100
    df_difficulty_change = df_filtered[df_filtered.index % 14 == 0].dropna(subset=['DIFFICULTY_GROWTH_RATE'])
    
    fig = make_subplots(rows=1, cols=1)
    
    fig.add_trace(
        go.Scatter(
            x=df_difficulty_change['Time'], 
            y=df_difficulty_change['DIFFICULTY_GROWTH_RATE'],
            mode='lines+markers', 
            line=dict(color='Teal', width=2),
            marker=dict(size=8, color='Teal'), 
            opacity=0.8,
            hovertemplate=(
                '<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                '<b>Growth Rate</b>: %{y:.2f}%<br>' +
                '<b>Difficulty</b>: %{customdata:,.0f}<extra></extra>'
            ),
            customdata=df_difficulty_change['DIFFICULTY_LATEST'],
            showlegend=False
        )
    )

    latest_data = df_difficulty_change.iloc[-1]
    add_pointer_text(fig, latest_data['Time'], latest_data['DIFFICULTY_GROWTH_RATE'], f"Latest Value<br>{latest_data['DIFFICULTY_GROWTH_RATE']:.2f}%")
    
    #fig = add_stats_box(fig, df_difficulty_change, 'DIFFICULTY_GROWTH_RATE')
    
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=600,
        yaxis_title="Growth Rate (%)",
        xaxis_title="Time",
        font=dict(color='white'),
    )
    
    return fig

def plot_daily_btc_fees(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    fig = px.line(df_filtered, x="Time", y="REVENUE_FROM_FEES", title="", markers=True,
                  labels={"REVENUE_FROM_FEES": "Fees (%)"})
    fig.update_traces(
        line=dict(width=2, color='orange'),
        marker=dict(size=5, color='orange'),
        opacity=0.8,
        hovertemplate='Time=%{x}<br>Fees (%)=%{y:.4f}<extra></extra>'
    )

    latest_data_point = df_filtered.iloc[-1]
    latest_time = latest_data_point['Time']
    latest_value = latest_data_point['REVENUE_FROM_FEES']
    add_pointer_text(fig, latest_time, latest_value, f"Latest Value<br>{latest_value:.4f}%")

    fig = add_stats_box(fig, df_filtered, 'REVENUE_FROM_FEES')

    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Fees (%)"
    )
    return fig