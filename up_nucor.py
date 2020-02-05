import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### latest 20 news

### Nucor Corporation 1|1
### All news come with one get request as json
### rather complex json structure
### detail page comes as json with html in releasetext
### goes back to 19980916


class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "nucor_2130800ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/nucor_2130800ARV001/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://nucorirservice.nucor.com/api/westnewsreleases'] 

    
    def parse(self, response):  # follow drop down menue for different years
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in body['newsReleases'][0]['newsCategory'][0]['newsRelease'][0:20]:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['date'][0]['date']
            item['HEADLINE'] = dat['title']
            item['DOCLINK'] = dat['releaseID']
            #item = {
            #          'PUBSTRING': dat['date'][0]['date'],
            #          'HEADLINE': dat['title'],
            #          'DOCLINK': dat['releaseID'],
            #          }
            base_url = 'https://nucorirservice.nucor.com/api/westnewsrelease/'
            url= base_url + dat['releaseID']
            if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = dat['PressReleaseDate']
                item['HEADLINE']= dat['Headline']
                item['DOCLINK']= url
                item['DESCRIPTION'] = ''
                yield item 


           # else:
           #     item = SwisscomIvCrawlerItem()
           #     item['file_urls'] = [url]
           #     item['PUBSTRING'] = dat['date'][0]['date']
           #     item['HEADLINE']= dat['Headline']
           #     item['DOCLINK']= url
           #     yield item 
   
        
    def parse_details(self, response):
        item = response.meta['item']
        body = json.loads(response.text)
        content = body['newsReleaseText']['releaseText'] 
        #quotes = Selector(text=content).xpath('//div[@class="xn-content"]//text()')
        name_regex = r'(Nucor\s*is\s*the\s*largest\s*steel\s*producer\s*in\s*the\s*United\s*States\s*and)(.|\s)*|(Nucor\s*and\s*its\s*affiliates\s*are\s*manufacturers\s*of\s*steel\s*products)(.|\s)*|(Certain\s*statements\s*made\s*in\s*this\s*news\s*release\s*are)(.|\s)*|(Certain\s*statements\s*contained\s*in\s*this\s*news\s*release\s*are)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*' ###|(\bAbout\s*Nucor\b)(.|\s)* | (\bAbout.Nucor\b)(.|\s)*
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=content).xpath('//div[@class="rich-text"]/div/center//text()|//div[@class="xn-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=content).xpath('//p/text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=content).xpath('//pre//text()|//p/text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)    
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
        else: 
            yield item



            