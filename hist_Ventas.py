import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Ventas Inc 1|1
### page comes in xml format
### use the ReleaseID to get to detailpage
### goes back to 20020102


class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "Venta_1030200ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Venta_1030200ARV001/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.ventasreit.com/sites/default/files/feeds/newsreleases.xml?1549981960762'] 

    
      
    def parse(self, response):
        auxs = response.xpath('//NewsReleases/NewsRelease')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./Date/text()').extract_first()
            item['HEADLINE']= aux.xpath('./Title/text()').extract_first()
            item['DOCLINK']= aux.xpath('./@ReleaseID').extract_first()
             #item = {
             #       'PUBSTRING': aux.xpath('./Date/text()').extract_first(),
             #       'HEADLINE': aux.xpath('./Title/text()').extract_first(),
             #       'DOCLINK': aux.xpath('./@ReleaseID').extract_first(),
             #       }
            base_url = 'http://phx.corporate-ir.net/phoenix.zhtml?c=73172&p=irol-newsArticle_Print&ID={}'
            ID = aux.xpath('./@ReleaseID').extract_first()
            aux_url= base_url.format(ID)
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
        name_regex = r'(Ventas.\s*Inc.\s*.\s*(an\s*S&P\s*500\s*company.\s*)?is\s*a\s*leading\s*real\s*estate\s*investment\s*trust)(.|\s)*|(Ventas.\s*Inc.\s*is\s*a\s*(leading\s*)?healthcare\s*real\s*estate\s*investment\s*trust)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Ventas\b)(.|\s)* | (\bAbout.Ventas\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//span[@class="ccbnTxt"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item



            