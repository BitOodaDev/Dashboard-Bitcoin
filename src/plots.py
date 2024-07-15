import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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

def plot_comparison_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    df_to_plot = df_filtered.melt(id_vars=['Time'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(df_to_plot, x="Time", y="Hash Rate", color='Rate Type', markers=True,
                  color_discrete_map={'Target Hash Rate': 'blue', 'HASH_RATE_MEAN': 'red'})

    fig.update_traces(line=dict(width=2), marker=dict(size=6), opacity=0.8)
    fig.update_traces(selector=dict(name='Target Hash Rate'), line=dict(width=3), marker=dict(size=7, symbol='circle'))
    fig.update_traces(selector=dict(name='HASH_RATE_MEAN'), opacity=0.5)
    fig = add_border(fig)
    fig.update_layout(
        height=535,
        width=700,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

def plot_interactive_chart(df, start_date, end_date, selected_column):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    fig = px.line(df_filtered, x="Time", y=selected_column, markers=True)
    fig.update_traces(line=dict(width=3), marker=dict(size=6), opacity=0.8)
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

def plot_daily_btc_fees(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    fig = px.line(df_filtered, x="Time", y="REVENUE_FROM_FEES", title="", markers=True)
    fig.update_traces(line=dict(width=2, color = 'orange'), marker=dict(size=5, color = 'orange'), opacity=0.8)
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

def plot_daily_btc_ex_fees(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()

    # Calculate Daily BTC Ex Fees
    df_filtered['DAILY_BTC_EX_FEES'] = df_filtered['VOLUME_MINED_SUM'] * df_filtered['REVENUE_FROM_FEES'] / (1 - df_filtered['REVENUE_FROM_FEES']) + df_filtered['VOLUME_MINED_SUM']

    fig = px.line(df_filtered, x="Time", y="DAILY_BTC_EX_FEES", title="", markers=True)
    fig.update_traces(line=dict(width=2, color='yellow'), marker=dict(size=5, color='yellow'), opacity=0.8)
    fig = add_border(fig)
    fig.update_layout(
        height=500,
        width=600,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig


# def plot_difficulty_growth_rate(df, start_date, end_date):
#     # Convert dates to datetime
#     start_date = pd.to_datetime(start_date)
#     end_date = pd.to_datetime(end_date)
    
#     # Filter the dataframe based on date range
#     df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
    
#     # Sort the dataframe by time to ensure chronological order
#     df_filtered = df_filtered.sort_values('Time')
    
#     # Calculate difficulty growth rate for every 14 days
#     df_filtered['DIFFICULTY_GROWTH_RATE'] = df_filtered['DIFFICULTY_LATEST'].pct_change(periods=14) * 100
    
#     # Filter out only the points where difficulty changes (every 14 days)
#     df_difficulty_change = df_filtered[df_filtered.index % 14 == 0].dropna(subset=['DIFFICULTY_GROWTH_RATE'])
    
#     # Create the plot
#     fig = px.line(df_difficulty_change, x="Time", y="DIFFICULTY_GROWTH_RATE", 
#                   title="Difficulty Growth Rate (14-day intervals)", markers=True)
    
#     # Update trace properties
#     fig.update_traces(line=dict(width=2, color='yellow'), marker=dict(size=8, color='yellow'), opacity=0.8)
    
#     # Add border (assuming add_border function is defined elsewhere)
#     fig = add_border(fig)
    
#     # Update layout
#     fig.update_layout(
#         height=300,
#         width=600,
#         margin=dict(l=10, r=10, t=30, b=10),
#         xaxis=dict(dtick="D14"),  # Set x-axis tick to every 14 days
#         yaxis_title="Growth Rate (%)",
#         xaxis_title="Date"
#     )
    
#     return fig

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
            line=dict(color='lavender', width=2),
            marker=dict(size=8, color='lavender'), 
            opacity=0.8,
            hovertemplate=(
                '<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                '<b>Growth Rate</b>: %{y:.2f}%<br>' +
                '<b>Difficulty</b>: %{customdata:,.0f}<extra></extra>'
            ),
            customdata=df_difficulty_change['DIFFICULTY_LATEST']
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Difficulty Growth Rate",
        height=450,
        width=600,
        margin=dict(l=5, r=5, t=30, b=5),
        yaxis_title="Growth Rate (%)",
        xaxis_title="Date",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode="x unified"
    )
    
    # Update x-axis
    fig.update_xaxes(
        tickformat="%b %Y",
        tickangle=45,
        tickmode='auto',
        nticks=10,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        zeroline=False,
    )
    
    # Update y-axis
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        zeroline=False,
    )
    
    # Add border
    fig.update_layout(
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="white", width=2),
            )
        ]
    )
    
    return fig
# def plot_difficulty_growth_rate(df, start_date, end_date):
#     start_date = pd.to_datetime(start_date)
#     end_date = pd.to_datetime(end_date)
#     df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)].copy()
#     df_filtered['Difficulty Growth Rate'] = df_filtered['DIFFICULTY_LATEST'].pct_change() * 100  # Calculate difficulty growth rate

#     # Identify difficulty change points based on block height being a multiple of 2016
#     df_filtered = df_filtered[df_filtered['BLOCK_HEIGHT'] % 2016 == 0]

#     fig = px.line(df_filtered, x="Time", y="Difficulty Growth Rate", markers=True)
#     fig.update_traces(line=dict(width=3), marker=dict(size=6), opacity=0.8)
#     fig = add_border(fig)
#     fig.update_layout(
#         height=450,
#         width=700,
#         margin=dict(l=10, r=10, t=10, b=10)
#     )
#     return fig