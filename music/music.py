import requests, time
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from music_db import *
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
# 创建请求头和requests会话对象session
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
           }
session = requests.session()

# 下载歌曲
def download(guid, songmid, cookie_dict):
    # 参数guid来自cookies的pgv_pvid
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&data=%7B%22req%22%3A%7B%22module%22%3A%22CDN.SrfCdnDispatchServer%22%2C%22method%22%3A%22GetCdnDispatch%22%2C%22param%22%3A%7B%22guid%22%3A%22'+guid+'%22%2C%22calltype%22%3A0%2C%22userip%22%3A%22%22%7D%7D%2C%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%22'+guid+'%22%2C%22songmid%22%3A%5B%22'+songmid+'%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%220%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3A0%2C%22format%22%3A%22json%22%2C%22ct%22%3A20%2C%22cv%22%3A0%7D%7D'
    r = session.get(url, headers=headers, cookies=cookie_dict)
    purl = r.json()['req_0']['data']['midurlinfo'][0]['purl']
    # 下载歌曲
    if purl:
        url = 'http://isure.stream.qqmusic.qq.com/%s' %(purl)
        print(url)
        r = requests.get(url, headers=headers)
        f = open('song/' + songmid + '.m4a', 'wb')
        f.write(r.content)
        f.close()
        return True
    else:
        return False

# 使用Selenium获取Cookies
def getCookies():
    chrome_options = Options()
    # 设置浏览器参数
    # --headless是不显示浏览器启动以及执行过程
    # chrome_options.add_argument('--headless')
    path = '../venv/Scripts/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    # 访问两个URL，QQ网站才能生成Cookies
    driver.get('https://y.qq.com/')
    time.sleep(5)
    # 某个歌手的歌曲信息，用于获取Cookies，因为不是全部请求地址都有Cookies
    url = 'https://y.qq.com/n/yqq/singer/0025NhlN2yWrP4.html'
    driver.get(url)
    time.sleep(5)
    cookie = driver.get_cookies()
    driver.quit()
    # Cookies格式化
    print(cookie)
    cookie_dict = {}
    for i in cookie:
        cookie_dict[i['name']] = i['value']
    return cookie_dict


# 获取歌手的全部歌曲
def get_singer_songs(singermid, cookie_dict):
    # 获取歌手姓名和歌曲总数
    url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?loginUin=0&hostUin=0&singermid=%s' \
          '&order=listen&begin=0&num=30&songstatus=1' % (singermid)
    r = session.get(url)
    # 获取歌手姓名
    song_singer = r.json()['data']['singer_name']
    # 获取歌曲总数
    songcount = r.json()['data']['total']
    # 根据歌曲总数计算总页数
    pagecount = math.ceil(int(songcount) / 30)
    # 循环页数，获取每一页歌曲信息
    for p in range(pagecount):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?loginUin=0&hostUin=0&singermid=%s' \
              '&order=listen&begin=%s&num=30&songstatus=1' % (singermid, p * 30)
        r = session.get(url)
        # 得到每页的歌曲信息
        music_data = r.json()['data']['list']
        # songname-歌名，ablum-专辑，interval-时长，songmid歌曲id，用于下载音频文件
        # 将歌曲信息存放字典song_dict，用于入库
        song_dict = {}
        for i in music_data:
            song_dict['song_name'] = i['musicData']['songname']
            song_dict['song_ablum'] = i['musicData']['albumname']
            song_dict['song_interval'] = i['musicData']['interval']
            song_dict['song_songmid'] = i['musicData']['songmid']
            song_dict['song_singer'] = song_singer
            insert_data(song_dict)
            # 下载歌曲
            guid = cookie_dict['pgv_pvid']
            info = download(guid, song_dict['song_songmid'], cookie_dict)
            # 入库处理，参数song_dict
            # if info:
            #     insert_data(song_dict)
            # song_dict清空处理
            song_dict = {}

# 获取当前字母下全部歌手
def get_genre_singer(index, page_list, cookie_dict):
    for page in page_list:
        url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22genre%22%3A-100%2C%22index%22%3A'+str(index)+'%2C%22sin%22%3A'+str((page-1)*80)+'%2C%22cur_page%22%3A'+str(page)+'%7D%7D%7D'
        r = session.get(url)
        # 循环每一个歌手
        for k in r.json()['singerList']['data']['singerlist']:
            singermid = k['singer_mid']
            get_singer_songs(singermid, cookie_dict)

# 单进程单线程
def get_all_singer():
    # 获取字母A-Z全部歌手
    cookie_dict = getCookies()
    for index in range(1, 28):
        # 获取每个字母分类下总歌手页数
        url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22genre%22%3A-100%2C%22index%22%3A' + str(index) + '%2C%22sin%22%3A0%2C%22cur_page%22%3A1%7D%7D%7D'
        r = session.get(url, headers=headers)
        total = r.json()['singerList']['data']['total']
        pagecount = math.ceil(int(total) / 80)
        page_list = [x for x in range(1, pagecount+1)]
        # 获取当前字母下全部歌手
        get_genre_singer(index, page_list, cookie_dict)

# 多线程
def myThread(index, cookie_dict):
    # 每个字母分类的歌手列表页数
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22genre%22%3A-100%2C%22index%22%3A' + str(
        index) + '%2C%22sin%22%3A0%2C%22cur_page%22%3A1%7D%7D%7D'
    r = session.get(url, headers=headers)
    total = r.json()['singerList']['data']['total']
    pagecount = math.ceil(int(total) / 80)
    page_list = [x for x in range(1, pagecount+1)]
    thread_number = 10
    # 将每个分类总页数平均分给线程数
    list_interval = math.ceil(len(page_list) / thread_number)

    # 设置线程对象
    Thread = ThreadPoolExecutor(max_workers=thread_number)
    for i in range(thread_number):
        # 计算每条线程应执行的页数
        start_num = list_interval * i
        if list_interval * (i + 1) <= len(page_list):
            end_num = list_interval * (i + 1)
        else:
            end_num = len(page_list)
        # 每个线程各自执行不同的歌手列表页数
        Thread.submit(get_genre_singer, index, page_list[start_num: end_num],cookie_dict)

# 多进程
def myProcess():
    with ProcessPoolExecutor(max_workers=27) as executor:
        cookie_dict = getCookies()
        for index in range(1, 28):
            # 创建27个进程，分别执行A-Z分类和特殊符号#
            executor.submit(myThread, index, cookie_dict)


if __name__=='__main__':
    # 执行多进程多线程
    # myProcess()
    # 执行单进程单线程
    get_all_singer()
