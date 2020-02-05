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
### Achtung might need to update date information in request
### scrape first two pages, latest 20 news

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
            'Referer': 'https://www.willistowerswatson.com/en-US/news/all-news',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            }

        #data = '''aq=(%40syssource%3D%3D(%22TW-Web-Index%22)%20NOT%20%40ftemplateid47442%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22))%20(%24qre(expression%3A'%40syscollection%3D%3D%22Sitecore%20Search%20Provider%22'%2C%20modifier%3A'100'))&cq=(NOT%20%40fid47442%20%3D%20%22D6382CC10793437EA0D08134EE84E61E%22)%20(NOT%20%40fid47442%20%3D%20%22FCED16F8543D4061A649CC424C5675F6%22)%20(NOT%20%40fid47442%20%3D%20%22738E07D76731440580533C4C1784236B%22)%20(NOT%20%40fid47442%20%3D%20%225AF208B93DCB489E8CCAFFAEDECAC119%22)%20(NOT%20%40fid47442%20%3D%20%228E8E6490FE3146D2A342A41AD9BE9DE4%22)%20(NOT%20%40fid47442%20%3D%20%22044E3C181B50406B9FECCC45BE2137D5%22)%20(NOT%20%40fid47442%20%3D%20%2282DF839A0C5044C6A001CCCC10705434%22)%20(NOT%20%40fid47442%20%3D%20%22205C09842D1C41828F0A9EA1605D06BA%22)%20(NOT%20%40fid47442%20%3D%20%2202F0BA3D7DA2461C95F2EBDCD9BB8B93%22)%20(NOT%20%40fid47442%20%3D%20%224D7AAF61CF804E13999432A862F559FA%22)%20(NOT%20%40fid47442%20%3D%20%228206006A582745EFB486A26C2263FE43%22)%20(NOT%20%40ftemplateid47442%20%3D%20%22FC665AAA-BC8F-4746-8A04-1AD387345BFB%22)%20(NOT%20%40twlanguage%20OR%20%40twlanguage%20%3D%20%22en%22)%20(%40sitename%20%3D%20%22wtw%22%20OR%20%40sitename%20%3D%20%22website%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage47442%20%3D%20%221%22)%20(%40flongid47442%20%3D%20%22%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%22)%20((%40fz95xlanguage47442%3D%3D%22en%22%20%40fz95xlatestversion47442%3D%3D%221%22))&language=en&firstResult=0&numberOfResults=10&excerptLength=200&enableDidYouMean=true&sortCriteria=fielddescending&sortField=%40displayz45xdate&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40businesssegment%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40countryz45xtagsz45xtitle%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40fdate47442%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-01-21%22%2C%22end%22%3A%229999-12-31%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-02-20%22%2C%22end%22%3A%222019-01-20%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01%22%2C%22end%22%3A%222018-02-20%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FBerlin&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D ''' 

        cookies = {'visid_incap_1246096': 'wgFCbe95SyK4NYfI2Ws8LMOpJV0AAAAAQUIPAAAAAAC5RjHeEIA4qCAJzCi1bLVn',
                   'incap_ses_288_1246096': 'lUyiG4iGr3okJ4lMBTH/A8SpJV0AAAAACjmsmGujE6h8doCwu5BF6Q==',
                   'wtw#lang': 'en-US',
                   'ASP.NET_SessionId': 'hmsqggo4r4fhid2pin1jfdeu',
                   '_ga': 'GA1.2.1308784828.1562749384',
                   '_gid': 'GA1.2.842751380.1562749384',
                   '__hstc': '49922809.9b007da796de7cb66418dc420c62289a.1562749384816.1562749384816.1562749384816.1',
                   'hubspotutk': '9b007da796de7cb66418dc420c62289a',
                   '__hssrc': '1',
                   'com.silverpop.iMAWebCookie': '058b9e08-10cb-ec86-5166-47618be23130',
                   'com.silverpop.iMA.session': '205cd3a1-4030-b11c-7b29-793904dc7c54',
                   'com.silverpop.iMA.page_visit': '-395271777:',
                   'notice_preferences': '2:',
                   'notice_gdpr_prefs': '0,1,2:',
                   'SC_ANALYTICS_GLOBAL_COOKIE': '656e33ee1aff48d4b2e210004b41d4f7|True',
                   'TS011777e6': '01bfca5a2507e58c66be8cd3778d1c9e555032bc3cc4430a895229b3e25c31d75c8f3c692ef7b2ca41390fdd58131bf9f0b04407cbb41e24b3836f83aad8cb1947536cea3348710c4a2c88a83f1a80084de1cfb28746be85c7a67c93568e4fb09bf4b60738',
                   '__hssc': '49922809.2.1562749384817',
                   '__atuvc': '3%7C28',
                   '__atuvs': '5d25a9c74875cc23002'}

        s_url = 'https://www.willistowerswatson.com/coveo/rest/v2?sitecoreItemUri=112b6fb5-0034-49c7-bb5f-cf4bea83106d&siteName=wtw&authentication'
                 #https://www.willistowerswatson.com/coveo/rest/v2/?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%3Flang%3Den%26ver%3D16&siteName=wtw
        for num in list(range(0, 12, 10)):  # loop iterating over different pages of ajax request; last number not in list anymore
            #data_aux = '''aq=(%40syssource%3D%3D(%22TW-Web-Index%22)%20NOT%20%40ftemplateid47442%3D%3D(%22adb6ca4f-03ef-4f47-b9ac-9ce2ba53ff97%22%2C%22fe5dd826-48c6-436d-b87a-7c4210c7413b%22))%20(%24qre(expression%3A'%40syscollection%3D%3D%22Sitecore%20Search%20Provider%22'%2C%20modifier%3A'100'))&cq=(NOT%20%40fid47442%20%3D%20%22D6382CC10793437EA0D08134EE84E61E%22)%20(NOT%20%40fid47442%20%3D%20%22FCED16F8543D4061A649CC424C5675F6%22)%20(NOT%20%40fid47442%20%3D%20%22738E07D76731440580533C4C1784236B%22)%20(NOT%20%40fid47442%20%3D%20%225AF208B93DCB489E8CCAFFAEDECAC119%22)%20(NOT%20%40fid47442%20%3D%20%228E8E6490FE3146D2A342A41AD9BE9DE4%22)%20(NOT%20%40fid47442%20%3D%20%22044E3C181B50406B9FECCC45BE2137D5%22)%20(NOT%20%40fid47442%20%3D%20%2282DF839A0C5044C6A001CCCC10705434%22)%20(NOT%20%40fid47442%20%3D%20%22205C09842D1C41828F0A9EA1605D06BA%22)%20(NOT%20%40fid47442%20%3D%20%2202F0BA3D7DA2461C95F2EBDCD9BB8B93%22)%20(NOT%20%40fid47442%20%3D%20%224D7AAF61CF804E13999432A862F559FA%22)%20(NOT%20%40fid47442%20%3D%20%228206006A582745EFB486A26C2263FE43%22)%20(NOT%20%40ftemplateid47442%20%3D%20%22FC665AAA-BC8F-4746-8A04-1AD387345BFB%22)%20(NOT%20%40twlanguage%20OR%20%40twlanguage%20%3D%20%22en%22)%20(%40sitename%20%3D%20%22wtw%22%20OR%20%40sitename%20%3D%20%22website%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage47442%20%3D%20%221%22)%20(%40flongid47442%20%3D%20%22%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%22)%20((%40fz95xlanguage47442%3D%3D%22en%22%20%40fz95xlatestversion47442%3D%3D%221%22))&language=en&firstResult={}&numberOfResults=10&excerptLength=200&enableDidYouMean=true&sortCriteria=fielddescending&sortField=%40displayz45xdate&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40businesssegment%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40countryz45xtagsz45xtitle%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%7D%2C%7B%22field%22%3A%22%40fdate47442%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-01-21%22%2C%22end%22%3A%229999-12-31%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-02-20%22%2C%22end%22%3A%222019-01-20%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01%22%2C%22end%22%3A%222018-02-20%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FBerlin&disableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%7D ''' 
            data_aux = '''actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-07-10T09%3A14%3A51.074Z%5C%22%22%2C%22internalTime%22%3A1562750091074%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-07-10T09%3A13%3A24.310Z%5C%22%22%2C%22internalTime%22%3A1562750004310%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-07-10T09%3A03%3A04.587Z%5C%22%22%2C%22internalTime%22%3A1562749384587%7D%5D&referrer=https%3A%2F%2Fwww.willistowerswatson.com%2Fen-US%2Fnews%2Fall-news&visitorId=&isGuestUser=false&aq=(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%22)%20(%40fz95xfullpath13762*%3D%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%22WTW-Web-Index%22)&cq=(%40fz95xlanguage13762%3D%3D%22en-US%22)%20(%40fz95xlatestversion13762%3D%3D1)&locale=en&maximumAge=900000&firstResult={}&numberOfResults=10&excerptLength=200&enableDidYouMean=false&sortCriteria=fielddescending&sortField=%40fdate13762&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40solution%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%2C%22advancedQueryOverride%22%3A%22(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%5C%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%5C%22)%20(%40fz95xfullpath13762*%3D%5C%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%5C%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%5C%22WTW-Web-Index%5C%22)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage13762%3D%3D%5C%22en-US%5C%22)%20(%40fz95xlatestversion13762%3D%3D1)%22%7D%2C%7B%22field%22%3A%22%40industry%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%2C%22advancedQueryOverride%22%3A%22(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%5C%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%5C%22)%20(%40fz95xfullpath13762*%3D%5C%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%5C%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%5C%22WTW-Web-Index%5C%22)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage13762%3D%3D%5C%22en-US%5C%22)%20(%40fz95xlatestversion13762%3D%3D1)%22%7D%2C%7B%22field%22%3A%22%40topic%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%2C%22advancedQueryOverride%22%3A%22(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%5C%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%5C%22)%20(%40fz95xfullpath13762*%3D%5C%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%5C%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%5C%22WTW-Web-Index%5C%22)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage13762%3D%3D%5C%22en-US%5C%22)%20(%40fz95xlatestversion13762%3D%3D1)%22%7D%2C%7B%22field%22%3A%22%40country%22%2C%22maximumNumberOfValues%22%3A5%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%2C%22advancedQueryOverride%22%3A%22(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%5C%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%5C%22)%20(%40fz95xfullpath13762*%3D%5C%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%5C%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%5C%22WTW-Web-Index%5C%22)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage13762%3D%3D%5C%22en-US%5C%22)%20(%40fz95xlatestversion13762%3D%3D1)%22%7D%2C%7B%22field%22%3A%22%40displayz45xdate%22%2C%22maximumNumberOfValues%22%3A3%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22rangeValues%22%3A%5B%7B%22start%22%3A%222019-06-10T04%3A14%3A49.000Z%22%2C%22end%22%3A%222019-07-10T04%3A14%3A49.000Z%22%2C%22label%22%3A%22Last%2030%20days%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%222018-07-10T04%3A14%3A49.000Z%22%2C%22end%22%3A%222019-06-10T04%3A14%3A49.000Z%22%2C%22label%22%3A%2231%20days%20to%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%2C%7B%22start%22%3A%220001-01-01T00%3A00%3A00.000Z%22%2C%22end%22%3A%222018-07-10T04%3A14%3A49.000Z%22%2C%22label%22%3A%22Over%20a%20year%20ago%22%2C%22endInclusive%22%3Atrue%7D%5D%2C%22advancedQueryOverride%22%3A%22(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20((%40ftemplateid13762%3D%3D%5C%22%7B4E9B7D45-60FE-4972-8C1F-9D3E802B5379%7D%5C%22)%20(%40fz95xfullpath13762*%3D%5C%22%2Fsitecore%2Fcontent%2FWTW%2FNews*%5C%22)%20(%40fisz32xdisplayedz32xonz32xlistingz32xpage13762%3D%3D1))%20(NOT%20%40fz95xtemplate13762%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%5C%22WTW-Web-Index%5C%22)%22%2C%22constantQueryOverride%22%3A%22(%40fz95xlanguage13762%3D%3D%5C%22en-US%5C%22)%20(%40fz95xlatestversion13762%3D%3D1)%22%7D%5D&retrieveFirstSentences=true&timezone=Europe%2FZurich&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&allowQueriesWithoutKeywords=true'''
            data = [data_aux.format(num)][0]
            yield scrapy.Request(s_url, method='POST', body=data, headers=headers, cookies=cookies, callback=self.parse)
    
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        for dat in body['results']:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['raw']['formattedz45xdisplayz45xdate']
            item['HEADLINE']=  dat['Title']
            item['DOCLINK']= dat['clickUri']
            #if not re.match(r'\d{2}. \d{4}', dat['raw']['formattedz45xdisplayz45xdate']):
            #    item['PUBSTRING'] = dat['Excerpt']
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
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div [@class="article-hero__overview text-faded"]//text() | //div [@class="col-12 col-xl-6 offset-xl-2"]//text()[not(ancestor::div[@class="mb-5"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item

                     



        
            