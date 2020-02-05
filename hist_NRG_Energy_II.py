# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### NRG Energy Inc. 2|2
### 2nd spider Newsroom
### get with json, content rather hidden in request, all news n one page
### detailpage comes with json
### back to 20150108

class QuotessSpider(scrapy.Spider):
    name = 'NRG_Energy_II_3749600ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/NRG_Energy_II_3749600ARV002/',
         'MEDIA_ALLOW_REDIRECTS' : 'True',
        }
    #custom_settings = {
    #    'SPLASH_URL': 'http://localhost:8050',
    #    'DOWNLOADER_MIDDLEWARES': {
    #        'scrapy_splash.SplashCookiesMiddleware': 723,
    #        'scrapy_splash.SplashMiddleware': 725,
    #        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    #    },
    #    'SPIDER_MIDDLEWARES': {
    #        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #    },
    #    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    #}
    start_urls = ['https://www.nrg.com/about/newsroom.nrgcontent.json?geolocationProvider=no_service']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 80, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.mccormickcorporation.com/api/sitecore/CORP18_generated_listing_with_filter?num_items=3&current_count={}&rootGuid=d0952d7d-aeea-4538-8c3f-0ad5cf3a95b7&templateGuids=02c1d0aa-0111-44a3-a3f0-5215df2d176f,9bdac2ca-5678-4cd7-84d8-21f5189f153a&category=All'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          body = json.loads(response.text)
          for aux in body['contentPayload']['children'][0]['payload']['primary'][1]['payload']['children'][0]['payload']['items']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['displayDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['header']
              item['DOCLINK']= aux['route']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.nrg.com'
              aux_url = aux['route'].split('html')[0] + 'nrgcontent.json?geolocationProvider=no_service'
              
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
        name_regex = r'(\bSafe\s*Harbor\b)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(NRG\s*is\s*a\s*leading\s*global\s*energy\s*company)(.|\s)*|(\bABOUT.NRG (?!\’s))(.|\s)*|(\bABOUT\s*NRG (?!\’s))(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            def getByKeyName(inputVariable, searchKey): ## Function to go through dictonary and find all keys named content and return their values
                foundItems = []
            
                if isinstance(inputVariable, dict):
                    for currentKey, currentVar in inputVariable.items():
                        if currentKey == searchKey:
                            foundItems = foundItems + [currentVar]
                        else:
                            foundItems = foundItems + getByKeyName(currentVar, searchKey)
                if isinstance(inputVariable, list):
                    for currentVar in inputVariable:
                        foundItems = foundItems + getByKeyName(currentVar, searchKey)
                            
                return foundItems

            body = json.loads(response.text)
            page_content =" ".join(getByKeyName(body, "content")) # get text content of page from "content-keys"
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=page_content).xpath('//p/text()').extract()), flags=re.IGNORECASE)
            #item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@data-component="RichText"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            #pdf_link = Selector(text=page_content).xpath('//p/a/@href').extract_first()
            
            pdf_link=body['contentPayload']['metadata']['canonical']

            if len(item['DESCRIPTION']) < 40:
                item['file_urls'] = [pdf_link]
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "node__content")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
       
       