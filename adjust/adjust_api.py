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


headers = {
    'content-type': 'application/json',
    'Accept': 'text/csv'
}


base_url = 'https://api.adjust.com/kpis/v1'


def saveData(result: dict):
    for key in result.keys():
        res = result.get(key)
        data = res.split('\n')
        titles = data[0].split(',')
        data = [[x for x in y.split(',')] for y in data[1:]]
        with open('{}.csv'.format(key), "w+", newline='') as f:
            writer = csv.writer(f)
            writer.writerows([titles])
            writer.writerows(data)
            data = csv.DictReader(f)
            writeExcel(getExcelData(key, data), key)
            f.close()


def getExcelData(key, data: csv.DictReader):
    if key == 'dau_android' or key == 'dau_ios':
        result
    return []

def writeExcel(data: list, key: str):
    wb: xlwt.Workbook = xlwt.Workbook()
    # 新建sheet
    ws: xlwt.Worksheet = wb.add_sheet(key, cell_overwrite_ok=True)
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
    for i in range(2, 7):
        for k in range(5):
            ws.write(i, k, i + k, style)
        # ws.write(i, 5, xlwt.Formula('SUM(A' + str(i + 1) + ':E' + str(i + 1) + ')'))
    # 插入图片，bmp格式，行数，列数，相对原来位置向下偏移的像素，相对原来位置向右偏移的像素，x缩放比例，y缩放比例
    # ws.insert_bitmap('', 9, 1, 2, 2, scale_x=0.3, scale_y=0.3)
    wb.save('result.xlsx')

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





