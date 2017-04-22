#!/usr/bin/python
# encoding: utf-8
import chardet
import json
import requests
import os
import time
import urllib
import re
import MySQLdb
import sys
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
#1491876516
DBUG   = 0
current_time=time.time()
print int(current_time)


reload(sys)
sys.setdefaultencoding('utf-8')
params={"category":"news_society",\
          "utm_source":'toutiao',\
             "widen":'1',\
              "max_behot_time":int(current_time),\
                 "max_behot_time_tmp":int(current_time),\
                 "tadrequire":"true",\
                      "as":"A1E5D8FEEC88ACF",\
                            "cp":"58EC98CACC9F6E1"}




headers={"Accept":"text/javascript, text/html, application/xml, text/xml, */*",\
         "Accept-Encoding":"gzip, deflate, sdch",\
	   "Accept-Language":"zh-CN,zh;q=0.8",\
         "Cookie":"sso_login_status=1; login_flag=ac72c76d5e1261ce9284e92691414e25; sid_tt=c157b51ac47deddb5f46934b3078fbbe; sid_guard='c157b51ac47deddb5f46934b3078fbbe|1489405562|2591999|Wed\054 12-Apr-2017 11:46:01 GMT'; uuid='w:5c1760ab1c6842c2a366a8eb552b8e94'; UM_distinctid=15ac77d2b85321-0bb5bad78c928e-3c654009-e1000-15ac77d2b86473; sessionid=c157b51ac47deddb5f46934b3078fbbe; _ba=BA0.2-20170313-51d9e-Bb4Gumy7MWjhjWt3WNaG; tt_webid=56685215380; csrftoken=a1e14aeb4cd5b3ac744b4ae36048fb85; utm_source=toutiao; _ga=GA1.2.1382893736.1489405555; CNZZDATA1259612802=1279854718-1489404305-%7C1491891748; __utmt=1; __utma=24953151.1382893736.1489405555.1491540884.1491896835.2; __utmb=24953151.2.10.1491896835; __utmc=24953151; __utmz=24953151.1491540884.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __tasessionId=gg3aa4v5o1491895601293",\
        "Host":"www.toutiao.com",\
      "Referer":"http://www.toutiao.com"}

reBODY =re.compile( r'<body.*?>([\s\S]*?)<\/body>', re.I)
reCOMM = r'<!--.*?-->'
reTRIM = r'<{0}.*?>([\s\S]*?)<\/{0}>'
reTAG  = r'<[\s\S]*?>|[ \t\r\f\v]'

reIMG  = re.compile(r'<img[\s\S]*?src=[\'|"]([\s\S]*?)[\'|"][\s\S]*?>')

class Extractor():
    def __init__(self, url = "", blockSize=3, timeout=5, image=False):
        self.url       = url
        self.blockSize = blockSize
        self.timeout   = timeout
        self.saveImage = image
        self.rawPage   = ""
        self.ctexts    = []
        self.cblocks   = []

    def getRawPage(self):
        try:
            resp = requests.get(self.url, timeout=self.timeout)
        except Exception as e:
            raise e

        if DBUG: print(resp.encoding)

        resp.encoding = "UTF-8"
        info=chardet.detect(resp.content).get('encoding','utf-8')
        html=resp.content.decode(info,'ignore').encode('utf-8')  
        return resp.status_code, html

    def processTags(self):
        self.body = re.sub(reCOMM, "", self.body)
        self.body = re.sub(reTRIM.format("script"), "" ,re.sub(reTRIM.format("style"), "", self.body))
        # self.body = re.sub(r"[\n]+","\n", re.sub(reTAG, "", self.body))
        self.body = re.sub(reTAG, "", self.body)

    def processBlocks(self):
        self.ctexts   = self.body.split("\n")
        self.textLens = [len(text) for text in self.ctexts]

        self.cblocks  = [0]*(len(self.ctexts) - self.blockSize - 1)
        lines = len(self.ctexts)
        for i in range(self.blockSize):
            self.cblocks = list(map(lambda x,y: x+y, self.textLens[i : lines-1-self.blockSize+i], self.cblocks))

        maxTextLen = max(self.cblocks)

        if DBUG: print(maxTextLen)

        self.start = self.end = self.cblocks.index(maxTextLen)
        while self.start > 0 and self.cblocks[self.start] > min(self.textLens):
            self.start -= 1
        while self.end < lines - self.blockSize and self.cblocks[self.end] > min(self.textLens):
            self.end += 1

        return "".join(self.ctexts[self.start:self.end])

    def processImages(self):
        self.body = reIMG.sub(r'{{\1}}', self.body)

    def getContext(self):
        code, self.rawPage = self.getRawPage()
        self.body = re.findall(reBODY, self.rawPage)[0]

        if DBUG: print(code, self.rawPage)

        if self.saveImage:
            self.processImages()
        self.processTags()
        return self.processBlocks()
        # print(len(self.body.strip("\n")))




base_url="http://www.toutiao.com/api/pc/feed/";
url=base_url+'?'+urllib.urlencode(params)

cp=ConfigParser.SafeConfigParser()
cp.read('env.config')
HOST=str(cp.get("database","host"))
USERNAME=str(cp.get("database","username"))
PASSWORD=str(cp.get("database","password"))
DBNAME=str(cp.get("database","dbname"))

db=MySQLdb.connect(HOST,USERNAME,PASSWORD,DBNAME)
db.set_character_set('utf8')

cursor=db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("SET collation_connection = utf8_general_ci")
sql="""
	insert into news(keyword,title,abstract,content,source,tag,class,datetime) values('1111','11111','11111','11111','111111','111111','11111',1111)

"""
#cursor.execute(sql)
#db.commit()
#db.close()

while True:
	print url
	post_data=requests.get(url,headers=headers)
	data=json.loads(post_data.text.decode('utf-8'))['data']
	next=json.loads(post_data.text.decode('utf-8'))['next']
	next_time=next['max_behot_time']
	#print type(data)
	#print len(data)
	for i in range(0,len(data)):
		print data[i]
		temp_url=' '
		article_genre=''
		title=''
		news_content=''
		news_origin=''
		source=''
		classify=''
		abstract=''
		html=''
		tags=''
		if data[i].has_key('chinese_tag') and data[i]['tag_url']!='video' and data[i]['more_mode']==True:
			if data[i]['chinese_tag']!= None:
				#print data[i]['chinese_tag']
				classify=urllib.urlencode(data[i]['chinese_tag'])
				#print type(classify)
			if data[i].has_key('title'):
				#print type(data[i]['title'])
				#title=data[i]['title'].decode('gbk','ignore').encode('utf-8','ignore')
				#print type(title)
				title=urllib.urlencode(data[i]['title'])
				#print type(title) 
				#print title
			if data[i].has_key('source'):
				source=urllib.urlencode(data[i]['source'])
				#print source
			if data[i].has_key('abstract'):

				abstract=urllib.urlencode(data[i]['abstract'])
			if data[i].has_key('source_url'):
				if data[i]['source_url'].startswith('/group'):
					temp_url="http://www.toutiao.com"+data[i]['source_url']
					#print temp_url
			if data[i].has_key('article_genre'):
				article_genre=data[i]['article_genre']
			if temp_url!=' ' and article_genre=='article':
				try:
					r=requests.get(temp_url,headers=headers,allow_redirects=True)
					r.encoding='utf-8'
				except:
					continue
				#print r.status_code
				info=chardet.detect(r.content).get('encoding','utf-8')
				html=r.content.decode(info,'ignore').encode('utf-8')
				#print type(html)
				temp=Selector(text=html).xpath(".//*[@id='article-main']/h1/text()").extract()
				if len(temp)!=0:
					title=temp[0]
				sel=Selector(text=html).xpath(".//*[@id='article-main']/div[2]/div").extract()
				if len(sel)!=0:
					for i in range(len(sel)):
						#print sel[i]
						news_origin+=sel[i]
					news_origin=urllib.urlencode(news_origin)
					news_tag=Selector(text=html).xpath(".//*[@id='article-main']/div[3]/div[1]/ul/li/a/text()").extract()
					if len(news_tag)!=0:
						for i in range(0,len(news_tag)):
							tags=tags+news_tag[i]+","
							sql_temp="select * from tag where tag='%s'"%(news_tag[i])
							#print sql_temp
							temp=cursor.execute(sql_temp)
							#print type(temp)
							if temp==0:
								cursor.execute("insert into %s (tag,frequency) values('%s','%d')"%('tag',news_tag[i],1))
							elif temp!=0:
								tag_data=cursor.fetchone()
								tag_frequency=int(tag_data[1])+1
								cursor.execute("update  %s  set frequency='%d' where tag='%s'"%('tag',tag_frequency,news_tag[i]))	
						
				elif len(sel)==0:

					sel=Selector(text=html).xpath(".//*[@id='article-main']/div[2]").extract()
					if len(sel)!=0:
						for i in range(len(sel)):
							#print sel[i]
							news_origin+=sel[i]
						news_origin=urllib.urlencode(news_origin)
					news_tag=Selector(text=html).xpath(".//*[@id='article-main']/div[3]/div[1]/ul/li/a/text()").extract()
					if len(news_tag)!=0:
						for i in range(0,len(news_tag)):
							tags=tags+news_tag[i]+","
							sql_temp="select * from tag where tag='%s'"%(news_tag[i])
							#print sql_temp
							temp=cursor.execute(sql_temp)
							#print type(temp)
							if temp==0:
								cursor.execute("insert into %s (tag,frequency) values('%s','%d')"%('tag',news_tag[i],1))
							elif temp!=0:
								tag_data=cursor.fetchone()
								tag_frequency=int(tag_data[1])+1
								cursor.execute("update  %s  set frequency='%d' where tag='%s'"%('tag',tag_frequency,news_tag[i]))
						
					elif len(sel)==0:
						continue
				news_content=Extractor(temp_url,blockSize=3, timeout=5, image=True)
				#print news_content.getContext()
				news_content=urllib.urlencode(news_content.getContext())
			

		if len(title)!=0 and len(news_content)!=0 and len(news_origin)!=0:
			datetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			
			#print type(abstract)
			#print "hehehe"
			sql="insert into %s (keyword,title,abstract,news_origin,news_content,source,tag,classify,datetime,news_tag)values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%('news',' ',title,abstract,news_origin,news_content,source,' ',classify,datetime,tags)
			cursor.execute(sql)
			db.commit()	
		time.sleep(1)					
	params['max_behot_time']=next_time
	params['max_behot_time_tmp']=next_time
	url=base_url+'?'+urllib.urlencode(params) 



db.close()         
