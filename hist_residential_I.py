# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem


### Equity Residential 1|1
### data from investor section
### post request with classic formdata
### data comes as html
### pdf in 2 urls is not recognized on cloud
### back to 20020314


class QuotessSpider(scrapy.Spider):
    name = 'RESI_2994000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/RESI_2994000ARV001/',
        }

      
    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '_ga=GA1.2.2037854888.1547545294; lc_sso8242681=1547545294716; __lc.visitor_id.8242681=S1547545289.a03d1e0f23; __utma=54402544.1399112333.1547545322.1547545322.1547545322.1; __utmz=54402544.1547545322.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=116083986.2037854888.1547545294.1547545348.1547555930.2; __utmz=116083986.1547555930.2.2.utmcsr=investors.equityapartments.com|utmccn=(referral)|utmcmd=referral|utmcct=/news.aspx; _ga=GA1.3.2037854888.1547545294; _gid=GA1.2.658801831.1549045848; _gid=GA1.3.658801831.1549045848',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'http://investors.equityapartments.com',
            'Referer': 'http://investors.equityapartments.com/News',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {
            'filingType': '',
            'filterBy':'',
            'filterMonths': '',
            'filterYears': '',
            'withPDF': 'false',
            }

        pages = list(range(0,75))
        #s_url = 'http://investors.equityapartments.com/News/103054/NewsData?pageIndex={}'
        for page in pages:
            s_url = 'http://investors.equityapartments.com/News/103054/NewsData?pageIndex={}'
            s_url = [s_url.format(page)][0]
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )


    def parse(self, response):
        auxs = response.xpath('//div[@class="col-sm-10"]')
        #item = SwisscomIvCrawlerItem()
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[@class="irwPRDate"]/text()').extract_first()
            item['HEADLINE']= aux.xpath('.//h4/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h4/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('.//div[@class="irwPRDate"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('.//h4/a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//h4/a/@href').extract_first(),
            #        }
            base_url = 'http://investors.equityapartments.com'
            url= base_url + aux.xpath('.//h4/a/@href').extract_first()
            #if not re.search('.pdf', url, re.IGNORECASE):
            if not re.search('.pdf', url.lower()):
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['HEADLINE']= dat['Headline']
                item['DOCLINK']= url
                item['DESCRIPTION'] = ''
                yield item 
        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Equity\s*Residential\s*is\s*an\s*S&P\s*500\s*company\s*focused\s*on)(.|\s)* |(\bAbout\s*Equity\s*Residential\b)(.|\s)* | (\bAbout.Equity.Residential\b)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
            #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
            #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="irwFilePageBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       






















