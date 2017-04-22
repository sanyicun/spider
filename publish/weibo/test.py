#!/usr/bin/python
#coding:utf-8 
import requests 
import common

import MySQLdb
import urllib
import sys
import re
import os

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
reload(sys)
sys.setdefaultencoding('utf-8')
db=MySQLdb.connect('127.0.0.1','root','hello1234','ai')
print db
db.set_character_set('utf8')
cursor=db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

def publish():  
	#sql="select * from news where title like '"+"%"+"%s"%(talk)+"%'"
	sql="select news_content from articles order by id desc limit 1"
	print sql 
	#print  type(sql.decode('utf-8','ignore').encode('utf-8'))
	#sql=sql.decode('utf-8','ignore').encode('utf-8')
	cursor.execute(sql)
	data=cursor.fetchone()
	#print data

	article=urllib.unquote(data[0])
	a=re.sub("{{(.*?)}}", " ",article)
	b=re.findall(r"{{(.*?)}}",article)
	print "hahahahaha"+str(len(b))
	#用正则表达式进行匹配  
	reg='src="(.*?)"'  
	imgre=re.compile(reg)  
	#查找所有  
	imglist=re.findall(imgre,article)  
	#遍历图片地址并保存  
	x=0
        '''
	for imgurl in imglist:  
		print imgurl
		x+=1
		urllib.urlretrieve(imgurl,'tmp/news_toutiao_%s.jpg' % x)  
	'''
	imgarr=[]
        for i in range(len(b)):
		imgurl=str(b[i])
		print imgurl
		x+=1
		filename='tmp/%s' % imgurl.split('/')[-1]
		imgarr.append(filename)
		urllib.urlretrieve(imgurl, filename)

	tr4s = TextRank4Sentence()
	tr4s.analyze(text=a, lower=True, source = 'all_filters')

	text=''		
	print( '摘要：' )
	for item in tr4s.get_key_sentences(num=2.5):
		#print(item.index, item.weight, item.sentence)
		#print(item.sentence)
		text=text + item.sentence
	print text

	if len(imgarr) > 0:   
		txtlen= len(text) if len(text) < 140 else 140
		common.send_text_pic(text[0:txtlen], imgarr[0])
		print "publish OK"

	else:
		print "no photo"
	'''
	for i in range(len(b)):
		file_temp='./news_toutiao_'+str(i)+'.png'
		os.remove(file_temp)
	'''


if __name__=='__main__':  
	common.setLoginPara()
	publish()
