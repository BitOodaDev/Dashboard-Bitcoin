import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def add_border(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        # paper_bgcolor="rgba(50, 50, 50, 0.5)",  # Set a translucent grey background for the entire paper
        # plot_bgcolor="rgba(30,30,30,0.8)",  # Set a translucent grey background for the plot area
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        showlegend=True
    )
    return fig



# def add_border(fig):
#     # Detect the current theme
#     theme = st.get_current_style()
    
#     # Debugging to verify the detected theme
#     st.write(f"Detected theme: {theme}")
    
#     # Set the layout based on the detected theme
#     if theme == "dark":
#         fig.update_layout(
#             margin=dict(l=10, r=10, t=10, b=10),
#             font=dict(color="white"),
#             paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
#             plot_bgcolor="rgba(30,30,30,1)",  # Dark grey plot area
#             xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
#             yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
#             showlegend=True,
#             legend=dict(
#                 bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='white')
#             )
#         )
#     elif theme == "light":
#         fig.update_layout(
#             margin=dict(l=10, r=10, t=10, b=10),
#             font=dict(color="black"),
#             paper_bgcolor="rgba(255, 255, 255, 1)", 
#             plot_bgcolor="rgba(240,240,240,1)",  # Light grey plot area
#             xaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             yaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             showlegend=True,
#             legend=dict(
#                 bgcolor='rgba(255,255,255,0)',
#                 font=dict(color='black')
#             )
#         )
#     else:
#         st.write("Unknown theme detected. Using default light theme settings.")
#         fig.update_layout(
#             margin=dict(l=10, r=10, t=10, b=10),
#             font=dict(color="black"),
#             paper_bgcolor="rgba(255, 255, 255, 1)", 
#             plot_bgcolor="rgba(240,240,240,1)",  # Light grey plot area
#             xaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             yaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             showlegend=True,
#             legend=dict(
#                 bgcolor='rgba(255,255,255,0)',
#                 font=dict(color='black')
#             )
#         )
#     return fig
# def add_border(fig):
#     theme = get_theme()
#     if theme == "Dark":
#         fig.update_layout(
#             margin=dict(l=10, r=10, t=10, b=10),
#             # paper_bgcolor="rgba(50, 50, 50, 0.5)",  # Set a translucent grey background for the entire paper
#             # plot_bgcolor="rgba(30,30,30,0.8)",  # Set a translucent grey background for the plot area
#             font=dict(color="white"),
#             xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
#             yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
#             showlegend=True
#     )

#     else:
#         fig.update_layout(
#             margin=dict(l=10, r=10, t=10, b=10),
#             paper_bgcolor="rgba(255, 255, 255, 1)",  # White background for the entire paper
#             plot_bgcolor="rgba(240, 240, 240, 1)",  # Light grey background for the plot area
#             font=dict(color="black"),
#             xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='black', mirror=True),
#             showlegend=True
#         )
#     return fig


def plot_comparison_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    # Rename HASH_RATE_MEAN to Observed Hash Rate
    df_filtered.rename(columns={'HASH_RATE_MEAN': 'Observed Hash Rate'}, inplace=True)
    
    df_to_plot = df_filtered.melt(id_vars=['Time'], value_vars=['Target Hash Rate', 'Observed Hash Rate'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(df_to_plot, x="Time", y="Hash Rate", color='Rate Type', markers=True,
                  color_discrete_map={'Target Hash Rate': 'blue', 'Observed Hash Rate': 'red'})

    fig.update_traces(line=dict(width=2), marker=dict(size=6), opacity=0.8)
    fig.update_traces(selector=dict(name='Target Hash Rate'), line=dict(width=3), marker=dict(size=7, symbol='circle'))
    fig.update_traces(selector=dict(name='Observed Hash Rate'), opacity=0.5)
    
    # Update hover template for both traces separately
    fig.for_each_trace(
        lambda trace: trace.update(
            hovertemplate=f'Rate Type={trace.name}<br>Time=%{{x}}<br>Hash Rate=%{{y:.2e}}'
        )
    )
    
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=700,
        margin=dict(l=10, r=10, t=10, b=10)
    )
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
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=500,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Price (USD)"
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
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Fees (%)"
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
    fig = add_border(fig)
    fig.update_layout(
        height=500,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Volume Mined Sum"
    )
    return fig


 
def plot_difficulty_growth_rate(df, start_date, end_date):
    # Convert dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter the dataframe based on date range
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    
    # Sort the dataframe by time to ensure chronological order
    df_filtered = df_filtered.sort_values('Time')
    
    # Calculate difficulty growth rate for every 14 days
    df_filtered['DIFFICULTY_GROWTH_RATE'] = df_filtered['DIFFICULTY_LATEST'].pct_change(periods=14) * 100
    
    # Filter out only the points where difficulty changes (every 14 days)
    df_difficulty_change = df_filtered[df_filtered.index % 14 == 0].dropna(subset=['DIFFICULTY_GROWTH_RATE'])
    
    # Create the plot
    fig = make_subplots(rows=1, cols=1)
    
    # Add trace for growth rate with difficulty value in hover
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
            showlegend= False
        )
    )
    
    fig = add_border(fig)
    # Update layout
    fig.update_layout(
        height=450,
        width=600,
        yaxis_title="Growth Rate (%)",
        xaxis_title="Time",
        font=dict(color='white'),
    )
    

    
    return fig
