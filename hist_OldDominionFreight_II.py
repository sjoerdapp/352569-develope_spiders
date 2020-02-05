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

### Old Dominion Freight Line Inc Inc 1|2
### 1st spider Investor Press Releases, 2nd spider News releases
### normal pos woth xpath, 
### back to 20160504


class QuotessSpider(scrapy.Spider):
    name = 'OldDominionFreight_II_1116100ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/OldDominionFreight_II_1116100ARV002/',
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
            'ADRUM': 'isAjax:true',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Faces-Request': 'partial/ajax',
            'Origin': 'https://www.odfl.com',
            'Referer': 'https://www.odfl.com/News/',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            #'X-Requested-With': 'XMLHttpRequest',
           }
        
        cookies = {'JSESSIONID': '0WXTCHOJz_A-0BybBYfEAz2ZzerS1sdAL2lyP3Kh.node7',
                   '_gcl_au': '1.1.719504077.1579805358',
                   '_ga': 'GA1.2.960952932.1579805358',
                   '_gid': 'GA1.2.1181630037.1579805358',
                   '_fbp': 'fb.1.1579805358125.1486871613',
                   'DCID': 'DC1',
                   'OptanonAlertBoxClosed': '2020-01-23T18:49:24.979Z',
                   'citrix_ns_id': 'dp7rGf8S0t5WSjvXIm+IEIhGnUU0001',
                   'citrix_ns_id_.odfl.com_%2F_wat': 'AAAAAAWnkaXb7DNwbUQ88B7_s14SuINlz7LcFPBqeSzjjTKKPxUdtJJlSDDfNSnAcXS5m0rvqYJHcjTlCzmxyY6oYuOV#y9xwya9VULI97Pik2+Y+nLaxs1MA&AAAAAAUGNQmCbXbkv8FYFgKrL4Hiv1W8bge2Yn-DWjht71xQV0IbeYibkYW-RwWSq_bBRWSLc4xUK0Tp-O5mg68cljMp#i+xozoEgOSC5MbnASmWInDfX7BwA&',
                   'ak_bmsc': 'E3BBA65D451B197EA3D28441AA9502F602179B04E72A000051292B5EFDF98061~plo4tu01exKczrwsf90FYfaWX3lKio4x9/ZjuWXMewKSm7SEf+BzQbjdJ5RySJhOVNZk9P6wr2RpyKQU2LJof98w8SLdEEuiub3PnY/pSL3Qt59OIK8RtKhCUFB1FdIB8Nn/ncETZTP25gSnQhAg2SlBKt/meMnby8eOyh021oILrHC//2iAKM0P3QpxEVTVa4Ezie9X1YWTd8eyyzXWzcGUctbnmCLvidyZG5i6Q89yHPB1L5UBhIreKtDVKX6bO0',
                   'OptanonConsent': 'isIABGlobal=false&datestamp=Fri+Jan+24+2020+18%3A28%3A52+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=5.10.0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&hosts=&consentId=c572dd7d-632d-4fda-9c87-d5cfc611c7a6&interactionCount=1&geolocation=CH%3BBS&AwaitingReconsent=false'
                   }

        data = {'newsFeed': 'newsFeed',
                'newsFeed:year': '2019',
                'newsFeed:category': 'all',
                'javax.faces.ViewState': '-1403843491905107044:7991286736957761190',
                'as_sfid': 'AAAAAAUDfcxexwa1ChStxA59uclffj-Em3oteqveTS7mRcKBgcZJmWDU18B_CIFJdrOlSOQOM9jYyeyc7mjWKyu69st08bLYxLadhQfgLOKMZRfKUmencO6grigX94a7p5TN51U=',
                'as_fid': '8678b442ac16d2f863742cddc0928613735c25c2',
                'javax.faces.source': 'newsFeed:year',
                'javax.faces.partial.event': 'change',
                'javax.faces.partial.execute': 'newsFeed:year newsFeed:category newsFeed:header newsFeed:newsArticles',
                'javax.faces.partial.render': 'newsFeed:year newsFeed:category newsFeed:header newsFeed:newsArticles',
                'javax.faces.behavior.event': 'valueChange',
                'javax.faces.partial.ajax': 'True'}

        for num in range(2016,2020):  # loop iterating over different pages of ajax request
            data['newsFeed:year'] = str(num)
            s_url = 'https://www.odfl.com/News/index.faces'
            yield FormRequest(url=s_url, formdata=data, headers=headers, cookies=cookies, callback=self.parse )
              


    def parse(self, response):
          body = response.text.split('CDATA[')[2].split(']')[0]
          auxs = Selector(text=body).xpath('//div[@id="newsFeed:j_idt33"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//p/strong/text()').extract_first().split('(')[1].split(')')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.odfl.com'
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
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="block- basic"]//text()[not(ancestor::h1 or ancestor::h2 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       