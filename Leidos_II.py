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

### Leidos Holdings Inc 1|2
### 1st spider Investor NEWS RELEASES, 2nd spider Insights
### Achtung hat problem mit dem encoding....vermutlich liegt es an der request
### classic post
### back to 20150105


class QuotessSpider(scrapy.Spider):
    name = 'Leidos_II_5133800ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Leidos_II_5133800ARV002/',
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
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.leidos.com',
            'Referer': 'https://www.leidos.com/insights?type=191',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }
        
        cookies = {'__cfduid': 'db5b9d38c17c3439f60b22af1328bc15d1576670585',
                   's_cc': 'true',
                   's_fid': '6DC591A271104031-3BF2385E9A2CFCB6',
                   's_sq': '%5B%5BB%5D%5D',
                   'tc_ptidexpiry': '1639742604330',
                   'tc_ptid': '6xgPTK7ejmjxi3Td4Ps8Hv',
                   'tc_ttid': '6v4F0FnwqhmffNQm7rfMsU',
                   '_ga': 'GA1.2.834529541.1576670605',
                   '_gid': 'GA1.2.433256756.1576670605',
                   '_mkto_trk': 'id:059-GQO-645&token:_mch-leidos.com-1576670605021-48180',
                   'nmstat': '1576670626767',
                   '_fbp': 'fb.1.1576670605320.1503740152',
                   '__qca': 'P0-107429144-1576670605409',
                   'OptanonAlertBoxClosed': '2019-12-18T12:04:04.292Z',
                   'contently_insights_user': 'd9eccp4fff6efdcod042',
                   'OptanonConsent': 'isIABGlobal=false&datestamp=Wed+Dec+18+2019+13%3A26%3A08+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=5.7.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_115232%3A1%2C0_132215%3A1%2C0_239439%3A1%2C0_206300%3A1%2C0_184359%3A1%2C102%3A1%2C104%3A1%2C106%3A1%2C111%3A1%2C117%3A1%2C131%3A1&AwaitingReconsent=false',
                   'x_contently_id:32bd1167402c46680bdfdf86a0c511b7': '{"s_id":"32bd1167402c46680bdfdf86a0c511b7","user_id":"d9eccp4fff6efdcod042","set_ts":1576670688414}',
                   '_gat_UA-75469281-7': '1',
                   }

        data = {'view_name': 'insights_overview',
                'view_display_id': 'block_1',
                'view_args': '',
                'view_path': '%2Finsights',
                'view_base_path': 'insights-overview-test',
                'view_dom_id': 'f1ed4ed4fc5eb3b51a473a1d74aad46241ccaebf3ac8a3af30f08e1e6166c7e8',
                'pager_element': '0',
                'type': '191',
                'market': 'All',
                'competency': 'All',
                'community': 'All',
                'page': '1',
                '_drupal_ajax': '1',
                'ajax_page_state%5Btheme%5D': 'leidos',
                'ajax_page_state%5Btheme_token%5D': '',
                'ajax_page_state%5Blibraries%5D': 'better_exposed_filters%2Fauto_submit%2Cbetter_exposed_filters%2Fgeneral%2Cclassy%2Fbase%2Cclassy%2Fmessages%2Cclassy%2Fnode%2Ccore%2Fhtml5shiv%2Ccore%2Fnormalize%2Clazy%2Flazy%2Cleidos%2Faccordion%2Cleidos%2Fchosen%2Cleidos%2Fhero_video%2Cleidos%2Finline_video%2Cleidos%2Finsights_overview%2Cleidos%2Fleidos%2Cleidos%2Fmarketo_modal%2Cleidos%2FmatchHeight%2Cleidos%2FreadTime%2Cleidos%2FstickyJumpNav%2Cleidos%2Ftabs%2Cleidos_jobs%2Fjob_search%2Comega%2Fomega_branding%2Comega%2Fomega_breadcrumbs%2Comega%2Fomega_forms%2Comega%2Fomega_html_elements%2Comega%2Fomega_main_menus%2Comega%2Fomega_messages%2Comega%2Fomega_pagers%2Comega%2Fomega_tabs%2Comega%2Fomega_taxonomy_terms%2Cparagraphs%2Fdrupal.paragraphs.unpublished%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cviews_infinite_scroll%2Fviews-infinite-scroll'
                }
        
        for num in range(0,2):  # loop iterating over different pages of ajax request
            data['page'] = str(num)
            s_url = 'https://www.leidos.com/views/ajax?type=191&_wrapper_format=drupal_ajax'
            yield FormRequest(url=s_url, formdata=data, headers=headers, cookies=cookies, callback=self.parse )
              


    def parse(self, response):
          body = body = json.loads(response.body.decode('utf-8'))
          auxs = Selector(text=body[2]['data']).xpath('//ul[@class="news-release-list"]/li')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              #item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date")]/div/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//p[@class="title lead"]/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.leidos.com/'
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
            item['PUBSTRING'] = response.xpath('//span[@class="field field--name-created field--type-created field--label-hidden"]/text()').extract_first()
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="clearfix text-formatted field field--name-field-formatted-text field--type-text-long field--label-hidden field__item"]//text()[not(ancestor::h1 or ancestor::h2 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       