from lxml import etree
from lxml import html
import lxml
import requests
import re
import pandas as pd
import datetime
import time
from tqdm import tqdm
from termcolor import colored

# laad urls
def loadUrls():
    # set base website for scraper
    urls = []
    # redlights heeft twee uitgangen, een voor excors en 1 voor thuisontvangst
    for types in ['thuisontvangst','escort']:
        url = ['https://www.redlights.nl/'+types+'/dames/?page=1']
        while ((url != [])&(url != ['#'])):
            html = requests.get(url[-1])
            resp = lxml.html.fromstring(html.content)
            # get advert urls 
            urls += resp.xpath('//*[contains(@id,"a-")]/figure/div/a/@href')
            # get next page    
            url = resp.xpath('/html/body/div[5]/div/div/div/main/section/div[3]/div/ul/li[12]/a/@href')
            
    return urls

# extract data from adverts 
def loadAdvertisements():
    # set start time for scraper
    start = time.time()
    print(colored('Scraper for redlights.nl strated at '+str(datetime.datetime.now().hour)+':'+
        str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
        str(datetime.datetime.now().month),'green'))
    print(colored('\nPlease wait while system is Loading urls...\n','yellow'))

    try:
        output_df = pd.DataFrame()
        urls = loadUrls()
        index = 0
        for url in tqdm(urls):
            temp_df = pd.DataFrame(index=[index])
            html = requests.get(url)
            resp = lxml.html.fromstring(html.content)
            meta = ' ;'.join(resp.xpath('/html/body/script[5]/text()'))
            temp_df['id'] = 'RL'+re.findall(r'[0-9]{5,7}',meta)[0]
            temp_df['datum'] = ' ;'.join(resp.xpath('/html/body/div[5]/div/div/div/main/div["[1-2]{1}"]/div/header/h6/strong/text()'))
            temp_df['leeftijd'] = ' ;'.join(resp.xpath('//dt[contains(text(),"Leeftijd")]/following-sibling::dd/text()'))
            temp_df['gender'] = ' ;'.join(resp.xpath('//dt[contains(text(),"Geslacht")]/following-sibling::dd/text()'))
            temp_df['locatie'] =  ' ;'.join(resp.xpath('//*[contains(text(),"Locatie")]/following-sibling::*//text()'))
            temp_df['type_ontvangst'] = ';'.join(re.findall(r'(prive-ontvangst|escort|thuisontvangst)',url))
            temp_df['afkomst'] =  ' ;'.join(resp.xpath('//dt[contains(text(),"Etniciteit")]/following-sibling::dd/text()'))
            temp_df['titel'] = 'null'
            temp_df['seksuele_voorkeur'] =  ' ;'.join(resp.xpath('//dt[contains(text(),"Geaardheid")]/following-sibling::dd/text()'))
            temp_df['algemene_info_bulk'] = ';'.join(resp.xpath('/html/body/div[5]/div/div/div/main/div[2]/div//text()'))
            temp_df['karakeristieken_bulk'] = ';'.join(resp.xpath('/html/body/div[5]/div/div/div/main/div[3]/section[1]//text()'))
            temp_df['prijzen'] =  9999
            temp_df['mogelijkheden'] = 'null'
            temp_df['werk_tijden_bulk'] = ';'.join(resp.xpath("//*[contains(text(),'Contacturen')]/following-sibling::div//text()"))
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1

        # aanbieder
        output_df['aanbieder'] = 'redlights.nl'

        # end time 
        end = time.time()
        print(colored('\nScraper for redlights.nl has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2))+'minutes!','green'))
        print(colored('---------------------------------------------------------------------\n\n','green'))   
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print(colored('WARNING!!! WARNING!!!','red'))
        print(colored('Spider for redlights.nl has failed:', 'red'))
        print(colored(e,'red'))
        print(colored('Please contact system admin...............','red'))
    
    return output_df
    