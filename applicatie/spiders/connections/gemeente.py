from __app__.applicatie.spiders.connections import connections
from __app__.applicatie.spiders.connections  import odata
import numpy as np
import re
# gemeente codes en namen toevoegen
#advertenties zonder plaats verwijderen
def getGmCodes(df):
    output = df.copy()

    # laad alle plaatsen en gemeente via Odata van CBS
    gemeente = odata.odataToDataframe(odata.urls['geo'],'84734NED/UntypedDataSet')
    woonplaats = odata.odataToDataframe(odata.urls['geo'],'84734NED/Woonplaatsen',\
        select='Key,Title')
    plaatsen = woonplaats.merge(gemeente, 'left', left_on='Key', right_on='Woonplaatsen')
    plaatsen = plaatsen[[
        'Title',
        'Key',
        'Naam_2',
        'Code_3',
        'Naam_4',
        'Code_5',
        'Naam_6',
        'Code_7']]
    plaatsen.columns = ['woonplaats','wp_code','gemeente','gm_code','provincie','pv_code','landsdeel','ld_code']

    # klein beetje schoonmaken
    for column in plaatsen.columns:
        try:
            plaatsen[column] = plaatsen[column].str.strip()
        except:
            print(column+' is not a string column')

    # den bosch en den haag hernoemen
    # plaatsnamen bestanden
    plaatsen['woonplaats'] = plaatsen['woonplaats'].str.replace("'s-Gravenhage",'Den Haag')
    plaatsen['gemeente'] = plaatsen['gemeente'].str.replace("'s-Gravenhage",'Den Haag')
    plaatsen['woonplaats'] = plaatsen['woonplaats'].str.replace("'s-Hertogenbosch",'Den Bosch')
    plaatsen['gemeente'] = plaatsen['gemeente'].str.replace("'s-Hertogenbosch",'Den Bosch')

    # gespiderde bestand 
    output['locatie'] = output['locatie'].str.replace(r"('s-Gravenhage|`s-Gravenhage|The Hague)",'Den Haag')
    output['locatie'] = output['locatie'].str.replace(r"('s-Hertogenbosch|`s-Hertogenbosch)",'Den Bosch')

    # maak een zoekstring van alle plaats en gemeente namen
    wpl = '\\b|\\b'.join(list(plaatsen['woonplaats'].drop_duplicates()))
    wpl = re.sub(r'(\(|\))|\?|\/','',wpl)
    gm = '\\b|\\b'.join(list(plaatsen['gemeente'].drop_duplicates()))
    gm = re.sub(r'(\(|\))|\?|\/','',gm)
    searchstr = gm+'\\b|\\b'+wpl

    # zoek voor plaatsen in de locatie kolom van de gespiderede advertenties
    output['locatie'] = output['locatie'].str.extract('(\('+searchstr+'\))')
    output['locatie'].fillna('null',inplace=True)
    output.rename(columns={'locatie':'woonplaats'},inplace=True)

    # laad twee mogelijkheden voor merge
    check = output[['id','woonplaats']]
    for typ in ['gemeente','woonplaats']:
        temp_df = plaatsen[[typ, 'gm_code']].drop_duplicates()
        check = check.merge(temp_df, 'left', left_on='woonplaats', right_on=typ)

    # selecteer eerst op gemeente match dan woonplaats en als laats plaatsen en buurtschappen
    check['gm_code'] = np.where(~check['gm_code_x'].isnull(),check['gm_code_x'],
        np.where(~check['gm_code_y'].isnull(),check['gm_code_y'],'GM9999'))

    # selecteer gm_code
    check = check[['id','gm_code']].drop_duplicates()

    # verwijder resultaten die niet in nederland zijn
    output = output.merge(check,'left')

    return output

