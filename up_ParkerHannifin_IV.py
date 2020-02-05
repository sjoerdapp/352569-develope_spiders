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

### UPDATES
### get lates 25 news

### Parker Hanfin Corporation 4|4
### 4th spider News Releases
### had to be transferred to scrapy as dexi was not able to manage anymore
### normal get with json, all data inkl detail page comes in first json request
### back to 20000104


class QuotessSpider(scrapy.Spider):
    name = 'ParkerHannifin_IV_2136700ARV004'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/arkerHannifin_IV_2136700ARV004/',
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
    start_urls = ['https://search.parker.com/api/apollo/collections/ParkerDotComMainMaster/query-profiles/parkerdotcom-en/select?_cookie=false&echoParams=all&facetMode=new&fq=countryId_ss:687PDC&fq=%7B!tag%3Dtag_siteSectionEN_fq%7DsiteSectionEN_fq:%22p1611390703%22&fq=%7B!tag%3Dtag_newsEventsTypeEN_fq%7DnewsEventsTypeEN_fq:%22p2424563%22&fq=-(newsEventsType_ss:Event+AND+-eventDisplayStart_dt:%5BNOW-3YEARS+TO+NOW%5D)&json.nl=arrarr&q=*&rows=25&sort=newsDate_dt+desc&start=0&tab=news-events&wt=json']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 80, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.mccormickcorporation.com/api/sitecore/CORP18_generated_listing_with_filter?num_items=3&current_count={}&rootGuid=d0952d7d-aeea-4538-8c3f-0ad5cf3a95b7&templateGuids=02c1d0aa-0111-44a3-a3f0-5215df2d176f,9bdac2ca-5678-4cd7-84d8-21f5189f153a&category=All'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          body = json.loads(response.body.decode('utf-8'))
          for aux in body['response']['docs']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['newsDate_dt'].split('T')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['titleEN_t'][0]
              doclink = aux['ot_id_s']
              detail_url = 'https://www.parker.com/portal/site/PARKER/menuitem.31c35c58f54e63cb97b11b10237ad1ca/?vgnextoid={}&vgnextchannel=9383fbdc71fd7310VgnVCM100000200c1dacRCRD&vgnextfmt=EN&newsroom=Y&vgnextcat=News%20Release%20Details'
              item['DOCLINK']= detail_url.format(doclink)
              description = aux['descriptionEN_t'][0]
              description = " ".join(Selector(text=description).xpath('//text()').extract())

              name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*| (Parker\s*Hannifin\s*is\s*a\s*Fortune\s*\d+\s*global\s*leader\s*in)(.|\s)*'
              name_regex_2=r'(\bAbout\s*Parker)(.|\s)*|(\bAbout.Parker\b)(.|\s)*|(\bABOUT.PARKER\b)(.|\s)*|(\bABOUT\s*PARKER\b)(.|\s)*'
              item['DESCRIPTION'] = re.sub(name_regex,'' ,description, flags=re.IGNORECASE)
              item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
              yield item
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              #base_url = 'https://www.mccormickcorporation.com'
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
    #        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//section[contains(@class, "text_module")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
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
    #   #