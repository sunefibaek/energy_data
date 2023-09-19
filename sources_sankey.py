import requests
#import json
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

response = requests.get(url='https://api.energidataservice.dk/dataset/ElectricityProdex5MinRealtime?limit=2')
result = response.json()

records = result.get('records', [])

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
print([labels.index(s) for s in df_sankey['source']])
print([labels[i] for i in [labels.index(s) for s in df_sankey['source']]])  

print([labels.index(s) for s in df_sankey['target']])
print([labels[i] for i in [labels.index(s) for s in df_sankey['target']]])  


color_array = [
    'rgba(0, 0, 0, 0.4)' if 'Non-Sustainable Sources' in s
    else 'rgba(46, 139, 87, 0.5)' if 'Total ProductionSustainable Sources' in s
    else 'rgba(255, 219, 88, 0.5)' if 'Sustainable SourcesSolarPower' in s
    else 'rgba(50, 150, 250, 0.6)'
    for s in df_sankey['source_target']
]

fig = go.Figure(data=[go.Sankey(  
    arrangement = "snap",  
    node = dict(  
        label=labels,    
        #x=[0.4, 0.1, 0.4, 0.4, 0.3, 0.2, 0.4],  # Same x-coordinate for 'SolarPower' and 'Non-Sustainable Sources'  
        x=[0.8, 0.2, 0.8, 0.8, 0.6, 0.4, 0.8],  # Same x-coordinate for 'SolarPower' and 'Non-Sustainable Sources'  
        y=[0.1, 0.4, 0.2, 0.3, 0.3, 0.4, 0.4],  # 'SolarPower' (index 3) has higher y-coordinate than 'Non-Sustainable Sources' (index 6)  
        pad=10    
    )  

,    
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