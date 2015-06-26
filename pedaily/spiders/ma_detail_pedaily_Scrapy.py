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

import HTMLParser      #用html空格等符号的转义

from pedaily.scrapy_redis.spiders import RedisSpider

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class pedaily(RedisSpider):
    download_delay=1
    writeInFile = 'ma_event_list'
    name = 'ma_detail_list'
    redis_key = 'ma_detail_url'

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
        html_parser = HTMLParser.HTMLParser()
        sel = response.selector
        info = []
        ma_event = sel.xpath("//div[@class='news-show']/h1/text()").extract()     #并购事件
        info = self.for_ominated_data(info, ma_event)
        clue = '并 &nbsp;购 &nbsp;方：'
        newclue = html_parser.unescape(clue) #html转义
        xpath_syntax = u"//b[text()='{m}']/following-sibling::*/text()".format(m=newclue)     #xpath选择语句
        acquirer = sel.xpath(xpath_syntax).extract() #并购方
        info = self.for_ominated_data(info, acquirer)
        ma_party = sel.xpath(u"//b[text()='被并购方：']/following-sibling::*/text()").extract()   #并并购方
        info = self.for_ominated_data(info, ma_party)
        try:
            ind_classi = sel.xpath(u"//b[text()='所属行业：']/following-sibling::*/text()").extract()     #所属行业
            ind_classi_join = []
            ind_classi_join.append('>'.join(ind_classi))
            info = self.for_ominated_data(info, ind_classi_join)
        except Exception, e:
            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
        start_date = sel.xpath(u"//b[text()='并购开始时间：']/../text()").extract()   #并购开始时间
        info = self.for_ominated_data(info, start_date)
        end_date = sel.xpath(u"//b[text()='并购结束时间：']/../text()").extract()   #并购结束时间
        info = self.for_ominated_data(info, end_date)
        status = sel.xpath(u"//b[text()='并购状态：']/../text()").extract()   #并购状态
        info = self.for_ominated_data(info, status)
        stock_right = sel.xpath(u"//b[text()='涉及股权：']/../text()").extract()   #涉及股权
        info = self.for_ominated_data(info, stock_right)
        VCPE = sel.xpath(u"//b[text()='是否VC/PE支持：']/../text()").extract()   #是否VC/PE支持
        info = self.for_ominated_data(info, VCPE)
        intro = sel.xpath(u"//b[text()='案例介绍：']/../following-sibling::p[1]/text()").extract()[0:1]   #案例介绍
        info = self.for_ominated_data(info, intro)
        
        item = PedailyItem()
        try:
            info = '\001'.join(info)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

