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
    writeInFile = 'ipo_event_list'
    name = 'ipo_detail_list1'
    redis_key = 'ipo_detail_url'

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
        ipo_event = sel.xpath("//div[@class='news-show']/h1/text()").extract()     #上市事件
        info = self.for_ominated_data(info, ipo_event)
        company = sel.xpath(u"//b[text()='公司名称：']/following-sibling::*/text()").extract() #公司名称
        info = self.for_ominated_data(info, company)
        try:
            ind_classi = sel.xpath(u"//b[text()='所属行业：']/following-sibling::*/text()").extract()     #所属行业
            ind_classi_join = []
            ind_classi_join.append('>'.join(ind_classi))
            info = self.for_ominated_data(info, ind_classi_join)
        except Exception, e:
            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
        date = sel.xpath(u"//b[text()='上市时间：']/../text()").extract() #上市时间
        info = self.for_ominated_data(info, date)
        addr = sel.xpath(u"//b[text()='上市地点：']/following-sibling::*/text()").extract()  #上市地点
        info = self.for_ominated_data(info, addr)
        stock_code = sel.xpath(u"//b[text()='股票代码：']/../text()").extract()   #股票代码
        info = self.for_ominated_data(info, stock_code)
        VCPE = sel.xpath(u"//b[text()='是否VC/PE支持：']/../text()").extract()   #是否VC/PE支持
        info = self.for_ominated_data(info, VCPE)
        inv_party = sel.xpath(u"//b[text()='投资方：']/following-sibling::*")   #投资方
        if len(inv_party) == 0:
            inv_party = sel.xpath(u"//b[text()='投资方：']/../text()").extract()   #投资方非公开的情况
        else:
            inv_party = sel.xpath(u"//b[text()='投资方：']/following-sibling::*/text()").extract()   #投资方已知的情况
        try:
            inv_party_join = []
            inv_party_join.append("/".join(inv_party))
            info = self.for_ominated_data(info, inv_party_join)
        except Exception, e:
            log.msg("inv_party={m},url={url}".format(m=e,url=response.url),level=log.ERROR)
        is_price = sel.xpath(u"//b[text()='发行价：']/../text()").extract()
        info = self.for_ominated_data(info, is_price)  #股票发行价
        circulation = sel.xpath(u"//b[text()='发行量：']/../text()").extract()  #发行量
        info = self.for_ominated_data(info, circulation) 
        intro = sel.xpath(u"//b[text()='案例介绍：']/../following-sibling::p[1]/text()").extract()[0:1]   #案例介绍
        info = self.for_ominated_data(info, intro)
        
        item = PedailyItem()
        try:
            info = '\001'.join(info)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

