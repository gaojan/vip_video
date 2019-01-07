#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Author: Jan Gao
# Date: 2019/1/4
# Description: 腾讯视频、优酷、爱奇艺、pptv、乐视vip视频下载
# Site: http://www.xrtpay.com/
# Copyright (c) ShenZhen XinRuiTai Payment Service Co.,Ltd. All rights reserved
"""
import os
import re
import shutil
import ssl
import traceback

import requests
from lxml import etree
from urllib.request import urlretrieve
from multiprocessing import Pool
ssl._create_default_https_context = ssl._create_unverified_context


class DownloadVideo(object):
    def __init__(self, url):
        self.get_url = 'http://jx.618g.com/?url=' + url
        self.header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                     'like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        self.url = ''
        self.thread_num = 32
        self.p = 0
        self.title = ''
        self.ts_list = []

    def get_page(self):
        """
        获取页面
        :return:
        """
        try:
            res = requests.get(self.get_url, headers=self.header)
            if 200 == res.status_code:
                print('获取目标网页成功， 准备下载ts...')
                self.header['referer'] = self.get_url
            return res.text
        except Exception:
            print(traceback.print_exc())
            print('获取目标网页失败，请检查错误重试')

    def parse_page(self, html):
        """
        解析页面
        :param html:
        :return:
        """
        el = etree.HTML(html)
        self.title = el.xpath('//title/text()')[0].replace(' ', '')
        print(self.title)
        m3u8_url = el.xpath('//div[@id="a1"]/iframe/@src')[0].split('url=')[1]
        print(m3u8_url)  # https://tudou.com-l-tudou.com/20181226/15303_6239bcf5/index.m3u8
        m3u8_text = self.get_m3u8_1(m3u8_url).strip()   # 1000k/hls/index.m3u8
        self.url = m3u8_url[:-10] + m3u8_text    # https://tudou.com-l-tudou.com/20181226/15303_6239bcf5/1000k/hls/index.m3u8
        self.get_m3u8_2(self.url)

    def get_m3u8_1(self, m3_url):
        """
        获取m3u8
        :param m3_url:
        :return:
        """
        try:
            resp = requests.get(m3_url, headers=self.header)
            print('获取ts文件成功，准备提取信息...')
            print(resp.text[-20:])
            return resp.text[-20:]  # 1000k/hls/index.m3u8
        except Exception as e:
            print('缓存文件请求错误1，请检查错误')
            print(e)

    def get_m3u8_2(self, url):
        """
        获取ts
        :param url:
        :return:
        """
        response = requests.get(url, headers=self.header)
        print(self.parse_ts(response.text))
        return self.parse_ts(response.text)

    def parse_ts(self, text):
        """
        解析匹配ts
        :param text:
        :return:
        """
        pattern = re.compile('.+ts')
        self.ts_list = re.findall(pattern, text)
        print('提取信息完成，准备下载...')
        self.pool()

    def save_ts(self, ts):
        """
        保存ts文件
        :return:
        """
        try:
            ts_url = self.url[:-10] + ts
            self.p += 1
            a = urlretrieve(ts_url, self.title + '/{}'.format(ts))
            print(a[0])
        except Exception as e:
            print('下载ts文件错误，请检查重试')
            print(e)

    def pool(self):
        print('需要下载的文件有：%s' % len(self.ts_list))
        if self.title not in os.listdir(os.path.dirname(__file__)):
            os.mkdir(self.title)
        pool = Pool(16)
        pool.map(self.save_ts, [ts for ts in self.ts_list])
        pool.close()
        pool.join()
        print('下载完成...')

        self.ts_to_mp4()

    def ts_to_mp4(self):
        print('ts文件正在转录mp4...')
        # win 系统
        # cmd_str = 'copy /b C:\Users\Desktop\古董局中局第11集\* C:\Users\Desktop\古董局中局第11集\new.mp4'
        # mac 或 linux
        cmd_str = 'cat' + os.path.dirname(__file__) + self.title + '/*.ts > hello.mp4'
        os.system(cmd_str)

        mv_name = self.title+'.mp4'
        if os.path.isfile(mv_name):
            print('ts转换完成，祝你观影愉快！')
            shutil.rmtree(self.title)


if __name__ == '__main__':
    v_url = 'https://v.qq.com/x/cover/9z88hz9qwugb8p1/s0029vmkpeh.html'
    # v_url = 'https://v.qq.com/x/cover/yqlvu10akee76oy.html'
    down = DownloadVideo(v_url)
    h = down.get_page()
    down.parse_page(h)


