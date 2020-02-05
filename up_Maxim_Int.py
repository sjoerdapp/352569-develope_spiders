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
### get actual year, if more than 20 news break

### Maxim Integrated Products Inc. 1|2
### 1st spider IR Press Releases, 2nd spider Newsroom
### two pages have different histories
### classic post with json, has some pdfs for earnings announcements
### goes back to 20020422

class BHGE(scrapy.Spider):
    name = "Maxim_Int_I_9698000ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Maxim_Int_I_9698000ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            #'Cookie': '_ga=GA1.2.9377599.1549202778; _gid=GA1.2.1210191223.1549202778; cookieAccept=true; _gat=1',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://investor.maximintegrated.com',
            'Referer': 'https://investor.maximintegrated.com/press-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseSelection":3,"pressReleaseBodyType":1,"pressReleaseCategoryWorkflowId":"00000000-0000-0000-0000-000000000000","year":2018}
        for year in list(range(2019, 2021)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://investor.maximintegrated.com/Services/PressReleaseService.svc/GetPressReleaseList'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        auxs = body['GetPressReleaseListResult']
        if len(auxs) > 20:
            auxs = auxs[0:20]

        for dat in auxs:
            item = {
                      'PUBSTRING': dat['PressReleaseDate'],
                      'HEADLINE': dat['Headline'],
                      'DOCLINK': dat['LinkToDetailPage'],
                      }
            base_url = 'https://investor.maximintegrated.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Maxim)(.|\s)*|(\bAbout.Maxim\b)(.|\s)*|(\bABOUT.Maxim\b)(.|\s)*|(\bABOUT\s*.MAXIM\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ,"".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
        item['DOCLINK'] = response.url
        #yield item
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ,"".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            yield item
        else:     
            yield item
           



        
            