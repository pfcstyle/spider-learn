from douban.items import DoubanItem
from scrapy.selector import Selector
from scrapy.spiders import Spider, Request
import configparser

class MovieSpider(Spider):
    # 属性name必须设置，而且是唯一命名，用于运行爬虫
    name = "Movie"
    # 设置允许访问域名
    allowed_domains = ["https://movie.douban.com"]

    # 设置URL
    start_urls = 'https://movie.douban.com/subject/%s/comments?start=%s&limit=20&sort=new_score&status=P'
    # 重写start_requests
    def start_requests(self):
        # 读取配置文件，获取电影ID并生成列表
        conf = configparser.ConfigParser()
        urlsList = []
        conf.read(self.settings.get('CONF'))
        temp = conf['config']
        if 'movieId' in temp.keys():
            urlsList = conf['config']['movieId'].split(',')

        for u in urlsList:
            # 根据电影ID选择爬取方式
            if str(u) in '26425063':
                value = True
            else:
                value = False
            # 每部电影爬取两页的评论
            for page in range(2):
                url = self.start_urls %(str(u), str(page * 20))
                yield Request(url=url, meta={'movieId': str(u), 'usedSelenium': value}, callback=self.parse)

    def parse(self, response):
        # 将响应内容生成Selector，用于数据清洗
        sel = Selector(response)
        # 定义DoubanItem对象
        item = DoubanItem()
        comments = sel.xpath('//div[@id="comments"]//div[@class="comment"]')
        for c in comments:
            item['movieId'] = response.meta['movieId']
            item['comment'] = ''.join(c.xpath('.//p//span//text()').extract()).strip()
            yield item

