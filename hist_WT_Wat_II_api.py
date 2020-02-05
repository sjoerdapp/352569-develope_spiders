import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Willis Towers Watson Public Limited Company 2|2
### 1st spider investors, 2nd spider Press site
### spider press site complex post request
### cookies have to be sent extra from header as dict
### some cookies have datatimes -> check if they still work and eventually adjust them
### data best send as string. Important no json

class BHGE(scrapy.Spider):
    name = "WT_wat_II_9900062ARV002"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/WT_wat_II_9900062ARV002/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset="UTF-8"',
            #'Cookie': 'ASP.NET_SessionId=wfjwtsuin1uafxe0x3oker1v; __RequestVerificationToken=QZpcBObmxUahsdj6xiNbLxayo8KGrV8NzkyPHG1lDFqUtqTIP43LRx3R4R4IkKTmVP1wR8KFMS_yISLxgBZ4w9KD9wI1; visid_incap_1246096=nu9KgX4GRbu+o2Vne+eawwktTlwAAAAAQUIPAAAAAAByH42r0JBEzG3yLY+HSfNu; resolution=1280; _ga=GA1.2.2143087210.1548627217; _gid=GA1.2.2052215443.1548627217; SC_ANALYTICS_GLOBAL_COOKIE=1a70df17b7a44f05b12fcc8f44eb006f|True; com.silverpop.iMAWebCookie=e6825de4-ce53-b87c-d433-c4e2a8d3c4c7; __atssc=google%3B1; notice_preferences=2:; notice_gdpr_prefs=0,1,2:; wtw#lang=en; s_cc=true; s_sq=%5B%5BB%5D%5D; TS0121b28a=01324cfcfdb153d0897d989eaec0ed1cc276d7cb94240d88e802eb66a90dd1eb377a64a91bcbbd3f93f7b9ad868d169863316919bd3a422b2bcb39b6e55011a922248f695dfab953cf1f0d8de39498458493472627a6e3b8ed973ccce9ef44a7791d809bad3b52a3744d062b7276183cd52dc1011b48879101bdd780ef2d314e569c43d330; incap_ses_699_1246096=12UZEJSDv184nLKEiFmzCT85TlwAAAAATFjqQuwIXYVksE2dsz+rpA==; _gat_UA-69683604-1=1; com.silverpop.iMA.session=4ec61dc9-91a3-4a8c-3226-074345e85bdb; com.silverpop.iMA.page_visit=1172829324:; __atuvc=4%7C5; __atuvs=5c4e394526deaf69000',
            'Origin': 'https://www.willistowerswatson.com',
            'Referer': 'https://www.willistowerswatson.com/en/press',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            }

        #data = '''aq=(%40syssource%3D%3D(%22TW-Web-Index%22)%20NOT%20%40ftemplateid47442%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22))%20(%24qre(expression%3A'%40syscollection%3D%3D%22Sitecore%20Search%20Provider%22'%2C%20modifier%3A'100'))&cq=(NOT%20%40fid47442%20%3D%20%22D6382CC10793437EA0D08134EE84E61E%22)%20(NOT%20%40fid47442%20%3D%20%22FCED16F8543D4061A649CC424C5675F6%22)%20(NOT%20%40fid47442%20%3D%20%22738E07D76731440580533C4C1784236B%22)%20(NOT%20%40fid47442%20%3D%20%225AF208B93DCB489E8CCAFFAEDECAC119%22)%20(NOT%20%40fid47442%20%3D%20%228E8E6490FE3146D2A342A41AD9BE9DE4%22)%20(NOT%20%40fid47442%20%3D%20%22044E3C181B50406B9FECCC45BE2137D5%22)%20(NOT%20%40fid47442%20%3D%20%2282DF839A0C5044C6A001CCCC10705434%22)%20(NOT%20%40fid47442%20%3D%20%22205C09842D1C41828F0A9EA1605D06BA%22)%20(NOT%20%40fid47442%20%3D%20%2202F0BA3D7DA2461C95F2EBDCD9BB8B93%22)%20(NOT%20%40fid47442%20%3D%20%224D7AAF61CF804E13999432A862F559FA%22)%20(NOT%20%40fid47442%20%3D%20%228206006A582745EFB486A26C2263FE43%22)%20(NOT%20%40ftemplateid47442%20%3D%20%22FC665AAA-BC8F-4746-8A04-1AD387345BFB%22)%20(NOT%20%40twlanguage%20OR%20%40twlanguage%20%3D%20%22en%22)%20(%40sitename%20%3D%20%22wtw%22%20OR%20%40sitename%20%3D%20%22website%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage47442%20%3D%20%221%22)%20(%40flongid47442%20%3D%20%22%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%22)%20((%40fz95xlanguage47442%3D%3D%22en%22%20%40fz95xlatestversion47442%3D%3D%221%22))&language=en&firstResult=0&numberOfResults=10&excerptLength=200&enableDidYouMean=true&sortCriteria=fielddescending&sortField=%40displayz45xdate&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40businesssegment%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40countryz45xtagsz45xtitle%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40fdate47442%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-01-21%22%2C%22end%22%3A%229999-12-31%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-02-20%22%2C%22end%22%3A%222019-01-20%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01%22%2C%22end%22%3A%222018-02-20%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FBerlin&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D ''' 

        cookies = {'visid_incap_1246096': 'nu9KgX4GRbu+o2Vne+eawwktTlwAAAAAQUIPAAAAAAByH42r0JBEzG3yLY+HSfNu',
                    '_ga': 'GA1.2.2143087210.1548627217',
                    'SC_ANALYTICS_GLOBAL_COOKIE': '1a70df17b7a44f05b12fcc8f44eb006f|True',
                    'com.silverpop.iMAWebCookie': 'e6825de4-ce53-b87c-d433-c4e2a8d3c4c7',
                    '__atssc': 'google%3B1',
                    'notice_preferences': '2:',
                    'notice_gdpr_prefs': '0,1,2:',
                    '__atuvc': '8%7C5%2C0%7C6%2C4%7C7',
                    'wtw#lang': 'en',
                    'ASP.NET_SessionId': 'sg2vkfeqj00ssxys30jknpte',
                    '__RequestVerificationToken': '_JNT7w3kcWA8aRZZfiIp7uV1PWfhkvuudK4fgue2kBICTvdQvkBCToHvzCRGGua3oiqVxxMguoj8UDIDynAyJHfW3wY1',
                    'TS0121b28a': '01324cfcfdfc173ac91c1bebf34a8ecf2649106c0e3381bd868516223b72d3345939cbf359e0d82bc0a8883e4f03d9ffc21b858e98acb103de6d4c31b4cca6ae62570302999e7a24ccf8bc2ba1234fdba8717840970243440272661475387324995140a40f6baf597d8d1983b7c010c856864ad39137bb0a986a445c4dd9c321ccd8a730a62a61f0ec7bf24221a77edf35c3f1f5f7',
                    'incap_ses_287_1246096': 'K9ZIa+BqA0OMHYlRU6L7AzNubVwAAAAAY3FA0R3/dM6FQhxglqqiYA==',
                    'resolution': '1920'}

        s_url = 'https://www.willistowerswatson.com/coveo/rest/v2/?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%3Flang%3Den%26ver%3D16&siteName=wtw'
                 #https://www.willistowerswatson.com/coveo/rest/v2/?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%3Flang%3Den%26ver%3D16&siteName=wtw
        for num in list(range(0, 750, 10)):  # loop iterating over different pages of ajax request; last number not in list anymore
            data_aux = '''aq=(%40syssource%3D%3D(%22TW-Web-Index%22)%20NOT%20%40ftemplateid47442%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22))%20(%24qre(expression%3A'%40syscollection%3D%3D%22Sitecore%20Search%20Provider%22'%2C%20modifier%3A'100'))&cq=(NOT%20%40fid47442%20%3D%20%22D6382CC10793437EA0D08134EE84E61E%22)%20(NOT%20%40fid47442%20%3D%20%22FCED16F8543D4061A649CC424C5675F6%22)%20(NOT%20%40fid47442%20%3D%20%22738E07D76731440580533C4C1784236B%22)%20(NOT%20%40fid47442%20%3D%20%225AF208B93DCB489E8CCAFFAEDECAC119%22)%20(NOT%20%40fid47442%20%3D%20%228E8E6490FE3146D2A342A41AD9BE9DE4%22)%20(NOT%20%40fid47442%20%3D%20%22044E3C181B50406B9FECCC45BE2137D5%22)%20(NOT%20%40fid47442%20%3D%20%2282DF839A0C5044C6A001CCCC10705434%22)%20(NOT%20%40fid47442%20%3D%20%22205C09842D1C41828F0A9EA1605D06BA%22)%20(NOT%20%40fid47442%20%3D%20%2202F0BA3D7DA2461C95F2EBDCD9BB8B93%22)%20(NOT%20%40fid47442%20%3D%20%224D7AAF61CF804E13999432A862F559FA%22)%20(NOT%20%40fid47442%20%3D%20%228206006A582745EFB486A26C2263FE43%22)%20(NOT%20%40ftemplateid47442%20%3D%20%22FC665AAA-BC8F-4746-8A04-1AD387345BFB%22)%20(NOT%20%40twlanguage%20OR%20%40twlanguage%20%3D%20%22en%22)%20(%40sitename%20%3D%20%22wtw%22%20OR%20%40sitename%20%3D%20%22website%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage47442%20%3D%20%221%22)%20(%40flongid47442%20%3D%20%22%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%22)%20((%40fz95xlanguage47442%3D%3D%22en%22%20%40fz95xlatestversion47442%3D%3D%221%22))&language=en&firstResult={}&numberOfResults=10&excerptLength=200&enableDidYouMean=true&sortCriteria=fielddescending&sortField=%40displayz45xdate&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40businesssegment%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40countryz45xtagsz45xtitle%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40fdate47442%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-01-21%22%2C%22end%22%3A%229999-12-31%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-02-20%22%2C%22end%22%3A%222019-01-20%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01%22%2C%22end%22%3A%222018-02-20%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FBerlin&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D ''' 
            data = [data_aux.format(num)][0]
            yield scrapy.Request(s_url, method='POST', body=data, headers=headers, cookies=cookies, callback=self.parse)
    
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        for dat in body['results']:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['raw']['formattedz45xdisplayz45xdate']
            item['HEADLINE']=  dat['Title']
            item['DOCLINK']= dat['clickUri']
            #item = {
            #          'PUBSTRING': dat['raw']['formattedz45xdisplayz45xdate'],
            #          'HEADLINE': dat['Title'],
            #          'DOCLINK': dat['clickUri'],
            #          }
           
            
            #base_url = 'https://www.eversource.com/content'
            url= dat['clickUri'] 
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request   

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Willis\s*Towers\s*Watson.s\s*Insurance\s*Consulting\s*(&\s*|and\s*)Technology\s*business\s*has\s*over)(.|\s)*|(\bAbout\s*Willis\s*Towers\s*Watson\b)(.|\s)* | (\bAbout.Wiilis.Towers.Watson\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div [@class="article-wrapper"]/article//h2//text() | //div [@class="article-wrapper"]/article/section//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item

                     



        
            