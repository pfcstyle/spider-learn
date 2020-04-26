# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# 自定义Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.http import HtmlResponse

class SeleniumMiddleware(object):
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        path = '../venv/Scripts/chromedriver81.exe'
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=path)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def process_request(self, request, spider):
        # 参数usedSelenium决定是否使用Selenium
        if request.meta['usedSelenium']:
            try:
                # 生成一个页面的driver对象
                self.driver.get(request.url)
                # 直接返回响应内容
                return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8',
                                    status=200)
            except:
                # 若出现异常，抛出HTTP状态码500
                return HtmlResponse(url=request.url, status=500, request=request)
        # 如不使用Selenium，则执行原有的访问方式
        else:
            return None

    def __del__(self):
        self.driver.close()

    @classmethod
    def from_crawler(cls, crawler):
        # 读取settings.py的SELENIUM_TIMEOUT
        # 用于初始化方法的实例化
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),)