import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Ameren Corporation 1|1
### investor page press releases
### classical post request
### dat goes back to 20120109


class BHGE(scrapy.Spider):
    name = "Ameren_2180800ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Ameren_2180800ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'bpazaws52gukakzc__ctrl0_ctl39_uccaptcha=cItdn1fgrJ69F1ILLeynSP9/KmkqdnYRtao6NHHJwwb3WCYVGWZ0gAAzIq26ZByZY5LOYUGeju0bPAsfH3CGBVm1HdRWZpMzdPME5Pv8zPEQ6O6WZy2Smj9yiCMAIA4RU0QPirGbdBtgzh63zeZeoQ==',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.amereninvestors.com',
            'Referer': 'https://www.amereninvestors.com/investor-news-and-events/financial-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseBodyType":0,"pressReleaseCategoryWorkflowId":"00000000-0000-0000-0000-000000000000","pressReleaseSelection":3,"year":2018}
        for year in list(range(2012, 2020)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://www.amereninvestors.com/Services/PressReleaseService.svc/GetPressReleaseList'
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
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['PressReleaseDate']
            item['HEADLINE'] = dat['Headline']
            item['DOCLINK'] = dat['LinkToDetailPage']
            #item = {
            #          'PUBSTRING': dat['PressReleaseDate'],
            #          'HEADLINE': dat['Headline'],
            #          'DOCLINK': dat['LinkToDetailPage'],
            #          }
            base_url = 'https://www.amereninvestors.com'
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
                item['DESCRIPTION'] = ''
                yield item 

    def parse_details(self, response):
        item = response.meta['item']
        ### Achtung (Forward(.|\s*)Looking\s*Statements)(.|\s)*| cuts out important part of ERNA
        name_regex = r'(Statements\s*in\s*this\s*release\s*not\s*based\s*on\s*historical\s*facts\s*are\s*considered)(.|\s)*|(St.\s*Louis\s*.\s*based\s*Ameren\s*Corporation\s*powers\s*the\s*quality)(.|\s)*|(\bAbout\s*Ameren\s*Corporation\b)(.|\s)* |(\bAbout.Ameren.Corporation\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        #yield item
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
        else: 
            yield item
           



        
            