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


def saveData(result):
    i=0
    for res in result:
        data = res.split('\n')
        keys = data[0].split(',')
        data = [[x for x in y.split(',')] for y in data[1:]]
        with open('{}.csv'.format(i), "r+", newline='') as f:
            writer = csv.writer(f)
            writer.writerows([keys])
            writer.writerows(data)
            data = csv.DictReader(f)
            column = [row['installs'] for row in data]
            f.close()
        i += 1


def writeExcel(data):
    wb = xlwt.Workbook()
    # 新建sheet
    ws = wb.add_sheet('0', cell_overwrite_ok=True)
    # 对齐
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    # 定义格式
    style = xlwt.XFStyle()
    style.alignment = alignment
    # 合并单元格(开始行，结束行， 开始列， 结束列， 内容， 格式）
    ws.write_merge(0, 0, 0, 5, 'neirong', style)
    # 写入数据（行, 列, 内容)
    for i in range(2, 7):
        for k in range(5):
            ws.write(i, k, i + k)
        ws.write(i, 5, xlwt.Formula('SUM(A' + str(i + 1) + ':E' + str(i + 1) + ')'))
    # 插入图片，bmp格式，行数，列数，相对原来位置向下偏移的像素，相对原来位置向右偏移的像素，x缩放比例，y缩放比例
    ws.insert_bitmap('', 9, 1, 2, 2, scale_x=0.3, scale_y=0.3)
    wb.save('result.xls')

async def getData(url, params):
    timeout = aiohttp.ClientTimeout(total=10)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params, headers=headers) as response:
            return await response.text()


def run():
    url = "{}/{}".format(base_url, app_token)
    for i in range(1):
        task = asyncio.ensure_future(getData(url, {}))
        tasks.append(task)
    result = loop.run_until_complete(asyncio.gather(*tasks))
    saveData(result)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./secret.ini')
    token = config.get('account', 'token')
    app_token = config.get('account', 'app_token')
    headers['Authorization'] = 'Token token={}'.format(token)
    tasks=[]
    loop = asyncio.get_event_loop()
    run()





