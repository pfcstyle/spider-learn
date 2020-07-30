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
csv_dir = './csv_event'
output_dir = './output'
output_file = '{}/output_event.xlsx'.format(output_dir)


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


def getExcelData(key: str, data: pd.DataFrame):
    all_excel_data = data.loc[(data['period'] == 0), ['date', 'converted_users', 'events_per_user']]
    all_excel_data.rename(columns={'date': 'date_{}'.format(key)}, inplace=True)
    # all_excel_data: pd.DataFrame = all_excel_data.set_index(['date']).unstack()
    return all_excel_data


def writeExcelByPandas(data: dict):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    writer = pd.ExcelWriter(output_file)
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
    start_time = config.get('event', 'start_time')
    end_time = config.get('event', 'end_time')
    countries = config.get('event', 'countries').split(',')
    os_names = config.get('event', 'os_names')
    events = pd.read_excel('./data/event-token-summary.xlsx')

    if os_names != 'ios' and os_names != 'android' \
            and os_names != 'ios,android' \
            and os_names != '' and os_names != 'android,ios':
        print('错误：os_names设置错误')
        exit(-1)
    else:
        os_names = os_names.split(',')

    if events.shape[0] != 2 or events.shape[1] < 2 \
            or (events.get('token') is None) or (events.get('event name') is None) \
            or len(events['token']) != len(events['event name']):
        print('错误：events设置错误')
        exit(-1)

    if len(countries) < 1:
        print('错误：没有设置国家')
        exit(-1)

    try:
        end_time = datetime.datetime.strptime(end_time, "%Y/%m/%d")
        start_time = datetime.datetime.strptime(start_time, "%Y/%m/%d")
    except Exception as err:
        print('错误：start_time or end_time设置错误')
        print(err)
        exit(-1)

    start_date = start_time.strftime('%Y-%m-%d')
    end_date = end_time.strftime('%Y-%m-%d')
    params_event = {
        "attribution_source": "dynamic",
        "attribution_type": "click",
        "end_date": end_date,
        "start_date": start_date,
        "os_names": "android",
        "events": "8w38y5",
        "grouping": "day,periods",
        "kpis": "converted_users,events_per_user",
        "period": "day",
        "reattributed": "all",
        "utc_offset": "+00:00"
    }

    for i in range(0, len(events['token'])):
        event_token = events['token'][i]
        event_name = events['event name'][i]
        for country in countries:
            params_event['countries'] = country
            params_event['events'] = event_token
            if len(os_names) < 1:
                params_key = '{}_{}'.format(country, event_name)
                del params_event['os_names']
                params[params_key] = params_event
                params_event = params_event.copy()
            else:
                for os in os_names:
                    params_key = '{}_{}_{}'.format(os, country, event_name)
                    params_event['os_names'] = os
                    params[params_key] = params_event
                    params_event = params_event.copy()



def run():
    setParamsAndUrls()
    # testSave()
    for key in params.keys():
        param = params.get(key)
        task = asyncio.ensure_future(getData(url_cohorts, param, key))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config.ini')
    secretConfig = configparser.ConfigParser()
    secretConfig.read('./secret.ini')
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





