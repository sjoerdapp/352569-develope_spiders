import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Iqvia Holdings Inc 3|4
### 2nd vor merger IMS, 
### classic post
### starts 20160904
### back to 20140102

class BHGE(scrapy.Spider):
    name = "IQVIA_III_IMS_9900204ARV003"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IQVIA_III_IMS_9900204ARV003/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': '_ga=GA1.2.457028218.1549013158; _gid=GA1.2.1122027351.1549013158; _gcl_au=1.1.2142990333.1549013158; coveo_visitorId=f5edb1dd-96b2-4dc9-8838-0701ce655475; bpazaws52gukakzc__ctrl0_ctl48_uccaptcha=0WiZX8eHpjPDgS56EMiZUQXMi0SdaKsJUhhf0NHk3Y2eTU3ZEuT+kQyed5kWXnklw536SkBTu91N8jFYl7+UYczKGdodmCgGhmKVo9uYIUIrUM9WcI8YfAt5brSkTDI6xUgAM4UjaW6/sraUwn7oLQ==; OptanonConsent=landingPath=NotLandingPage&datestamp=Fri+Feb+01+2019+19%3A15%3A09+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=3.6.15&groups=1%3A1&AwaitingReconsent=false; OptanonAlertBoxClosed=2019-02-01T18:15:09.658Z; lastTab=.module-tab--third',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://ir.iqvia.com',
            'Referer': 'https://ir.iqvia.com/investors/press-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"e6b27ee9-9f40-4656-bc8c-c8b8562fe8a2","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2015}
        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"d2e53d2f-4abe-4483-90a4-bf3f94fadf38","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2015}
        for year in list(range(2014, 2017)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://ir.iqvia.com/Services/PressReleaseService.svc/GetPressReleaseList'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in body['GetPressReleaseListResult']:
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*IMS\s*Health\b)(.|\s)* |(\bAbout.IMS.Health\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            yield item
        else:     
            yield item
           



        
            