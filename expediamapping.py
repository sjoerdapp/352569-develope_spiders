import scrapy
import json
import re

from collections import defaultdict


class ExpediaMapping(scrapy.Spider):
    name = "expediamapping"

    start_urls = [
        'https://ir.expediagroup.com/financial-information/quarterly-results',
    ]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.css('.view-grouping'):
            year = year_div.xpath('./h2/text()').extract_first()
            for line in year_div.css('.view-grouping-content > div'):
                if 'acc-title' in line.attrib['class']:
                    quarter = line.root.text
                else:
                    for item in line.css('.item-list a'):
                        text = item.root.text.lower()
                        href = item.attrib['href']
                        if any(x in text for x in ['earnings release', 'results']):  # noqa
                            self.doc_mapping[year][quarter].setdefault('er', href)  # noqa
                        if 'earnings call transcript' in text:
                            self.doc_mapping[year][quarter].setdefault('ect', href)  # noqa
        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))  # noqa
        yield scrapy.Request(
            'https://media.expediagroup.com/press-releases?l=25',
            callback=self.parse_pr_list)

    def parse_pr_list(self, response):
        for link in response.css('.wd_item_list .wd_title a'):
            yield response.follow(link.attrib['href'], callback=self.parse_pr)

    def parse_pr(self, response):
        text = " ".join(response.xpath('//div[contains(@class, "wd_subtitle")]//text() | //div[contains(@class, "wd_body wd_news_body")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract())
        text = text.lower()
        title_el = response.css('.wd_title')[0]
        title = title_el.root.text
        quarter_match = re.search(r'\bQ([1-4])\b', title)
        if not quarter_match:
            return
        quarter = {
            '1': 'First Quarter',
            '2': 'Second Quarter',
            '3': 'Third Quarter',
            '4': 'Fourth Quarter',
        }.get(quarter_match.group(1))
        year = re.search(r'\b(20[0-9]{2})\b', title).group(1)
        if re.search('earnings release [^.]* available', text):
            yield {
                'title': title,
                'earnings_release': self.doc_mapping[year][quarter].get('er'),
            }