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
    base_url = 'https://www.sexjobs.nl'
    urls = []
    url = ['/dames-van-plezier/?land-filter=nl&provincie-filter=&plaats-filter=&only_pictures=&page=1']

    while url != ['javascript:void(0)']:
        html = requests.get(base_url+url[0])
        resp = lxml.html.fromstring(html.content)
        # get advert urls 
        urls += resp.xpath('//*[@id="content"]/div/div/div[2]/div[2]/div/div[1]/div/a/@href')
        # get next page    
        url = resp.xpath('//*[contains(@rel, "next")]//@href') 

    # add base url
    urls = [base_url + s for s in urls]
    # remove duplicates
    urls = list(dict.fromkeys(urls))

    return urls

# extract data from adverts 
def loadAdvertisements():
    # set start time for scraper
    start = time.time()
    print(colored('Scraper for sexjobs.nl strated at '+str(datetime.datetime.now().hour)+':'+
        str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
        str(datetime.datetime.now().month),'green'))
    print(colored('\nPlease wait while system is Loading urls...\n','yellow'))

    try:
        # create empty df for appendong results
        output_df = pd.DataFrame()
        urls = loadUrls()
        index = 0

        for url in tqdm(urls):
            temp_df = pd.DataFrame(index=[index])
            html = requests.get(url)
            resp = lxml.html.fromstring(html.content)
            temp_df['id'] = 'SJ'+re.findall(r'[0-9]{5,7}',url)[0]
            temp_df['datum'] = ' ;'.join(resp.xpath('//*[@id="content"]/div/div/article/div[2]/div[2]/div[2]/ul/li["[2-3]{1}"]/text()'))
            temp_df['leeftijd'] = 'null'
            temp_df['gender'] = 'vrouw'
            temp_df['locatie'] = ' ;'.join(resp.xpath('//td[contains(text(),"Plaats")]/following-sibling::td/text()'))
            temp_df['type_ontvangst'] = 'null'
            temp_df['afkomst'] = 'null'
            temp_df['titel'] = 'null'
            temp_df['seksuele_voorkeur'] = 'null'
            temp_df['algemene_info_bulk'] = ';'.join(resp.xpath('//*[@id="content"]/div/div//text()'))
            temp_df['prijzen'] = 'null'
            temp_df['mogelijkheden'] = 'null'
            temp_df['werk_tijden_bulk'] = 'null'
            temp_df['karakeristieken_bulk'] = 'null'
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1

        # aanbieder
        output_df['aanbieder'] = 'sexjobs.nl'

        # end time 
        end = time.time()
        print(colored('\nScraper for sexjobs.nl has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2))+'minutes!','green'))
        print(colored('---------------------------------------------------------------------\n\n','green'))
    
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print(colored('WARNING!!! WARNING!!!','red'))
        print(colored('Spider for sexjobs.nl has failed:', 'red'))
        print(colored(e,'red'))
        print(colored('Please contact system admin...............','red'))
    
    return output_df
    
    
