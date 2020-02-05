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

### CenterPoint Energy 2|2
### 2nd spider News articles
### using splash as data comes in json within sourcecode
### data comes in sêcond XHR request....search in response
### request sends actual date CAUTION For Updates!
### back to 20020208


class QuotessSpider(scrapy.Spider):
    name = 'CenterP_II_2093900ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/CenterP_II_2093900ARV002/',
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
            'Content-Type': 'text/xml',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.centerpointenergy.com',
            'Referer': 'https://www.centerpointenergy.com/en-us/corporate/about-us/news',
            'Request-Context': 'appId=cid-v1:eea2d368-7c13-4c9c-90fb-3534ce473714',
            'Request-Id': '|msB+2.r0a3E',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-RequestDigest': '0x33872137A89571B21E50FA3AEF9DCC145CA91A370D922FE0C2753AB42BFF8E94E463D1DFB1D217C6D77FC153100090F1906F0E8A26DEF14D9EFEB81B32D6C980,24 Mar 2019 17:45:37 -0000',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = '''<Request xmlns="http://schemas.microsoft.com/sharepoint/clientquery/2009" SchemaVersion="15.0.0.0" LibraryVersion="15.0.0.0" ApplicationName="Javascript Library"><Actions><ObjectPath Id="1" ObjectPathId="0" /><SetProperty Id="2" ObjectPathId="0" Name="TimeZoneId"><Parameter Type="Number">11</Parameter></SetProperty><SetProperty Id="3" ObjectPathId="0" Name="QueryTemplate"><Parameter Type="String">(contentclass:sts_listitem OR IsDocument:True) SPSiteUrl:http://authoring.mycenterpointenergy.com ListId:241edddb-1443-40e4-9f7a-03d2d2191036&#10;(SchedulingStartDateOWSDateTime&lt;={Today} OR CalculatedStartDate:"Immediately")&#10;(SchedulingEndDateOWSDateTime&gt;={Today} OR CalculatedEndDate:"Never")&#10; ApprovalStatus=0</Parameter></SetProperty><ObjectPath Id="5" ObjectPathId="4" /><Method Name="Add" Id="6" ObjectPathId="4"><Parameters><Parameter Type="String">SchedulingStartDateOWSDateTime</Parameter><Parameter Type="Number">1</Parameter></Parameters></Method><SetProperty Id="7" ObjectPathId="0" Name="StartRow"><Parameter Type="Number">10</Parameter></SetProperty><SetProperty Id="8" ObjectPathId="0" Name="Culture"><Parameter Type="Number">-1</Parameter></SetProperty><SetProperty Id="9" ObjectPathId="0" Name="RowsPerPage"><Parameter Type="Number">10</Parameter></SetProperty><SetProperty Id="10" ObjectPathId="0" Name="RowLimit"><Parameter Type="Number">10</Parameter></SetProperty><SetProperty Id="11" ObjectPathId="0" Name="TotalRowsExactMinimum"><Parameter Type="Number">21</Parameter></SetProperty><SetProperty Id="12" ObjectPathId="0" Name="SourceId"><Parameter Type="Guid">{8413cd39-2156-4e00-b54d-11efd9abdb89}</Parameter></SetProperty><ObjectPath Id="14" ObjectPathId="13" /><Method Name="SetQueryPropertyValue" Id="15" ObjectPathId="13"><Parameters><Parameter Type="String">SourceName</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">Local SharePoint Results</Property></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="16" ObjectPathId="13"><Parameters><Parameter Type="String">SourceLevel</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">Ssa</Property></Parameter></Parameters></Method><SetProperty Id="17" ObjectPathId="0" Name="Refiners"><Parameter Type="String">RefinableString06(sort=name/ascending,filter=15/0/*),RefinableString08(sort=name/ascending,filter=15/0/*),RefinableString03(sort=name/descending,filter=15/0/*),owstaxIdCNPx0020Newsx0020Hierarchy(sort=frequency/ascending,filter=5/0/L*)</Parameter></SetProperty><ObjectPath Id="19" ObjectPathId="18" /><Method Name="Add" Id="20" ObjectPathId="18"><Parameters><Parameter Type="String">Path</Parameter></Parameters></Method><Method Name="Add" Id="21" ObjectPathId="18"><Parameters><Parameter Type="String">CNPImageOWSIMGE</Parameter></Parameters></Method><Method Name="Add" Id="22" ObjectPathId="18"><Parameters><Parameter Type="String">Title</Parameter></Parameters></Method><Method Name="Add" Id="23" ObjectPathId="18"><Parameters><Parameter Type="String">CNPContentBodyOWSHTML</Parameter></Parameters></Method><Method Name="Add" Id="24" ObjectPathId="18"><Parameters><Parameter Type="String"> PageOWSMTXT</Parameter></Parameters></Method><Method Name="Add" Id="25" ObjectPathId="18"><Parameters><Parameter Type="String">ListItemID</Parameter></Parameters></Method><Method Name="Add" Id="26" ObjectPathId="18"><Parameters><Parameter Type="String">PublishingStartDateOWSDATE</Parameter></Parameters></Method><ObjectPath Id="28" ObjectPathId="27" /><Method Name="Add" Id="29" ObjectPathId="27"><Parameters><Parameter Type="String">Title</Parameter></Parameters></Method><Method Name="Add" Id="30" ObjectPathId="27"><Parameters><Parameter Type="String">Path</Parameter></Parameters></Method><Method Name="Add" Id="31" ObjectPathId="27"><Parameters><Parameter Type="String">Author</Parameter></Parameters></Method><Method Name="Add" Id="32" ObjectPathId="27"><Parameters><Parameter Type="String">SectionNames</Parameter></Parameters></Method><Method Name="Add" Id="33" ObjectPathId="27"><Parameters><Parameter Type="String">SiteDescription</Parameter></Parameters></Method><SetProperty Id="34" ObjectPathId="0" Name="TrimDuplicates"><Parameter Type="Boolean">false</Parameter></SetProperty><Method Name="SetQueryPropertyValue" Id="35" ObjectPathId="13"><Parameters><Parameter Type="String">TryCache</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">true</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">3</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="Null" /></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="36" ObjectPathId="13"><Parameters><Parameter Type="String">UpdateLinksForCatalogItems</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">true</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">3</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="Null" /></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="37" ObjectPathId="13"><Parameters><Parameter Type="String">EnableStacking</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">true</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">3</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="Null" /></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="38" ObjectPathId="13"><Parameters><Parameter Type="String">ListId</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">f6253504-da34-46a8-96e1-b3ab1fc576aa</Property></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="39" ObjectPathId="13"><Parameters><Parameter Type="String">ListItemId</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">1962</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">2</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="Null" /></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="40" ObjectPathId="13"><Parameters><Parameter Type="String">Timeout</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">60000</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">2</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="Null" /></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="41" ObjectPathId="13"><Parameters><Parameter Type="String">TermId</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">2f384e53-6085-4ddd-ade2-e8687085c1eb</Property></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="42" ObjectPathId="13"><Parameters><Parameter Type="String">TermSetId</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">b96eed18-e586-499d-8747-c51cce013634</Property></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="43" ObjectPathId="13"><Parameters><Parameter Type="String">TermStoreId</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">8cea7337-ec1d-49fb-9c02-43443482d285</Property></Parameter></Parameters></Method><Method Name="SetQueryPropertyValue" Id="44" ObjectPathId="13"><Parameters><Parameter Type="String">FillIn</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">false</Property></Parameter></Parameters></Method><SetProperty Id="45" ObjectPathId="0" Name="ResultsUrl"><Parameter Type="String">https://www.centerpointenergy.com/en-us/corporate/about-us/news#k=#s=11</Parameter></SetProperty><SetProperty Id="46" ObjectPathId="0" Name="BypassResultTypes"><Parameter Type="Boolean">true</Parameter></SetProperty><SetProperty Id="47" ObjectPathId="0" Name="ClientType"><Parameter Type="String">ContentSearchRegular</Parameter></SetProperty><SetProperty Id="48" ObjectPathId="0" Name="EnableInterleaving"><Parameter Type="Boolean">false</Parameter></SetProperty><SetProperty Id="49" ObjectPathId="0" Name="ProcessBestBets"><Parameter Type="Boolean">false</Parameter></SetProperty><Method Name="SetQueryPropertyValue" Id="50" ObjectPathId="13"><Parameters><Parameter Type="String">QuerySession</Parameter><Parameter TypeId="{b25ba502-71d7-4ae4-a701-4ca2fb1223be}"><Property Name="BoolVal" Type="Boolean">false</Property><Property Name="IntVal" Type="Number">0</Property><Property Name="QueryPropertyValueTypeIndex" Type="Number">1</Property><Property Name="StrArray" Type="Null" /><Property Name="StrVal" Type="String">1640fa90-85a5-47ca-bd3b-e3f57b7cc8b3</Property></Parameter></Parameters></Method><SetProperty Id="51" ObjectPathId="0" Name="ProcessPersonalFavorites"><Parameter Type="Boolean">false</Parameter></SetProperty><SetProperty Id="52" ObjectPathId="0" Name="SafeQueryPropertiesTemplateUrl"><Parameter Type="String">querygroup://webroot/Pages/News.aspx?groupname=Default</Parameter></SetProperty><SetProperty Id="53" ObjectPathId="0" Name="IgnoreSafeQueryPropertiesTemplateUrl"><Parameter Type="Boolean">false</Parameter></SetProperty><ObjectPath Id="55" ObjectPathId="54" /><ExceptionHandlingScope Id="56"><TryScope Id="58"><Method Name="ExecuteQueries" Id="60" ObjectPathId="54"><Parameters><Parameter Type="Array"><Object Type="String">4e67e4e6-a08f-4b64-aa4f-b0d8e3542b10Default</Object></Parameter><Parameter Type="Array"><Object ObjectPathId="0" /></Parameter><Parameter Type="Boolean">true</Parameter></Parameters></Method></TryScope><CatchScope Id="62" /></ExceptionHandlingScope></Actions><ObjectPaths><Constructor Id="0" TypeId="{80173281-fffd-47b6-9a49-312e06ff8428}" /><Property Id="4" ParentId="0" Name="SortList" /><Property Id="13" ParentId="0" Name="Properties" /><Property Id="18" ParentId="0" Name="SelectProperties" /><Property Id="27" ParentId="0" Name="HitHighlightedProperties" /><Constructor Id="54" TypeId="{8d2ac302-db2f-46fe-9015-872b35f15098}" /></ObjectPaths></Request> '''
        for year in list(range(2009, 2020)):  # loop iterating over different pages of ajax request
            data["year"] = year
            s_url = 'https://www.centerpointenergy.com/en-us/_vti_bin/client.svc/ProcessQuery'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse) 

      


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['GetPressReleaseListResult']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['PressReleaseDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['Headline']
              item['DOCLINK']= dat['LinkToDetailPage'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.cmsenergy.com'
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
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       