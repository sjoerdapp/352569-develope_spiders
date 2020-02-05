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

### McCormick & Company Incorporated 1|2
### 2nd spider News Center
### normal get with json 
### back to 20141211


class QuotessSpider(scrapy.Spider):
    name = 'Copart_java_test'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Copart_java_test/',
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
    #start_urls = ['https://www.copart.com/CMS/en/Content/us/en/Press-Releases/Index']

    def start_requests(self):
          cookies = {'visid_incap_242093': 'hNdQyqTwTEC1aTSkenP+XNnzlF0AAAAAQUIPAAAAAAA74AecfgRCt51IIGUlpO8y',
           '_ga': 'GA1.2.2083824430.1570042845',
           '_fbp': 'fb.1.1570042845432.1489735536',
           's_fid': '047F10C633DB0B0F-29600A9B268F541E',
           's_vi': '[CS]v1|2ECA7C2805311BE5-4000019260005AB1[CE]',
           'userLang': 'en',
           '_gid': 'GA1.2.593559968.1574172423',
           'copartTimezonePref': '%7B%22displayStr%22%3A%22CET%22%2C%22offset%22%3A1%2C%22dst%22%3Afalse%2C%22windowsTz%22%3A%22Europe%2FBerlin%22%7D',
           'timezone': 'Europe%2FBerlin',
           's_ev1': 'web_footer_pressreleases_en',
           's_cc': 'true',
           'g2usersessionid': 'e792fb427388bfbfd2f6d8c82163d763',
           'G2JSESSIONID': 'ED9F85BA3DDA5EF39C013F6389CCEFDC-n1',
           'incap_ses_578_242093': 'mGCqEr37girjWOuvl3gFCLQW1V0AAAAA2MA6YyjVXmDUuElGXG3szA==',
           's_pv': 'public%3APress-Releases-Index',
           's_vnum': '1576764423849%26vn%3D2',
           's_invisit': 'true',
           's_lv_s': 'Less%20than%201%20day',
           's_depth': '2',
           's_ppvl': 'public%253APress-Releases-Index%2C67%2C67%2C1089%2C1287%2C1089%2C1920%2C1200%2C1%2CP',
           's_nr': '1574246853730-Repeat',
           's_lv': '1574246853731',
           's_ppv': 'public%253APress-Releases-Index%2C83%2C83%2C1089%2C998%2C1089%2C1920%2C1200%2C1%2CL'}

          headers = {
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                      'Accept-Encoding': 'gzip, deflate, br',
                      'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                      'cache-control': 'max-age=0',
                      #'Content-Type': 'application/x-www-form-urlencoded; charset="UTF-8"',
                      'if-modified-since': 'Tue, 19 Nov 2019 20:53:12 GMT',
                      'if-none-match': 'W/"1574196792"',
                      'sec-fetch-mode': 'navigate',
                      'sec-fetch-site': 'none',
                      'sec-fetch-user': '?1',
                      'upgrade-insecure-requests': '1',
                      #'Cookie': 'ASP.NET_SessionId=wfjwtsuin1uafxe0x3oker1v; __RequestVerificationToken=QZpcBObmxUahsdj6xiNbLxayo8KGrV8NzkyPHG1lDFqUtqTIP43LRx3R4R4IkKTmVP1wR8KFMS_yISLxgBZ4w9KD9wI1; visid_incap_1246096=nu9KgX4GRbu+o2Vne+eawwktTlwAAAAAQUIPAAAAAAByH42r0JBEzG3yLY+HSfNu; resolution=1280; _ga=GA1.2.2143087210.1548627217; _gid=GA1.2.2052215443.1548627217; SC_ANALYTICS_GLOBAL_COOKIE=1a70df17b7a44f05b12fcc8f44eb006f|True; com.silverpop.iMAWebCookie=e6825de4-ce53-b87c-d433-c4e2a8d3c4c7; __atssc=google%3B1; notice_preferences=2:; notice_gdpr_prefs=0,1,2:; wtw#lang=en; s_cc=true; s_sq=%5B%5BB%5D%5D; TS0121b28a=01324cfcfdb153d0897d989eaec0ed1cc276d7cb94240d88e802eb66a90dd1eb377a64a91bcbbd3f93f7b9ad868d169863316919bd3a422b2bcb39b6e55011a922248f695dfab953cf1f0d8de39498458493472627a6e3b8ed973ccce9ef44a7791d809bad3b52a3744d062b7276183cd52dc1011b48879101bdd780ef2d314e569c43d330; incap_ses_699_1246096=12UZEJSDv184nLKEiFmzCT85TlwAAAAATFjqQuwIXYVksE2dsz+rpA==; _gat_UA-69683604-1=1; com.silverpop.iMA.session=4ec61dc9-91a3-4a8c-3226-074345e85bdb; com.silverpop.iMA.page_visit=1172829324:; __atuvc=4%7C5; __atuvs=5c4e394526deaf69000',
                      #'Origin': 'https://www.willistowerswatson.com',
                      #'Referer': 'https://www.willistowerswatson.com/en/press',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                      }
          s_url = 'https://www.copart.com/CMS/en/Content/us/en/Press-Releases/Index'
          yield scrapy.Request(s_url, method='GET', headers=headers, cookies=cookies, callback=self.parse)
    #     years = list(range(0, 80, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.mccormickcorporation.com/api/sitecore/CORP18_generated_listing_with_filter?num_items=3&current_count={}&rootGuid=d0952d7d-aeea-4538-8c3f-0ad5cf3a95b7&templateGuids=02c1d0aa-0111-44a3-a3f0-5215df2d176f,9bdac2ca-5678-4cd7-84d8-21f5189f153a&category=All'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          item = {'text' : response.text}
          yield item
          #data = re.findall("var articles =(.+?);\n", response.body.decode("utf-8"), re.S)
          #if data:
          #  body = json.loads(data[0])
          #if body:
          #  print (body)
          #for aux in body['press_releases']:
          #    item = SwisscomIvCrawlerItem()
          #    item['PUBSTRING'] = aux['publish_date'] # cuts out the part berfore the date as well as the /n at the end of the string
          #    item['HEADLINE']= aux['title']
          #    item['DOCLINK']= aux['url']
          #    #item = {
          #    #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
          #    #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
          #    #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
          #    #        }
          #    base_url = 'https://www.l3harris.com/press-releases'
          #    aux_url = item['DOCLINK']
          #    
          #    if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
          #      if aux_url.startswith('http'):
          #          url= aux_url
          #          item['file_urls'] = [url]
          #          item['DOCLINK'] = url
          #          item['DESCRIPTION'] = ''
          #          yield item
          #      
          #      else:
          #          url= base_url + aux_url
          #          item['file_urls'] = [url]
          #          item['DOCLINK'] = url
          #          item['DESCRIPTION'] = ''
          #          yield item
          #    else:
          #      if aux_url.startswith('http'):
          #          url= aux_url
          #          request = scrapy.Request(url=url, callback=self.parse_details)
          #          request.meta['item'] = item
          #          yield request
          #          
          #      
          #      else:
          #          url= base_url + aux_url
          #          request = scrapy.Request(url=url, callback=self.parse_details)
          #          request.meta['item'] = item
          #          yield request
               
        
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
       
       