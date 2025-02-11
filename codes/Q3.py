import plotly.graph_objects as go
import pandas as pd

data = pd.read_excel('./data/win_loss_data.xlsx')
data = data.drop_duplicates(subset=['Hospital', 'Contract Status', 'Month Won or Lost'])[:-3]
df = data.copy()
df['Quarter'] = df['Month Won or Lost'].apply(lambda x: ((x.month-1)//3) + 1)
df['Quarter_New'] = df.apply(lambda row: str(row['Month Won or Lost'].year) + '-' + 'Q' + str(row['Quarter']).split('.')[0], axis=1)
z = df.groupby(['Quarter_New', 'Contract Status'], as_index=False)['Total Births'].sum()
zz = pd.pivot_table(z, index='Quarter_New', columns='Contract Status', values='Total Births', aggfunc='sum').reset_index().rename_axis(None, axis=1)
zz = zz.fillna(0)
zz.columns = ['Quarter', 'Births_Lost', 'Births_Won']

# Calculate Net Hospitals Won (Cumulative Sum for Rolling Basis)
zz['Net_Births_Won'] = (zz['Births_Won'] - zz['Births_Lost']).cumsum()

df = zz.copy()

def format_with_k(value):
    if value >= 1000:
        return f"{value / 1000:.1f}K"  # Format value as K, with one decimal place
    else:
        return str(value)

# Apply the formatting function to the "Hospitals_Won" and "Hospitals_Lost" columns
df['Births_Won_Text'] = df['Births_Won'].apply(format_with_k)
df['Births_Lost_Text'] = df['Births_Lost'].apply(format_with_k)
df['Net_Births_Won_Text'] = df['Net_Births_Won'].apply(format_with_k)

# Create a stacked bar chart for Births won and lost with labels
stacked_bar = go.Bar(
    x=df['Quarter'],
    y=df['Births_Won'],
    name='Births Won',
    marker=dict(color='pink'),  # Pink color for "Won"
    text=df['Births_Won_Text'],  # Add text labels for the won Births
    textposition='auto',  # Position the text inside the bars
    textfont=dict(color='black', size=10),  # Text color for labels inside the bars
    insidetextanchor='start',  # Ensure the text is aligned to the bottom of the bar
    offsetgroup=1 
)

stacked_bar_lost = go.Bar(
    x=df['Quarter'],
    y=df['Births_Lost'],
    name='Births Lost',
    marker=dict(color='lightgrey'),  # Red color for "Lost"
    text=df['Births_Lost_Text'],  # Add text labels for the lost Births
    textposition='inside',  # Position the text inside the bars
    textfont=dict(color='black', size=10),  # Text color for labels inside the bars
    insidetextanchor='end',  # Ensure the text is aligned to the bottom of the bar
    offsetgroup=0
)

# Create a line chart for Net Births Won on a rolling basis with labels
line_chart = go.Scatter(
    x=df['Quarter'],
    y=df['Net_Births_Won'],
    mode='lines+markers+text',  # Add text labels on the markers
    name='Net Births Won',
    line=dict(color='hotpink', width=2),  # Hot pink line color
    marker=dict(color='hotpink', size=8),  # Pink markers for the line
    text=df['Net_Births_Won_Text'],  # Add text labels for the net Births won
    textposition='top center',  # Position the text above the markers
    textfont=dict(color='hotpink', size=10)  # Text color for the line chart labels
)

# Create the figure and add the bar and line charts
fig = go.Figure(data=[stacked_bar, stacked_bar_lost, line_chart])

# Update layout with dual y-axes
fig.update_layout(
    title='Net Births Won (Rolling)',
    title_font=dict(size=18, color='hotpink'),
    yaxis_title='Count of Births (Won/Lost)',
    yaxis=dict(
        title='Count of Births (Won/Lost)',
        titlefont=dict(size=14, color='hotpink'),
        tickfont=dict(size=12, color='pink')
    ),
    # Define second y-axis for the net Births won line chart
    yaxis2=dict(
        title='Net Births Won (Rolling)',
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
        #tickvals=df['Quarter'],  # Explicitly define tick positions (all Quarters will be shown)
        #ticktext=df['Quarter']  # Display the actual Quarter names as ticks
        tickfont=dict(color='hotpink'),
        title='Quarter', 
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
    selector=dict(name="Net Births Won"),
    yaxis="y2"  # Assign the line chart to the second y-axis
)

# Show the plot
#fig.show()
