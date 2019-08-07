'''
Created on 2019年2月22日

@author: Administrator
'''
import urllib, gzip, os
import http.cookiejar
import traceback
import socket
import requests
import sys
import shutil
from bs4 import BeautifulSoup
from SQL.SQL_Action import SQL_ACTION
from Tools.scripts.objgraph import ignore
from time import sleep
from contextlib import closing
from PB.Progress_Bar import ProgressBar


class get_title_list(object):
    socket.setdefaulttimeout(20)
    # 根据网站报头信息设置headers
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'http://xn--11x805d.ml/index.php',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
    }

    # 构造文件头
    def getOpener(self, header):
        # 设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
        cookieJar = http.cookiejar.CookieJar()
        cp = urllib.request.HTTPCookieProcessor(cookieJar)
        opener = urllib.request.build_opener(cp)
        headers = []
        for key, value in header.items():
            elem = (key, value)
            headers.append(elem)
        opener.addheaders = headers
        return opener

    # 解压缩函数
    def ungzip(self, data):
        try:
            # print("正在解压缩...")
            data = gzip.decompress(data)
            # print("解压完毕...")
        except:
            print("未经压缩，无需解压...")
        return data

    # 读取页面函数
    # http://2dizhi.me/bbs/forum-64-1.html   东方
    def getUrlData(self, url):
        try:
            res = self.opener.open(url)
            data = res.read()
            # 解压缩
            data = self.ungzip(data)
        except:
            print('打开web链接问题')
            traceback.print_exc()
            data = ''
            return data
        # with open("c:/a.html", "wb+") as f:
        #    f.write(data)
        #   print('写入页面成功')
        return data

    opener = getOpener(headers, headers)

    def get_List(self, url, part_name):
        list_title_all = []
        sa = SQL_ACTION(1)
        page_index = 101
        max_page = 192
        while page_index <= max_page:
            print(page_index)
            tmp_url = url + str(page_index)
            print(tmp_url)
            data = self.getUrlData(tmp_url)
            data = data.decode('GB18030', errors=ignore)
            soup = BeautifulSoup(data, 'html.parser')
            tags = soup.find_all('td', class_='tal')
            # print(len(tags))
            try:
                tags[-1]
            except:
                print('未获取到列表')
                # os._exit(0)
            # print(tag)
            for td in tags:
                a = td.find('a')
                title_link = 'http://xn--11x805d.ml/' + a['href']
                title = a.get_text()
                forum = part_name
                list_title = [title, title_link, forum]
                list_title_all.append(list_title)
                print(title)
                print(title_link)
            page_index += 1

            sql = 'insert into title (title,title_url,forum) values (%s,%s,%s)'
            sa.ExcuteSQL(sql, list_title_all)
            list_title_all = []
            sleep(2)
        sa.db.close()

    def get_pic(self):
        sa = SQL_ACTION(1)
        # print('共%s条记录'% len(title_list))
        while 1:
            title_list = sa.GetQuery("select id,title,title_url from title where is_dl=0 and is_check=0  limit 0,1")
            if len(title_list) == 0:
                break
            index = 1
            for row in title_list:
                x = 0
                tid = row[0]
                title = row[1]
                turl = row[2]
                is_dl = 0
                title = title.replace(':', '')
                title = title.replace('?', '')
                title = title.replace('<', '')
                title = title.replace('>', '')
                title = title.replace('|', '')
                title = title.replace('', '')
                list_pic = []
                print('当前下载第%s/%s条数据' % (index, len(title_list)))
                print('标题:%s,链接:%s' % (title, turl))
                try:
                    sql = 'update title set is_check=1 where id=%s'
                    sa.ExcuteSQL(sql, [[tid]])
                    data = self.getUrlData(turl)
                    if data == '':
                        sql = 'update title set is_dl=2 where id=%s'
                        print('标记为打开页面无数据')
                        index += 1
                        sa.ExcuteSQL(sql, [[tid]])
                        continue
                    data = data.decode('GB18030', errors=ignore)
                    print('获取data')
                    soup = BeautifulSoup(data, 'html5lib')
                    print('获取soup')
                    tag = soup.find('div', class_='tpc_content do_not_catch')
                    print('获取tag')
                    imgs = tag.find_all('input')
                    print('开始下载%s' % title)
                    for img in imgs:
                        img_link = img.get('data-src')
                        file_type = img_link.split('.')[-1]
                        print('开始下载' + img_link)
                        result = self.dl_img(img_link, title, '%s.%s' % (x, file_type))
                        if result == 2:  # 连接失败尝试再次连接
                            print('连接失败尝试再次连接')
                            result = self.dl_img(img_link, title, '%s.%s' % (x, file_type))
                        if result == 1:
                            is_dl = 1
                            print('下载完成')
                        x += 1
                        list_pic.append([id, img_link, '', is_dl])
                except:
                    traceback.print_exc()
                    index += 1
                    print('获取图片失败')
                    sql = 'update title set is_dl=1,is_check=0 where id=%s'
                    print('标记已下载中.....')
                    sa.ExcuteSQL(sql, [[tid]])
                    continue

                # sql='delete from title_pic where title_id=%s'
                # sa.ExcuteSQL(sql,[[tid]])
                # sql='insert into title_pic (title_id,pic_url,pic_type,is_dl) values (%s,%s,%s,%s)'
                # sa.ExcuteSQL(sql, list_pic)
                sql = 'update title set is_dl=1,is_check=0 where id=%s'
                print('标记已下载中.....')
                index += 1
                sa.ExcuteSQL(sql, [[tid]])
                try:
                    path = 'D:\cl\%s' % title
                    file_count = len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))])
                    print('该文件夹下文件数为:%s' % file_count)
                    if file_count == 0:
                        shutil.rmtree(path)
                        print('删除空文件夹成功')
                except:
                    print('删除空文件夹失败')
        sa.db.close()

    def dl_img(self, url, title, filename):
        base_title = 'd:\\cl\\'
        file_address = base_title + title + '\\' + filename
        if not os.path.exists(base_title + title):
            print('创建文件夹:{}'.format(base_title + title))
            os.makedirs(base_title + title)
        if os.path.exists(file_address):
            print('%s 已存在' % filename)
            return 1
        try:
            '''
            with open(base_title, 'wb') as f:
                response = urllib.request.urlopen(url)
                f.write(response.read())
                f.close()
            '''
            with closing(requests.get(url, stream=True, timeout=(10, 40))) as html:
                if html.status_code != 200:
                    return 2
                chunk_size = 102400  # 单次请求最大值
                content_size = int(html.headers['content-length'])
                # temp_size=0
                print('该图片大小为%sKB' % str(int(content_size / 1024)))
                progress = ProgressBar('进程1:' + filename, total=content_size,
                                       unit="", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
                if int(html.headers['content-length']) > 5120:
                    with open(file_address, 'wb') as file:  # 以byte形式将图片数据写入
                        for data in html.iter_content(chunk_size=chunk_size):
                            if data:
                                file.write(data)
                                '''
                                temp_size+=len(data)
                                done=int(50*temp_size/content_size)
                                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / content_size))
                                sys.stdout.flush()
                                '''
                            progress.refresh(count=len(data))
                        file.flush()
                        file.close()  # 关闭文件
                        return 1
                else:
                    print('该文件小于5K,作废')
                    return 0
            '''
            html = requests.get(url,stream=True,timeout=(4, 10))
            file_address=base_title+title+'\\'+filename
            print('该图片大小为%s' % html.headers['content-length'])
            if int(html.headers['content-length'])<1024:
                with open(file_address,'wb') as file:  # 以byte形式将图片数据写入
                    file.write(html.content)
                    file.flush()    
                    file.close()  # 关闭文件
                    return 1
            else:
                print('该文件小于1K,作废')
            '''
        except:
            traceback.print_exc()
            print('下载失败')
            return 0

    def __init__(self, params):
        '''
        Constructor
        '''
