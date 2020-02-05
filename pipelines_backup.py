# -*- coding: utf-8 -*-

# Define your item pipelines here
#ITEM_PIPELINES = {'scrapy.pipelines.files.FilesPipeline': 1}
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re

from pkg_resources import resource_filename
from jsonschema import Draft4Validator

validator = Draft4Validator({
   "$schema": "http://json-schema.org/draft-07/schema#",
   "type": ["object"],
   "required": ["HEADLINE", "PUBSTRING", "DESCRIPTION", "files"],
 	#"additionalProperties": True,
 	"properties": {
 	  "HEADLINE": {
 	    "type": "string",
 	    "minLength": 10,
 	    "pattern": "([a-z-A-Z]+.*){10}"
 	  },
 	  "PUBSTRING": {
 	    "type": "string",
 	    "minLength": 6,
 	    "pattern": "([0-9]+.*){4}"
 	  },
 	  "DESCRIPTION": {
 	    "type": "string",
 	    "minLength": 20,
 	    "pattern": "([a-z-A-Z]+.*){10}"
 	  },
    "DOCLINK": {
      "type": "string",
      "minLength": 6,
      "pattern": "([a-z-A-Z]+.*){6}"
    },
    "file_urls": {
           "type": "array",
           "items": {
               "type": "string"
              },
    }
 	}
})


class MyValidationPipeline(object):
    def process_item(self, item, spider):
        # Convert item to a dictionary if it's an Item class
        item = dict(item)

        # Collect errors in this array
        errors = []

        # Do manual checks
        #if not item.get('DESCRIPTION') or not re.search('[a-zA-Z]', item['DESCRIPTION']) and not item.get('file_urls'):
        #    errors.append('Need "body" or at least one "file_urls"')
        
        #spider.logger.warning('Item type {}'.format(type(item)))
        for error in validator.iter_errors(item):
            errors.append(error.message)
        if errors:
            spider.logger.error('Item failed validation!\nItem: {}\nErrors:\n{}'.format(
                json.dumps(item, indent=4),
                '\n'.join(' - ' + error for error in errors)
            ))
            item['_validation'] = 'failed'
        return item


class SwisscomIvCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item
