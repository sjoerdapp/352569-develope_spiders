
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
### latest 20 news hence first two pages

### International Paper Company 1|1
### spider scraping news room
### klassisch json with aspx
### goes back to 20040107


class BHGE(scrapy.Spider):
    name = "Inter_Pap_2099400ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Inter_Pap_2099400ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': '_ga=GA1.2.2127427800.1549558903; _gid=GA1.2.583084637.1549558903',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'http://internationalpaper2015.q4web.com',
            'Referer': 'http://internationalpaper2015.q4web.com/news-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"e6b27ee9-9f40-4656-bc8c-c8b8562fe8a2","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2015}
        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","ItemCount":10,"StartIndex":0,"Signature":""},"pressReleaseSelection":3,"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","year":-1}
        for year in list(range(0, 12, 10)):  # loop iterating over different pages of ajax request
            data['serviceDto']["StartIndex"] = year
            s_url = 'http://internationalpaper2015.q4web.com/Services/PressReleaseService.svc/GetPressReleaseList'
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
            item['HEADLINE']= dat['Headline']
            item['DOCLINK']= dat['LinkToDetailPage']
            #item = {
            #          'PUBSTRING': dat['PressReleaseDate'],
            #          'HEADLINE': dat['Headline'],
            #          'DOCLINK': dat['LinkToDetailPage'],
            #          }
            base_url = 'http://internationalpaper2015.q4web.com'
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
        name_regex = r'(International\s*Paper\s*\(\s*NYSE\s*:\s*IP\s*\)\s*is\s*a\s*global\s*paper\s*and\s*packaging\s*company)(.|\s)*|(Headquartered\s*in\s*the\s*United\s*States.\s*International\s*Paper)(.|\s)*|(Statements\s*in\s*this\s*news\s*release\s*that\s*are\s*not\s*historical\s*are\s*forward.\s*looking.)(.|\s)*|(Statements\s*in\s*this\s*press\s*release\s*that\s*are\s*not\s*historical\s*are\s*forward.\s*looking.)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*International\s*Paper\b)(.|\s)* |(\bAbout.International.Paper\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex ,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex ,'' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not item['DESCRIPTION']:
                pdf_url = response.xpath('//div[@class="ModuleLinks"]/a/@href').extract_first() #.encode("utf-8")
                help_url = 'https:'
                url = help_url + pdf_url
                item['file_urls'] = [url]
                item['DOCLINK']= url
                item['DESCRIPTION'] = ''
                yield item
            else: 
                yield item
        else:     
            yield item
           



        
            