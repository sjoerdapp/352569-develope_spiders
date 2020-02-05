import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Northern Trust Corporation 2|2
### scrapes earnings press resleases with pdf links extracted via google only availible starting 2015

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "North_T_II_3275000ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://sp5001/North_T_II_3275000ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.northerntrust.com/about-us/investor-relations'] 

    
    def parse(self, response):  # follow drop down menue for different years
        urls = [
         'https://www.northerntrust.com/documents/earnings/2018/q4-2018-northern-trust-quarterly-earnings-release.pdf?bc=25823127',
         'https://m.northerntrust.com/documents/earnings/2018/q3-2018-northern-trust-quarterly-earnings-release.pdf',
         'https://www.northerntrust.com/documents/earnings/2018/q2-2018-northern-trust-quarterly-earnings-release.pdf',
         'https://www.northerntrust.com/documents/earnings/2018/q1-2018-northern-trust-quarterly-earnings-release.pdf',
         'https://www.northerntrust.com/documents/earnings/2017/q4-2017-northern-trust-quarterly-earnings-release.pdf?bc=25682400',
         'https://www.northerntrust.com/documents/earnings/2017/q3-2017-northern-trust-quarterly-earnings-release.pdf',
         'https://www.ntrs.com/documents/earnings/2017/q2-2017-northern-trust-quarterly-earnings-release.pdf?bc=25639200',
         'https://www.northerntrust.com/documents/earnings/2017/q1-2017-northern-trust-quarterly-earnings-release.pdf?bc=24885474',
         'https://www.northerntrust.com/documents/earnings/2016/q4-2016-northern-trust-quarterly-earnings-release.pdf',
         'https://www.northerntrust.com/documents/earnings/2016/q3-2016-northern-trust-quarterly-earnings-release.pdf?bc=24614756',
         'https://www.northerntrust.com/documents/earnings/2016/q2-2016-northern-trust-quarterly-earnings-release.pdf',
         'https://www.northerntrust.com/documents/earnings/2016/q1-2016-northern-trust-quarterly-earnings-release.pdf?bc=24361675',
         'https://www.northerntrust.com/documents/earnings/2015/q4-2015-northern-trust-quarterly-earnings-release.pdf?bc=24221770',
         'https://www.northerntrust.com/documents/earnings/2015/q3-2015-northern-trust-quarterly-earnings-release.pdf?bc=24090938',
         'https://www.northerntrust.com/documents/earnings/2015/q2-2015-northern-trust-quarterly-earnings-release.pdf?bc=23959761',
         'https://www.northerntrust.com/documents/earnings/2015/q1-2015-northern-trust-quarterly-earnings-release.pdf?bc=23829788',
         ]
         #years = list(range(0, 123)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
        for url in urls:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = url.split("earnings/")[1].split('/q')[0]
            item['HEADLINE']= url.split("earnings/")[1].split('.pdf')[0]
            item['DOCLINK']= url
            item['file_urls'] = [url]
            yield item
             #aux_url = 'http://ir.amd.com/news-releases?field_nir_news_date_value%5Bmin%5D=&items_per_page=10&field_nir_news_type_target_id%5B3886%5D=3886&field_nir_news_type_target_id%5B3891%5D=3891&field_nir_news_type_target_id%5B3896%5D=3896&page={}'
             #year_url = [aux_url.format(year)][0]
             #yield scrapy.Request(url=year_url, callback=self.parse_next)

    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    #def parse_next(self, response):
    #    auxs = response.xpath('//table//tr[not(ancestor::thead)]')
    #    for aux in auxs:
    #        item = SwisscomIvCrawlerItem()
    #        item['PUBSTRING'] = aux.xpath('./td/text()[1]').extract_first().split("    ")[1].split("\n")[0]
    #        item['HEADLINE']= aux.xpath('./td/div/a[2]/text()').extract_first()
    #        item['DOCLINK']= aux.xpath('./td/div/a[2]/@href').extract_first()
    #        #item = {
    #        #        'PUBSTRING': aux.xpath('./td/text()[1]').extract_first().split("    ")[1].split("\n")[0], # cuts out the part berfore the date as well as the /n at the end of the string
    #        #        'HEADLINE': aux.xpath('./td/div/a[2]/text()').extract_first(),
    #        #        'DOCLINK': aux.xpath('./td/div/a[2]/@href').extract_first(),
    #        #        }
    #        base_url = 'http://ir.amd.com'
    #        next_url = aux.xpath('./td/div/a[2]/@href').extract_first()
    #        if next_url.startswith('http'):
    #            item['file_urls'] = [next_url]
    #            yield item
#
#    #        else:     
#    #            url= base_url + next_url
#    #            request = scrapy.Request(url=url, callback=self.parse_details)
#    #            request.meta['item'] = item
#    #            yield request
#    #    
#    #def parse_details(self, response):
#    #    item = response.meta['item']
#    #    #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
#    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*AMD\b)(.|\s)* | (\bAbout.AMD\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="node__content"]//text()').extract()))
#    #    item['DOCLINK'] = response.url
#    #    #if not item['DESCRIPTION']:
#    #    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Corning\b)(.|\s)* | (\bAbout.Corning.Incorporated\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]//text()').extract()))
#    #    #   
#    #    yield item
#
#

            