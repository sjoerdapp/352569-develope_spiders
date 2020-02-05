import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### BorgWarner Inc 1|2
### 1st spider Press Releases, 2nd spider investors
### spider press site complex post request
### cookies have to be sent extra from header as dict
### some cookies have datatimes -> check if they still work and eventually adjust them
### data best send as string. Important no json

class BHGE(scrapy.Spider):
    name = "BorgWarner_I_2993600ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/BorgWarner_I_2993600ARV001/',
        }
    #handle_httpstatus_list = [404]
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://sp5001/PAY_II_6333000ARV002/',
    #    }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        yield scrapy.http.Request(
            'https://www.borgwarner.com/newsroom/press-releases', 
        callback=self.parse)

        #data = '''aq=(%40syssource%3D%3D(%22TW-Web-Index%22)%20NOT%20%40ftemplateid47442%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22))%20(%24qre(expression%3A'%40syscollection%3D%3D%22Sitecore%20Search%20Provider%22'%2C%20modifier%3A'100'))&cq=(NOT%20%40fid47442%20%3D%20%22D6382CC10793437EA0D08134EE84E61E%22)%20(NOT%20%40fid47442%20%3D%20%22FCED16F8543D4061A649CC424C5675F6%22)%20(NOT%20%40fid47442%20%3D%20%22738E07D76731440580533C4C1784236B%22)%20(NOT%20%40fid47442%20%3D%20%225AF208B93DCB489E8CCAFFAEDECAC119%22)%20(NOT%20%40fid47442%20%3D%20%228E8E6490FE3146D2A342A41AD9BE9DE4%22)%20(NOT%20%40fid47442%20%3D%20%22044E3C181B50406B9FECCC45BE2137D5%22)%20(NOT%20%40fid47442%20%3D%20%2282DF839A0C5044C6A001CCCC10705434%22)%20(NOT%20%40fid47442%20%3D%20%22205C09842D1C41828F0A9EA1605D06BA%22)%20(NOT%20%40fid47442%20%3D%20%2202F0BA3D7DA2461C95F2EBDCD9BB8B93%22)%20(NOT%20%40fid47442%20%3D%20%224D7AAF61CF804E13999432A862F559FA%22)%20(NOT%20%40fid47442%20%3D%20%228206006A582745EFB486A26C2263FE43%22)%20(NOT%20%40ftemplateid47442%20%3D%20%22FC665AAA-BC8F-4746-8A04-1AD387345BFB%22)%20(NOT%20%40twlanguage%20OR%20%40twlanguage%20%3D%20%22en%22)%20(%40sitename%20%3D%20%22wtw%22%20OR%20%40sitename%20%3D%20%22website%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage47442%20%3D%20%221%22)%20(%40flongid47442%20%3D%20%22%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%22)%20((%40fz95xlanguage47442%3D%3D%22en%22%20%40fz95xlatestversion47442%3D%3D%221%22))&language=en&firstResult=0&numberOfResults=10&excerptLength=200&enableDidYouMean=true&sortCriteria=fielddescending&sortField=%40displayz45xdate&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40businesssegment%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40countryz45xtagsz45xtitle%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40fdate47442%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-01-21%22%2C%22end%22%3A%229999-12-31%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-02-20%22%2C%22end%22%3A%222019-01-20%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01%22%2C%22end%22%3A%222018-02-20%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FBerlin&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D ''' 

        #cookies = {'ASP.NET_SessionId': 'qiwxj0b2ksp4lece40ngprh4',
        #            '_ga': 'A1.2.890213369.1563141441',
        #            'cookieconsent_status': 'dismiss',
        #            '_gid': 'GA1.2.672569217.1563273511',
        #            }

            
    
    def parse(self, response):
        auxs = response.xpath('//div[@class="row widget-row"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "h5")]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('.//h3/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h3/a/@href').extract_first()
            
            base_url = 'https://www.borgwarner.com'
            aux_url = item['DOCLINK']
            
            if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
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

        yield FormRequest.from_response(
                response, formid='form1',
                #formdata={
                #    # ctl01.x/y indicates the "next page" button, ctl00.x/y is previous page
                #    'USNewsView$dpNextPrevLink$ctl01$ctl01.x': '17',
                #    'USNewsView$dpNextPrevLink$ctl01$ctl01.y': '15',
                #},
            )

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'xxx'#(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="sfnewsContent sfcontent"]//text()[not(ancestor::div[@class="nesTitle"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if re.search(r'Download\s*the\s*complete\s*news\s*release\s*below', item['DESCRIPTION']):
                pdf_link = response.xpath('//div[@id="MainContent_C016_divDownloads"]//li/a/@href').get_first()
                item['file_urls'] = [pdf_link]

            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item


        
            