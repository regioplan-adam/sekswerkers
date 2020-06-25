# RUN ALL SCRAPERS AND START CLEANING BEFORE UPLOADING INTO THE DATAWAREHOUSE
from spiders import topescortbabes
from spiders import kinky
from spiders import redlight
from spiders import sexguide
from spiders import sexjobs
import math
import numpy as np
import calendar
import pandas as pd
from time import strptime
import datetime
import re
from spiders.connections import gemeente
from spiders.connections import connections
from spiders.connections import odata
import dicts

###############################################################################################################
############################################ STEP 1 - START SCRAPERS ##########################################
###############################################################################################################

def runSpiders():
    a = topescortbabes.loadAdvertisements()
    b = kinky.loadAdvertisements()
    c = redlight.loadAdvertisements()
    d = sexguide.loadAdvertisements()
    e = sexjobs.loadAdvertisements()
    df = a.append(b).append(c).append(d).append(e)
    # set index
    df.index = range(len(df))
    
    return df

df = runSpiders()


###############################################################################################################
########################################## STEP 2 - CLEANING RESULTS ##########################################
###############################################################################################################
'''In deze sectie worden alle kolommen geschoond en waar nodig aangevuld met informatie uit de bulk data
waar er geen vaiabele gevonden wordt worden de kolommen met een standaard waarde gevuld
voor INTEGERS/FLOATS is dat 9999 en voor STRING variables is dat "null". Waar nodig wordt de data verrijkt 
met andere data bestanden. Tot slot wordt de data in het data warehouse opgeslagen'''


# #### Datum TODO!!!!!!!!!!!!!!!
# df['datum'] = df['datum'].str.replace('Aangemaakt: ([0-9]{2}-[0-9]{2}-20[0-9]{2})', '')
# # Datum omzetten


# maanden = {
#     '(januari':'01',
#     'februari':'02',
#     'maart':'03',
#     'april':'04',
#     'mei': '05',
#     'juni':'06',
#     'juli':'07',
#     'augustus':'08',
#     'september':'09',
#     'oktober':'10',
#     'november':'11',
#     'december':'12',}


# for x in df.index:
#     day = re.findall('([0-9]{1,2})',df['datum'][x])[0]
#     month = maanden[re.findall('([a-z]{3,12})',df['datum'][x])[0]]
#     currmont = dt.datetime.now().month
#     curryear = dt.datetime.now().year
#     year = str(curryear) if int(month) <= currmont else str(curryear - 1)
#     df['datum'][x] = day+'/'+str(month)+'/'+year



# # plaatsingsdatum omzetten naar datum format
# for x in df.index:
#     day = re.findall('([0-9]{2})',df['datum'][x])[0]
#     month = str(strptime(re.findall('([A-z]{3})',df['datum'][x])[0],'%b').tm_mon)
#     currmont = dt.datetime.now().month
#     curryear = dt.datetime.now().year
#     year = str(curryear) if int(month) <= currmont else str(curryear - 1)
#     df['datum'][x] = day+'/'+str(month)+'/'+year
# # TODO!!!!!!!!!!!!!!!

##### leeftijd
df['leeftijd'] = df['leeftijd'].str.extract('([0-9]{2})')

# for missing ages check the bulk tekst to find age
df['lft'] = df['algemene_info_bulk'].str.extract(\
    r'([0-9]{2} year|[0-9]{2}jr|[0-9]{2}j|[0-9]{2} ja[a-z]{2,4}|meid van [0-9]{2})')
df['lft'] = df['lft'].str.extract('([0-9]{2,4})')
df['leeftijd'] = np.where(df['leeftijd'].isnull(), df['lft'],df['leeftijd'])
df.drop(columns=['lft'],inplace=True)

# fill empty values
df['leeftijd'].fillna(9999, inplace=True)


##### gender
df['gender'] = df['gender'].str.extract(r'(\w+)')
df['gender'] = df['gender'].str.lower()


#### woonplaats
df = gemeente.getGmCodes(df)


#### type ontvangst 
for row in df.index:
    pattern = r'(prive-ontvangst|escort|thuisontvangst|Prive-ontvangst|Escort|Thuisontvangst|Massage|massage)'
    string = df['algemene_info_bulk'][row] + df['type_ontvangst'][row]
        # zoeken naar type ontvangst
    results = re.findall(pattern,string)
        # eerste letters omzetten naar hoohfdletter
    results = [r[0].upper()+r[1:] for r in results]    
        # namen aanpassen voor generieke waardes
    results = [re.sub(r'Prive-ontvangst', 'Thuisontvangst', r) for r in results]
        # Dubbele namen verwijderen
    results = list(dict.fromkeys(results))
        # aan dataframe toevoegen
    df['type_ontvangst'][row] = ' & '.join(results)


#### Afkomst
df['afkomst'] = df['afkomst'].str.replace('( ;.*| \(.*)','')
df['afkomst'] = df['afkomst'].str.strip()
for a in list(dicts.afkomst):
    df['afkomst'] = df['afkomst'].str.replace(a,dicts.afkomst[a])


#### Seksuele Voorkeur
df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.replace('( ;.*| \(.*)','')
df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.strip()
for g in list(dicts.geaardheid):
    df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.replace(g,dicts.geaardheid[g])


#### Prijzen TODO!!!!!!!!!!!!!!!

## TODO!!!!!!!!!!!!!!!

# #### kolommen opschonenen en lege waarden invullen om klaar te maken voor upload in het data warehouse TODO!!!!!!!!!!!!!!!
# for column in list(df.iloc[:,1:6]):
#     df[column] = df[column].str.strip()

# for column in list(df.iloc[:,6:13]):
#     df[column] = df[column].str.replace('[^A-Za-z0-9€]+', ' ')
#     df[column] = df[column].str.strip()

# for column in list(df):
#     try:
#         df[column] = df[column].str.replace("'", "`")
#     except:
#         print(column+' is not a string column')
## TODO!!!!!!!!!!!!!!!
