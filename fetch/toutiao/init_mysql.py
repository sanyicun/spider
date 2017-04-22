#!/usr/bin/python
#coding:utf-8


import MySQLdb
import urllib
import sys


#select * from news where title like '%武汉%';

reload(sys)
sys.setdefaultencoding('utf-8')
db=MySQLdb.connect('127.0.0.1','root','hello1234','spider')
print db
db.set_character_set('utf8')
cursor=db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
print cursor

url="日前，昌平区有关领导带领相关职能部门及部分镇（街）负责人专题调研拆违工作{{http://p1.pstatp.com/large/1b7a0006cbf16c01b49f}}在城南街道旧县奶牛场地块区领导一行深入了解该地块拆违腾退情况及城南街道下一步拆违工作计划旧县奶牛场位于城南街道旧县村北腾退范围为奶牛场所涉及的全部非住宅房屋以"
print type(url)
url=url.decode('gbk','ignore').encode('utf-8','replace')
url=urllib.urlencode({"url":url})
print type(url)
cursor.execute('SELECT VERSION()')
data=cursor.fetchone()

print data

cursor.execute('DROP TABLE IF EXISTS news')
cursor.execute('DROP TABLE IF EXISTS tag')
sql="""create table news(
      id  int AUTO_INCREMENT PRIMARY KEY NOT NULL , 
	keyword text,
	title text,
	abstract text,
	news_origin text,
	news_content text,
	source text,
	tag text,
	classify text,
	datetime text,
	news_tag text) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
"""
sql_tag="""create table tag(
	tag text,
	frequency int) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
"""
#sql="""create table t(title text)"""

cursor.execute(sql)
cursor.execute(sql_tag)
#sql="""
#	insert into news(keyword,title,abstract,content,source,tag,class,datetime) #values('1111','11111','11111','11111','111111','111111','11111',1111)
param='武汉'.decode('utf-8').encode('utf-8')
print type(param)
print type(unicode(param))
sql="select * from news where title like '"+"%"+"%s"%(param)+"%'"
print sql 
#print  type(sql.decode('utf-8','ignore').encode('utf-8'))
#sql=sql.decode('utf-8','ignore').encode('utf-8')
#cursor.execute(sql)
#data=cursor.fetchone()
#print data

#print data[2].decode('utf-8')



#t=cursor.execute("select * from tag where tag='%s'"%('苗侨伟'))
#data=cursor.fetchone()
#print type(data)
#print data[0]
#"""
#sql="insert into %s (title) values('%s')"%('t',url)
#print sql
#cursor.execute(sql)
#db.commit()
db.close()
