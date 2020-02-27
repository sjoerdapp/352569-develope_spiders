
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import requests
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from scrapy import FormRequest


### Discovery Communications Inc. 2|2
### 2nd spider newsroom
### trick system by requesting all in one page and than use xpath 
# normal simple post with formdata, content comes as html under json key html
### back to 20100105



class QuotessSpider(scrapy.Spider):
    name = 'Test_DiscoveryCom_II_4701100ARV002'
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://352569/DiscoveryCom_II_4701100ARV002/',
    #    }

    start_urls = ['https://corporate.discovery.com/discovery-newsroom/?P=340']

    #def start_requests(self):
    #    headers = {
    #                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #                'accept-encoding': 'gzip, deflate, br',
    #                'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    #                'cookie': '_ga=GA1.2.1502014306.1579858238; _gid=GA1.2.1368996451.1582642606',
    #                #'_ga=GA1.2.665324667.1558623191; _gid=GA1.2.915133571.1558623191; s_cc=true; s_sq=%5B%5BB%5D%5D',
    #                'sec-fetch-dest': 'document',
    #                'sec-fetch-mode': 'navigate',
    #                'sec-fetch-user': '?1',
    #                'upgrade-insecure-requests': '1',
    #                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    #       }
    ##    #data = {'action': 'wds_corporate_newsroom_load_more',
    ##    #        'wp_nonce': 'f314e95df8',
    ##    #        'page': '100',
    ##    #        'post_type': 'discovery-newsroom'
    ##    #        }
##
##   # #   
 #   #    s_url = 'https://corporate.discovery.com/discovery-newsroom/?P=340'
    #    yield scrapy.Request(url=s_url, method='GET', headers=headers, callback=self.parse )

    def parse(self, response):
          #body = json.loads(response.text)
          #content = body['html']
          
          #auxs = Selector(text=content).xpath('//article')
          auxs = response.xpath('//div[@class="articles"]/article[contains(@id, "post-")]')
          #body = str(response.body)
          #item = SwisscomIvCrawlerItem()
          #item['DOCLINK']= response.xpath('//div[@class="articles"]/article[contains(@id, "post-51390")]//text()').extract()#body[0 : 10000]#str(response.body)#
          #yield item
          for aux in auxs[0:20]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//time[contains(@class, "published")]/text()').extract_first()
              item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()
              #yield item  #

              base_url = 'https://corporate.discovery.com'
              aux_url = item['DOCLINK'] 
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Discovery)(.|\s)*|(\bAbout.Discovery\b)(.|\s)*|(\bABOUT.Discovery\b)(.|\s)*|(\bABOUT\s*.DISCOVERY\b)(.|\s)*'
        if not item['HEADLINE']:
          item['HEADLINE'] = ''.join(response.xpath('//header[@class="entry-header"]//text()').extract())

        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="entry-content"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
          #auxs = response.xpath('//article')
          #body = response.body
          #item = {
          #            'Body': body,
          #    #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
          #    #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
          #            }
          	  #yield item