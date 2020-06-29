# RUN ALL SCRAPERS AND START CLEANING BEFORE UPLOADING INTO THE DATAWAREHOUSE
from .spiders import topescortbabes
from .spiders import kinky
from .spiders import redlight
from .spiders import sexguide
from .spiders import sexjobs
import math
import numpy as np
import calendar
import pandas as pd
from time import strptime
import datetime
import re
from __app__.applicatie.spiders.connections import gemeente
from __app__.applicatie.spiders.connections  import connections
from __app__.applicatie.spiders.connections  import odata
from __app__.applicatie.spiders.connections  import outlook
from . import dicts
from termcolor import colored

###############################################################################################################
############################################ STEP 1 - START SCRAPERS ##########################################
###############################################################################################################
def main():
    def runSpiders():
        a = topescortbabes.loadAdvertisements()
        b = kinky.loadAdvertisements()
        c = redlight.loadAdvertisements()
        d = sexguide.loadAdvertisements()
        e = sexjobs.loadAdvertisements()
        df = a.append(b).append(c).append(d).append(e)
        # set index
        df.index = range(len(df))
        print(colored('Pages are loaded and ready to be uploaded in the datawarehouse at ' +str(datetime.datetime.now().hour)+':'+
            str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
            str(datetime.datetime.now().month),'green'))
        print(colored('--------------------------------------------------------------------------------------\n\n','green'))

        return df

    df = runSpiders()


    ###############################################################################################################
    ########################################## STEP 2 - CLEANING RESULTS ##########################################
    ###############################################################################################################
    '''In deze sectie worden alle kolommen geschoond en waar nodig aangevuld met informatie uit de bulk data
    waar er geen vaiabele gevonden wordt worden de kolommen met een standaard waarde gevuld
    voor INTEGERS/FLOATS is dat 9999 en voor STRING variables is dat "null". Waar nodig wordt de data verrijkt 
    met andere data bestanden. Tot slot wordt de data in het data warehouse opgeslagen'''


    #### Opschoon defenities 
    #### Datum
    def datumLaden(input_df):
        df = input_df.copy()
        datestr = '[0-9]{2,4}.[0-9]{2}.[0-9]{2,4}'
        df['aangemaakt'] = df['datum'].str.extract(\
            r'(Aangemaakt: '+datestr+'|since '+datestr+'|sinds\: [0-9]{2} [A-z]{2,8} [0-9]{4}|[0-9]{2} [A-Z]{1}[A-z]{1,8}|, [0-9]{2}.*? \-)')
        df['aangemaakt'] = df['aangemaakt'].str.extract(r'([0-9]{2,4}.*)')
        df['aangemaakt'] = df['aangemaakt'].str.replace(r'([^A-z0-9])',' ')
        df['aangemaakt'] = df['aangemaakt'].fillna('null')

        # omzetten naar juiste datum volgorde
        for row in df.index:
            if df['aangemaakt'][row] == 'null':
                df['aangemaakt'][row] = 'null'
            elif bool(re.search('[0-9]{4}', df['aangemaakt'][row][0:4])):
                dm = re.findall('\\b[0-9]{2}\\b',df['aangemaakt'][row])
                yy = re.findall('\\b[0-9]{4}\\b',df['aangemaakt'][row])
                df['aangemaakt'][row] = dm[1]+' '+dm[0]+' '+yy[0]
            elif bool(re.search('[A-z]{1}', df['aangemaakt'][row])):
                day = re.findall('([0-9]{1,2})',df['aangemaakt'][row])[0]
                month = dicts.maanden[re.findall('([A-z]{3,12})',df['aangemaakt'][row].lower())[0]]
                # find year 
                if bool(re.search('[0-9]{4}', df['aangemaakt'][row])):
                    year = re.findall('\\b[0-9]{4}\\b',df['aangemaakt'][row])[0]
                else:
                    currmont = datetime.datetime.now().month
                    curryear = datetime.datetime.now().year
                    year = str(curryear) if int(month) <= currmont else str(curryear - 1)
                df['aangemaakt'][row] = day+' '+str(month)+' '+year

        df['datum'] = df['aangemaakt'].str.replace(' ','/')

        return df

    ##### leeftijd
    def leeftijdLaden(input_df):
        df = input_df.copy()

        df['leeftijd'] = df['leeftijd'].str.extract('([0-9]{2})')

        # for missing ages check the bulk tekst to find age
        df['lft'] = df['algemene_info_bulk'].str.extract(\
            r'([0-9]{2} year|[0-9]{2}jr|[0-9]{2}j|[0-9]{2} ja[a-z]{2,4}|meid van [0-9]{2})')
        df['lft'] = df['lft'].str.extract('([0-9]{2,4})')
        df['leeftijd'] = np.where(df['leeftijd'].isnull(), df['lft'],df['leeftijd'])
        df.drop(columns=['lft'],inplace=True)

        # fill empty values
        df['leeftijd'].fillna('9999', inplace=True)

        return df

    ##### gender
    def genderLaden(input_df):
        df = input_df.copy()
        df['gender'] = df['gender'].str.extract(r'(\w+)')
        df['gender'] = df['gender'].str.lower()

        return df

    #### type ontvangst
    def typeOntvangstLaden(input_df):
        df = input_df.copy()
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

        return df

    #### Afkomst
    def afkomstLaden(input_df):
        df = input_df.copy()
        df['afkomst'] = df['afkomst'].str.replace('( ;.*| \(.*)','')
        df['afkomst'] = df['afkomst'].str.strip()
        for a in list(dicts.afkomst):
            df['afkomst'] = df['afkomst'].str.replace(a,dicts.afkomst[a])

        return df

    #### Seksuele Voorkeur
    def seksueleVoorkeurLaden(input_df):
        df = input_df.copy()
        df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.replace('( ;.*| \(.*)','')
        df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.strip()
        for g in list(dicts.geaardheid):
            df['seksuele_voorkeur'] = df['seksuele_voorkeur'].str.replace(g,dicts.geaardheid[g])

        return df

    #### Prijzen 
    def prijzenLaden(input_df):
        df = input_df.copy()
        df['prijzen'] = df['prijzen'].astype(str)
        # eerst even een beetje opschonen
        df['prijzen'] = df['prijzen'].str.replace('\n',' ')
        df['prijzen'] = df['prijzen'].str.replace(' ','')
        df['prijzen'] = df['prijzen'].str.replace(';',' ')

        df['prijzen'] = df['prijzen'].str.replace(r'(hPrice)','uur')

        # apparte kolom voor escort prijzen
        df['escort_prijzen'] =  df['prijzen'].str.extract(r'(Escort.*Prijzen|Escort.*)')

        for col in ['prijzen','escort_prijzen']:
            # prijzen per uur uit tekst filteren
            for u in [2,1]:
                df[str(u)+'uur'] = df[col].str.extract('(\\b'+str(u)+'uur.{1,3}[0-9]{2,3})')
                df[str(u)+'uur'] = round(df[str(u)+'uur'].str.extract('([0-9]{2,3}$)').astype(float)/u,0)

            # prizjen per minuten uit tekst filteren
            for m in [60,45,30,15]:
                df[str(m)+'min'] = df[col].str.extract('(\\b'+str(m)+'minuten.{1,3}[0-9]{2,3})')
                df[str(m)+'min'] = round(df[str(m)+'min'].str.extract('([0-9]{2,3}$)').astype(float)/m*60,0)

            df[col] = np.where(~df['1uur'].isnull(),df['1uur'],
                np.where(~df['2uur'].isnull(),df['2uur'],
                    np.where(~df['60min'].isnull(),df['60min'],
                        np.where(~df['45min'].isnull(),df['45min'],
                            np.where(~df['30min'].isnull(),df['30min'],
                                np.where(~df['15min'].isnull(),df['15min'],'9999'))))))

        df.drop(columns=['2uur','1uur','60min','45min','30min','15min'], inplace=True)

        return df


    #### woonplaats
    df = datumLaden(df)
    df = leeftijdLaden(df)
    df = gemeente.getGmCodes(df)
    df = df.sort_values('gm_code').drop_duplicates('id',keep='last')
    df = genderLaden(df)
    df = typeOntvangstLaden(df)
    df = afkomstLaden(df)
    df = seksueleVoorkeurLaden(df)
    df = prijzenLaden(df)


    #### kolommen opschonenen en lege waarden invullen om klaar te maken voor upload in het data warehouse
    for column in list(df):
        df[column] = df[column].str.replace('[^A-Za-z0-9€\.\/\&\-\:]+', ' ')
        df[column] = df[column].str.strip()

    # éen kolom met alle bulktekst 
    df['advertentie_tekst'] = 'TITEL; '+df['titel']+' ALGEMENE INFO; '+df['algemene_info_bulk']\
        +' KARAKTERISTIEKEN; '+df['karakeristieken_bulk']+' MOGELIJKHEDEN; '+df['mogelijkheden']\
            +' WERKTIJDEN; '+df['werk_tijden_bulk']

    # selecteer kolommen die behouden moeten worden
    df = df[[
        'id',
        'aanbieder',
        'datum',
        'gender',
        'type_ontvangst',
        'afkomst',
        'leeftijd',
        'prijzen',
        'escort_prijzen',
        'woonplaats',
        'gm_code',
        'scr_tag',
        'url',
        'advertentie_tekst']]

    # datatype aanpassen naar int
    for col in list(df)[6:9]:
        df[col] = np.where((df[col]=='')|(df[col].isnull()),'9999',df[col])
        df[col] = df[col].astype(float)
        df[col] = round(df[col],0)
        df[col] = df[col].astype(int)

    # lege waarden vull voor overige kolommen
    for col in list(df)[:6]+list(df)[9:]:
        df[col] = np.where((df[col]=='')|(df[col].isnull()),'null',df[col])

    # timestamp toevoegen
    df['timestamp'] = int(round(datetime.datetime.now().timestamp(),0))

    ###############################################################################################################
    ########################################## STEP 3 - TO DATAWAREHOUSE ##########################################
    connections.insertVariblesIntoTable('sekswerkersScraper',df,'sk_id')

    # set timestamp
    timest = str(int(round(datetime.datetime.now().timestamp(),0)))

    outlook.sendEmail(
        receivers='database.admin@regioplan.nl', 
        subject='scraper-'+timest,
        message='Hi\nScraper has succsefully ran at '+timest,
        sender='anne.leemans@regioplan.nl')
    
    

