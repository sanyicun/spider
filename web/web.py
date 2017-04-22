#!/usr/bin/python
#coding:utf-8 
import tornado.web  
import tornado.ioloop  
from tornado.options import define,options,parse_command_line  
import requests 
define('port',default=8999,help='run on the port',type=int)  


import MySQLdb
import urllib
import sys


reload(sys)
sys.setdefaultencoding('utf-8')
db=MySQLdb.connect('127.0.0.1','root','hello1234','spider')
print db
db.set_character_set('utf8')
cursor=db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

l=[]
class MainHandler(tornado.web.RequestHandler):  
    def get(self):  
        self.render('index.html',title='homepage',items=l)  
    def post(self):  
        count=1  
        print(self.request.remote_ip)  
        talk=self.get_argument('talk')  
        print type(talk)
	sql="select * from news where title like '"+"%"+"%s"%(talk)+"%'"
	print sql 
	#print  type(sql.decode('utf-8','ignore').encode('utf-8'))
	#sql=sql.decode('utf-8','ignore').encode('utf-8')
	cursor.execute(sql)
	data=cursor.fetchone()
	print data
	print talk  
        l.append(talk)
	
	arg={'arg':data}
	requests.post("http://127.0.0.1:10000/",data=arg)
        self.render('index.html',title='homepage',items=l)  
def main():  
    parse_command_line()  
    app=tornado.web.Application(  
            [  
                (r'/',MainHandler),  
                ],  
            )  
  
    app.listen(options.port)  
    tornado.ioloop.IOLoop.instance().start()  
      
if __name__=='__main__':  
    main()  
