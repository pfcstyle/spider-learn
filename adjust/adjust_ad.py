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
csv_dir = './csv_ad'
output_file = 'output_ad{}.xlsx'


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
        f = open('{}/{}.csv'.format(csv_dir, key), "w+", newline='')
        writer = csv.writer(f)
        writer.writerows([titles])
        writer.writerows(data)
        f.close()
        data = pd.DataFrame(pd.read_csv('{}/{}.csv'.format(csv_dir, key)))
        final_excel_data[key] = getExcelData(key, data)
        # final_excel_data[key] = data
    writeExcelByPandas(final_excel_data)


def secondToMinuteS(frame):
    m, s = divmod(frame['time_spent_per_user'], 60)
    m = 0 if np.isnan(m) else m
    s = 0 if np.isnan(s) else s
    return '{}m {}s'.format(int(m), int(s))


def getExcelData(key: str, data: pd.DataFrame):
    return data.loc[:,
           ['tracker_name', 'installs', 'ctr', 'click_conversion_rate', 'revenue', 'cost', 'return_on_investment',
            'rcr']]


def writeExcelByPandas(data: dict):
    start_time = config.get('ad', 'start_time')
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

    start_time = config.get('ad', 'start_time')
    end_time = config.get('ad', 'end_time')
    period = config.getint('ad', 'period')
    try:
        end_time = datetime.datetime.strptime(end_time, "%Y/%m/%d")
        start_time = datetime.datetime.strptime(start_time, "%Y/%m/%d")
    except Exception as err:
        print('错误：start_time or end_time设置错误')
        print(err)
        exit(-1)

    start_date = start_time.strftime('%Y-%m-%d')
    params_ad = {
        "attribution_source": "dynamic",
        "attribution_type": "click",
        "end_date": "",
        "start_date": start_date,
        "event_kpis": "all_events|revenue",
        "grouping": "trackers",
        "kpis": "installs, ctr, click_conversion_rate, revenue, cost, return_on_investment, rcr, paid_impressions, "
                "ecpm, paid_clicks, ecpc, paid_installs, ecpi, cohort_revenue, cohort_gross_profit",
        "partner_ids": 34,
        "reattributed": "all",
        "utc_offset": "+00:00"
    }

    delta_days = (end_time - start_time).days + 1
    if delta_days < period:
        print('错误：周期设置大于起始和终止时间间隔')
        exit(-1)
    num = int(delta_days / period) + 1
    for i in range(num):
        iend_time = start_time + datetime.timedelta(days=period * (i + 1) - 1)
        if iend_time > end_time:
            iend_time = end_time
        end_date = iend_time.strftime('%Y-%m-%d')
        params_ad["end_date"] = end_date
        params[end_date] = params_ad.copy()


def run():
    setParamsAndUrls()
    for key in params.keys():
        param = params.get(key)
        task = asyncio.ensure_future(getData(url_ad, param, key))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)


if __name__ == '__main__':
    secretConfig = configparser.ConfigParser()
    secretConfig.read('./secret.ini')
    config = configparser.ConfigParser()
    config.read('./config.ini')
    token = secretConfig.get('account', 'token')
    app_token = secretConfig.get('account', 'app_token')
    tracker_token = secretConfig.get('account', 'tracker_token')
    headers['Authorization'] = 'Token token={}'.format(token)
    url_ad = "{}/{}/trackers/{}".format(base_url, app_token, tracker_token)
    params = {}
    tasks = []
    result = {}
    loop = asyncio.get_event_loop()
    run()





