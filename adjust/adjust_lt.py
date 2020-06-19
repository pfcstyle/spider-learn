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

import os
import shutil


headers = {
    'content-type': 'application/json',
    'Accept': 'text/csv'
}


base_url = 'https://api.adjust.com/kpis/v1'
csv_dir = './csv_lt'
output_file = 'output_lt{}.xlsx'


def saveData(result: dict):
    if os.path.exists(csv_dir):
        shutil.rmtree(csv_dir)
    os.mkdir(csv_dir)

    final_excel_data = {}
    for key in result.keys():
        res = result.get(key)
        data = res.split('\n')
        titles = data[0].split(',')
        data = [[x for x in y.split(',')] for y in data[1:]]
        f = open('{}/{}.csv'.format(csv_dir, key), "w+", newline='', encoding='utf-8')
        writer = csv.writer(f)
        writer.writerows([titles])
        writer.writerows(data)
        f.close()
        data = pd.DataFrame(pd.read_csv('{}/{}.csv'.format(csv_dir, key)))
        final_excel_data[key] = getExcelData(key, data)
        print('正在处理{}'.format(key))
    writeExcelByPandas(final_excel_data)


def testSave():
    final_excel_data = {}
    for key in params.keys():
        data = pd.DataFrame(pd.read_csv('{}/{}.csv'.format(csv_dir, key)))
        final_excel_data[key] = getExcelData(key, data)
    writeExcelByPandas(final_excel_data)


def mergeData(data: list):
    merged_data = data[0]
    i = 0
    for ele in data:
        if i == 0:
            i += 1
            continue
        merged_data = pd.merge(merged_data, ele, how="outer", on='tracker_name')

    return merged_data



def secondToMinuteS(frame):
    m, s = divmod(frame['time_spent_per_user'], 60)
    m = 0 if np.isnan(m) else m
    s = 0 if np.isnan(s) else s
    return '{}m {}s'.format(int(m), int(s))


def getExcelData(key: str, data: pd.DataFrame):
    data: pd.DataFrame = data.loc[:, ['date', 'period', 'retention_rate']]
    data: pd.DataFrame = data.set_index(['date', 'period']).unstack()
    data.dropna(how='all', inplace=True)
    data.dropna(how='all', inplace=True, axis=1)
    # data = data.apply(lambda row: None if row.isnull().sum() >= len(row) else row, axis=1)
    all_excel_data = data.copy(deep=True)

    column_num = data.shape[1]
    for period in [30, 60, 90, 100, 120]:
        if period > column_num - 1:
            continue
        temp_data: pd.DataFrame = data.iloc[:, 0: period + 1]
        # all_excel_data["{}d".format(period)] = temp_data.apply(lambda row: None if len(row.dropna()) < period + 1 and row[len(period)] else row.sum(), axis=1)
        all_excel_data["{}d".format(period)] = temp_data.apply(lambda row: row.sum(), axis=1)
    # all_excel_data = all_excel_data.drop(labels=[1, 2])
    return all_excel_data


def writeExcelByPandas(data: dict):
    start_time = config.get('lt', 'start_time')
    start_time = datetime.datetime.strptime(start_time, "%Y/%m/%d")
    start_date = start_time.strftime('%Y-%m-%d')
    writer = pd.ExcelWriter(output_file.format(start_date))
    for key in data.keys():
        df: pd.DataFrame = data.get(key)
        df.to_excel(writer, key)
    writer.save()


async def getData(url, params, key):
    timeout = aiohttp.ClientTimeout(total=300)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params, headers=headers) as response:
            res = await response.text()
            result[key] = res


def setParamsAndUrls():

    start_time = config.get('lt', 'start_time')
    try:
        start_time = datetime.datetime.strptime(start_time, "%Y/%m/%d")
    except Exception as err:
        print('错误：start_time or end_time设置错误')
        print(err)
        exit(-1)
    end_time = start_time + datetime.timedelta(days=120)
    start_date = start_time.strftime('%Y-%m-%d')
    end_date = end_time.strftime('%Y-%m-%d')
    params_android = {
        "attribution_source": "dynamic",
        "attribution_type": "click",
        "end_date": end_date,
        "start_date": start_date,
        "cohort_period_filter": "0 - 120",
        "event_kpis": "all_events|revenue",
        "grouping": "day,periods",
        "kpis": "retention_rate",
        "period": "day",
        "reattributed": "all",
        "utc_offset": "+00:00",
        "os_names": "android"
    }

    countries = ['jp', 'us', 'kr', 'cn', 'hk,mo,tw']
    # countries = ['jp']
    for country in countries:
        params_android = params_android.copy()
        params_android['os_names'] = 'android'
        params_android['countries'] = country

        params_ios = params_android.copy()
        params_ios['os_names'] = 'ios'

        country_key_android = 'cohorts_android_{}'.format(country)
        country_key_ios = 'cohorts_ios_{}'.format(country)

        params[country_key_android] = params_android

        params[country_key_ios] = params_ios


def run():
    setParamsAndUrls()
    # testSave()
    print("正在请求数据。。。")
    for key in params.keys():
        param = params.get(key)
        task = asyncio.ensure_future(getData(url_cohorts, param, key))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)
    print("处理完成")


if __name__ == '__main__':
    secretConfig = configparser.ConfigParser()
    secretConfig.read('./secret.ini')
    config = configparser.ConfigParser()
    config.read('./config.ini')
    token = secretConfig.get('account', 'token')
    app_token = secretConfig.get('account', 'app_token')
    tracker_token = secretConfig.get('account', 'tracker_token')
    headers['Authorization'] = 'Token token={}'.format(token)
    url_cohorts = "{}/{}/cohorts".format(base_url, app_token)
    params = {}
    tasks = []
    result = {}
    loop = asyncio.get_event_loop()
    run()





