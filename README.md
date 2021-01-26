# weather_crawler
## 爬取《天气后报》网站中中国各城市的历史天气(某年一月一日~至今）
### config.py
START_TIME = "2018"  // 开始年份，可调整
ROOT_URl = "http://www.tianqihoubao.com"  // 网站根目录
BASE_URL = "http://www.tianqihoubao.com/lishi"  // 爬虫目标目录
### crawler.py
算法：
循环请求某城市某月所有天气的网址，在网址中获取此月所有日期的天气。
输出：
文件：省名.xlsx; sheet：城市名; 表格：日期/天气状况/气温/风力风向
