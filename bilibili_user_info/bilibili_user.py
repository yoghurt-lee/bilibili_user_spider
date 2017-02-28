#coding:utf-8
import json
import random
import time, requests

import MySQLdb
from time import sleep


Headers = [ 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                'Opera/9.25 (Windows NT 5.1; U; en)',
                'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",] #备用header头，防止被封 

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Referer': 'http://space.bilibili.com/',
}
Referer_url = 'http://space.bilibili.com/'
url = 'http://space.bilibili.com/ajax/member/GetInfo'
conn = MySQLdb.connect(host='localhost', user='root', passwd='helloworld', port=3306,db='bilibili_user',charset='utf8')
#代理IP
proxies = {
        'http': '120.52.72.52:80',
        'https': '106.46.136.73:808',
}
def writeintoMySQL(data):
    if data.get('status') is True:
        data = data['data']
        mid = data['mid'] #注册编号
        name = data['name'] #昵称
        current_level = data['level_info']['current_level'] #b站等级
        sex = data["sex"] #性别
        sign = data['sign'] #个性签名
        regtime = 0 if data.get('regtime') is None else data['regtime'] #注册时间
        regtime_format = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(regtime))
        fans = data['fans'] #粉丝数
        info = (mid,name,current_level,sex,sign,regtime_format,fans)
        print info
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='helloworld', port=3306,db='bilibili_user',charset='utf8')
            cur = conn.cursor()
            cur.execute("insert into user_info values(%s,%s,%s,%s,%s,%s,%s)",info)
            cur.close()
            conn.commit()
        except MySQLdb.Error, e:
            raise e
        
def getuserInfo(mid):
    sleep(random.uniform(2,5))
    submit_data = {'mid':mid,'_':time.time()*1000}
    headers['Referer'] = Referer_url+str(mid)
    num = random.randint(0,7)
    headers['User-Agent'] = Headers[num]
    data = requests.post(url=url,headers=headers, data=submit_data,proxies = proxies).content
    if data is None: return
    data = json.loads(data)
    writeintoMySQL(data)

def createDB():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='helloworld', port=3306,charset='utf8')
        cur = conn.cursor()
        cur.execute('create database if not exists bilibili_user')
        conn.select_db('bilibili_user')
        cur.execute("create table user_info(mid int primary key,name varchar(20),\
        level int,sex varchar(2),sign varchar(200),regtime varchar(20),fans int)")
    except MySQLdb.Error, e:
        raise e

def start():
    from multiprocessing.dummy import Pool
    pool = Pool(processes=2)
    ids = range(779,3000) 
    pool.map(getuserInfo,ids)
    pool.close()
    pool.join()

def closedb():
    conn.close()
if __name__ == '__main__':
    #createDB() #if don't exist database and table,use this method to create;
    start()
    closedb()
