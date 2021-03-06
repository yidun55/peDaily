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
    """
    usage: scrapy crawl ma_list -a redis_key='your_key' -a start_url='http://zdb.pedaily.cn/pe/1/'
    """
    download_delay = 1
    name = "pe_list"
    start_urls = []
    myRedis = redis.StrictRedis(host='localhost',port=6379)
    def __init__(self,redis_key,start_url):
        self.redis_key = redis_key
        self.__class__.start_urls.append(start_url)

    def parse(self, response):
        """
        extract the total pages
        """
        sel = response.selector
        try:
            total_page = sel.xpath("//div[@class='page-list page']/a[3]/text()").extract()[0]
        except Exception,e:
            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
        url = response.url[:-2]
        for i in range(1, int(total_page)+1):
            yield Request(url+str(i)+"/", callback=self.extract_url, dont_filter=True)

    def extract_url(self, response):
        """
        extract url of detail information
        """
        sel = response.selector
        detail_url = sel.xpath(u"//table//a[text()='详情']/@href").extract()
        base_url = "http://zdb.pedaily.cn"
        try:
            detail_url = [base_url+url for url in detail_url]
        except Exception,e:
            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
        for url in detail_url:
            self.__class__.myRedis.lpush(self.redis_key, url)


#    def for_ominated_data(self,info_list,i_list):
#        """
#        some elements are ominated, set the ominated elements
#        as "" 
#        """
#        try:
#            if len(i_list) == 0:
#                i_list.append("")
#            else:
#                pass
#            assert len(i_list) == 1, "the element must be unique"
#            info_list.extend(i_list)
#            # print 'you work'
#            return info_list
#        except Exception, e:
#            print 'i work'
#            log.msg(e, level=log.ERROR)
#
#
#    def extract_detail(self, response):
#        """
#        extract detail information
#        """
#        sel = response.selector
#        info = []
#        inv_event = sel.xpath("//div[@class='news-show']/h1/text()").extract()     #投资事件
#        info = self.for_ominated_data(info, inv_event)
#        date = sel.xpath("//b[text()='投资时间：']/../text()").extract() #投资时间
#        info = self.for_ominated_data(info, date)
#        inv_party = sel.xpath(u"//b[text()='投 资 方：']/following-sibling::*/text()").extract()   #投资方
#        info = self.for_ominated_data(info, inv_party)
#        funded_party = sel.xpath(u"//b[text()='受 资 方：']/following-sibling::*/text()").extract()   #受资方
#        info = self.for_ominated_data(info, funded_party)
#        turn = sel.xpath("//b[text()='轮    次：']/../text()").extract() #轮次
#        info = self.for_ominated_data(info, turn)
#        try:
#            ind_classi = sel.xpath(u"//b[text()='行业分类：']/following-sibling::*/text()").extract()
#            ind_classi_join = []
#            ind_classi_join.append('>'.join(ind_classi))
#            info = self.for_ominated_data(info, ind_classi_join)
#        except Exception, e:
#            log.msg("message={m},url={url}".format(m=e, url=response.url),level=log.ERROR)
#        fund = sel.xpath(u"//b[text()='金    额：']/../text()").extract()
#        info = self.for_ominated_data(info, fund)
#        intro = sel.xpath(u"//b[text()='案例介绍：']/../following-sibling::p[1]/text()").extract()
#        info = self.for_ominated_data(info, intro)
#
#        try:
#            info = '\001'.join(info)
#            item['content'] = info
#            yield item
#        except Exception, e:
#            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)
#
#
#
#
#
#
#
