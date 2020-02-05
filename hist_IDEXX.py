import scrapy
import re
import json
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### IDEXX Laboratories 1||1
### 1 spider News page
### all news on 1 page with standard get request, 
### howeve complicated xpath structure -> work with Selector
### Pubstring has to be manipulated

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "IDEXX_1098900ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IDEXX_1098900ARV001/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.idexx.com/en/about-idexx/news/'] 

    
 
    def parse(self, response):
        auxxs = response.xpath('//div[contains(@class, "panel-default")]')
        for auxx in auxxs:
            year = re.search(r'(\d{4})', auxx.xpath('.//span[@class="link-inner"][contains(text(), "press releases")]/text()').extract_first()).group()
            auxs = auxx.xpath('.//div[@class="panel-body"]/p')
            #response.xpath('//span[@class="link-inner"][contains(text(), "press releases")]')
            for aux in auxs:
                item = SwisscomIvCrawlerItem()
                #year = re.search(r'(\d{4})', aux.xpath('.//span[@class="link-inner"][contains(text(), "press releases")]/text()').extract_first()).group()
                item['PUBSTRING'] = aux.xpath('./text()').extract_first()
                if re.search(r'([a-zA-Z]+.\d+)', item['PUBSTRING']):
                  item['PUBSTRING'] = re.search(r'([a-zA-Z]+.\d+)', item['PUBSTRING']).group() + ' ' + year
    
                item['HEADLINE']= aux.xpath('./a/text()').extract_first()
                if not re.search('[a-zA-Z]', item['HEADLINE']):
                  item['HEADLINE']= aux.xpath('./a/span[@class="link-inner"]/text()').extract_first()

                item['DOCLINK']= aux.xpath('./a/@href').extract_first()
                #item = {
                #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
                #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
                #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
                #        }
                base_url = 'https://www.idexx.com'
                aux_url = item['DOCLINK']

                if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
                  if aux_url.startswith('http'):
                      url= aux_url
                      item['file_urls'] = [url]
                      item['DOCLINK'] = url
                      item['DESCRIPTION'] = ''
                      #if re.search(r'(\d{8})', url):   
                      #  item['PUBSTRING'] = 'FF' #re.search(r'(\d{8})', url).group()
                      #  yield item
                      #else:
                      if re.search(r'([a-zA-Z]+.\d+..\d{4})', item['HEADLINE']):
                            item['PUBSTRING'] = re.search(r'([a-zA-Z]+.\d+..\d{4})', item['HEADLINE']).group()
                            yield item
                  
                  else:
                      url= base_url + aux_url
                      item['file_urls'] = [url]
                      item['DOCLINK'] = url
                      item['DESCRIPTION'] = ''
                      
                      if re.search(r'([a-zA-Z]+.\d+)', item['HEADLINE']):
                        item['PUBSTRING'] = re.search(r'([a-zA-Z]+.\d+)', item['HEADLINE']).group() +' '+ year
                        #item['PUBSTRING'] = re.search(r'(\d{8})', url).group()
                        yield item
                      else:
                        if 'IDEXX Announces Third Quarter Results' in item['HEADLINE']:
                          if '2017' in url:
                            item['PUBSTRING'] = 'October 31 2017' #re.search(r'(\d{8})', url).group()
                            yield item
                          else:  
                            item['PUBSTRING'] = 'November 01 2018' #re.search(r'(\d{8})', url).group()
                            yield item
                        if re.search(r'([a-zA-Z]+.\d+..\d{4})', item['HEADLINE']):
                              item['PUBSTRING'] = re.search(r'([a-zA-Z]+.\d+..\d{4})', item['HEADLINE']).group()
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*IDEXX\s*Laboratories\b)(.|\s)*|(\bAbout.IDEXX.Laboratories\b)(.|\s)*'
        if not re.search('[a-zA-Z]', item['PUBSTRING']):
            item['PUBSTRING'] = re.search(r'\d{8}', item['DOCLINK']).group()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "col-sm-9")]/p//text() | //div[contains(@class, "col-xs-offset-0 col-md-9")]//text()[not(ancestor::h3 or ancestor::h4 or ancestor::h2)][not(ancestor::div[@class="share-module"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="container"]/h3/text() | //div[contains(@class, "col-xs-offset-0 col-md-8")]//text()[not(ancestor::h1)][not(ancestor::h3 or ancestor::h4 or ancestor::h2)][not(ancestor::div[@class="share-module"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
                #item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item   
            
        
    



            