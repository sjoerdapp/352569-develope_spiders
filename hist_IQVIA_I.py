import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem



### Iqvia Holdings Inc 1|4
### 1st - 3rd spider IR Press Releases, 1st, after merger, 2nd vor merger Quintiles, 3rd vor merger IMS, 4th Newsroom
### complex post with cookies etc.
### some cookies have datatimes -> check if they still work and eventually adjust them
### back to 20161003

class BHGE(scrapy.Spider):
    name = "IQVIA_I_9900204ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IQVIA_I_9900204ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=wfjwtsuin1uafxe0x3oker1v; __RequestVerificationToken=QZpcBObmxUahsdj6xiNbLxayo8KGrV8NzkyPHG1lDFqUtqTIP43LRx3R4R4IkKTmVP1wR8KFMS_yISLxgBZ4w9KD9wI1; visid_incap_1246096=nu9KgX4GRbu+o2Vne+eawwktTlwAAAAAQUIPAAAAAAByH42r0JBEzG3yLY+HSfNu; incap_ses_699_1246096=HiaqBZ7M32/A/7CEiFmzCQotTlwAAAAAI9fEn5aBkIKfUs8LfwPi/w==; resolution=1280; _ga=GA1.2.2143087210.1548627217; _gid=GA1.2.2052215443.1548627217; SC_ANALYTICS_GLOBAL_COOKIE=1a70df17b7a44f05b12fcc8f44eb006f|True; com.silverpop.iMAWebCookie=e6825de4-ce53-b87c-d433-c4e2a8d3c4c7; com.silverpop.iMA.session=4a39918a-e64c-5844-9911-e72b9397c21b; __atssc=google%3B1; notice_preferences=2:; notice_gdpr_prefs=0,1,2:; wtw#lang=en; TS0121b28a=01324cfcfdfb57d0358aa556081f9d4ff643b444b077a75b91f442ab3d165868768e18339207dcd1c3cb461452c31a365a10df7804d0c3658a38ae5a93c5757a5d7261b214e4d88545290dc90cb4c247a842e198f4193303f594dca76eae250c22c98768f4b899bf599b585668b8c0efa92d60f4814d5ff61fc373f6a118f609bba6c77a59; s_cc=true; com.silverpop.iMA.page_visit=-914277475:1172829324:47:; __atuvc=3%7C5; __atuvs=5c4e2d11e1e41c02002; s_sq=%5B%5BB%5D%5D; _gat_UA-69683604-1=1',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://ir.iqvia.com',
            'Referer': 'https://ir.iqvia.com/investors/press-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        for year in list(range(2016, 2020)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://ir.iqvia.com/Services/PressReleaseService.svc/GetPressReleaseList'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        auxs = body['GetPressReleaseListResult']
        for dat in auxs:
            item = SwisscomIvCrawlerItem()
            item = {
                      'PUBSTRING': dat['PressReleaseDate'],
                      'HEADLINE': dat['Headline'],
                      'DOCLINK': dat['LinkToDetailPage'],
                      }
            base_url = 'https://ir.iqvia.com'
            url= base_url + dat['LinkToDetailPage']
            if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = dat['PressReleaseDate']
                item['HEADLINE']= dat['Headline']
                item['DOCLINK']= url
                yield item 

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*IQVIA\b)(.|\s)* |(\bAbout.IQVIA\b)(.|\s)*|(\bAbout\s*QuintilesIMS\b)(.|\s)* |(\bAbout.QuintilesIMS\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub( name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            yield item
        else:     
            yield item
           



        
            