import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Ametek Inc 2|2
###  2nd spider Product and business news;
### only difference is announcements regarding presentations at industrial conferences, eg. 20161104
### post request with payload
### history back to 2014, also page only goes to 2016

class BHGE(scrapy.Spider):
    name = "Ametek_II_3205400ARV002"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Ametek_II_3205400ARV002/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=cggg2scdibyaygxt2wajnhz1; ametek#lang=en; sxa_site=ametek; _ga=GA1.2.1082766406.1550514435; _gid=GA1.2.1286491396.1550514435; SC_ANALYTICS_GLOBAL_COOKIE=e7a3fc0d94fc4d318afe7a94acf15376|True; _gat=1; __unam=3427471-16901dce324-c354e93-15; AWSALB=Wrx/VjmCODFncwOkp0W+H0Kkr6kYICk8io8xCDhWBMc3uXU8S+w9l0m0k4ehY/OicNBvq8C8Ebc9Ho4QuCSNQOQH9Agp7qokxF5YvkhYWrAPHqmzOGg+Btx8Pz5a; site24x7rumID=2822201765689083.1550514432822',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.ametek.com',
            'Referer': 'https://www.ametek.com/pressreleases/productnews',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        datas = [{"resultsAlreadyRendered":"0","countResultsToFetch":"30","yearFolder":"/2020","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"200","yearFolder":"/2019","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"100","yearFolder":"/2018","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"100","countResultsToFetch":"50","yearFolder":"/2018","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"{3F315F9A-FFEC-4C8D-98BA-CCA96214BAD1}","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"100","yearFolder":"/2017","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"100","countResultsToFetch":"10","yearFolder":"/2017","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"{4A6E9F36-4A14-46F7-AED0-8880F7CF6D00}","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"90","yearFolder":"/2016","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"90","countResultsToFetch":"50","yearFolder":"/2016","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"{823B5E12-8F0D-4272-B5A8-E61951D174E8}","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"100","yearFolder":"/2015","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"100","countResultsToFetch":"50","yearFolder":"/2015","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"{239B1B14-49FB-46B3-944D-2FF393D47D02}","homeNodeName":"Ametek;web;en"},
                {"resultsAlreadyRendered":"0","countResultsToFetch":"200","yearFolder":"/2014","newsTags":"{11FFA60B-F40E-4C7C-9D59-DA29845B22E0};{2F5CA473-70B2-4B12-8ED0-75E5079F0FBA};{6CC64C86-60C8-4E4B-8925-CCF85D305CFF};{CE21931A-7D59-4D34-BCA0-CCAB63B2D043}","languageName":"en","lastShownItemId":"","homeNodeName":"Ametek;web;en"},]
        


        for data in datas:#list(range(2014, 2021)):  # loop iterating over different pages of ajax request
            #data["yearFolder"] = '/' + str(year)
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(AMETEK.\s*Inc..?\s*(\(\s*www.wabtec.com\s*\)\s*)?is\s*a\s*leading\s*global\s*(provider|manufacturer))(.|\s)*'
        name_regex_2=r'(\bAbout\s*Ametek)(.|\s)*|(\bAbout\s*AMETEK\b)(.|\s)*|(\bABOUT.Ametek\b)(.|\s)*|(\bABOUT\s*AMETEK\b)(.|\s)*|(\bCorporate\s*Profile\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="rte_content"]//text()').extract()))
        item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
        item['DOCLINK'] = response.url
        yield item
        #if not item['DESCRIPTION']:
        #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*SBA\s*Communications\b)(.|\s)* |(\bAbout.SBA.Communications\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
        #    yield item
        #else:     
        #    yield item
           



        
            