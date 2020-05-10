# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     adjust_api
   Description :
   Author :       developer
   date：          2020/5/6
-------------------------------------------------
   Change Activity:
                   2020/5/6:
-------------------------------------------------
"""
__author__ = 'developer'

import configparser
import datetime

from aiohttp import ClientSession
import asyncio
import aiohttp
import csv
import xlwt
import pandas as pd
import numpy as np
import time

import  os


headers = {
    'content-type': 'application/json',
    'Accept': 'text/csv'
}


base_url = 'https://api.adjust.com/kpis/v1'


def saveData(result: dict):
    if not os.path.exists('./csv'):
        os.mkdir('./csv')
    final_excel_data = {}
    for key in result.keys():
        res = result.get(key)
        data = res.split('\n')
        titles = data[0].split(',')
        data = [[x for x in y.split(',')] for y in data[1:]]
        f = open('csv/{}.csv'.format(key), "w+", newline='')
        writer = csv.writer(f)
        writer.writerows([titles])
        writer.writerows(data)
        f.close()
        data = pd.DataFrame(pd.read_csv('csv/{}.csv'.format(key)))
        final_excel_data[key] = getExcelData(key, data)
    writeExcelByPandas(final_excel_data)


def secondToMinuteS(frame):
    m, s = divmod(frame['time_spent_per_user'], 60)
    m = 0 if np.isnan(m) else m
    s = 0 if np.isnan(s) else s
    return '{}m {}s'.format(int(m), int(s))


def getExcelData(key: str, data: pd.DataFrame):
    if key.find('dau') > -1:
        return data.loc[:, ['date', 'installs', 'daus']]
    if key.find('cohorts') > -1: # retention_rate  sessions_per_user time_spent_per_user
        # 筛选行
        data: pd.DataFrame = data.loc[((data['period'] == 0) | (data['period'] == 1) | (data['period'] == 3) | (data['period'] == 7) | (data['period'] == 14) | (data['period'] == 30)), ['date', 'period', 'retention_rate', 'sessions_per_user', 'time_spent_per_user']]
        data['retention_rate'] = data.apply(lambda row: None if row['period'] == 0 else row['retention_rate'], axis=1)
        data['sessions_per_user'] = data.apply(lambda row: None if row['period'] > 0 else row['sessions_per_user'], axis=1)
        data['time_spent_per_user'] = data.apply(lambda row: None if row['period'] > 0 else secondToMinuteS(row), axis=1)
        data: pd.DataFrame = data.set_index(['date', 'period']).unstack()
        # data.columns.names = ['items', 'period']
        # data: pd.DataFrame = data.swaplevel('items', 'period', axis=1)
        # data: pd.DataFrame = data.groupby(data['period']).apply(lambda df: df).unstack(0)
        return data


def writeExcelByPandas(data: dict):
    writer = pd.ExcelWriter('output.xlsx')
    for key in data.keys():
        df: pd.DataFrame = data.get(key)
        df.to_excel(writer, key)
    writer.save()


def writeExcel(data: dict):
    wb: xlwt.Workbook = xlwt.Workbook()
    # 新建sheet

    # 对齐
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT
    alignment.vert = xlwt.Alignment.VERT_CENTER
    # 定义格式
    style = xlwt.XFStyle()
    style.alignment = alignment
    # 合并单元格(开始行，结束行， 开始列， 结束列， 内容， 格式）
    # ws.write_merge(0, 0, 0, 5, 'neirong', style)
    # 写入数据（行, 列, 内容)
    total_rows = 0
    ws: xlwt.Worksheet = wb.add_sheet('dau', cell_overwrite_ok=True)
    has_create_ca = False
    has_create_ci = False
    for key in data.keys():
        if key.find('cohorts_android') > -1 and not has_create_ca:
            total_rows = 0
            ws: xlwt.Worksheet = wb.add_sheet('cohorts_android', cell_overwrite_ok=True)
            has_create_ca = True
        if key.find('cohorts_ios') > -1 and not has_create_ci:
            total_rows = 0
            ws: xlwt.Worksheet = wb.add_sheet('cohorts_ios', cell_overwrite_ok=True)
            has_create_ci = True
        ws.write(total_rows, 0, key, style)
        total_rows += 1
        df: pd.DataFrame = data.get(key)# 二维数据
        col_num = 0
        max_row_num = 0

        for column_name in df.columns:
            row_num = total_rows
            ws.write(row_num, col_num, column_name, style)
            row_num += 1
            for row_name in df.index:
                v = df.at[row_name, column_name]
                if type(v) is np.int64:
                    v = int(v)
                ws.write(row_num, col_num, v, style)
                row_num += 1
            col_num += 1
            max_row_num = max(max_row_num, row_num)
        total_rows += (max_row_num + 1)

        # ws.write(i, 5, xlwt.Formula('SUM(A' + str(i + 1) + ':E' + str(i + 1) + ')'))
    # 插入图片，bmp格式，行数，列数，相对原来位置向下偏移的像素，相对原来位置向右偏移的像素，x缩放比例，y缩放比例
    # ws.insert_bitmap('', 9, 1, 2, 2, scale_x=0.3, scale_y=0.3)
    wb.save('result.xls')


async def getData(url, params, key):
    timeout = aiohttp.ClientTimeout(total=30)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params, headers=headers) as response:
            res = await response.text()
            result[key] = res


def setDauParamsAndUrls():
    url_dau = "{}/{}".format(base_url, app_token)
    urls['dau_android'] = url_dau
    urls['dau_ios'] = url_dau

    end_time = config.get('dau', 'end_time')
    try:
        if end_time == 'today':
            end_time = datetime.datetime.now()
        else:
            end_time = time.strptime(end_time, "%Y/%m/%d")
    except Exception as err:
        print('错误：dau end_time设置错误')
        exit(-1)

    day_num = int(config.get('dau', 'day_num'))
    start_time = end_time - datetime.timedelta(days=day_num)
    today = datetime.datetime.now()
    params_android = {
        "attribution_source": "dynamic",
        "attribution_type": "all",
        "end_date": end_time.strftime('%Y-%m-%d'),
        "event_kpis": "all_events|revenue",
        "grouping": "dates",
        "kpis": "installs, daus",
        "os_names": "android",
        "reattributed": "installs, daus",
        "start_date": start_time.strftime('%Y-%m-%d'),
        "utc_offset": "+00:00"
    }
    # 获取所有国家
    params_ios = params_android.copy()
    params_ios['os_names'] = 'ios'
    params['dau_android'] = params_android
    params['dau_ios'] = params_ios

    # 根据国家获取
    countries = ['jp', 'us', 'kr', 'cn', 'hk,mo,tw']
    for country in countries:
        params_android = params_android.copy()
        country_key_android = 'dau_android_{}'.format(country)
        country_key_ios = 'dau_ios_{}'.format(country)
        urls[country_key_android] = url_dau
        params_android['countries'] = country
        params[country_key_android] = params_android

        urls[country_key_ios] = url_dau
        params_ios = params_android.copy()
        params_ios['os_names'] = 'ios'
        params[country_key_ios] = params_ios


def setCohortsParamsAndUrls():
    url_cohorts = "{}/{}/cohorts".format(base_url, app_token)

    end_time = config.get('cohorts', 'end_time')
    try:
        if end_time == 'today':
            end_time = datetime.datetime.now()
        else:
            end_time = time.strptime(end_time, "%Y/%m/%d")
    except Exception as err:
        print('错误：cohorts end_time设置错误')
        exit(-1)

    day_num = int(config.get('cohorts', 'day_num'))
    start_time = end_time - datetime.timedelta(days=day_num)
    params_android = {
        "attribution_source": "dynamic",
        "attribution_type": "click",
        "cohort_period_filter": "0-32",
        "end_date": end_time.strftime('%Y-%m-%d'),
        "countries": 'jp',
        "event_kpis": "all_events|revenue",
        "grouping": "date,periods",
        "kpis": "retention_rate,sessions_per_user,time_spent_per_user",
        "os_names": "android",
        "period": "day",
        "reattributed": "all",
        "start_date": start_time.strftime('%Y-%m-%d'),
        "utc_offset": "+00:00"
    }
    params_ios = params_android.copy()
    params_ios['os_names'] = 'ios'
    # 按国家获取
    countries = ['jp', 'us', 'kr', 'cn', 'hk,mo,tw']
    # countries = ['jp']
    for country in countries:
        params_android = params_android.copy()
        country_key_android = 'cohorts_android_{}'.format(country)
        country_key_ios = 'cohorts_ios_{}'.format(country)
        urls[country_key_android] = url_cohorts
        params_android['countries'] = country
        params[country_key_android] = params_android

        urls[country_key_ios] = url_cohorts
        params_ios = params_android.copy()
        params_ios['os_names'] = 'ios'
        params[country_key_ios] = params_ios


def run():
    setDauParamsAndUrls()
    setCohortsParamsAndUrls()
    for key in params.keys():
        param = params.get(key)
        task = asyncio.ensure_future(getData(urls.get(key), param, key))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./secret.ini')
    token = config.get('account', 'token')
    app_token = config.get('account', 'app_token')
    headers['Authorization'] = 'Token token={}'.format(token)
    urls={}
    params={}
    tasks = []
    result = {}
    loop = asyncio.get_event_loop()
    run()





