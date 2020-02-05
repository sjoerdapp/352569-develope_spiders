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

### National Oilwell Varco Inc. 2|2
### 2nd spider News
### post with payload 
### back to 20190311


class QuotessSpider(scrapy.Spider):
    name = 'National_OilwellVarco_II_3176900ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/National_OilwellVarco_II_3176900ARV002/',
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
    #start_urls = ['https://www.tsys.com/news-innovation/press-media/press-releases']

    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            #'Connection': 'keep-alive',
            #'Content-Length': '316',
            'cache-control': 'max-age=0',
            'Content-Type': 'application/json',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.nov.com',
            'Referer': 'https://www.nov.com/about/news',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
           }

        cookies = {'__cfduid': 'd28df722868fea771826d672aed7544cb1576579960',
                'ARRAffinity': '4b1aa7b3c0134c0d38bb5b22eadb6a0cd19c7de07d0069cac0d578e9c3355b35',
                '__RequestVerificationToken': '2--XWJ8zbKkG2V5CXwlhnf4XpWxpB_ajLA1dhSaGxS0dEPO-iwUMz2sC5sL0EZymTCiXaAW31PRYd5JGokyVQzEqD7iAsKJfIN1lAso_In41',
                'DisableNonEssentialCookies': 'false',
                'ASP.NET_SessionId': 'pnuhlj0lbi2gqaek3xmgekml',
                'SC_ANALYTICS_GLOBAL_COOKIE': '1307154c5b8e41c6bdaa830b688b0f73|False',
                '_gcl_au': '1.1.1558171619.1576579967',
                '_ga': 'GA1.2.1549196110.1576579967',
                '_gid': 'GA1.2.490005950.1576579967',
                '_gat_UA-570640-1': '1',
                '_hjid': 'b1346a69-884c-4d17-99f2-a428ad85a615',
                '_hjIncludedInSample': '1'}

        data = {"feedId":"9a608591-392e-42b7-a5a0-020a48b9ffed","pageIndex":4,"filterQuery":[{"businesssegment":""},{"when":""}]}
        for year in list(range(0, 5)):  # loop iterating over different pages of ajax request
            data["pageIndex"] = year
            s_url = 'https://www.nov.com/filteredfeed-api/getfilteredfeed'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, cookies=cookies, callback=self.parse) 

      


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['Cards']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['PublishedDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['Heading']
              item['DOCLINK']= dat['CTALink'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.nov.com'
              aux_url = item['DOCLINK']
              
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
        name_regex = r'xxx'#(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*TSYS\b)(.|\s)*|(\bABOUT.TSYS\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="D10-article-subhead__inner"]//text() | //div[@class="D5-article-text-inner rte"]//text()[not(ancestor::span[contains(@class, "infobar")])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       