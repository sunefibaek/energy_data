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

title = "Danish Energy Production at " + df['Minutes5DK'].iloc[0]

df['Non-Sustainable Sources'] = df['ProductionLt100MW'] + df['ProductionGe100MW']  
df_prep = df.drop(["ProductionGe100MW","ProductionLt100MW","PriceArea","Minutes5UTC", "ExchangeNetherlands","ExchangeNorway","ExchangeSweden","BornholmSE4","ExchangeGreatBelt","ExchangeGermany"], axis=1)
print(df_prep)

df = df_prep.sum(numeric_only=True).to_frame().T 
df['PriceArea'] = "All"
print(df)


df['WindPower'] = df['OffshoreWindPower'] + df['OnshoreWindPower']  

#df['Non-Sustainable Sources'] = df['ProductionLt100MW'] + df['ProductionGe100MW']    
    
df_wind_solar_prod = df[['PriceArea', 'WindPower', 'SolarPower', 'Non-Sustainable Sources']].melt(id_vars='PriceArea', value_vars=['WindPower', 'SolarPower', 'Non-Sustainable Sources'], var_name='target', value_name='value')    
df_wind_solar_prod['source'] = 'Total Production' 

df_wind_split = df[['PriceArea', 'OffshoreWindPower', 'OnshoreWindPower']].melt(id_vars='PriceArea', value_vars=['OffshoreWindPower', 'OnshoreWindPower'], var_name='target', value_name='value')  
df_wind_split['source'] = 'WindPower'  

#df_prod_split = df[['PriceArea', 'ProductionLt100MW', 'ProductionGe100MW']] #.melt(id_vars='PriceArea', value_vars=['ProductionLt100MW', 'ProductionGe100MW'], var_name='target', value_name='value')  
#df_prod_split['source'] = 'Non-Sustainable Sources'

df_sankey = pd.concat([df_wind_solar_prod, df_wind_split])[['source', 'target', 'value']]  
print(df_sankey)

# Define color for each label  
colors = ['lightblue', 'lightgreen', 'lightgreen', 'purple', 'lightblue', 'orange'] 
labels = list(df_sankey['source'].unique()) + list(df_sankey['target'].unique())  

fig = go.Figure(data=[go.Sankey(  
    node = dict(  
        pad = 15,  
        thickness = 20,  
        line = dict(color = "black", width = 0.5),  
        label = labels,  
        color = "darkgrey"  #colors
    ),  
    link = dict(  
        source = [labels.index(s) for s in df_sankey['source']],  
        target = [labels.index(t) for t in df_sankey['target']],  
        value = df_sankey['value'],  
        color = ['rgba(0, 0, 0, 0.4)' if s == 'Non-Sustainable Sources' else 'rgba(50, 150, 250, 0.6)' for s in df_sankey['target']]  # Specify color for each flow  
    )  
)])  
  
fig.update_layout(title_text=title, font_size=10)  
fig.show()  

# Write the plot to an HTML file  
pio.write_html(fig, 'sankey.html') 

