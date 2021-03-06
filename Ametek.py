import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### do not neeed investor page scraped for that porpus
### Ametek Inc 1|2
### 1 spider corporate and financial releases, 2nd spider Press Releases;
### there exists an IR site 'http://phx.corporate-ir.net/phoenix.zhtml?c=104638&p=irol-news&nyo=3' but seems it has the same news as the Corporate and Financial Releases
### only difference is announcements regarding presentations at industrial conferences, eg. 20161104
### post request with payload
### history back to 2014, also page only goes to 2016

class BHGE(scrapy.Spider):
    name = "Ametek_I"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Ametek_I/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=cggg2scdibyaygxt2wajnhz1; ametek#lang=en; sxa_site=ametek; _ga=GA1.2.1082766406.1550514435; _gid=GA1.2.1286491396.1550514435; SC_ANALYTICS_GLOBAL_COOKIE=e7a3fc0d94fc4d318afe7a94acf15376|True; __unam=3427471-16901dce324-c354e93-6; AWSALB=jan3dW448kS9KSXshRtttMxxg8u58nuqAK1v6F1+10yVWqwBfoLVl4ZTl9b78Bbf5sfPCAr+elg9qsDfMcOlL5F5Ow+wMzHSXEF9OMBA/ftp5+ct91aFZwZ6BZzf; site24x7rumID=2822201765689083.1550515037643',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.ametek.com',
            'Referer': 'https://www.ametek.com/pressreleases/corporateandfinancialnews',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        data = {"resultsAlreadyRendered":"0","countResultsToFetch":"50","yearFolder":"/2018","newsTags":"{37086DDC-6D24-4A42-B2D6-676575BD3104};{15CFED0E-39EE-40FD-A8BE-4112166C40AE}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"}
        for year in list(range(2014, 2020)):  # loop iterating over different pages of ajax request
            data["yearFolder"] = '/' + str(year)
            s_url = 'https://www.ametek.com/GlobalSearch.asmx/GetNews'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        dats = json.loads(body['d'])
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in dats:
            item = {
                      'PUBSTRING': dat["NewsDate"],
                      'HEADLINE': dat["NewsTitle"],
                      'DOCLINK': dat["NewsUrl"],
                      }
            base_url = 'https://www.ametek.com'
            url= base_url + dat["NewsUrl"]
            if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = dat["NewsDate"]
                item['HEADLINE']= dat["NewsTitle"]
                item['DOCLINK']= url
                yield item 

    def parse_details(self, response):
        item = response.meta['item']
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*SBA\s*Communications\b)(.|\s)* |(\bAbout.SBA.Communications\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="rte_content"]//text()').extract()))
        item['DOCLINK'] = response.url
        yield item
        #if not item['DESCRIPTION']:
        #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*SBA\s*Communications\b)(.|\s)* |(\bAbout.SBA.Communications\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
        #    yield item
        #else:     
        #    yield item
           



        
            