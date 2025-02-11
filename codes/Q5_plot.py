import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

data = pd.read_excel('./data/win_loss_data.xlsx')
data = data.drop_duplicates(subset=['Hospital', 'Contract Status', 'Month Won or Lost'])[:-3]


x = data.groupby(['State', 'Contract Status'], as_index=False)['Hospital'].count()
xx = pd.pivot_table(x, index='State', columns='Contract Status', values='Hospital', aggfunc='sum').reset_index().rename_axis(None, axis=1)
xx = xx.fillna(0).copy()
xx.columns = ['State', 'Hospitals Lost', 'Hospitals Won']
xx['Net Hospitals Won'] = xx['Hospitals Won'] - xx['Hospitals Lost']

# Convert the data into a DataFrame
df = xx.copy()
# Create the choropleth map
fig = px.choropleth(df,
                    locations='State',  # Column with state names
                    locationmode='USA-states',  # Use USA state codes for mapping
                    color='Net Hospitals Won',  # Color the states by the net hospitals won
                    title="Net Hospitals Won by State",
                    hover_name='Net Hospitals Won', 
                    color_continuous_scale=['red', 'white', 'green'],  # Customize the color scale
                    range_color=[-15, 15], 
                    labels={'Net Hospitals Won': 'Net Hospitals Won'},  # Label for the color scale
                    scope="usa"  # Focus on the United States
                    )

fig.add_scattergeo(
    locations=df['State'],
    locationmode="USA-states", 
    text = df["State"].astype(str) + ": " + [x.split('.')[0] for x in df["Net Hospitals Won"].astype(str)],
    mode='text',
)

fig.update_layout(
    font=dict(
        size=9,  # Set the font size here
        color="black"
    )
)
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

# Show the plot
#fig.show()
