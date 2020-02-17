import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrape actual year, if more than 20 news, cut off


### Twitter Inc 1|2
### 1st spider Investor 2nd spider blog
### 1st spider Investor
### classic combo post request.payload + json
### post request using payload not form data
### content comes as standart json with payload
### Description taken from pdf 


class BHGE(scrapy.Spider):
    name = "twitter_I_9900249ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/twitter_I_9900249ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': '_ga=GA1.2.1216204916.1547660679',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://investor.twitterinc.com',
            'Referer': 'https://investor.twitterinc.com/financial-information/financial-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseBodyType":3,"pressReleaseSelection":3,"pressReleaseCategoryWorkflowId":"00000000-0000-0000-0000-000000000000","excludeSelection":1,"year":2018}
        for year in list(range(2019, 2021)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        body = body['GetPressReleaseListResult']
        if len(body) >20:
            body = body[0:20]

        for dat in body:
            item = SwisscomIvCrawlerItem()
            #item['file_urls'] = [dat['DocumentPath']]
            item['PUBSTRING'] = dat['PressReleaseDate']
            item['HEADLINE']= dat['Headline']
            item['DOCLINK']= dat['LinkToDetailPage']
            
            base_url = 'https://investor.twitterinc.com'
            aux_url = dat['LinkToDetailPage']
            
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


            #item['DESCRIPTION'] = ''
            #if not re.search('[a-zA-Z]', item['file_urls'][0]):
            #    base_url = 'https://s22.q4cdn.com/826641620' 
            #    item['DOCLINK']= base_url + dat['LinkToDetailPage']
            #    item['file_urls'] = [base_url + dat['LinkToDetailPage']]
            #    yield item
            #else:
            #    yield item
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Twitter(.|\s*) Inc)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            twitter_reg = r'(Twit\s*\d.jpg)|(twitter\s*\d\s*a.jpg)|(TWTR13Q4.\d+.jpg)|(twitter\s*\d.jpg)'
            item['DESCRIPTION'] = re.sub( twitter_reg, '', re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE))
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = ''
                yield item
            else:
                yield item
           



        
            