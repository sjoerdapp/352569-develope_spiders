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
### first two pages, latest 20 news

### Conagra Brands Inc. 1|1
### 1st spider News room all releases, Investor NEWS RELEASES seem to be subset of all news reelases
### classic post with xpath
### back to 20031124


class QuotessSpider(scrapy.Spider):
    name = 'ConagraBrands_2049500ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/ConagraBrands_2049500ARV001/',
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
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            #'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.conagrabrands.com',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            #'Referer': 'https://www.cmsenergy.com/investor-relations/news-releases/default.aspx',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }
        
        #cookies = {'_evidon_consent_cookie' : '{"consent_date":"2019-10-10T15:08:04.554Z"}',
        #            '_ga': 'GA1.2.2026785616.1570720088',
        #            #'cookieconsent_status': 'dismiss',
        #            '_gid': 'GA1.2.1978920602.1570720088',
        #            }

        data = {'view_name': 'news_landing_page',
                'view_display_id': 'page_news_releases_landing',
                'view_args': '',
                'view_path': '%2Fnews-room',
                'view_base_path': 'news-room',
                'view_dom_id': '05fc0051ee561540f2a4ba90f20c46d7aaac3e988f70d16edfc70e87f6b6f1b6',
                'pager_element': '0',
                'news-release-category': 'All',
                'news-release-year': 'All',
                'page': '1',
                '_drupal_ajax': '1',
                'ajax_page_state%5Btheme%5D': 'corporate',
                'ajax_page_state%5Btheme_token%5D': '',
                'ajax_page_state%5Blibraries%5D': 'conagra_corp_animated_blocks%2Fmain%2Cconagra_full_bleed%2Ffull_bleed_module%2Cconagra_gtm%2Fcrownpeak%2Ccore%2Fhtml5shiv%2Ccorporate%2Fglobal%2Ccorporate%2Fview-page-news-landing%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cviews_infinite_scroll%2Fviews-infinite-scroll',
                }

        for num in range(0, 2):  # 103loop iterating over different pages of ajax request
            data['page'] = str(num)
            s_url = 'https://www.conagrabrands.com/views/ajax?_wrapper_format=drupal_ajax'
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
              


    def parse(self, response):
          body = json.loads(response.text)
          key = list(body[3].keys())
          if not 'data' in key:
            auxs = Selector(text=body[4]['data']).xpath('//ul[@class="news-release-list"]/li')

          else:
            auxs = Selector(text=body[3]['data']).xpath('//ul[@class="news-release-list"]/li')



          
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date")]/div/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.conagrabrands.com'
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
        name_regex_2=r'(\bAbout\s*Conagra)(.|\s)*|(\bAbout.Conagra\b)(.|\s)*|(\bABOUT.Conagra\b)(.|\s)*|(\bABOUT\s*.CONAGRA\b)(.|\s)*|(\bAbout\s*ConAgra)(.|\s)*|(\bAbout.ConAgra\b)(.|\s)*|(\bABOUT.ConAgra\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="block- basic"]//text()[not(ancestor::h1 or ancestor::h2 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       