import re
import requests
from lxml import etree
import pymysql

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123123', db='福州大学教务处',
                         charset='utf8')
    cursor = db.cursor()
    cursor.execute("SET @@global.sql_mode= ''")
    cnt = 0
    # 获取首页信息，并爬取总页码
    home_url = 'https://jwch.fzu.edu.cn/jxtz.htm'
    home_response = requests.get(url=home_url, headers=headers)
    home_response.encoding = home_response.apparent_encoding
    home_response = home_response.text
    # 存储首页的信息
    with open('./jwc.htm', 'w', encoding='utf-8') as fp:
        fp.write(home_response)
    # 正则表达式获取页码
    page_num_format = '<span class="p_no"><a href="jxtz/1.htm">(.*?)</a></span>'
    page_num = re.findall(page_num_format, home_response, re.S)
    page_num = int(page_num[0])
    print('总页数为', page_num, '页')
    # 使用xpath来爬取页面信息 首页单独爬取
    tree = etree.HTML(home_response)
    li_list = tree.xpath('//ul[@class="list-gl"]/li')
    for li in li_list:
        time = li.xpath('./span/text()')[0].replace('\r\n', '')
        time = time.replace(' ', '')
        if time == '':
            time = li.xpath('./span/font/text()')[0].replace('\r\n', '')
            time = time.replace(' ', '')
        column = li.xpath('./text()')[1].replace(' ', '')
        column = column.replace('\r\n', '')
        title = li.xpath('./a/text()')[0]
        info_url = 'https://jwch.fzu.edu.cn/' + li.xpath('./a/@href')[0]
        info = time + column + title + ' ' + info_url
        print(info)
        cnt += 1


        # 爬取详情页新闻
        detail = requests.get(url=info_url,headers=headers)
        detail.encoding = detail.apparent_encoding
        detail = detail.text
        tree = etree.HTML(detail)
        pre_news = tree.xpath('.//div[@class="v_news_content"]//p')
        all_content = ''
        for mew in pre_news:
            if len(mew.xpath('./span'))==0:
                detail_list = './span/span'
            else:
                detail_list = './span'
            news = [i.xpath('string(.)') for i in mew.xpath(detail_list)]
            content = ''
            for part in news:
                content += part
            content = content.replace('\r\n','')
            content = content.replace(' ','')
            if len(content):
                all_content += content.strip()
        print(all_content)
        # 爬取详情页附件
        file_li_list = tree.xpath('.//div[@class="xl_main"]/ul/li')
        file_url = []
        file_name = []
        if len(file_li_list):
            for file_li in file_li_list:
                file_url.append('https://jwch.fzu.edu.cn' + file_li.xpath('./a/@href')[0])
                file_name.append(file_li.xpath('./a/text()')[0])
                print('附件名: ' + file_name[-1] + '\n附件地址: ' + file_url[-1])
        # 将标题、栏目、时间存入数据库
        sql = """
                                INSERT INTO FZU ( col, title, time, num, url, all_content, file1, file1_url, file2, file2_url, file3, file3_url, file4, file4_url, file5, file5_url)
                                VALUES ("{0}", "{1}", "{2}", {3}, "{4}", "{5}","{6}","{7}","{8}","{9}","{10}","{11}","{12}","{13}","{14}","{15}");
                         """

        try:
            # 执行sql语句
            if len(file_li_list) == 0:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, '无', '无', '无', '无', '无', '无',
                               '无', '无', '无', '无'))
            if len(file_li_list) == 1:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, file_name[0], file_url[0], '无', '无',
                               '无', '无', '无', '无', '无', '无'))
            if len(file_li_list) == 2:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, file_name[0], file_url[0], file_name[1],
                               file_url[1], '无', '无', '无', '无', '无', '无'))
            if len(file_li_list) == 3:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, file_name[0], file_url[0], file_name[1],
                               file_url[1], file_name[2], file_url[2], '无', '无', '无', '无'))
            if len(file_li_list) == 4:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, file_name[0], file_url[0], file_name[1],
                               file_url[1], file_name[2], file_url[2], file_name[3], file_url[3], '无', '无'))
            if len(file_li_list) == 5:
                cursor.execute(
                    sql.format(column, title, time, cnt, info_url, all_content, file_name[0], file_url[0], file_name[1],
                               file_url[1], file_name[2], file_url[2], file_name[3], file_url[3], file_name[4],
                               file_url[4]))
            # 提交到数据库执行
            db.commit()
        except:
            # 如果发生错误则回滚
            db.rollback()
        print('')
    # 对后续页面进行爬取，爬满一百条，使用cnt计数
    for page in range(page_num -1, page_num -5, -1):
        pre_later_url = 'https://jwch.fzu.edu.cn/jxtz/%d.htm'
        later_url = format(pre_later_url % page)
        later_response = requests.get(url=later_url, headers=headers)
        later_response.encoding = later_response.apparent_encoding;
        later_response = later_response.text
        tree = etree.HTML(later_response)
        li_list = tree.xpath('//ul[@class="list-gl"]/li')
        for li in li_list:
            time = li.xpath('./span/text()')[0].replace('\r\n', '')
            time = time.replace(' ', '')
            if time == '':
                time = li.xpath('./span/font/text()')[0].replace('\r\n', '')
                time = time.replace(' ', '')
            column = li.xpath('./text()')[1].replace(' ', '')
            column = column.replace('\r\n', '')
            title = li.xpath('./a/text()')[0]
            info_url = 'https://jwch.fzu.edu.cn/' + li.xpath('./a/@href')[0]
            info = time + column + title + ' ' + info_url
            print(info)
            cnt += 1

            # 爬取详情页新闻
            detail = requests.get(url=info_url, headers=headers)
            detail.encoding = detail.apparent_encoding
            detail = detail.text
            tree = etree.HTML(detail)
            pre_news = tree.xpath('.//div[@class="v_news_content"]//p')
            all_content = ''
            for mew in pre_news:
                if len(mew.xpath('./span')) == 0:
                    detail_list = './span/span'
                else:
                    detail_list = './span'
                news = [i.xpath('string(.)') for i in mew.xpath(detail_list)]
                content = ''
                for part in news:
                    content += part;
                content = content.replace('\r\n', '')
                content = content.replace(' ', '')
                if len(content):
                    all_content += content.strip()
            print(all_content)
            # 爬取详情页附件
            file_li_list = tree.xpath('.//div[@class="xl_main"]/ul/li')
            file_url = []
            file_name = []
            if len(file_li_list):
                for file_li in file_li_list:
                    file_url.append( 'https://jwch.fzu.edu.cn' + file_li.xpath('./a/@href')[0])
                    file_name.append( file_li.xpath('./a/text()')[0])
                    print('附件名: ' + file_name[-1] + '\n附件地址: ' + file_url[-1])
            # 将标题、栏目、时间存入数据库
            sql = """
                        INSERT INTO FZU ( col, title, time, num, url, all_content, file1, file1_url, file2, file2_url, file3, file3_url, file4, file4_url, file5, file5_url)
                        VALUES ("{0}", "{1}", "{2}", {3}, "{4}", "{5}","{6}","{7}","{8}","{9}","{10}","{11}","{12}","{13}","{14}","{15}");
                 """

            try:
                # 执行sql语句
                if len(file_li_list)==0:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:],'无','无','无','无','无','无','无','无','无','无'))
                if len(file_li_list)==1:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:], file_name[0],file_url[0],'无','无','无','无','无','无','无','无'))
                if len(file_li_list)==2:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:], file_name[0],file_url[0],file_name[1],file_url[1],'无','无','无','无','无','无'))
                if len(file_li_list)==3:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:], file_name[0], file_url[0], file_name[1], file_url[1], file_name[2], file_url[2],'无','无','无','无'))
                if len(file_li_list)==4:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:], file_name[0], file_url[0], file_name[1], file_url[1], file_name[2], file_url[2],file_name[3],file_url[3],'无','无'))
                if len(file_li_list)==5:
                    cursor.execute(sql.format(column, title, time, cnt, info_url, all_content[:1000:], file_name[0], file_url[0], file_name[1], file_url[1], file_name[2], file_url[2],file_name[3],file_url[3],file_name[4],file_url[4]))
                # 提交到数据库执行
                db.commit()
            except:
                # 如果发生错误则回滚
                db.rollback()
            print('')
    cnt = str(cnt)
    print('爬取了'+cnt+'条信息!!!!')
