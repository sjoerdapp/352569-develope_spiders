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
from scrapy.http import FormRequest

### UPDATES
### get latest 20 news (all news one page)

### Royal Caribbean Cruises Ltd 1|2
### 1st spider IR Press Releases, "nd spider Presscenter
### classic post with xpath
### back to 20000719


class QuotessSpider(scrapy.Spider):
    name = 'RoyalCaribbean_I_2981900ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/RoyalCaribbean_I_2981900ARV001/',
         'CRAWLERA_ENABLED': False,
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
        yield scrapy.http.Request(
            'https://www.rclinvestor.com/press-releases/',
        )
              


    def parse(self, response):
          #body = json.loads(response.text)
          auxs = response.xpath('//div[@class="release"]')
          for aux in auxs[0:20]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./p[@class="date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./p/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./p/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.rclinvestor.com'
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

          next_link = response.xpath('//a[@class="btn load-more"]/@data-paged').extract_first()
          #sel = js2xml.parse(next_link)
          #target = str(sel.xpath('//arguments/string/text()')[0])
          #yield FormRequest(url='https://www.rclinvestor.com/wp/wp-admin/admin-ajax.php',
          #   headers={
          #      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          #      'Origin: https':'//www.rclinvestor.com',
          #      'Referer': 'https://www.rclinvestor.com/press-releases/',
          #      'Sec-Fetch-Mode': 'cors',
          #      'Sec-Fetch-Site': 'same-origin',
          #      'X-Requested-With': 'XMLHttpRequest',
          #   },
          #   formdata={
          #      'action': 'press_filter',
          #      'year': '',
          #      'category': '',
          #      "paged": next_link,
          #      #'buProdListScriptMgr': 'content_1$contentright_1$upnlNewsReleases|content_1$contentright_1$DataPagerNewsTop$ctl02$ctl00',
          #      #'content_1$contentright_1$hdnBusinessUnit': '',
          #      #'__EVENTARGUMENT': '',
          #   },
          #   callback=self.parse,
          #)     
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Royal\b)(.|\s)*|(\bAbout.Royal\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="after_header"]//div[@class="row"]/div[@class="col"]//text()[not(ancestor::h1 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       