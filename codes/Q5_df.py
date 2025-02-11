import pandas as pd
import json
data = pd.read_excel('./data/win_loss_data.xlsx')
data = data.drop_duplicates(subset=['Hospital', 'Contract Status', 'Month Won or Lost'])[:-3]
states = json.load(open("./data/states.json", 'rb'))
abb = dict(map(reversed, states.items()))

df = data.copy()
x = df.groupby(['State', 'Contract Status'], as_index=False)['Hospital'].count()
xx = pd.pivot_table(x, index='State', columns='Contract Status', values='Hospital', aggfunc='sum').reset_index().rename_axis(None, axis=1)
xx = xx.fillna(0).copy()
xx['State'] = xx['State'].map(abb)
xx = xx.dropna().reset_index(drop=True)
xx.columns = ['State', 'Hospitals Lost', 'Hospitals Won']
xx['Net Hospitals Won'] = xx['Hospitals Won'] - xx['Hospitals Lost']
xx = xx[['State', 'Hospitals Won', 'Hospitals Lost', 'Net Hospitals Won']]
xx = xx.sort_values('Hospitals Won', ascending=False).reset_index(drop=True)