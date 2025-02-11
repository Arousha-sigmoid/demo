import plotly.graph_objects as go
import pandas as pd

data = pd.read_excel('./data/win_loss_data.xlsx')
data = data.drop_duplicates(subset=['Hospital', 'Contract Status', 'Month Won or Lost'])[:-3]
z = data.groupby(['Month Won or Lost', 'Contract Status'], as_index=False)['Hospital'].count()
zz = pd.pivot_table(z, index='Month Won or Lost', columns='Contract Status', values='Hospital', aggfunc='sum').reset_index().rename_axis(None, axis=1)
zz['Month Won or Lost'] = zz['Month Won or Lost'].apply(lambda x: str(x)[:7])
zz = zz.fillna(0)
zz.columns = ['Month', 'Hospitals_Lost', 'Hospitals_Won']
zz['Net_Hospitals_Won'] = (zz['Hospitals_Won'] - zz['Hospitals_Lost']).cumsum()

df = zz.copy()

# Create a stacked bar chart for hospitals won and lost with labels
stacked_bar = go.Bar(
    x=df['Month'],
    y=df['Hospitals_Won'],
    name='Hospitals Won',
    marker=dict(color='pink'),  # Pink color for "Won"
    text=df['Hospitals_Won'],  # Add text labels for the won hospitals
    textposition='auto',  # Position the text inside the bars
    textfont=dict(color='black', size=8),  # Text color for labels inside the bars
    insidetextanchor='start',  # Ensure the text is aligned to the bottom of the bar
    offsetgroup=1 
)

stacked_bar_lost = go.Bar(
    x=df['Month'],
    y=df['Hospitals_Lost'],
    name='Hospitals Lost',
    marker=dict(color='lightgrey'),  # Red color for "Lost"
    text=df['Hospitals_Lost'],  # Add text labels for the lost hospitals
    textposition='inside',  # Position the text inside the bars
    textfont=dict(color='black', size=8),  # Text color for labels inside the bars
    insidetextanchor='end',  # Ensure the text is aligned to the bottom of the bar
    offsetgroup=0
)

# Create a line chart for Net Hospitals Won on a rolling basis with labels
line_chart = go.Scatter(
    x=df['Month'],
    y=df['Net_Hospitals_Won'],
    mode='lines+markers+text',  # Add text labels on the markers
    name='Net Hospitals Won (Rolling)',
    line=dict(color='hotpink', width=2),  # Hot pink line color
    marker=dict(color='hotpink', size=8),  # Pink markers for the line
    text=df['Net_Hospitals_Won'],  # Add text labels for the net hospitals won
    textposition='top center',  # Position the text above the markers
    textfont=dict(color='hotpink', size=9)  # Text color for the line chart labels
)

# Create the figure and add the bar and line charts
fig = go.Figure(data=[stacked_bar, stacked_bar_lost, line_chart])

# Update layout with dual y-axes
fig.update_layout(
    title='Hospitals Won and Lost with Net Hospitals Won (Rolling)',
    title_font=dict(size=18, color='hotpink'),
    yaxis_title='Count of Hospitals (Won/Lost)',
    yaxis=dict(
        title='Count of Hospitals (Won/Lost)',
        titlefont=dict(size=14, color='hotpink'),
        tickfont=dict(size=12, color='pink')
    ),
    # Define second y-axis for the net hospitals won line chart
    yaxis2=dict(
        title='Net Hospitals Won (Rolling)',
        titlefont=dict(size=14, color='hotpink'),
        tickfont=dict(size=12, color='pink'),
        overlaying='y',  # Overlays the second axis on the same plot
        side='right',  # Place the second axis on the right
        showgrid=False  # Optionally hide the grid on the right axis
    ),
    barmode='stack',  # Stack the bars for "Won" and "Lost"
    plot_bgcolor='white',  # Set the background color to white
    template='plotly_white',  # Use a white template for a clean appearance
    legend_title="Hospital Data",
    xaxis=dict(
        tickangle=45,  # Rotate the x-axis labels for better readability
        tickmode='array',  # Use an array for x-tick values
        #tickvals=df['Month'],  # Explicitly define tick positions (all months will be shown)
        #ticktext=df['Month']  # Display the actual month names as ticks
        tickfont=dict(color='hotpink'),
        title='Month', 
        titlefont=dict(color='hotpink'),
    ),
    showlegend=True,
    legend=dict(
        x=1.05,  # Move the legend outside the plot area
        y=1.2,  # Position it at the top-right of the chart
        orientation='v',  # Arrange the legend items vertically
        title='',  # Set the legend title
        traceorder='normal'  # Display legend items in the order of appearance
    )
)

# Add the secondary y-axis to the line chart (using yaxis2)
fig.update_traces(
    selector=dict(name="Net Hospitals Won (Rolling)"),
    yaxis="y2"  # Assign the line chart to the second y-axis
)

# Show the plot
#fig.show()
