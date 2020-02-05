import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
 
### TransDigm Group Incorporated 1|1 
### 1st scraper IR press releases
### IR  post request mit FormData
### normal get
### back to 20060419

class BHGE(scrapy.Spider):
    name = "Trans_Dig_9900106ARV001"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Trans_Dig_9900106ARV001/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        
        for year in list(range(2006,2020)):  # loop iterating over different pages of ajax request; last number not in list anymore
            aux_url = 'https://www.transdigm.com/investor-relations/news-releases/?myyear={}'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse)
    
    def parse(self, response):
        #body= json.loads(response.text)  # load jason response from post request
        quotes = response.xpath('//table[not(contains(@class, "stock"))]//tr')[1:] # deletes first element from list
        #quotes = Selector(text=body).xpath('//div[@class="view-all-right"]') # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote.xpath('./td[1][not(contains(text(), "Date"))]/text()').extract_first()
            item['HEADLINE']=  quote.xpath('./td[2][not(contains(text(), "Title"))]/a/text()').extract_first()
            item['DOCLINK']=  quote.xpath('./td[2][not(contains(text(), "Title"))]/a/@href').extract_first()

            base_url = 'https://www.transdigm.com'
            aux_url=  quote.xpath('./td[2][not(contains(text(), "Title"))]/a/@href').extract_first()
            

            if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*TransDigm\b)(.|\s)* | (\bAbout.TransDigm\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="xn-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="entry-content"]//text()[not(ancestor::h2 or ancestor::div[@width="100%"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
                   
        
            