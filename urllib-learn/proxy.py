import urllib.request
url = 'https://movie.douban.com/'
# 设置代理IP
proxy_handler = urllib.request.ProxyHandler({
    'http': '218.56.132.157:8080',
    'https': '183.30.197.29:9797'})
# 必须使用build_opener()函数来创建带有代理IP功能的opener对象
opener = urllib.request.build_opener(proxy_handler)
response = opener.open(url)
html = response.read().decode('utf-8')
f = open('code3.txt', 'w', encoding='utf8')
f.write(html)
f.close()
