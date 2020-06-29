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
    base_url = 'https://www.kinky.nl'
    urls = []
    dates = []
    url = ['/vrouwen/?page=2']
    while url != []:
        html = requests.get(base_url+url[0])
        resp = lxml.html.fromstring(html.content)
        # get advert urls 
        urls += resp.xpath('/html/body/div/main/div[2]/div[2]/div[*]/div/a/@href')
        # get upload date
        dates += resp.xpath("//li[contains(@class, 'sub-item date')]/text()")
        # get next page    
        url = resp.xpath("/html/body/div/main/div[2]/div[2]/ul/li[6]/a/@href")

    # add base url
    urls = [base_url + s for s in urls]
    # remove trailing spaces from dates
    pattern = re.compile(r'\n                    |\n                ')
    dates = [pattern.sub('', item) for item in dates]

    return urls, dates

# extract data from adverts 
def loadAdvertisements():
    # set start time for scraper
    start = time.time()
    print(colored('Scraper for kinky.nl strated at '+str(datetime.datetime.now().hour)+':'+
        str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
        str(datetime.datetime.now().month),'green'))
    print(colored('\nPlease wait while system is Loading urls...\n','yellow'))

    
    try:
        output_df = pd.DataFrame()
        results = loadUrls()
        urls = results[0]
        dates = results[1]
        index = 0
        for url,date in zip(tqdm(urls),dates):
            temp_df = pd.DataFrame(index=[index])
            html = requests.get(url)
            resp = lxml.html.fromstring(html.content)
            temp_df['id'] = 'KY'+';'.join(re.findall(r'[0-9]{5,7}',url))
            temp_df['datum'] = date
            temp_df['leeftijd'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[1]/div[1]/p[1]/span/text()'))
            temp_df['gender'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[1]/div[1]/p[2]/span/text()'))
            locatie = ';'.join(resp.xpath("//*[@id='overview-section']/div[1]/div[1]/p[5]/span/text()"))
            temp_df['locatie'] = locatie if locatie != '' else ';'.join(resp.xpath("//*[@id='overview-section']/div[1]/div[1]/p[4]/span/text()"))
            temp_df['type_ontvangst'] =  ';'.join(re.findall(r'(prive-ontvangst|escort|thuisontvangst)',url))
            temp_df['afkomst'] = ';'.join(resp.xpath('//*[contains(text(), "Afkomst")]/parent::*/following-sibling::p[1]/text()'))
            temp_df['titel'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[1]/h1/text()'))
            temp_df['seksuele_voorkeur'] = ';'.join(resp.xpath('//*[contains(text(), "Seksuele voorkeur")]/parent::*/following-sibling::p[1]/text()'))
            temp_df['algemene_info_bulk'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[1]/div[2]/p[2]/text()'))+\
                ';'.join(resp.xpath('//*[@id="overview-section"]/div[1]/div[1]/p/span/text()'))
            temp_df['karakeristieken_bulk'] = ';'.join(resp.xpath("//div[contains(@class,'characteristics')]//text()"))
            temp_df['prijzen'] =  ';'.join(resp.xpath("//div[contains(@class,'prices')]//text()"))
            temp_df['mogelijkheden'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[6]/div/p/text()'))
            temp_df['werk_tijden_bulk'] = ';'.join(resp.xpath('//*[@id="overview-section"]/div[7]/div/p/text()'))
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1

        # aanbieder
        output_df['aanbieder'] = 'kinky.nl'

        # end time 
        end = time.time()
        print(colored('\nScraper for kinky.nl has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2))+'minutes!','green'))
        print(colored('---------------------------------------------------------------------\n\n','green'))
    
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print(colored('WARNING!!! WARNING!!!','red'))
        print(colored('Spider for kinky.nl has failed:', 'red'))
        print(colored(e,'red'))
        print(colored('Please contact system admin...............','red'))
    
    return output_df
    

