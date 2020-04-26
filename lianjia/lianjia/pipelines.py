# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
# 导入setting配置信息
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

# 定义映射类
Base = declarative_base()
# 小区信息表
class villageInfo(Base):
    __tablename__ = 'villageInfo'
    id = Column(Integer(), primary_key=True)
    region_rid = Column(String(100), comment='小区编号')
    name = Column(String(100), comment='小区名称')
    area = Column(String(100), comment='小区位置')
    buildYear = Column(Text(), comment='建成日期')
    buildType = Column(String(100), comment='建筑类型')
    buildCost = Column(String(100), comment='物业费用')
    costCompany = Column(String(100), comment='物业公司')
    developers = Column(String(100), comment='开发商')
    buildCount = Column(String(100), comment='楼栋总数')
    houseCount = Column(String(100), comment='房屋总数')
    nearby = Column(String(100), comment='附近门店')
    log_date = Column(DateTime(), default=datetime.now, onupdate=datetime.now, comment='记录日期')
# 房屋信息表
class houseInfo(Base):
    __tablename__ = 'houseInfo'
    id = Column(Integer(), primary_key=True)
    house_hid = Column(String(100), comment='房屋编号')
    acreage = Column(String(100), comment='建筑面积')
    type = Column(String(100), comment='房屋户型')
    high = Column(String(100), comment='所在楼层')
    structure = Column(String(100), comment='户型结构')
    innerAcreage = Column(String(100), comment='套内面积')
    style = Column(String(100), comment='建筑类型')
    orientation = Column(String(100), comment='房屋朝向')
    framework = Column(String(100), comment='建筑结构')
    renovation = Column(String(100), comment='装修情况')
    proportion = Column(String(100), comment='梯户比例')
    elevator = Column(String(100), comment='配备电梯')
    years = Column(String(100), comment='产权年限')
    price = Column(String(100), comment='售价')
    unitPrice = Column(String(100), comment='每平方售价')
    listingTime = Column(String(100), comment='挂牌时间')
    tradingRights = Column(String(100), comment='交易权属')
    lastTransaction = Column(String(100), comment='上次交易')
    use = Column(String(100), comment='房屋用途')
    life = Column(String(100), comment='房屋年限')
    belong = Column(String(100), comment='产权所属')
    url = Column(String(100), comment='地址链接')
    region_rid = Column(String(100), comment='小区编号')
    log_date = Column(DateTime(), default=datetime.now, onupdate=datetime.now, comment='记录日期')

class LianjiaPipeline(object):
    def __init__(self):
        # 初始化，连接数据库
        conntion = settings['SQLITE_CONNECTION']
        engine = create_engine(conntion, echo=False)
        DBSession = sessionmaker(bind=engine)
        self.SQLsession = DBSession()
        # 创建数据表
        Base.metadata.create_all(engine)

        ##  删除数据表
        # houseInfo.drop(bind=engine)
        # Base.metadata.drop_all(engine)

# 写入房屋信息
    def house_db(self, info):
        house_hid = info['house_hid']
        # 判断是否已存在记录
        temp = self.SQLsession.query(houseInfo).filter_by(house_hid=house_hid).first()
        if temp:
            temp.acreage = info.get('acreage', '')
            temp.type = info.get('type', '')
            temp.high = info.get('high', '')
            temp.structure = info.get('structure', '')
            temp.innerAcreage = info.get('innerAcreage', '')
            temp.style = info.get('style', '')
            temp.orientation = info.get('orientation', '')
            temp.framework = info.get('framework', '')
            temp.renovation = info.get('renovation', '')
            temp.proportion = info.get('proportion', '')
            temp.elevator = info.get('elevator', '')
            temp.years = info.get('years', '')
            temp.price = info.get('price', '')
            temp.unitPrice = info.get('unitPrice', '')
            temp.listingTime = info.get('listingTime', '')
            temp.tradingRights = info.get('tradingRights', '')
            temp.lastTransaction = info.get('lastTransaction', '')
            temp.use = info.get('use', '')
            temp.life = info.get('life', '')
            temp.belong = info.get('belong', '')
            temp.url = info.get('url', '')
            temp.region_rid = info.get('region_rid', '')
        else:
            inset_data = houseInfo(
                house_hid=info.get('house_hid', ''),
                acreage=info.get('acreage', ''),
                type=info.get('type', ''),
                high=info.get('high', ''),
                structure=info.get('structure', ''),
                innerAcreage=info.get('innerAcreage', ''),
                style=info.get('style', ''),
                orientation=info.get('orientation', ''),
                framework=info.get('framework', ''),
                renovation=info.get('renovation', ''),
                proportion=info.get('proportion', ''),
                elevator=info.get('elevator', ''),
                years=info.get('years', ''),
                price=info.get('price', ''),
                unitPrice=info.get('unitPrice', ''),
                listingTime=info.get('listingTime', ''),
                tradingRights=info.get('tradingRights', ''),
                lastTransaction=info.get('lastTransaction', ''),
                use=info.get('use', ''),
                life=info.get('life', ''),
                belong=info.get('belong', ''),
                url=info.get('url', ''),
                region_rid=info.get('region_rid', ''),
            )
            self.SQLsession.add(inset_data)
        self.SQLsession.commit()

    # 写入小区信息
    def village_db(self, info):
        region_rid = info['region_rid']
        # 判断是否已存在记录
        temp = self.SQLsession.query(villageInfo).filter_by(region_rid=region_rid).first()
        if temp:
            temp.name = info.get('name')
            temp.area = info.get('area', '')
            temp.buildYear = info.get('buildYear', '')
            temp.buildType = info.get('buildType', '')
            temp.buildCost = info.get('buildCost', '')
            temp.costCompany = info.get('costCompany', '')
            temp.developers = info.get('developers', '')
            temp.buildCount = info.get('buildCount', '')
            temp.houseCount = info.get('houseCount', '')
            temp.nearby = info.get('nearby', '')
        else:
            inset_data = villageInfo(
                region_rid=info.get('region_rid', ''),
                name=info.get('name'),
                area=info.get('area', ''),
                buildYear=info.get('buildYear', ''),
                buildType=info.get('buildType', ''),
                buildCost=info.get('buildCost', ''),
                costCompany=info.get('costCompany', ''),
                developers=info.get('developers', ''),
                buildCount=info.get('buildCount', ''),
                houseCount=info.get('houseCount', ''),
                nearby=info.get('nearby', '')
            )
            self.SQLsession.add(inset_data)
        self.SQLsession.commit()

    # 入库处理
    def process_item(self, item, spider):
        self.house_db(item['houseInfo'])
        self.village_db(item['villageInfo'])
        return item