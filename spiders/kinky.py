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
    base_url = 'https://www.kinky.nl'
    urls = []
    dates = []
    url = ['/vrouwen/?page=107']
    while url != []:
        html = requests.get(base_url+url[0])
        resp = lxml.html.fromstring(html.content)
        # get advert urls 
        urls += resp.xpath('/html/body/div/main/div[2]/div[2]/div[*]/div/a/@href')
        # get upload date
        dates += resp.xpath("//li[contains(@class, 'sub-item date')]/text()")
        # do something
        print('urls from page '+re.findall(r'[0-9]{1,3}',url[0])[0]+' imported')
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
    print('Scraper for kinky.nl strated at '+str(datetime.datetime.now().hour)+':'+
        str(datetime.datetime.now().minute)+' on '+str(datetime.datetime.now().day)+'/'+
        str(datetime.datetime.now().month))
    try:
        output_df = pd.DataFrame()
        results = loadUrls()
        urls = results[0]
        dates = results[1]
        index = 0
        for url,date in zip(urls,dates):
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
            temp_df['alt_tag'] = ';'.join(resp.xpath('//img[contains(@alt, "")]/@alt'))
            temp_df['scr_tag'] = ';'.join(resp.xpath('//a[contains(@href, ".jpg")]/@href'))
            temp_df['url'] =  url
            output_df = output_df.append(temp_df)
            index += 1
            print('page '+str(index)+' from '+str(len(urls))+' loaded!')

        # aanbieder
        output_df['aanbieder'] = 'kinky.nl'

        # end time 
        end = time.time()
        print('Scraper for kinky.nl has successfully finnished with '+ str(len(output_df)) + ' records found\n'
        'Total elapesed time is: '+str(round((end - start)/60,2)), 'minutes!')
    
    # if error occurs reccord error and print in console 
    except Exception as e:
        end = time.time()
        print('Spider for kinky.nl has failed with the following error:')
        print(e)
        print('Total elapesed time is: '+str(round((end - start)/60,2)), 'minutes!')
    
    return output_df
    

