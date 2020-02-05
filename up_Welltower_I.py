# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import json
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from scrapy.selector import Selector

### UPDATES
### scrape latest 20 news

### Welltower Inc 1|1
### Spider collects press releases from investor page
### all data comes from first initial request
### back to 19981007


class QuotessSpider(scrapy.Spider):
    name = 'Welltower_2105000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Welltower_2105000ARV001/',
        }
    #http_user = '535209af07354fbbb4110611b27f7504'
    #custom_settings = {
    #    'ROBOTSTXT_OBEY':'False',
    #    'USER_AGENT': "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
    #    }
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://testqualcom/discover/',
    #    'SPLASH_URL': 'http://localhost:8050',
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'scrapy_splash.SplashCookiesMiddleware': 723,
    #         'scrapy_splash.SplashMiddleware': 725,
    #         'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    #     },
    #     'SPIDER_MIDDLEWARES': {
    #         'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #     },
    #     'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    #}
    start_urls = ['https://welltower.com/wp-content/themes/sage-master/lib/client/press-releases.php'] 

    
    def parse(self, response):  # follow drop down menue for different years
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in body[0:20]:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['releaseDate']['date'].split('T')[0]
            item['HEADLINE']= dat['title']
            item['DOCLINK']= dat['id']
            #item = {
            #          'PUBSTRING': dat['Date'],
            #          'HEADLINE': dat['Title'],
            #          'DOCLINK': dat['@attributes']['ReleaseID'],
            #          }
            base_url = 'https://welltower.com/investors/press-release-details/?id='
            aux_url = str(item['DOCLINK'])
            
            if '.pdf' in aux_url:
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Welltower\b)(.|\s)* | (\bAbout.Welltower\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub( name_regex,'' ," ".join(response.xpath('//div[@class="xn-content"]//text()[not(ancestor::chron)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub( name_regex,'' ," ".join(response.xpath('//div[@class="bk-rich-text"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item

        else:
            yield item

        
        