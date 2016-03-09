#!/usr/bin/env python
#coding:utf-8

import requests
from bs4 import BeautifulSoup
import pymysql,os,re

user=os.environ.get('user')
password=os.environ.get('password')
conn=pymysql.connect(host='localhost',unix_socket='/var/run/mysqld/mysqld.sock',
                     user=user,passwd=password,db='mysql',charset='utf8')

cur=conn.cursor()
cur.execute("USE wikipedia")
headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
        "Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8"}
session=requests.Session()

def insertPageIfNotExists(url):
    cur.execute("SELECT * FROM pages WHERE url=%s",(url))
    if cur.rowcount==0:
        cur.execute("INSERT INTO pages (url) VALUES (%s)",(url))
        conn.commit()
        return cur.lastrowid
    else:
        return cur.fetchone()[0]

def insertLink(fromPageId, toPageId):
    cur.execute("SELECT * FROM links WHERE fromPageId=%s AND toPageId=%s",
                (int(fromPageId),int(toPageId)))
    if cur.rowcount==0:
        cur.execute("INSERT INTO links (fromPageId, toPageId) VALUES (%s,%s)",
                (int(fromPageId),int(toPageId)))
        conn.commit()

pages=set()
def getLinks(pageUrl,recursionLevel):
    global pages
    if recursionLevel>4:
        print("Finished!")
        return;
    pageId=insertPageIfNotExists(pageUrl)
    url="http://en.wikipedia.org"+pageUrl
    req=session.get(url,headers=headers)
    bsObj=BeautifulSoup(req.text)
    for link in bsObj.findAll("a", href=re.compile("^(/wiki/)((?!:).)*$")):
        insertLink(pageId,insertPageIfNotExists(link.attrs['href']))
        if link.attrs['href'] not in pages:
            newPage=link.attrs['href']
            pages.add(newPage)
            getLinks(newPage,recursionLevel+1)

getLinks("/wiki/Kevin_Bacon",0)
cur.close()
conn.close()
