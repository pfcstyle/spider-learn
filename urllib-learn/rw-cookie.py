import urllib.request
from http import cookiejar
filename = 'cookie.txt'
# MozillaCookieJar保存cookie
cookie = cookiejar.MozillaCookieJar(filename)
# HTTPCookieProcessor创建cookie处理器
handler = urllib.request.HTTPCookieProcessor(cookie)
# 创建自定义opener
opener = urllib.request.build_opener(handler)
# open方法打开网页
response = opener.open('https://movie.douban.com/')
# 保存cookie文件
cookie.save()


# read
# import urllib.request
# from http import cookiejar
# filename = 'cookie.txt'
# # 创建MozillaCookieJar对象
# cookie = cookiejar.MozillaCookieJar()
# # 读取cookie内容到变量
# cookie.load(filename)
# # HTTPCookieProcessor创建cookie处理器
# handler = urllib.request.HTTPCookieProcessor(cookie)
# # 创建opener
# opener = urllib.request.build_opener(handler)
# # opener打开网页
# response = opener.open('https://movie.douban.com/')
# # 输出结果
# print(cookie)