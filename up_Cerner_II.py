import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### first 25 news, high news frequency

### Cerner Corporation 2|2
### 2 spiders 1st IR News Releases (back to 2013), 2nd Blog (back to 2016)
### Blog goes back to 2016 and has slightly more news than IR News Releases
### standard get
### goes back to 20161101


class BHGE(scrapy.Spider):
    name = "Cerner_II_8786000ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Cerner_II_8786000ARV002/',
        }
    #handle_httpstatus_list = [404]
    #custom_settings = {
    #      'USER_AGENT' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'        
    ##     'JOBDIR' : 'None',
    ##     'FILES_STORE' : 's3://sp5001/PAY_II_6333000ARV002/',
    #    }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    start_urls = ['https://www.cerner.com/blog'] 
    user_agent = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36']    
    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(0, 1)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.cerner.com/blog?pn={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

   
    
    def parse_next(self, response):
        auxs = response.xpath('//div[@class="blogPostContainer"]/div[contains(@class,"card-list-card")]')
        for aux in auxs[0:25]:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//section/a/div/p/span[1]/text()').extract_first()
            item['HEADLINE']= aux.xpath('.//section/a/div/h2/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//section/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('.//section/a/div/p/span[1]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('.//section/a/div/h2/text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//section/a/@href').extract_first(),
            #        }
            base_url = 'https://www.cerner.com'
            aux_url = aux.xpath('.//section/a/@href').extract_first()
            
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
        name_regex = r"""(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Cerner\s*.s\s*health\s*(information\s*)?technologies\s*connect\s*people(.)?(\s*and)?\s*information)(.|\s)*|"""##|(\bAbout\s*Cerner\b)(.|\s)* | (\bAbout.Cerner\b)(.|\s)*"""
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath(' //div[@itemprop="articleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
        


        
            