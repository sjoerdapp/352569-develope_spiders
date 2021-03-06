
import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from collections import defaultdict








class QuotessSpider(scrapy.Spider):
    name = 'Expedia_I_4701300ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Kellogg_I_2104100ARV001/',
        }
    start_urls = ['https://investor.kelloggs.com/QuarterlyResults#0']

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.xpath('//div[contains(@class, "panel panel-default")]'):
            year = re.search(r'\d{4}', year_div.xpath('.//a/span[@class="irwQRTitle"]/text()').extract_first()).group(0)
            quarter = re.search(r'\D+', year_div.xpath('.//a/span[@class="irwQRTitle"]/text()').extract_first()).group(0).rstrip()
            href = year_div.xpath('//div[@class="panel-body"]/ul/li/a[contains(text(), "Earnings Release") or contains(text(), "Press Release")]/@href').extract_first()
            if '../' in href:
              href = 'https://investor.kelloggs.com' + year_div.xpath('//div[@class="panel-body"]/ul/li/a[contains(text(), "Earnings Release") or contains(text(), "Press Release")]/@href').extract_first().split('..')[1]
            self.doc_mapping[year][quarter].setdefault('er', href)

        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4))) 



    #name = 'Comerica_II_1261000ARV002'
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://352569/Comerica_II_1261000ARV002/',
    #    }
    #start_urls = [
    #    'http://investor.comerica.com/phoenix.zhtml?c=114699&p=irol-reportsother',
    #]
#
#    #def __init__(self, *pargs, **kwargs):
#    #    super().__init__(*pargs, **kwargs)
#    #    self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))
#
#    #def parse(self, response):
#    #    for year_div in response.xpath('//table[@class="reportsOtherTable"]'):
#    #        Ttl_year = year_div.xpath('.//span[@class="ccbnTblTtl"]/text()').extract_first()
#    #        year = re.search(r'\d{4}', Ttl_year).group(0)
#    #        for idx, line in enumerate(year_div.xpath('.//tr[@class="ccbnBgTblOdd"]/td'), start=1):
#    #            href = line.xpath('.//a[contains(text(), "News Release")]/@href').extract_first()
#    #            
#    #            quarter = 'Q' + str(idx)
#    #            self.doc_mapping[year][quarter].setdefault('er', href)
#    #    
#    #    self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))
#    #    doc_mapping = self.doc_mapping['2018']['Q2'].get('er')
#    #    return doc_mapping
#