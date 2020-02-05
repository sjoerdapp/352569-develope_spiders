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
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### title page + 5 following pages, always three nes per request page, latest 21 news
### 

### United Contitnetal Holdings Inc. 1|1   2
### 1st spider Newsroom 2nd spider Investor Earnings releases but is not used as it links to newsroom
### launch two different requests
### get with json, comes in very long json file
### can cut the rewquest short and exclude some payload
### back to 20160121


class QuotessSpider(scrapy.Spider):
    name = 'United_Continental_9900040ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/United_Continental_9900040ARV001/',
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
    start_urls = ['https://hub.united.com/res/bootstrap/data.js?page_id=803502&site_id=10370665&resource_id=sp_803502&mode=full']

    def parse(self, response):  # follow drop down menue for different years

        body = json.loads(response.text)
        auxs = body['posts_by_source']['nrstream']
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux['formated_full_created_ts'] # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux['headline']
            item['DOCLINK']= aux['source_url']
            
            if item['DOCLINK'] and not re.search('[a-zA-Z]', item['DOCLINK']):
              item['DOCLINK'] = response.url

            elif not item['DOCLINK']:
              item['DOCLINK'] = response.url

            
            name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*United\b)(.|\s)*|(\bABOUT.United\b)(.|\s)*'
            name_regexx =r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*' 
            text = " ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::*[@class="shortcode-media shortcode-media-rebelmouse-image"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract())
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::*[@class="shortcode-media shortcode-media-rebelmouse-image"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if re.search(r'\d{4}\s*operational\s*results', text):
              item['DESCRIPTION'] = re.sub(name_regexx,'' ," ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::*[@class="shortcode-media shortcode-media-rebelmouse-image"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            yield item
            #if not item['DOCLINK']:
            #  item['DOCLINK'] = aux['google_amp_post_url']
            ##item = {
            ##        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
            ##        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
            ##        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
            ##        }
            #base_url = 'https://hub.united.com'
            #aux_url = item['DOCLINK']
            #
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


        years = list(range(0, 6)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'https://hub.united.com/res/load_more_posts/data.js?site_id=10370665&pn={}&resource_id=pp_2636713876&site_id=10370665'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.text)
          auxs = body['posts_by_source']['frontpage_newsroom']
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['formated_full_created_ts'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['headline']
              item['DOCLINK']= aux['source_url']
              
              if item['DOCLINK'] and not re.search('[a-zA-Z]', item['DOCLINK']):
                item['DOCLINK'] = response.url

              elif not item['DOCLINK']:
                item['DOCLINK'] = response.url
              
              name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*United\b)(.|\s)*|(\bABOUT.United\b)(.|\s)*'
              name_regexx =r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*' 
              text = " ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract())
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
              if re.search(r'\d{4}\s*operational\s*results', text):
                item['DESCRIPTION'] = re.sub(name_regexx,'' ," ".join(Selector(text=aux['body']).xpath('//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
              yield item
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              #base_url = 'https://hub.united.com'
              #aux_url = aux['source_url']
              #
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
    #    name_regex = r'xxx'#(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
    #    #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
    #    if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
    #        item['file_urls'] = [response.url]
    #        item['DOCLINK'] = response.url
    #        item['DESCRIPTION'] = ''
    #        yield item
    #    else:
    #        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="wd_subtitle wd_language_left"]/text() | //div[@class="wd_body wd_news_body"]//text()[not(ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #        item['DOCLINK'] = response.url
    #        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
    #            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//article//text()[not(ancestor::h1 or ancestor::amp-img or ancestor::div[@class="byline-amp"] or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #            yield item
    #        else:
    #            yield item
       
       