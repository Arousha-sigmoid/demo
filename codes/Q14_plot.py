import plotly.graph_objects as go

import pandas as pd


z = pd.read_csv('./data/kroger.csv')

d = z.copy()

line_chart = go.Scatter(
    x=d['month'],
    y=d['2023'],
    mode='lines+markers+text',  # Add text labels on the markers
    name='2023',
    line=dict(color='red', width=2),  # Hot pink line color
    marker=dict(color='red', size=5),  # Pink markers for the line
    text=d['2023_text'],  # Add text labels for the net Births won
    textposition='top center',  # Position the text above the markers
    textfont=dict(color='red', size=8),  # Text color for the line chart labels
    customdata=d['2023_text'],
    hovertemplate='Month: %{x}<br>Year: 2023<br>POS Sales: %{customdata}<extra></extra>')


# Create a line chart for Net Births Won on a rolling basis with labels
line_chart_2 = go.Scatter(
    x=d['month'],
    y=d['2024'],
    mode='lines+markers+text',  # Add text labels on the markers
    name='2024',
    line=dict(color='green', width=2),  # Hot pink line color
    marker=dict(color='green', size=5),  # Pink markers for the line
    text=d['2024_text'],  # Add text labels for the net Births won
    textposition='top center',  # Position the text above the markers
    textfont=dict(color='green', size=8),  # Text color for the line chart labels
    customdata=d['2024_text'],
    hovertemplate='Month: %{x}<br>Year: 2024<br>POS Sales: %{customdata}<extra></extra>')

fig = go.Figure(data=[line_chart, line_chart_2])

# Update layout with dual y-axes
fig.update_layout(
    title='YoY POS Sales Comparison - Kroger - 2023 and 2024',
    title_font=dict(size=18, color='hotpink'),
    yaxis_title='POS Sales',
    yaxis=dict(
        range=[0, 85000000],
        title='POS Sales',
        titlefont=dict(size=14, color='hotpink'),
        tickfont=dict(size=12, color='pink')
    ),
    plot_bgcolor='white',  # Set the background color to white
    template='plotly_white',  # Use a white template for a clean appearance
    xaxis=dict(
        ticks='inside',          # Display tick marks outside the plot
        tickwidth=2,              # Width of tick marks
        ticklen=10,                # Length of tick marks
        tickcolor = 'hotpink',
        tickangle=45,  # Rotate the x-axis labels for better readability
        tickmode='array',  # Use an array for x-tick values
        tickvals= d['month'],  # Explicitly define tick positions (all Quarters will be shown)
        #ticktext=df['Quarter']  # Display the actual Quarter names as ticks
        tickfont=dict(color='hotpink'),
        title='Month', 
        titlefont=dict(color='hotpink'),
    ),
    showlegend=True,
    legend=dict(
        x=1.1,  # Move the legend outside the plot area
        y=0.5,  # Position it at the top-right of the chart
        orientation='v',  # Arrange the legend items vertically
        title='Year',  # Set the legend title
        traceorder='reversed',  # Display legend items in the order of appearance
    )
)

# Show the plot
#fig.show()