# 导入urllib
import urllib.request
url = 'https://movie.douban.com/'
# 自定义请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
    'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Referer': 'https://movie.douban.com/',
    'Connection': 'keep-alive'}
# 设置request的请求头
req = urllib.request.Request(url, headers=headers)
# 使用urlopen打开req
html = urllib.request.urlopen(req).read().decode('utf-8')
# 写入文件
f = open('code2.txt', 'w', encoding='utf8')
f.write(html)
f.close()