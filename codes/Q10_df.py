import plotly.graph_objects as go
import pandas as pd
import json

data = pd.read_csv('./data/sales_brands_total.csv')
xx = data[['Brand', 'Total POS Sales']].copy()