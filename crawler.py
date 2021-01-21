# @Author  : 习健丰 (jeffxi@fuzhi.ai)
# @Desc    : 爬取《天气后报》网站中中国各城市的历史天气(2018~至今）

import time
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "http://www.tianqihoubao.com/lishi/beijing.html"
START_TIME = "2018"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/72.0.3626.121 Safari/537.36'
}


# class Crawler:
#     _base_url = "http://www.tianqihoubao.com/lishi/"
def month_scraper(url):
    """
    读取需要的所有月份的url，返回一个地区历史每天的天气
    :param url: 查询网址
    :return: dataframe
    """
    html = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(html.content, "lxml")

    # 数据清洗
    lst = soup.find_all('div', attrs={'id': 'content', 'class': 'wdetail'})[0]
    years = lst.find_all('h2')
    seasons = lst.find_all('div', class_="box pcity")
    # 找到指定年份，没有则返回
    count = 0
    for year in years:
        if START_TIME in str(year):
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
            print(url)
    print(urls)
    # 获取链接里面的内容
    _url = "http://www.tianqihoubao.com/"
    total_frame = pd.DataFrame()#合并还有问题
    for url in urls:
        frame = date_scraper(_url + url)
        total_frame = pd.concat(total_frame, frame)
    print(total_frame)


def date_scraper(url):
    """
    读取当月内所有日期的天气
    :param url: 查询网址
    :return: dataframe
    """
    # 请求数据
    try:
        html = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(html.content, "lxml")
    except:
        print("请求失败")
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
    frame = pd.DataFrame(month_data, columns=titles)
    return frame


def remove_tag(lst):
    for i in range(len(lst)):
        lst[i] = lst[i].get_text()
    return lst


if __name__ == '__main__':
    # data = date_scraper(BASE_URL)
    month_scraper(BASE_URL)
