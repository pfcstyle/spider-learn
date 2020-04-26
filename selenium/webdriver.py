# 导入Selenium的webdriver类
from selenium import webdriver
# 设置变量url，用于浏览器访问
url = 'https://www.baidu.com/'
# 将webdriver类实例化，将浏览器设定为Google Chrome
# 参数executable_path是设置chromedriver的路径
# http://chromedriver.chromium.org/downloads 版本对照表
# http://npm.taobao.org/mirrors/chromedriver
# http://chromedriver.storage.googleapis.com/index.html
# 下载对应版本
path = '../venv/Scripts/chromedriver81.exe'
browser = webdriver.Chrome(executable_path=path)
# 打开浏览器并访问百度网址
browser.get(url)
