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
csv_dir = './csv_once'
output_dir = './output'
output_file = 'output/output_once.xlsx'


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
        getExcelData(key, data, final_excel_data)
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


def getExcelData(key: str, data: pd.DataFrame, final_excel_data: dict):
    all_excel_data = data.loc[(data['period'] == 0), ['date', 'converted_users']]
    # all_excel_data.rename(columns={'converted_users': key}, inplace=True)
    # all_excel_data: pd.DataFrame = all_excel_data.set_index(['date', 'period']).unstack()
    country_key = 'jp'
    if key.find('jp') > -1:
        country_key = 'jp'
    elif key.find('us') > -1:
        country_key = 'us'
    else:
        country_key = 'kr'
    if country_key not in final_excel_data.keys():
        final_excel_data[country_key] = all_excel_data
        final_excel_data[country_key].rename(columns={'converted_users': key}, inplace=True)
    else:
        final_excel_data[country_key][key] = all_excel_data['converted_users']
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

    params_once = {
        "attribution_source": "dynamic",
        "attribution_type": "click",
        "end_date": "2020-06-22",
        "start_date": "2020-06-18",
        "cohort_period_filter": "0-4",
        "events": "8w38y5",
        "event_kpis": "all_events|revenue",
        "grouping": "day,periods",
        "kpis": "converted_users,events_per_user",
        "period": "day",
        "reattributed": "all",
        "utc_offset": "+00:00"
    }

    events = pd.read_excel('./data/once-token-summary.xlsx', squeeze = True)

    # events = ["8w38y5"]
    countries = ['jp', 'us', 'kr']
    # countries = ['jp']
    for event in events:
        for country in countries:
            params_once = params_once.copy()
            params_once['countries'] = country
            params_once['events'] = event
            country_event_key = 'cohorts_{}_{}'.format(event, country)

            params[country_event_key] = params_once

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





