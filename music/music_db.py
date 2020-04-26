from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 连接数据库
engine=create_engine("sqlite:///music.db",echo=False)
# 创建会话对象，用于数据表的操作
DBSession = sessionmaker(bind=engine)
SQLsession = DBSession()
Base = declarative_base()

# 映射数据表
class song(Base):
    # 表名
    __tablename__ ='song'
    # 字段，属性
    song_id = Column(Integer, primary_key=True)
    song_name = Column(String(50))
    song_ablum = Column(String(50))
    song_interval = Column(String(50))
    song_songmid = Column(String(50))
    song_singer = Column(String(50))
# 创建数据表
Base.metadata.create_all(engine)
# 数据入库
def insert_data(song_dict):
    # 连接数据库
    engine = create_engine("sqlite:///music.db")
    # 创建会话对象，用于数据表的操作
    DBSession = sessionmaker(bind=engine)
    SQLsession = DBSession()
    data = song(
        song_name = song_dict['song_name'],
        song_ablum = song_dict['song_ablum'],
        song_interval = song_dict['song_interval'],
        song_songmid = song_dict['song_songmid'],
        song_singer = song_dict['song_singer'],
    )
    SQLsession.add(data)
    SQLsession.commit()


if __name__ == '__main__':
    # 创建数据表
    Base.metadata.create_all(engine)