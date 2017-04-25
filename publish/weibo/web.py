#!/usr/bin/python
#coding:utf-8 
import tornado.web  
import tornado.ioloop
import common
from tornado.options import define,options,parse_command_line  
 
define('port',default=10000,help='run on the port',type=int)  

import urllib
import sys
import time
import re

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
reload(sys)
sys.setdefaultencoding('utf-8')
#db=MySQLdb.connect('127.0.0.1','root','','test')
#print db
#db.set_character_set('utf8')
#cursor=db.cursor()
#cursor.execute('SET NAMES utf8;')
#cursor.execute('SET CHARACTER SET utf8;')
#cursor.execute('SET character_set_connection=utf8;')

l=[]
wb=common.WeiboAPI()  
class MainHandler(tornado.web.RequestHandler):  
    def get(self):  
        self.render('index.html',title='homepage',items=l)  

    def post(self):  
        count=1  
        print(self.request.remote_ip) 
        if self.request.body_arguments.has_key('arg'):
            arg=self.request.body_arguments['arg']
            #print (arg[0] )
	    #print (arg[1])
	    #print (arg[2])
            print ("------------------")
            #print (urllib.unquote(arg[2]))
            #print ('----------------')
            #abstract= urllib.unquote(arg[3])[9:]
            #print abstract
            #print ('-------------------')
            #news_origin=urllib.unquote(arg[4])[12:]
            print ('-------------------')
            article=urllib.unquote(arg[5])[13:]
	    a=re.sub("{{(.*?)}}", " ",article)
	    b=re.findall(r"{{(.*?)}}",article)
	    x=0
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
		text=text + item.sentence
	    print text
	    if len(imgarr) > 0:   
		txtlen= len(text) if len(text) < 140 else 140
		wb.send_text_pic(text[0:txtlen], imgarr[0])
		print "publish OK"

	    else:
		print "no photo"
		
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
