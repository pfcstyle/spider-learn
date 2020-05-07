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


headers = {
    'content-type': 'application/json',
    'Accept': 'text/csv'
}


base_url = 'https://api.adjust.com/kpis/v1'


def saveData(result: dict):
    final_excel_data = {}
    for key in result.keys():
        res = result.get(key)
        data = res.split('\n')
        titles = data[0].split(',')
        data = [[x for x in y.split(',')] for y in data[1:]]
        f = open('{}.csv'.format(key), "w+", newline='')
        writer = csv.writer(f)
        writer.writerows([titles])
        writer.writerows(data)
        f.close()
        data = pd.DataFrame(pd.read_csv('{}.csv'.format(key)))
        final_excel_data[key] = getExcelData(key, data)
    writeExcel(final_excel_data)


def getExcelData(key, data: pd.DataFrame):
    if key == 'dau_android' or key == 'dau_ios':
        return data.loc[:, ['date', 'installs', 'daus']]


def writeExcel(data: dict):
    wb: xlwt.Workbook = xlwt.Workbook()
    # 新建sheet
    ws: xlwt.Worksheet = wb.add_sheet('data', cell_overwrite_ok=True)
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
    for key in data.keys():
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
    timeout = aiohttp.ClientTimeout(total=10)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params, headers=headers) as response:
            res = await response.text()
            result[key] = res


def run():
    url = "{}/{}".format(base_url, app_token)
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    last_week = today - datetime.timedelta(days=7)
    params = {}
    params_android = {
        "attribution_source": "dynamic",
        "attribution_type": "all",
        "end_date": tomorrow.strftime('%Y-%m-%d'),
        "event_kpis": "all_events|revenue",
        "grouping": "dates",
        "kpis": "installs, daus",
        "os_names": "android",
        "reattributed": "installs, daus",
        "start_date": last_week.strftime('%Y-%m-%d'),
        "utc_offset": "+00:00"
    }
    params_ios = params_android.copy()
    params_ios['os_names'] = 'ios'
    params['dau_android'] = params_android
    params['dau_ios'] = params_ios
    for key in params.keys():
        param = params.get(key)
        task = asyncio.ensure_future(getData(url, param, key))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./secret.ini')
    token = config.get('account', 'token')
    app_token = config.get('account', 'app_token')
    headers['Authorization'] = 'Token token={}'.format(token)
    tasks = []
    result = {}
    loop = asyncio.get_event_loop()
    run()





