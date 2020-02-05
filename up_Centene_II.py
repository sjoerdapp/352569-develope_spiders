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
from scrapy.selector import Selector

### Centene Corp 2|2
### 1st spider Investor Press Releases, 2nd spider Featured Stories
### normal get with json, description comes also in json 
### back to 20180801


class QuotessSpider(scrapy.Spider):
    name = 'Centene_II_4254000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Centene_II_4254000ARV002/',
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
    start_urls = ['https://www.centene.com/featured-stories-archive.centenedotcomnews.json?pageSize=9999',
                  ]

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 80, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.mccormickcorporation.com/api/sitecore/CORP18_generated_listing_with_filter?num_items=3&current_count={}&rootGuid=d0952d7d-aeea-4538-8c3f-0ad5cf3a95b7&templateGuids=02c1d0aa-0111-44a3-a3f0-5215df2d176f,9bdac2ca-5678-4cd7-84d8-21f5189f153a&category=All'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          body = json.loads(response.text)
          for aux in body['newsResults'][0:20]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['time'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['title']
              item['DOCLINK']= aux['path']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              content = aux['description']
              item['DESCRIPTION'] = " ".join(Selector(text=content).xpath('//p/text()').extract())
              base_url = 'https://www.centene.com'
              aux_url = item['DOCLINK']
              item['DOCLINK'] = base_url + aux_url
              yield item

              #if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
              #  if aux_url.startswith('http'):
              #      url= aux_url
              #      item['file_urls'] = [url]
              #      item['DOCLINK'] = url
              #      item['DESCRIPTION'] = ''
              #      yield item
              #  
              #  else:
              #      url= base_url + aux_url
              #      item['file_urls'] = [url]
              #      item['DOCLINK'] = url
              #      item['DESCRIPTION'] = ''
              #      yield item
              #else:
              #  if aux_url.startswith('http'):
              #      url= aux_url
              #      request = scrapy.Request(url=url, callback=self.parse_details)
              #      request.meta['item'] = item
              #      yield request
              #      
              #  
              #  else:
              #      url= base_url + aux_url
              #      request = scrapy.Request(url=url, callback=self.parse_details)
              #      request.meta['item'] = item
              #      yield request
               
        
    #def parse_details(self, response):
    #    item = response.meta['item']
    #    name_regex = r'xxx'#(This\s*release\scontains\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
    #    #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
    #    if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
    #        item['file_urls'] = [response.url]
    #        item['DOCLINK'] = response.url
    #        item['DESCRIPTION'] = ''
    #        yield item
    #    else:
    #        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="row pb-5"]/div[@class="col"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #        item['DOCLINK'] = response.url
    #        if not item['DESCRIPTION']:
    #            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "node__content")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
    #                item['DESCRIPTION'] = 'FEHLER'
    #                yield item
    #            else:
    #                yield item
    #        else:
    #            yield item
    #   
       