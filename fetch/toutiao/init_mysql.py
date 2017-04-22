#!/usr/bin/python
#coding:utf-8

import MySQLdb
import urllib
import sys
import ConfigParser

cp=ConfigParser.SafeConfigParser()
cp.read('env.config')
HOST=str(cp.get("database","host"))
USERNAME=str(cp.get("database","username"))
PASSWORD=str(cp.get("database","password"))
DBNAME=str(cp.get("database","dbname"))


reload(sys)
sys.setdefaultencoding('utf-8')
db=MySQLdb.connect(HOST,USERNAME,PASSWORD)
print db
db.set_character_set('utf8')
cursor=db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
	     
cursor.execute('create database if not exists ' + DBNAME)
db.select_db(DBNAME)

cursor.execute('DROP TABLE IF EXISTS articles')
cursor.execute('DROP TABLE IF EXISTS tags')
cursor.execute('DROP TABLE IF EXISTS publish')

sql_articles="""create table articles(
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
sql_tags="""create table tags(
        id  int AUTO_INCREMENT PRIMARY KEY NOT NULL , 
	tag text,
	frequency int,
	datetime text
	) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
"""
#used
sql_publish = """create table publish(
        id  int AUTO_INCREMENT PRIMARY KEY NOT NULL , 
	docid int,
	int pub_platform,
	title text,
	content text,
	datetime text
	) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
"""
#sql="""create table t(title text)"""

cursor.execute(sql_articles)
cursor.execute(sql_tags)
cursor.execute(sql_publish)
#db.commit()
db.close()
