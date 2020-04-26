from lianjia.items import LianjiaItem
from scrapy.selector import Selector
from scrapy.spiders import Spider, Request
import configparser, json

class HouseSpider(Spider):
    # 属性name必须设置，而且是唯一命名，用于运行爬虫
    name = "House"
    # 设置允许访问域名
    allowed_domains = ["lianjia.com"]
    # 设置URL
    start_urls = 'https://%s.lianjia.com/ershoufang/pg%s/'
    # 重写start_requests
    def start_requests(self):
        # 读取配置文件，获取电影ID并生成列表
        conf = configparser.ConfigParser()
        domainList = []
        conf.read(self.settings.get('CONF'))
        temp = conf['LJ']
        if 'domain' in temp.keys():
            domainList = conf['LJ']['domain'].split(',')
        for d in domainList:
            self.domain = d
            headers = self.settings.get('DEFAULT_REQUEST_HEADERS')
            headers['Host'] = self.domain + '.lianjia.com'
            headers['Upgrade-Insecure-Requests'] = '1'
            for p in range(100):
                url = self.start_urls %(self.domain, str(p+1))
                yield Request(url=url, headers=headers, meta={'headers': headers}, callback=self.pageInfo)

    def pageInfo(self, response):
        sel = Selector(response)
        headers = response.meta['headers']
        houseURL = sel.xpath('//ul[@class="sellListContent"]/li')
        for u in houseURL:
            url = ''.join(u.xpath('.//div[@class="title"]//a//@href').extract()).strip()
            yield Request(url=url, headers=headers, callback=self.housePage)

    def housePage(self, response):
        houseInfo = {}
        villageInfo = {}
        sel = Selector(response)
        # 房屋信息
        houseInfo['url'] = response.url
        houseInfo['house_hid'] = response.url.split('/')[-1].split('.')[0]
        houseInfo['price'] = ''.join(sel.xpath('//span[@class="total"]//text()').extract())+ ''.join(sel.xpath('//span[@class="unit"]//span//text()').extract())
        houseInfo['unitPrice'] = ''.join(sel.xpath('//span[@class="unitPriceValue"]//text()').extract())
        baseInfo = sel.xpath('//div[@class="base"]//li')
        # 基本信息
        for b in baseInfo:
            i = ''.join(b.xpath('.//text()').extract())
            if '房屋户型' in str(i):
                houseInfo['type'] = i.replace('房屋户型', '')
            elif '所在楼层' in str(i):
                houseInfo['high'] = i.replace('所在楼层', '')
            elif '建筑面积' in str(i):
                houseInfo['acreage'] = i.replace('建筑面积', '')
            elif '户型结构' in str(i):
                houseInfo['structure'] = i.replace('户型结构', '')
            elif '套内面积' in str(i):
                houseInfo['innerAcreage'] = i.replace('套内面积', '')
            elif '建筑类型' in str(i):
                houseInfo['style'] = i.replace('建筑类型', '')
            elif '房屋朝向' in str(i):
                houseInfo['orientation'] = i.replace('房屋朝向', '')
            elif '建筑结构' in str(i):
                houseInfo['framework'] = i.replace('建筑结构', '')
            elif '装修情况' in str(i):
                houseInfo['renovation'] = i.replace('装修情况', '')
            elif '梯户比例' in str(i):
                houseInfo['proportion'] = i.replace('梯户比例', '')
            elif '配备电梯' in str(i):
                houseInfo['elevator'] = i.replace('配备电梯', '')
            elif '产权年限' in str(i):
                houseInfo['years'] = i.replace('产权年限', '')
        # 交易信息
        transaction = sel.xpath('//div[@class="transaction"]//li')
        for t in transaction:
            i = ''.join(t.xpath('.//span//text()').extract())
            if '挂牌时间' in str(i):
                houseInfo['listingTime'] = i.replace('挂牌时间', '').strip()
            elif '交易权属' in str(i):
                houseInfo['tradingRights'] = i.replace('交易权属', '').strip()
            elif '上次交易' in str(i):
                houseInfo['lastTransaction'] = i.replace('上次交易', '').strip()
            elif '房屋用途' in str(i):
                houseInfo['use'] = i.replace('房屋用途', '').strip()
            elif '房屋年限' in str(i):
                houseInfo['life'] = i.replace('房屋年限', '').strip()
            elif '产权所属' in str(i):
                houseInfo['belong'] = i.replace('产权所属', '').strip()
        # 小区信息
        villageInfo['region_rid'] = ''.join(sel.xpath('//a[@class="info "]//@href').extract()).split('xiaoqu/')[1].replace('/','')
        houseInfo['region_rid'] = villageInfo['region_rid']
        villageInfo['area'] = ''.join(sel.xpath('//div[@class="areaName"]//a//text()').extract())
        villageURL = 'https://%s.lianjia.com/xiaoqu/%s/' %(self.domain, villageInfo['region_rid'])
        # 构建请求头
        headers = self.settings.get('DEFAULT_REQUEST_HEADERS')
        headers['Host'] = self.domain + '.lianjia.com'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Referer'] = houseInfo['url']
        yield Request(url=villageURL, headers=headers, meta={'houseInfo': houseInfo, 'villageInfo': villageInfo}, callback=self.villagePage, dont_filter=True)

    def villagePage(self, response):
        houseInfo = response.meta['houseInfo']
        villageInfo = response.meta['villageInfo']
        sel = Selector(response)
        villageInfo['name'] = ''.join(sel.xpath('//h1[@class="detailTitle"]//text()').extract())
        villageInfo['area'] = ''.join(sel.xpath('//div[@class="detailDesc"]//text()').extract())
        info = sel.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]')
        villageInfo['buildYear'] = ''.join(info[0].xpath('.//text()').extract())
        villageInfo['buildType'] = ''.join(info[1].xpath('.//text()').extract())
        villageInfo['buildCost'] = ''.join(info[2].xpath('.//text()').extract())
        villageInfo['costCompany'] = ''.join(info[3].xpath('.//text()').extract())
        villageInfo['developers'] = ''.join(info[4].xpath('.//text()').extract())
        villageInfo['buildCount'] = ''.join(info[5].xpath('.//text()').extract())
        villageInfo['houseCount'] = ''.join(info[6].xpath('.//text()').extract())
        villageInfo['nearby'] = ''.join(info[7].xpath('.//text()').extract())
        # 入库处理
        item = LianjiaItem()
        item['houseInfo'] = houseInfo
        item['villageInfo'] = villageInfo
        yield item
