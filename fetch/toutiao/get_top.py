#!/usr/bin/python
#coding:utf-8
import MySQLdb
import urllib
import sys
import threading
import requests
import time
reload(sys)
sys.setdefaultencoding('utf-8')

global timer
def f():
	db=MySQLdb.connect('127.0.0.1','root','hello1234','spider')
	print db
	db.set_character_set('utf8')
	cursor=db.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')
	sql="select * from tag   order by frequency desc"
	cursor.execute(sql)
	data=cursor.fetchone()
	print type(data)
	print data[0],data[1]
	max=data[1]
	sql="select * from tag where frequency=%d"%(max)
	cursor.execute(sql)
	data=cursor.fetchall()
	print data[0][0]

	sql="select news_tag,news_content from news where news_tag like '"+"%"+"%s"%(data[0][0])+"%'"
	cursor.execute(sql)
	m=cursor.fetchall()
	print len(m)
	for i in range(0,len(m)):
		#print data[i][1]
		content=urllib.unquote(m[i][1][13:])
		print content
		data={"temp":content}
		requests.post("http://127.0.0.1:10000/",data=data)
		time.sleep(1)
	#sql="insert into %s (title) values('%s')"%('t',url)
	#print sql
	#cursor.execute(sql)
	#db.commit()
	db.close()
	#timer = threading.Timer(2.0, f)
	#timer.start()
	
if __name__=='__main__':
	#timer = threading.Timer(2.0, f)
	#timer.start()
	f()
