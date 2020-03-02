import time
import requests
from parsel import Selector
import csv
import os
import pymysql

headers = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://weibo.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    'Cookie': 'SINAGLOBAL=5561046828017.373.1536412390357; SCF=Aq6tD6JNaUwCXdiKGLXFffddxFx5ldMG3v6jEPob4uKP73MMRkzXgxMiXDOL9_iMhXvahQI-VCA4CHtRPZFKOlI.; SUHB=0V5lXQibLJoqt7; ALF=1582199144; SUB=_2AkMrJZA6f8NxqwJRmP4Qz2jkbo93zQDEieKdeWHhJRMxHRl-yT9jqlUftRB6AKW-1cJOKFKabZeqn0SsG7uWKTzylFYS; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWPgCrXu39ZRoQ-4wHOpm7Z; UOR=www.google.de,www.weibo.com,www.baidu.com; _s_tentry=-; Apache=3846238035068.0503.1580212596766; ULV=1580212596940:27:8:3:3846238035068.0503.1580212596766:1580135291928',
    'Host': 's.weibo.com'
}
url = 'https://s.weibo.com/top/summary'
response = requests.get(url, headers=headers)
# print(response.text)
html = response.text
selector = Selector(text=html)
all_info = selector.css('#pl_top_realtimehot > table > tbody > tr')
# print(all_info)
current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
data = [
    ('热搜排名', '标题', '热度', '热搜状态'),
    ('当前时间', current_time, '', '', '')
]
# 连接阿里云服务器数据库
connection = pymysql.connect(host='*',  # MySQL所在电脑的 ip
                             port=3306,  # 端口
                             user='*',  # 用户名
                             password='*',  # 密码
                             db='*'  # 数据库名
                             )  # 字符编码

# print(connection)

cursor = connection.cursor()

for info in all_info:

    topic_rank = info.css('tr > td.td-01.ranktop ::text').get()
    if topic_rank == None:
        topic_rank = str(0)

    topic_title = info.css('tr > td.td-02 > a ::text').get()
    topic_hot_degree = info.css('tr > td.td-02 > span ::text').get()
    if topic_hot_degree == None:
        topic_hot_degree = str(0)
    topic_status = info.css('tr > td.td-03 > i ::text').get()
    # topic_link = info.css('tr > td.td-02 > a ::attr(href)').get()
    sql = """INSERT INTO wb_hot_rank(`rank`, `hot_degree`, `status`, `title`) VALUES ("%s","%s","%s","%s");""" % (
        topic_rank, topic_hot_degree, topic_status, topic_title)

    cursor.execute(sql)

    connection.commit()

    # print(topic_rank,topic_title,topic_hot_degree,topic_status)
    each_data = (topic_rank, topic_title, topic_hot_degree, topic_status)
    data.append(each_data)
# print(data)
# timestamp = str(time.time())
# print('正在保存', current_time, '热搜')
file_name = '新浪微博热搜' + '.csv'
with open(file_name, 'a', newline='') as file:
    csv_writer = csv.writer(file)
    for i in data:
        csv_writer.writerow(i)
# print('保存完毕')
connection.close()
