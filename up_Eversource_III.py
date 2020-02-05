import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
import datetime

### UPDATES
### first 4 pages, lates 20 news

### Eversource Energy 3|4
### all in all 4 spiders 3 for different regeions and 4th for investor page
### 3rd spider conneticut
### have to converst timestamp
### classic post with payload and json content

class BHGE(scrapy.Spider):
    name = "EverS_III_2129900ARV003"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/EverS_III_2129900ARV003/',
        }
    #handle_httpstatus_list = [404]
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://sp5001/PAY_II_6333000ARV002/',
    #    }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json',
            #'Cookie': '_ga=GA1.2.1216204916.1547660679',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.eversource.com',
            'Referer': 'https://www.eversource.com/content/ct-c/about/news-room/connecticut/connecticut-news',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"request":{"NewsgroupId":"bc2f880f-1b52-67e3-9dbd-ff0000e2e88e","DetailsPageId":"1abd890f-1b52-67e3-9dbd-ff0000e2e88e","ListPageUrl":"www.eversource.com/content/ct-c/about/news-room/connecticut/connecticut-news","CurrentPage":5,"ItemsPerPage":5,"DateFilter":None,"CategoryFilter":None,"TagFilter":None}}
        s_url = 'https://www.eversource.com/content/Sitefinity/Public/Services/News/NewsService.svc/GetNewsPosts'
        yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
    
    def parse(self, response): 
        body = json.loads(response.text)
        page_num = body['TotalPages'] + 1 # as last element of the range is not part of the range anymore
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json',
            #'Cookie': '_ga=GA1.2.1216204916.1547660679',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.eversource.com',
            'Referer': 'https://www.eversource.com/content/ct-c/about/news-room/connecticut/connecticut-news',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }
        data = data = {"request":{"NewsgroupId":"bc2f880f-1b52-67e3-9dbd-ff0000e2e88e","DetailsPageId":"1abd890f-1b52-67e3-9dbd-ff0000e2e88e","ListPageUrl":"www.eversource.com/content/ct-c/about/news-room/connecticut/connecticut-news","CurrentPage":1,"ItemsPerPage":5,"DateFilter":None,"CategoryFilter":None,"TagFilter":None}}
        for num in list(range(0, 5)):  # loop iterating over different pages of ajax request; last number not in list anymore
            data['request']['CurrentPage'] = num
            s_url = 'https://www.eversource.com/content/Sitefinity/Public/Services/News/NewsService.svc/GetNewsPosts'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse_next)    
    


    def parse_next(self, response):
        body = json.loads(response.text)  # load jason response from post request
        for dat in body['NewsPosts']:
            #transform 13 digit unit date
            timestamp = dat['Date'].split('(')[1].split(')')[0]
            your_dt = datetime.datetime.fromtimestamp(int(timestamp)/1000)
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = your_dt.strftime("%Y-%m-%d %H:%M:%S")
            item['HEADLINE']= dat['Title']
            item['DOCLINK']= dat['DetailsPageUrl']
            
            
            base_url = 'https://www.eversource.com/content'
            aux_url = base_url + dat['DetailsPageUrl'][1:]  # omitts the first element from the string
            
            if '.pdf' in aux_url.lower():
                if aux_url.startswith('http'):
                    url= aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
                
                else:
                    url= base_url + aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
            else:
                if aux_url.startswith('http'):
                    url= aux_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + aux_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
           

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Eversource\s*\(\s*NYSE\s*:\s*ES\s*\)\s*transmits\s*and\s*delivers\s*electricity\s*and\s*natural\s*gas)(.|\s)*|(Eversource\s*\(\s*NYSE\s*:\s*ES\s*\)\s*transmits\s*and\s*delivers\s*electricity\s*to)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Eversource:\b)(.|\s)*| (\bAbout.Eversource:\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="article-content"]//text()[not(ancestor::h1 or ancestor::div[contains(@class, "data-table")])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="article-content"]/*[not(descendant::h1)]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item

        else:
                yield item
        
             



        
            