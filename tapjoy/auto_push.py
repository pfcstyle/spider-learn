import requests, time, datetime
import math
import configparser
import pickle
import re
import xlrd
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from push_notification import push_notification, createiOSPushByAndroid
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

# 创建请求头和requests会话对象session
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}
session = requests.session()
file_name = 'cookies.pkl'

def compare_time(time1):
    d1 = datetime.datetime.strptime(time1, '%Y/%m/%d %H:%M')
    d2 = datetime.datetime.now()
    delta = d1 - d2
    if delta.seconds > 3600:
        return True
    else:
        return False

def readExcel():
    res: list = []
    wb = xlrd.open_workbook('push.xlsx')
    # 获取Sheets总数
    ws_count = wb.nsheets
    # 通过索引顺序获取Sheets
    # ws = wb.sheets()[0]
    # ws = wb.sheet_by_index(0)
    # 通过Sheets名获取Sheets
    ws = wb.sheet_by_index(1)
    time_ws = wb.sheet_by_index(0)
    if not time_ws:
        print('错误：时间表没有填')
        return
    # 获得所有行列
    nrows = ws.nrows
    ncols = ws.ncols
    countrys = {
        'KO': 'South Korea',
        'JP': 'Japan',
        'US': 'Korea,Japan,China,Taiwan',
        'CN': 'China',
        'TW': 'Taiwan'
    }
    languages = {
        'KO': 'Korean',
        'JP': 'Japanese',
        'US': 'Korean,Japanese,Simplified Chinese,Traditional Chinese',
        'CN': 'Simplified Chinese',
        'TW': 'Traditional Chinese'
    }
    # 按列（日期）开始
    for i in range(1, ncols):
        # 获取整列内容
        col_values = ws.col_values(i)
        date = col_values[0]
        if not date:
            print('错误：第{}列日期为空'.format(i + 1))
            continue
        timeStruct = time.strptime(date, "%Y/%m/%d")
        # timeStruct = time.localtime(date)
        for j in range(1, nrows):
            message = str(col_values[j])
            if not message:
                print('警告：第{}列第{}行内容为空'.format(i + 1, j + 1))
            if message:
                country = ws.cell(j, 0).value
                push_android = push_notification()
                push_android.name = '{}_{}_AOS'.format(country, time.strftime("%m%d", timeStruct))
                push_android.platform = 'Android'

                push_android.country = countrys.get(country, 'no')
                if country == 'no':
                    print('错误：第{}行国家错误'.format(j + 1))
                    continue
                push_android.isExcludeCountry = country == 'US'

                push_android.language = languages.get(country)
                push_android.isExcludeLanguage = country == 'US'

                push_android.date = time.strftime("%Y/%m/%d", timeStruct)
                times = str(time_ws.cell(j, i).value).split(':')
                if len(times) != 2:
                    print('错误：第{}列第{}行时间格式错误。'.format(i + 1, j + 1))
                    continue
                push_android.hour = times[0]
                push_android.minute = times[1]
                com_time = "{} {}:{}".format(push_android.date, push_android.hour, push_android.minute)
                if ~compare_time(com_time):
                    print('错误：第{}列第{}行时间距离当前时间小于1小时。'.format(i + 1, j + 1))
                    continue

                # message_split = message.split('{#}')
                message_split = message.split('{#}')
                if len(message_split) != 2:
                    print('错误：第{}列第{}行内容错误：分隔符数量错误。'.format(i + 1, j + 1))
                    continue

                push_android.messageTitle = message_split[0].strip()
                push_android.messageContent = message_split[1].strip()

                push_ios = createiOSPushByAndroid(push_android)
                res.append(push_android)
                res.append(push_ios)

    print(res)
    return res


def getPureDomainCookies(cookies):
    domain2cookie = {}  # 做一个域到cookie的映射
    for cookie in cookies:
        domain = cookie['domain']
        if domain in domain2cookie:
            domain2cookie[domain].append(cookie)
        else:
            domain2cookie[domain] = []
    maxCnt = 0
    ansDomain = ''
    for domain in domain2cookie.keys():
        cnt = len(domain2cookie[domain])
        if cnt > maxCnt:
            maxCnt = cnt
            ansDomain = domain
    ansCookies = domain2cookie[ansDomain]
    return ansCookies


# 使用Selenium获取Cookies
def startChrome():
    chrome_options = Options()
    # 设置浏览器参数
    # --headless是不显示浏览器启动以及执行过程
    # chrome_options.add_argument('--headless')
    # 通过驱动器程序启动chrome
    path = '../venv/Scripts/chromedriver81.exe'
    driver = webdriver.Chrome(executable_path=path, options=chrome_options)
    driver.maximize_window()

    pushs = readExcel()
    if len(pushs) < 1:
        print('错误：有效推送为0个。')
        driver.close()
        return

    login(driver)

    # create_single_push(driver, pushs[-1])
    for push in pushs:
        create_single_push(driver, push)
        time.sleep(5)

    # cookie = driver.get_cookies()
    # if cookie.count() == 0:
    #     driver.get()
    # # Cookies格式化
    # print(cookie)
    # cookie_dict = {}
    # for i in cookie:
    #     cookie_dict[i['name']] = i['value']
    # print(cookie_dict)
    # return cookie_dict


def login(driver: webdriver.Chrome):
    url = 'https://ltv.tapjoy.com/s/l#session/login?next=https%3A%2F%2Fltv.tapjoy.com%2Fs%2F5d4401f8-0800-8000-8000-7a5cca0009d3%2Fmonetization%23push%2Fedit%3Ftype%3Dmanual'
    driver.get(url)
    driver.implicitly_wait(30)
    # 判断login页面是否加载完成
    condition = expected_conditions.visibility_of_element_located((By.ID, 'password'))
    WebDriverWait(driver=driver, timeout=10, poll_frequency=0.5).until(condition)
    config = configparser.ConfigParser()
    config.read('./secret.ini')
    driver.find_element_by_id('email').send_keys(config.get('account', 'username'))
    driver.find_element_by_id('password').send_keys(config.get('account', 'password'))
    time.sleep(1)
    driver.find_element_by_class_name('session_btn_primary').click()
    time.sleep(10)
    # save cookie
    # cookies = driver.get_cookies()
    # if cookies:
    #     f = open(file_name, 'wb')
    #     # cookies = getPureDomainCookies(cookies)
    #     f.write(pickle.dumps(cookies))
    #     f.close()
    #     # 需要时间写cookie
    #     time.sleep(10)


def create_single_push(driver: webdriver.Chrome, push: push_notification):
    driver.get('https://ltv.tapjoy.com/s/5d4401f8-0800-8000-8000-7a5cca0009d3/monetization#push/edit?type=manual')
    driver.implicitly_wait(30)
    condition = expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '.well.basic .body'))
    WebDriverWait(driver=driver, timeout=10, poll_frequency=0.5).until(condition)

    try:
        close_notice_text = driver.find_element_by_id('btnNoticeClose')
        size = close_notice_text.size
        if size['height'] > 1 and size['width'] > 1:
            close_notice_text.click()
    except NoSuchElementException:
        print('no notice ')
    except ElementNotInteractableException:
        print('sss')


    # 基本信息
    basic_info_body = driver.find_element_by_css_selector('.well.basic .body')
    basic_info_body.find_element_by_css_selector(':nth-child(1) [name=name]').send_keys(push.name)
    # iOS
    if push.platform == 'iOS':
        basic_info_body.find_element_by_css_selector(':nth-child(2) .btn-group :nth-child(1)').click()
    else:
        basic_info_body.find_element_by_css_selector(':nth-child(2) .btn-group :nth-child(2)').click()

    # 目标用户
    target_body = driver.find_element_by_css_selector('.well.target_user_segment .body .target_body .target_section')
    # 国家
    # 点击国家  展示列表
    target_body.find_element_by_css_selector(':nth-child(1) .multi_select').click()
    # Japan
    country_list = target_body.find_element_by_css_selector(':nth-child(1) ul')
    countries = push.country.split(',')
    for country in countries:
        country_list.find_element_by_partial_link_text(country).click()
    # 收起列表
    time.sleep(1)
    target_body.find_element_by_css_selector(':nth-child(1) .multi_select').click()
    time.sleep(1)
    # target_body.find_element_by_css_selector(':nth-child(1) .multi_select').click()
    # 不包括这些
    if push.isExcludeCountry:
        target_body.find_element_by_css_selector(':nth-child(1) input[type=checkbox]').click()

    # 语言
    # 点击语言  展示列表
    language_select = target_body.find_element_by_css_selector(':nth-child(5) .multi_select')
    driver.execute_script("arguments[0].scrollIntoView();", language_select)
    time.sleep(1)
    # 有时候需要全局css选择器才可以
    language_toggle = driver.find_element_by_css_selector('.well.target_user_segment .body .target_body .target_section :nth-child(5) .multi_select >.btn')
    # language_select.click()
    # driver.execute_script("arguments[0].click();", language_toggle)
    # driver.execute_script("arguments[0].classList.add('open');", language_select)
    # language_select.click()
    webdriver.ActionChains(driver).move_to_element(language_toggle)
    driver.execute_script("arguments[0].focus();", language_toggle)
    driver.execute_script("arguments[0].click();", language_toggle)
    # 语言列表
    time.sleep(1)
    language_list = driver.find_element_by_css_selector('.well.target_user_segment .body .target_body .target_section :nth-child(5) .multi_select >ul')
    # Japanese
    lans = push.language.split(',')
    for lan in lans:
        language_list.find_element_by_partial_link_text(lan).click()
    # 收起列表
    driver.execute_script("arguments[0].click();", language_toggle)
    # 不包括这些
    if push.isExcludeLanguage:
        exclude = driver.find_element_by_css_selector('.well.target_user_segment .body .target_body .target_section :nth-child(5) input[type=checkbox]')
        driver.execute_script("arguments[0].click();", exclude)

    # 计划日程
    schedule_body = driver.find_element_by_css_selector('.well.schedule .body')
    # 滚动到日程
    driver.execute_script("arguments[0].scrollIntoView();", schedule_body)
    time.sleep(1)
    # 预约
    driver.execute_script("arguments[0].click();", schedule_body.find_element_by_css_selector('.radio-inline input[value=reserve]'))
    time.sleep(1)
    # 时间
    # 天
    schedule_body.find_element_by_css_selector('.btn_daterangepicker').send_keys(push.date)
    selectors = schedule_body.find_elements_by_css_selector('.schedule_selector .select_droppdown')
    # 时
    selectors[0].click()
    hour_list = selectors[0].find_element_by_css_selector('ul')
    hour_list.find_element_by_partial_link_text(push.hour).click()
    # 分
    selectors[1].click()
    minute_list = selectors[1].find_element_by_css_selector('ul')
    minute_list.find_element_by_partial_link_text(push.minute).click()

    # 信息
    message_body = driver.find_element_by_css_selector('.well.message .body')
    # 滚动
    driver.execute_script("arguments[0].scrollIntoView();", message_body)
    time.sleep(2)
    # 信息
    # title
    message_title_ele = message_body.find_element_by_css_selector(':nth-child(3) input[name=message_title]')
    sendKeysWithEmojis(driver, message_title_ele, push.messageTitle)
    message_content_ele = message_body.find_element_by_css_selector(':nth-child(3) textarea[name=message]')
    sendKeysWithEmojis(driver, message_content_ele, push.messageContent)
    # 发送状态
    message_body.find_element_by_css_selector('.radio .onShowAlways').click()

    # 排程
    driver.find_element_by_css_selector('#page > div.page_content.container-fluid.push_index > div > div.form_btn > button.btn.btn_primary').click()
    # condition = expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#pushTable > table > tbody > tr:nth-child(1) > td:nth-child(1)'))
    # WebDriverWait(driver=driver, timeout=10, poll_frequency=0.5).until(condition)



def sendKeysWithEmojis(driver: webdriver.Chrome, element: webelement.WebElement, text: str):
    script = "var elm = arguments[0]," \
             "txt = arguments[1];elm.value += txt;" \
             "elm.dispatchEvent(new Event('keydown', {bubbles: true}));" \
             "elm.dispatchEvent(new Event('keypress', {bubbles: true}));" \
             "elm.dispatchEvent(new Event('input', {bubbles: true}));" \
             "elm.dispatchEvent(new Event('keyup', {bubbles: true}));"
    driver.execute_script(script, element, text)


if __name__ == '__main__':
    startChrome()
    print('完成！')
    time.sleep(100)

