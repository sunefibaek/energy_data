import requests
import json   
import pandas as pd  
import plotly.io as pio
import plotly.graph_objects as go  

# your code to get data  
response = requests.get(url='https://api.energidataservice.dk/dataset/ElectricityProdex5MinRealtime?limit=2')  
result = response.json()  
  
# get the records part of the json  
records = result.get('records', [])  
  
# create a dataframe from the records  
df = pd.json_normalize(records) 
print(df)    

title = "Danish Energy Production at " + df['Minutes5DK'].iloc[0]

df['Non-Sustainable Sources'] = df['ProductionLt100MW'] + df['ProductionGe100MW']  
df_prep = df.drop(["ProductionGe100MW","ProductionLt100MW","PriceArea","Minutes5UTC", "ExchangeNetherlands","ExchangeNorway","ExchangeSweden","BornholmSE4","ExchangeGreatBelt","ExchangeGermany"], axis=1)
print(df_prep)

df = df_prep.sum(numeric_only=True).to_frame().T 
df['PriceArea'] = "All"
print(df)

df['WindPower'] = df['OffshoreWindPower'] + df['OnshoreWindPower']  
df['Sustainable Sources'] = df['OffshoreWindPower'] + df['OnshoreWindPower'] + df['SolarPower']  
print(df) 

df_sustanability = df[['PriceArea', 'Sustainable Sources', 'Non-Sustainable Sources']].melt(id_vars='PriceArea', value_vars=['Sustainable Sources', 'Non-Sustainable Sources'], var_name='target', value_name='value')    
df_sustanability['source'] = 'Total Production' 
print(df_sustanability)

df_sustain_split = df[['PriceArea', 'WindPower', 'SolarPower']].melt(id_vars='PriceArea', value_vars=['WindPower', 'SolarPower'], var_name='target', value_name='value')  
df_sustain_split['source'] = 'Sustainable Sources'  
print(df_sustain_split)

df_wind_split = df[['PriceArea', 'OffshoreWindPower', 'OnshoreWindPower']].melt(id_vars='PriceArea', value_vars=['OffshoreWindPower', 'OnshoreWindPower'], var_name='target', value_name='value')  
df_wind_split['source'] = 'WindPower'  
print(df_wind_split)

df_sankey = pd.concat([df_sustanability, df_sustain_split, df_wind_split])[['source', 'target', 'value']]
print(df_sankey)

df_sankey['source_target'] = df_sankey['source'] + df_sankey['target']
print(df_sankey)

labels = list(df_sankey['source'].unique()) + list(df_sankey['target'].unique())
labels = list(set(labels)) 
print(labels)

# Calculate color array 
color_array = [
    'rgba(0, 0, 0, 0.4)' if 'Non-Sustainable Sources' in s
    else 'rgba(46, 139, 87, 0.5)' if 'Total ProductionSustainable Sources' in s
    else 'rgba(255, 219, 88, 0.5)' if 'Sustainable SourcesSolarPower' in s
    else 'rgba(50, 150, 250, 0.6)'
    for s in df_sankey['source_target']
]

fig = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = labels,
        color = "darkgrey"
    ),
    link = dict(
        source = [labels.index(s) for s in df_sankey['source']],
        target = [labels.index(t) for t in df_sankey['target']],
        value = df_sankey['value'],
        color = color_array
    )
)])

fig.update_layout(title_text=title, font_size=10)
fig.show()

# Write the plot to an HTML file
pio.write_html(fig, 'index.html')