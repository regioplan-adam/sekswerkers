from lxml import etree
from lxml import html
import lxml
import requests
import re
import pandas as pd
import datetime
import time

# laad urls
def loadUrls():
    # set base website for scraper
    base_url = 'https://topescortbabes.com'
    urls = []
    url = ['/netherlands/escorts?page=40']
    while url != 'end':
        html = requests.get(base_url+url[-1])
        resp = lxml.html.fromstring(html.content)
        # find end of list
        # get advert urls 
        urls += resp.xpath('//*[@id="homepage_right"]/div[6]/ul/li/a/@href')
        # do something
        # get next page    
        new_url = resp.xpath('//*[@id="homepage_right"]/div[*]/a/@href')
        print('urls from page '+re.findall(r'[0-9]{1,3}',url[-1])[0]+' imported')
        # check for end of the line
        url = 'end' if re.findall(r'[0-9]{1,3}',url[-1])[0] > re.findall(r'[0-9]{1,3}',new_url[-1])[0] else new_url

    # remove duplicates
    urls = list(dict.fromkeys(urls))

    return urls

# extract data from adverts 
def loadAdvertisements():
    # set start time for scraper
    start = time.time()
    print('Scraper for topescortbabes.com strated at '+str(datetime.datetime.now().hour)+':'+
        str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
        str(datetime.datetime.now().month))
    try:
        output_df = pd.DataFrame()
        urls = loadUrls()
        index = 0

        for url in urls:
            temp_df = pd.DataFrame(index=[index])
            html = requests.get(url)
            resp = lxml.html.fromstring(html.content)
            temp_df['id'] = 'TE'+';'.join(re.findall(r'[0-9]{5,7}',url))
            temp_df['datum'] = ' ;'.join(resp.xpath('//*[@id="homepage"]/main/div[1]/div[3]/div[2]/text()'))
            temp_df['leeftijd'] = ' ;'.join(resp.xpath('//h4[contains(text(),"Age")]/following-sibling::span/text()'))
            temp_df['gender'] = 'vrouw'
            temp_df['locatie'] = ' ;'.join(resp.xpath('//h4[contains(text(),"Base City")]/following-sibling::a[2]/text()'))
            temp_df['type_ontvangst'] = 'escort'
            temp_df['afkomst'] = ' ;'.join(resp.xpath('//h4[contains(text(),"Nationality")]/following-sibling::span/text()'))
            temp_df['titel'] = 'null'
            temp_df['seksuele_voorkeur'] = ' ;'.join(resp.xpath('//h4[contains(text(),"Orientation")]/following-sibling::span/text()'))
            temp_df['algemene_info_bulk'] = ';'.join(resp.xpath('//*[@id="accord-about"]/div[2]/p/text()'))
            temp_df['karakeristieken_bulk'] = ';'.join(resp.xpath('//*[@id="accord-personal-data"]/div[2]/div//text()'))
            temp_df['prijzen'] =  ' ;'.join(resp.xpath('//div[contains(@class,"price-item")]//text()'))
            temp_df['mogelijkheden'] = 'null'
            temp_df['werk_tijden_bulk'] = ';'.join(resp.xpath("//ul[contains(@class,'available-wrapper')]//text()"))
            temp_df['alt_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1
            print('page '+str(index)+' from '+str(len(urls))+' loaded!')

        # aanbieder
        output_df['aanbieder'] = 'topescortbabes.com'

        # end time 
        end = time.time()
        print('Scraper for topescortbabes.com has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2)), 'minutes!')
    
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print('Spider for topescortbabes.com has failed with the following error:')
        print(e)
        print('Total elapesed time is: '+str(round((end - start)/60,2)), 'minutes!')
    
    return output_df
    