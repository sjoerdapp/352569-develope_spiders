
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
         'FILES_STORE' : 's3://352569/Expedia_I_4701300ARV001/',
        }
    
    start_urls = [
        'https://investor.comerica.com/quarterly-results',
    ]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.xpath('//div[contains(@class, "wd_category wd_category")]'):
            Ttl_year = year_div.xpath('.//h1/text()').extract_first()
            year = re.search(r'\d{4}', Ttl_year).group(0)
            for idx, line in enumerate(year_div.xpath('.//div[contains(@class,"item")]'), start=1):
                href = line.xpath('./p/a[contains(text(), "News Release")]/@href').extract_first()
                
                quarter = ''.join(line.xpath('./div/text()').extract())
                
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