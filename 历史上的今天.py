import re
import requests
from lxml import etree
import pymysql

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123123', db='历史上的今天',
                         charset='utf8')
    cursor = db.cursor()
    #cursor.execute("SET @@global.sql_mode= ''")
    #db.commit()
    for month in range(2,13,1):
        mmonth = str(month)
        url = 'https://baike.baidu.com/cms/home/eventsOnHistory/%02d.json'%month
        response = requests.get(url=url, headers=headers,timeout=114514)
        dic_response = response.json()['%02d'%month]
        tree = etree.HTML(url)
        # print(dic_response)
        for day in dic_response:
            list_response = dic_response[day]
            print(day + ':')
            # list_response是每个日期的完整信息 各个重大年份存在列表里面
            for dic_event in list_response:
                year = dic_event['year'].strip()
                event = dic_event['type']
                title = dic_event['title']
                tree = etree.HTML(title)
                title = tree.xpath('.//text()')
                title = ''.join(title)
                title = title.replace('\n','')
                link = dic_event['link']
                link_response = requests.get(url=link, headers=headers,timeout=114514)
                link_response.encoding = link_response.apparent_encoding
                link_response = link_response.text
                #print(link_response)
                link_tree = etree.HTML(link_response)
                content = link_tree.xpath('.//meta[@name="description"]/@content')
                if len(content)==0:
                    content.append("百度百科词条丢了！！！！")
                content = content[0]
                sql = """
                            INSERT INTO history_event_of_days (date,event,year,title,url,info)
                            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');
                      """
                print(event + ' ' + year + ' ' + title + ' ' + link)
                print(content)
                try:
                    cursor.execute(sql.format(day,event,year,title,link,content))
                    db.commit()
                except:
                    db.rollback()
                    print("未知错误！！！危")
    # for div in div_list:
    #     para = div.xpath('.///text()')
    # print(link_response)

    # print(content[0])
