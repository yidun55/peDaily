#coding: utf-8

"""
  从redis上读取url,请求，解析出目标数据
  auther:yidun55
  email:heshang1203@sina.com
  date:2015/06/24
"""

from scrapy import log
from scrapy.http import Request,FormRequest
from scrapy.conf import settings
from scrapy.spider import Spider
from pedaily.items import *

import re


from pedaily.scrapy_redis.spiders import RedisSpider
from pedaily.extract_xpath.inv_xpath import inv_extract 
from pedaily.extract_xpath.pe_xpath import pe_extract

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class pedaily(RedisSpider, Spider):
    download_delay=1
    writeInFile = 'enterprise_info_list'
    name = 'enterprise_detail_list'
    redis_key = 'enterprise_detail_url'

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
        name = sel.xpath(u"//div[@class='news-show company-show']/h1/text()").extract()  #公司名称
        info = self.for_ominated_data(info, name)
        co_abbr = sel.xpath(u"//div[@class='news-show company-show']/h1/em/text()").extract()  #公司简称
        info = self.for_ominated_data(info, co_abbr)
        en_name = sel.xpath(u"//div[@class='news-show company-show']/h2/text()").extract()  #公司英文名称
        info = self.for_ominated_data(info, en_name)
        found_date = sel.xpath(u"//div[@class='box-caption']//li[contains(text(),'成立时间：')]/text()").re(ur'成立时间：([\d\D]*)')  #成立时间
        info = self.for_ominated_data(info, found_date)
        headquarters = sel.xpath(u"//div[@class='box-caption']//li[contains(text(),'机构总部：')]/text()").re(ur'机构总部：([\d\D]*)')  #机构总部
        info = self.for_ominated_data(info, headquarters)
        in_class = sel.xpath(u"//div[@class='box-caption']//li[contains(text(),'所属行业：')]/text()").re(ur'所属行业：([\d\D]*)')  #所属行业
        info = self.for_ominated_data(info, in_class)
        websit = sel.xpath(u"//div[@class='box-caption']//li[text()='官方网站：']/a/@href").extract()   #官方网站
        info = self.for_ominated_data(info, websit)
        fox_tel_zip = sel.xpath(u"//div/p/text()").extract() #提取传真，联系电话，邮政编码，详细地址。
        result = []
        for i in fox_tel_zip:
            result.append(i.strip())
        raw = "\002".join(result)
        blank_unicode = '\xe3\x80\x80\xe3\x80\x80'
        blank_unicode = blank_unicode.decode("utf-8").encode("utf-8")
        fox_re = ur"传%s真：([\w\W]*?)\002" %blank_unicode
        fox = re.findall(fox_re, raw)    #传真i
        info = self.for_ominated_data(info, fox)
        tel = re.findall(ur"联系电话：([\w\W]*?)\002", raw)  #联系电话
        info = self.for_ominated_data(info, tel)
        zip_code = re.findall(ur"邮政编码：([\w\W]*?)\002", raw)  #邮政编码
        info = self.for_ominated_data(info, zip_code)
        addr = re.findall(ur"详细地址：([\w\W]*?)\002", raw)  #详细地址
        info = self.for_ominated_data(info, addr)
        url_list = sel.xpath(u"//table/tr//a[text()='详情']/@href").extract()
        if len(url_list) == 0:  
            """
            如果该公司没有投资和募资的记录，则只记录当前页面中有关公司的信息
            """
            item = PedailyItem()
            try:
                info = '\001'.join(info)
                item['content'] = info
                yield item
            except Exception, e:
                log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

        else:
            """
            如果有有关公司投资募资的信息，先判断是投资还是募资事件，并根据具体的情况调用相应的函数提取投资募资信息，并将这些信息附加到已提取的信息后，最后加入文件。
            """
            base_url = 'http://zdb.pedaily.cn'
            for url in url_list:
                if url.split('/')[1] == 'inv':
#                    yield FormRequest(base_url+url,callback=lambda response, info=info:self.inv_detail(response,info),dont_filter=True)
                    yield Request(base_url+url, meta={'info_list':info},callback=self.inv_detail, dont_filter=True)
                elif url.split('/')[1] == 'pe':
                   # yield Request(base_url+url,callback=lambda response, info=info:self.pe_detail(response,info),dont_filter=True)
                   yield Request(base_url+url, meta={'info_list':info},callback=self.pe_detail, dont_filter=True)
                else:
                    log.msg("out of inv and pe {url}".format(url=response.url),level=log.ERROR)

    def inv_detail(self, response):
        """
        提取公司有投资的信息
        """
       # log.msg("inv_detail work ooo",level=log.INFO)
        info_list = response.meta['info_list']
        print "\001".join(info_list)
        invParse = inv_extract()
        info = invParse.parse(response)
        info_list.append("投资事件")
        info_list.extend(info)
        print "\001".join(info_list)

        item = PedailyItem()
        try:
            info = '\001'.join(info_list)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)

    def pe_detail(self, response):
        """
        提取公司募资的信息
        """
        info_list = response.meta['info_list']
        peParse = pe_extract()
        info = peParse.parse(response)
        info_list.append("募资事件")
        info_list.extend(info)

        item = PedailyItem()
        try:
            info = '\001'.join(info_list)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('content:{content}, url={url}'.format(content=info, url=response.url), level=log.ERROR)





