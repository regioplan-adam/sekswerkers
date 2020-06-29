from spiders.connections import connections
import pandas as pd
import numpy as np

df = connections.readDb('SELECT TOP 100 * FROM sekswerkersScraperBulk')

df['corona'] = df['algemene_info_bulk'].str.extract(r'(.{1,100}corona.{1,100}|.{1,100}Corona.{1,100})')
df['meldingen'] = np.where(df['corona'].isnull(),0,1)
df['corona'].fillna('null', inplace=True)
df.to_csv('output/corona.csv', sep=';', index=False)
