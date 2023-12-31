import requests
#import json
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

response = requests.get(url='https://api.energidataservice.dk/dataset/ElectricityProdex5MinRealtime?limit=2')
result = response.json()

records = result.get('records', [])

df = pd.json_normalize(records)

title = "Danish Energy Production at " + df['Minutes5DK'].iloc[0]

df['Non-Sustainable Sources'] = df['ProductionLt100MW'] + df['ProductionGe100MW']  
df_prep = df.drop(["ProductionGe100MW","ProductionLt100MW","PriceArea","Minutes5UTC", "ExchangeNetherlands","ExchangeNorway","ExchangeSweden","BornholmSE4","ExchangeGreatBelt","ExchangeGermany"], axis=1)

df = df_prep.sum(numeric_only=True).to_frame().T
df['PriceArea'] = "All"

df['WindPower'] = df['OffshoreWindPower'] + df['OnshoreWindPower']  
df['Sustainable Sources'] = df['OffshoreWindPower'] + df['OnshoreWindPower'] + df['SolarPower']  

df_sustanability = df[['PriceArea', 'Sustainable Sources', 'Non-Sustainable Sources']].melt(id_vars='PriceArea', value_vars=['Sustainable Sources', 'Non-Sustainable Sources'], var_name='target', value_name='value')
df_sustanability['source'] = 'Total Production'

df_sustain_split = df[['PriceArea', 'WindPower', 'SolarPower']].melt(id_vars='PriceArea', value_vars=['WindPower', 'SolarPower'], var_name='target', value_name='value')
df_sustain_split['source'] = 'Sustainable Sources'

df_wind_split = df[['PriceArea', 'OffshoreWindPower', 'OnshoreWindPower']].melt(id_vars='PriceArea', value_vars=['OffshoreWindPower', 'OnshoreWindPower'], var_name='target', value_name='value')
df_wind_split['source'] = 'WindPower'

df_sankey = pd.concat([df_sustanability, df_sustain_split, df_wind_split])[['source', 'target', 'value']]

df_sankey['source_target'] = df_sankey['source'] + df_sankey['target']

labels = list(df_sankey['source'].unique()) + list(df_sankey['target'].unique())
labels = list(set(labels))

color_array = [
    'rgba(0, 0, 0, 0.6)' if 'Non-Sustainable Sources' in s
    else 'rgba(46, 139, 87, 0.6)' if 'Total ProductionSustainable Sources' in s
    else 'rgba(255, 219, 88, 0.6)' if 'Sustainable SourcesSolarPower' in s
    else 'rgba(50, 150, 250, 0.6)'
    for s in df_sankey['source_target']
]

if (df_sankey.loc[df_sankey['target'] == 'SolarPower', 'value'] == 0).any():  
    x_axis = [0.8, 0.2, 0.8, 0.6, 0.4, 0.8]
    y_axis = [0.1, 0.4, 0.2, 0.3, 0.3, 0.4]
else:  
    x_axis = [0.8, 0.2, 0.8, 0.8, 0.6, 0.4, 0.8]
    y_axis = [0.1, 0.4, 0.2, 0.3, 0.3, 0.3, 0.4]

fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    
    node = dict(
        label=labels,
        x = x_axis, #x=[0.8, 0.2, 0.8, 0.8, 0.6, 0.4, 0.8],
        y = y_axis, #y=[0.1, 0.4, 0.2, 0.3, 0.3, 0.3, 0.4],
# Index Label                       X       Y
# 0     OffshoreWindPower         0.4     0.1
# 1     Total Production          0.1     0.4
# 2     OnshoreWindPower          0.4     0.2
# 3     SolarPower                0.4     0.3
# 4     WindPower                 0.3     0.4
# 5     Sustainable Sources       0.2     0.4
# 6     Non-Sustainable Sources   0.4     0.4        
        pad=10,
        color = 'lightgray'
    ),

    link = dict(  
        source = [labels.index(s) for s in df_sankey['source']],  
        target = [labels.index(t) for t in df_sankey['target']],  
        value = df_sankey['value'],  
        color = color_array  
    )  
)])  

fig.update_layout(title_text=title, font_size=14)
fig.show()

pio.write_html(fig, 'index.html')