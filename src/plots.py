import pandas as pd
import plotly.express as px

def add_border(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(50, 50, 50, 0.5)",  # Set a translucent grey background for the entire paper
        plot_bgcolor="rgba(30,30,30,0.8)",  # Set a translucent grey background for the plot area
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        yaxis=dict(showgrid=True, gridcolor='gray', zeroline=True, showline=True, linewidth=2, linecolor='white', mirror=True),
        showlegend=True
    )
    return fig

def plot_comparison_chart(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)].copy()
    df_filtered['Target Hash Rate'] = df_filtered['DIFFICULTY_LATEST'] * 144 / (60 * 60 * 24)
    
    df_to_plot = df_filtered.melt(id_vars=['t'], value_vars=['Target Hash Rate', 'HASH_RATE_MEAN'],
                                  var_name='Rate Type', value_name='Hash Rate')

    fig = px.line(df_to_plot, x="t", y="Hash Rate", color='Rate Type', markers=True,
                  color_discrete_map={'Target Hash Rate': 'blue', 'HASH_RATE_MEAN': 'red'})

    fig.update_traces(line=dict(width=2), marker=dict(size=8), opacity=0.8)
    fig.update_traces(selector=dict(name='Target Hash Rate'), line=dict(width=3), marker=dict(size=10, symbol='circle'))
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
    df_filtered = df[(df['t'] >= start_date) & (df['t'] <= end_date)].copy()

    fig = px.line(df_filtered, x="t", y=selected_column, markers=True)
    fig.update_traces(line=dict(width=3), marker=dict(size=6), opacity=0.8)
    fig = add_border(fig)
    fig.update_layout(
        height=450,
        width=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig
