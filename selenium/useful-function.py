# 导入Options类
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
url = 'https://movie.douban.com/'
# Options类实例化
chrome_options = Options()
# 设置浏览器参数
# --headless是不显示浏览器启动以及执行过程
chrome_options.add_argument('--headless')
# 设置lang和User-Agent信息，防止反爬虫检测
chrome_options.add_argument('lang=zh_CN.UTF-8')
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
chrome_options.add_argument('User-Agent=' + UserAgent)
# 启动浏览器并设置chrome_options参数
path = '../venv/Scripts/chromedriver81.exe'
driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
# 浏览器窗口最大化
# driver.maximize_window()
# 浏览器窗口最小化
# driver.minimize_window()
driver.get(url)
# 获取网页的标题内容
print(driver.title)
# page_source是获取网页的HTML代码
print(driver.page_source)