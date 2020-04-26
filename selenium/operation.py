
from selenium import webdriver
url = 'https://ssl.zc.qq.com/v3/index-chs.html?from=pt'
path = '../venv/Scripts/chromedriver81.exe'
driver = webdriver.Chrome(executable_path=path)
driver.get(url)
# 输入名字和密码
driver.find_element_by_id('nickname').send_keys('pythonAuto')
driver.find_element_by_id('password').send_keys('pythonAuto123')
# 获取手机号码下方的tips内容
tipsValue = driver.find_element_by_xpath(
'//div[3]/div[2]/div[1]/form/div[7]/div').text
print(tipsValue)
# 勾选同时开通QQ空间
driver.find_element_by_class_name('checkbox').click()
# 点击“注册”按钮
driver.find_element_by_id('get_acc').submit()

####################################################################################################
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium import webdriver
path = '../venv/Scripts/chromedriver81.exe'
driver = webdriver.Chrome(executable_path=path)
url = 'https://passport.bilibili.com/login'
driver.get(url)
# 双击登录
element = driver.find_element_by_class_name('tit')
ActionChains(driver).double_click(element).perform()
# 设置延时，否则会导致操作过快
time.sleep(3)
# 拖拉滑条
element = driver.find_element_by_class_name('gt_slider_knob,gt_show')
ActionChains(driver).drag_and_drop_by_offset(element, 100, 0).perform()


####################################################################################################
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
path = '../venv/Scripts/chromedriver81.exe'
driver = webdriver.Chrome(executable_path=path)
driver.get("http://www.baidu.com")

# 获取输入框标签对象
element = driver.find_element_by_id('kw')
# 输入框输入内容
element.send_keys("Python你")
time.sleep(2)

# 删除最后的一个文字
element.send_keys(Keys.BACK_SPACE)
time.sleep(2)

# 添加输入空格键 + “教程”
element.send_keys(Keys.SPACE)
element.send_keys("教程")
time.sleep(2)

# ctrl+a 全选输入框内容
element.send_keys(Keys.CONTROL, 'a')
time.sleep(2)

# ctrl+x 剪切输入框内容
element.send_keys(Keys.CONTROL, 'x')
time.sleep(2)

# ctrl+v 粘贴内容到输入框
element.send_keys(Keys.CONTROL, 'v')
time.sleep(2)

# 通过回车键来代替单击操作
driver.find_element_by_id('su').send_keys(Keys.ENTER)

