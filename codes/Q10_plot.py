import plotly.graph_objects as go

import pandas as pd


z = pd.read_csv('./data/sales_brands_monthly.csv')

def format_with_m(value):
    if value >=1000000000:
        return f"${round(value / 1000000000, 2)}B"  # Format value as B, with one decimal place
    elif value >= 1000000:
        return f"${round(value / 1000000, 2)}M"  # Format value as M, with one decimal place
    elif value>=1000:
        return f"${round(value / 1000, 2)}K"  # Format value as K, with one decimal place
    else:
        return f"${round(value, 2)}"
    
months = z['date']
brand_1_sales = z['ENFAMIL']
brand_1_text = z['ENFAMIL'].apply(format_with_m)
brand_2_sales = z['ENFAMIL WIC']
brand_2_text = z['ENFAMIL WIC'].apply(format_with_m)
brand_3_sales = z['NUTRAMIGEN / ALLERGY']
brand_3_text = z['NUTRAMIGEN / ALLERGY'].apply(format_with_m)
brand_4_sales = z['ENFAGROW']
brand_4_text = z['ENFAGROW'].apply(format_with_m)
brand_5_sales = z['NUTRAMIGEN']
brand_5_text = z['NUTRAMIGEN'].apply(format_with_m)

# Create scatter plots
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=months, y=brand_1_sales, customdata=brand_1_text, mode='lines+markers', name='Enfamil', marker=dict(color='red'),
    hovertemplate='<b>Enfamil</b><br>Month: %{x}<br>Sales: %{customdata}<extra></extra>'  # Customize hover text
))
              
fig.add_trace(go.Scatter(
    x=months, y=brand_2_sales, customdata=brand_2_text, mode='lines+markers', name='Enfamil WIC', marker=dict(color='hotpink'),
    hovertemplate='<b>Enfamil WIC</b><br>Month: %{x}<br>Sales: %{customdata}<extra></extra>'
))
fig.add_trace(go.Scatter(
    x=months, y=brand_3_sales, customdata=brand_3_text, mode='lines+markers', name='Nutramigen / Allergy', marker=dict(color='magenta'),
    hovertemplate='<b>Nutramigen / Allergy</b><br>Month: %{x}<br>Sales: %{customdata}<extra></extra>'
))
fig.add_trace(go.Scatter(
    x=months, y=brand_4_sales, customdata=brand_4_text, mode='lines+markers', name='Enfagrow', marker=dict(color='lightpink'),
    hovertemplate='<b>Enfagrow</b><br>Month: %{x}<br>Sales: %{customdata}<extra></extra>'
))
fig.add_trace(go.Scatter(
    x=months, y=brand_5_sales, customdata=brand_5_text, mode='lines+markers', name='Nutramigen', marker=dict(color='purple'),
    hovertemplate='<b>Nutramigen</b><br>Month: %{x}<br>Sales: %{customdata}<extra></extra>'
))

# Add title and labels
fig.update_layout(
    title='Monthly Sales of Top 5 Brands',
    title_font=dict(size=18, color='hotpink'),
    yaxis= dict(title='POS Sales', titlefont = dict(color='black'), tickfont=dict(color='black')),
    showlegend=True,
    xaxis=dict(
        tickangle=45,  # Rotate the x-axis labels for better readability
        tickmode='array',  # Use an array for x-tick values
        tickfont=dict(color='black'),
        title='Month', 
        titlefont=dict(color='black'),
    ),
    template='plotly_white'
)

# Show the plot
#fig.show()
