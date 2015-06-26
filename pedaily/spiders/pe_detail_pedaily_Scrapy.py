#coding: utf-8

"""
  从redis上读取url,请求，解析出目标数据
  auther:yidun55
  email:heshang1203@sina.com
  date:2015/06/24
"""

from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from pedaily.items import *


from pedaily.scrapy_redis.spiders import RedisSpider

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class pedaily(RedisSpider):
    download_delay=1
    writeInFile = 'pe_event_list'
    name = 'pe_detail_list'
    redis_key = 'pe_detail_url'

    def for_ominated_data(self,info_list,i_list):
        """
        some elements are ominated, set the ominated elements
        as "" 
        """
        try:
            if len(i_list) == 0:
                i_list.append("")
            else:
                pass
            assert len(i_list) == 1, "the element must be unique"
            i_list_strip = []
            i_list_strip.append(i_list[0].strip())  #去除两端的/n,/t/r
            info_list.extend(i_list_strip)
            # print 'you work'
            return info_list
        except Exception, e:
            log.msg('i work {m} info = {info}'.format(m=e, info='\001'.join(info_list)), level=log.ERROR)


    def parse(self, response):
        """
        extract detail information
        """
        sel = response.selector
        info = []
        pe_event = sel.xpath("//div[@class='news-show']/h1/text()").extract()     #募资事件
        info = self.for_ominated_data(info, pe_event)
        found_name = sel.xpath(u"//b[text()='基金名称：']/../text()").extract()   #基金名称
        info = self.for_ominated_data(info, found_name)
        date = sel.xpath(u"//b[text()='成立时间：']/../text()").extract()   #成立时间
        info = self.for_ominated_data(info, date)
        #ad_name = sel.xpath(u"//b[text()='管理机构名称：']/following-sibling::*/text()").extract() #管理机构名称
        ad_name = sel.xpath(u"//b[text()='管理机构名称：']/following-sibling::*")   #管理机构名称
        if len(ad_name) == 0:
            ad_name = sel.xpath(u"//b[text()='管理机构名称：']/../text()").extract()   #管理机构名称非公开的情况
        else:
            ad_name = sel.xpath(u"//b[text()='管理机构名称：']/following-sibling::*/text()").extract()   #管理机构名称已知的情况
        info = self.for_ominated_data(info, ad_name)
        type1 = sel.xpath(u"//b[text()='资本类型：']/../text()").extract()   #资本类型
        info = self.for_ominated_data(info, type1)
        currency = sel.xpath(u"//b[text()='币种：']/../text()").extract()   #币种
        info = self.for_ominated_data(info, currency)
        status = sel.xpath(u"//b[text()='募集状态：']/../text()").extract()   #募集状态
        info = self.for_ominated_data(info, status)
        size = sel.xpath(u"//b[text()='目标规模：']/../text()").extract()   #目标规模
        info = self.for_ominated_data(info, size)
        sum1 = sel.xpath(u"//b[text()='募集金额：']/../text()").extract()   #募集金额
        info = self.for_ominated_data(info, sum1)
        intro = sel.xpath(u"//b[text()='案例介绍：']/../following-sibling::p[1]/text()").extract()[0:1]   #案例介绍
        info = self.for_ominated_data(info, intro)
        
        item = PedailyItem()
        try:
            info = '\001'.join(info)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

