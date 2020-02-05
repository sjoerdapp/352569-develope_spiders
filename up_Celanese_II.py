import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
import js2xml
import scrapy.http
import scrapy

### UPDATES
### scrape actual page, if more pages would get complex

### Celanese Corporation 2|2
### 2nd spider News and Media
### compley post with Form. Form is taken from response and than used for next request 
### need to follow pagination links
### back to 20120216


class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = 'Celanese_II_9900286ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/RCelanese_II_9900286ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    #start_urls = ['https://ir.regions.com/news-and-events/press-releases/2018'] 

    
    def start_requests(self):
        yield scrapy.http.Request(
            'https://www.celanese.com/news-media.aspx',
        )

         
    
    def parse(self, response):
        auxs = response.xpath('//ul[@class="article_list"]/li')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//span[@class="date"]/text()').extract_first()
            item['HEADLINE']= " ".join(aux.xpath('.//p/a/text()').extract()).split('read')[0]
            item['DOCLINK']= aux.xpath('.//p/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./td//div[@class="field__item"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td/a[2]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td/a[2]/@href').extract_first(),
            #        }
            base_url = 'https://www.celanese.com'
            aux_url = item['DOCLINK']
            
            if '.pdf' in aux_url.lower():
                if aux_url.startswith('http'):
                    url= aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    yield item
                
                else:
                    url= response.urljoin(aux_url)
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    yield item
            else:
                if aux_url.startswith('http'):
                    url= aux_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= response.urljoin(aux_url)
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
        
        #next_link = response.xpath('//div[contains(@class, "topPagination")]//a[text()=">"]/@href').extract_first().split('javascript:')[-1]
        #sel = js2xml.parse(next_link)
        #target = str(sel.xpath('//arguments/string/text()')[0])
        #yield scrapy.http.FormRequest.from_response(
        #    response,
        #    formid='mailtoform',
        #    formdata={
        #        "__EVENTTARGET": target,
        #        'buProdListScriptMgr': 'content_1$contentright_1$upnlNewsReleases|content_1$contentright_1$DataPagerNewsTop$ctl02$ctl00',
        #        'content_1$contentright_1$hdnBusinessUnit': '',
        #        '__EVENTARGUMENT': '',
        #    },
        #    callback=self.parse,
        #)


    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Celanese)(.|\s)*|(\bAbout.Celanese\b)(.|\s)*|(\bABOUT.Celanese\b)(.|\s)*|(\bABOUT\s*.CELANESE\b)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="content newsDetailscontent"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            #if not item['DESCRIPTION']:
            #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Corning\b)(.|\s)* | (\bAbout.Corning.Incorporated\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]/div[@class="node__content"]/*[not(self::div[@class="box__right"] or self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
            #   
            yield item



            