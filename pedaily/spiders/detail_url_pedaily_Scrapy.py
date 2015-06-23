#coding: utf-8

"""
  从投资界上爬取投资事件等数据
  auther: bill_cpp
  email:bill_cpp@sina.com
  date:2015/6/23
"""

from scrapy.spider import Spider
from scrapy.http import Request
from scrapy import log
import redis

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class pedaily(Spider):
    name = "pedaily_list"
    start_urls = []
    myRedis = redis.StrictRedis(host='localhost',port=6379)
    def __init__(self,redis_key,start_url):
        self.redis_key = redis_key
        self.__class__.start_urls.append(start_url)

    def parse(self, response):



