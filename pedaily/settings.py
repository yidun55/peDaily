# -*- coding: utf-8 -*-

# Scrapy settings for pedaily project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'pedaily'

SPIDER_MODULES = ['pedaily.spiders']
NEWSPIDER_MODULE = 'pedaily.spiders'

DEFAULT_ITEM_CLASS='pedaily.items.PedailyItem'

LOG_FILE='/root/dyh/data/pedaily/loginv_error_redo'

DOWNLOAD_TIMEOUT = 180

ITEM_PIPELINES = {
            'pedaily.pipelines.PedailyPipeline': 300,
            'pedaily.scrapy_redis.pipelines.RedisPipeline': 400,
        }

REDIS_HOST = '10.5.13.22'
REDIS_PORT = 6379
REDIS_STORAGE_HOST = '10.5.13.22'
REDIS_STORAGE_PORT = 6379

SCHEDULER = 'pedaily.scrapy_redis.scheduler.Scheduler'

SCHEDULER_PERSIST = True

SCHEDULER_QUEUE_CLASS = 'pedaily.scrapy_redis.queue.SpiderQueue'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'pedaily (+http://www.yourdomain.com)'
