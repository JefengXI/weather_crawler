# @Desc    : 爬取《天气后报》网站中中国各城市的历史天气(2018~至今），按照省存为.xlsx文件,一个sheet为一个城市

import random
from time import sleep
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import config as cfg


def province_scraper(url):
    """
    以省划分csv文件，依次访问每个省，存为csv文件
    :param url:
    :return: None
    """
    soup = require_data(url)

    # 数据清洗
    lst = soup.find_all('div', class_="citychk")
    lst = lst[0].find_all('dl')
    for i in lst:
        # 以省为单位新建文件
        province = i.find('b').get_text()
        writer = pd.ExcelWriter('data/' + province + '.xlsx')
        # 找到所有城市标签
        cities_tag = i.find_all('a')
        # 首行为省名，去掉
        cities_tag.pop(0)
        for j in cities_tag:
            city_name = j.get_text()
            city_url = j['href']
            print(city_name, city_url)
            frame = month_scraper(cfg.ROOT_URl + city_url)
            frame.to_excel(writer, sheet_name=city_name, index=None)
        writer.close()


def month_scraper(url):
    """
    读取某城市需要的所有月份的url，返回一个地区历史每天的天气
    :param url: 查询网址
    :return: month_frame: dataframe
    """
    soup = require_data(url)

    # 数据清洗
    lst = soup.find_all('div', attrs={'id': 'content', 'class': 'wdetail'})[0]
    years = lst.find_all('h2')
    seasons = lst.find_all('div', class_="box pcity")
    # 找到指定年份，没有则返回
    count = 0
    for year in years:
        if cfg.START_TIME in str(year):
            break
        count += 1
    if not years:
        print("无此年份")
        return 0

    # 获取各月份网址链接
    seasons = seasons[count:]
    urls = []
    extra_path = '/lishi/'  # 有些href里面的网址会缺损这一个路径，很迷
    for season in seasons:
        months = season.find_all('a')
        for month in months:
            url = month['href']
            if extra_path not in url:
                url = extra_path + url
            urls.append(url)
    # 获取链接里面的内容
    month_list = []
    for url in urls:
        frame = date_scraper(cfg.ROOT_URl + url)
        month_list.append(frame)
    month_frame = pd.concat([f for f in month_list], axis=0, ignore_index=True)
    return month_frame


def date_scraper(url):
    """
    读取当月内所有日期的天气,返回一个月内的所有历史天气
    :param url: str
    :return: date_frame: dataframe
    """
    # 请求数据
    soup = require_data(url)

    # 数据清洗
    lst = soup.find_all('tr')
    titles = remove_tag(lst.pop(0).find_all('b'))
    month_data = []
    # 将标签整理成列表并规范格式
    for i in range(len(lst)):
        item = [''] * 4
        item[0] = ''.join(lst[i].find_all('a')[0].get_text().split())
        item[1] = ''.join(lst[i].find_all('td')[1].get_text().split())
        item[2] = ''.join(lst[i].find_all('td')[2].get_text().split())
        item[3] = ''.join(lst[i].find_all('td')[3].get_text().split())
        month_data.append(item)
    date_frame = pd.DataFrame(month_data, columns=titles)
    return date_frame


def require_data(url):
    # 请求数据
    max_retry = 0
    while max_retry < 5:
        try:
            html = requests.get(url=url, headers=cfg.HEADER, timeout=5)
            soup = BeautifulSoup(html.content, "lxml")
            print("网址:{0}请求成功!".format(url))
            return soup
        except:
            max_retry += 1
            print("网址:{0}请求失败，重试第{1}次".format(url, max_retry))
            sleep(random.uniform(0.5, 3))
    print("服务器拒绝响应")
    exit(1)


def remove_tag(lst):
    """
    去除列表中标签值的标签
    :param lst:[tag]
    :return: list:[str]
    """
    for i in range(len(lst)):
        lst[i] = lst[i].get_text()
    return lst


if __name__ == '__main__':
    province_scraper(cfg.BASE_URL)
