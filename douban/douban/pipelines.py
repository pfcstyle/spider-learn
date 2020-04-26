# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# 导入setting配置信息
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

Base = declarative_base()
class scrapy_db(Base):
    __tablename__ = 'douban_db'
    id = Column(Integer(), primary_key=True)
    movieId = Column(String(100))
    comment = Column(String(2000))

class DoubanPipeline(object):
    def __init__(self):
        # 初始化，连接数据库
        conntion = settings['MYSQL_CONNECTION']
        engine = create_engine(conntion, echo=False, pool_size=2000)
        DBSession = sessionmaker(bind=engine)
        self.SQLsession = DBSession()
        # 创建数据表
        Base.metadata.create_all(engine)

    def process_item(self, item, spider):
        # 入库处理
        self.SQLsession.execute(scrapy_db.__table__.insert(),
                                {'comment': item['comment'].replace("\n", ""),
                                 'movieId': item['movieId']})
        self.SQLsession.commit()
        return item
