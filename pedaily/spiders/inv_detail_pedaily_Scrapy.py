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
    writeInFile = 'investment_event_list'
    name = 'inv_detail_list'
    redis_key = 'pedaily_detail_url'

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
        inv_event = sel.xpath("//div[@class='news-show']/h1/text()").extract()     #投资事件
        info = self.for_ominated_data(info, inv_event)
        date = sel.xpath(u"//b[text()='投资时间：']/../text()").extract() #投资时间
        info = self.for_ominated_data(info, date)
        inv_party = sel.xpath(u"//b[text()='投 资 方：']/following-sibling::*")   #投资方
        if len(inv_party) == 0:
            inv_party = sel.xpath(u"//b[text()='投 资 方：']/../text()").extract()   #投资方非公开的情况
        else:
            inv_party = sel.xpath(u"//b[text()='投 资 方：']/following-sibling::*/text()").extract()   #投资方已知的情况
        try:
            inv_party_join = []
            inv_party_join.append("/".join(inv_party))
            info = self.for_ominated_data(info, inv_party_join)
        except Exception, e:
            log.msg("inv_party={m},url={url}".format(m=e,url=response.url),level=log.ERROR)
        funded_party = sel.xpath(u"//b[text()='受 资 方：']/following-sibling::*/text()").extract()   #受资方
        info = self.for_ominated_data(info, funded_party)
        x1 = u"//b[text()='轮"
        x2 = "\xe3\x80\x80\xe3\x80\x80".decode("utf-8").encode("utf-8")
        x3 = u"次：']/../text()"
        x = x1 + x2 + x3
        turn = sel.xpath(x).extract() #轮次
        info = self.for_ominated_data(info, turn)
        try:
            ind_classi = sel.xpath(u"//b[text()='行业分类：']/following-sibling::*/text()").extract()
            ind_classi_join = []
            ind_classi_join.append('>'.join(ind_classi))
            info = self.for_ominated_data(info, ind_classi_join)
        except Exception, e:
            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
        x1 = u"//b[text()='金"
        x2 = "\xe3\x80\x80\xe3\x80\x80".decode("utf-8").encode("utf-8")
        x3 = u"额：']/../text()"
        x = x1 + x2 + x3
        fund = sel.xpath(x).extract()
        info = self.for_ominated_data(info, fund)
        intro = sel.xpath(u"//b[text()='案例介绍：']/../following-sibling::p[1]/text()").extract()
        info = self.for_ominated_data(info, intro)
        
        item = PedailyItem()
        try:
            info = '\001'.join(info)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

