from lxml import etree
from lxml import html
import lxml
import requests
import re
import pandas as pd
import datetime
import time
from tqdm import tqdm
import os
from termcolor import colored

# laad urls
def loadUrls():
    # set base website for scraper
    base_url = 'https://www.sexguide.nl/'
    urls = []
    url = ['https://www.sexguide.nl/page-2.html']
    end = ''
    while url != []:
        html = requests.get(url[0])
        resp = lxml.html.fromstring(html.content)
        # get advert urls 
        urls += resp.xpath('//*[contains(@class, "h3title")]//@href')
        # get next page    
        url = resp.xpath('//*[contains(@rel, "next")]//@href') 


    return urls

# extract data from adverts 
def loadAdvertisements():
    # set start time for scraper
    start = time.time()
    print(colored('Scraper for sexguide.nl strated at '+str(datetime.datetime.now().hour)+':'+
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
            temp_df['id'] = 'SG'+';'.join(re.findall(r'[0-9]{5,7}',url))
            temp_df['datum'] = ';'.join(resp.xpath('//*[@id="infoToggle"]/div/p/text()'))
            temp_df['leeftijd'] = ';'.join(resp.xpath('//h1[contains(@class, "heading-title")]//text()'))
            temp_df['gender'] = 'vrouw'
            temp_df['locatie']  = ';'.join(resp.xpath('//div[contains(text(), "Stad")]/following-sibling::span//text()'))
            temp_df['type_ontvangst'] = 'escort'
            temp_df['afkomst'] = ';'.join(resp.xpath('//div[contains(text(), "Afkomst")]/following-sibling::span//text()'))
            temp_df['titel'] = 'null'
            temp_df['seksuele_voorkeur'] = ';'.join(resp.xpath('//div[contains(text(), "Oriëntatie")]/following-sibling::span//text()'))
            temp_df['algemene_info_bulk'] = ';'.join(resp.xpath('//*[@id="infoToggle"]/text()'))
            temp_df['karakeristieken_bulk'] = ';'.join(resp.xpath('//*[contains(text(),"People")]/parent::*/following-sibling::*//text()'))
            temp_df['prijzen'] = 9999
            temp_df['mogelijkheden'] = ';'.join(resp.xpath('//*[contains(text(),"Services")]/parent::*/following-sibling::*//text()'))
            temp_df['werk_tijden_bulk'] = ';'.join(resp.xpath('//div[contains(text(), "Werktijd")]/following-sibling::*//text()'))
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1

        # aanbieder
        output_df['aanbieder'] = 'sexguide.nl'

        # end time 
        end = time.time()
        print(colored('\nScraper for sexguide.nl has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2))+'minutes!','green'))
        print(colored('---------------------------------------------------------------------\n\n','green'))
    
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print(colored('WARNING!!! WARNING!!!','red'))
        print(colored('Spider for sexguide.nl has failed:', 'red'))
        print(colored(e,'red'))
        print(colored('Please contact system admin...............','red'))
    
    return output_df
    
