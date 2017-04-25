# -*- coding: utf-8 -*-
#author: Andrew (contact@andrewpd.com)
import ConfigParser
from weibo import APIClient
from weibo import APIError
import urllib,urllib2
import cookielib
import requests
import binascii
import rsa
import base64
import re
import json
import codecs
import os
import time
import random
import yaml
import threading
import Queue
import datetime
import calendar
import pytz
#from http_helper import*
#设置参数
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
PUBKEY = ''

class WeiboAPI():
	def __init__(self):
		cp=ConfigParser.SafeConfigParser()
		cp.read('../../config/env.config')
		self.appkey = str(cp.get("weibo","appkey"))
		self.appsecret= str(cp.get("weibo","appsecret"))
		self.callback= str(cp.get("weibo","callback"))
		self.username = str(cp.get("weibo","username"))
		self.pwd = str(cp.get("weibo","password"))
	 	self.client = APIClient(app_key=self.appkey, app_secret=self.appsecret, redirect_uri=self.callback)
	 	self.weibo_login(self.username, self.pwd)

	def weibo_login(self,username, password):
		cookie_file = 'weibo_login_cookies.dat'
		code = self.get_code(username, password, cookie_file)
		if code is None:
			print "Login failed"
			return None
		self.set_parameters(code)

 
	def set_parameters(self,code):
		r= self.client.request_access_token(code)
		access_token = r.access_token #sina返回的token
		expires_in = r.expires_in #token过期的时间

		self.client.set_access_token(access_token, expires_in)
		print "ok !"
    		return self.client

   
	def get_prelogin_status(self,username):
    		prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=openapi&callback=sinaSSOController.preloginCallBack&su=' + self.get_user(username) + \
     		'&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1487555417094';
    		data = urllib2.urlopen(prelogin_url).read()
    		#print data
    		p = re.compile('\((.*)\)')
    
    		try:
		        json_data = p.search(data).group(1)
        		data = json.loads(json_data)
        		servertime = str(data['servertime'])
        		pubkey = str(data['pubkey'])
        		nonce = data['nonce']
        		rsakv = data['rsakv']
        		showpin = data['showpin']
        		pcid = data['pcid']
			print "get prelogin status ok"
        		return servertime, nonce, rsakv, pubkey, showpin, pcid
    		except:
        		print 'getting prelogin status met error!'
        		return None

	def get_code(self, username, pwd, cookie_file):
    		ticket = self.get_ticket(username, pwd, cookie_file)
		if ticket is None:
			return None
    		fields={  
                'action': 'login',  
                'display': 'default',  
                'withOfficalFlag': '0',  
                'quick_auth': 'null',  
                'withOfficalAccount': '',  
                'scope': '',  
                'ticket': ticket,  
                'isLoginSina': '',  
                'response_type': 'code',  
                'regCallback': 'https://api.weibo.com/2/oauth2/authorize?client_id='+self.appkey+'&response_type=code&display=default&redirect_uri='+self.callback+'&from=&with_cookie=',  
                'redirect_uri':self.callback,  
                'client_id':self.appkey,  
                'appkey62': '52laFx',  
                'state': '',  
                'verifyToken': 'null',  
                'from': '',  
                'switchLogin':'0',  
                'userId':'',
                'passwd':''
            	}  
        	headers = {  
                "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",  
                "Referer": 'https://api.weibo.com/oauth2/default.html',  
                "Content-Type": "application/x-www-form-urlencoded"}  
        	post_url='https://api.weibo.com/oauth2/authorize'  
        	get_code_url=requests.post(post_url,data=fields,headers=headers)
        	print get_code_url.url
        	code=get_code_url.url.split('=')[1]
        	print code
        	return code

        def verify_code(self, pcid):
            url = 'http://login.sina.com.cn/cgi/pin.php?r={randint}&s=0&p={pcid}'.format(  
                randint=int(random.random() * 1e8), pcid=pcid)  
            filename = 'pin.png'  
            if os.path.isfile(filename):  
                os.remove(filename)  
           
            urllib.urlretrieve(url, filename)  
            if os.path.isfile(filename):  # get verify code successfully  
                #  display the code and require to input  
                from PIL import Image
        #        import subprocess  

        #        proc = subprocess.Popen(['display', filename], shell=True)
                im = Image.open(filename)
                im.show()
        #        proc.stdout.read().decode('gbk')
                code = raw_input('请输入验证码:'.decode('utf-8').encode('gbk'))
                os.remove(filename)  
        #        proc.kill()  
                return dict(pcid=pcid, door=code)  
            else:  
                return dict()
        def get_ticket(self, username,pwd,cookie_file):
            login_data = {
                'entry': 'openapi',
                'gateway': '1',
                'from': '',
                'savestate': '0',
                'userticket': '1',
                'pagerefer':'',
                'ct':'1800',
                's':'1',
                'vsnf': '1',
                'vsnval':'',
                'door':'',
                'appkey':'',
                'su': '',
                'service': 'miniblog',
                'servertime': '',
                'nonce': '',
                'pwencode': 'rsa2',
                'rsakv': '1330428213',
                'sp': '',
                'sr':'1920*1080',
                'encoding': 'UTF-8',
                'cdult':'2',
                'domain':'weibo.com',
                'prelt': '2140', 
                'returntype': 'TEXT'
                }

            cookie_jar2     = cookielib.LWPCookieJar()
            cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
            opener2         = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
            urllib2.install_opener(opener2)
            #login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=1450667802929'
            try:
                servertime, nonce, rsakv, pubkey, showpin, pcid = self.get_prelogin_status(username)
            except:
            	print "error get prelogin status!."
                return None
            #Fill POST data
        #    print 'starting to set login_data'
            login_data['servertime'] = servertime
            login_data['nonce'] = nonce
            login_data['su'] = self.get_user(username)
            login_data['sp'] = self.get_pwd_rsa(pwd, servertime, nonce, pubkey)
            login_data['rsakv'] = rsakv
            if showpin == 1:
                login_data.update(self.verify_code(pcid))
            login_data = urllib.urlencode(login_data)
            http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
            req_login  = urllib2.Request(
                url = login_url,
                data = login_data,
                headers = http_headers
            )
            result = urllib2.urlopen(req_login)
            text = result.read()
            text_data = json.loads(text)
            try:
                
                ticket = text_data['ticket']
                print "ticket success!"
            except KeyError:
                print "ticket Error!"
                print text_data['reason'].encode('utf-8')
            
            return ticket
            
        def get_pwd_rsa(self,pwd, servertime, nonce, pubkey):
            #n, n parameter of RSA public key, which is published by WEIBO.COM
            #hardcoded here but you can also find it from values return from prelogin status above
        #    weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
            weibo_rsa_n = pubkey
            #e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
            weibo_rsa_e = 65537
            message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
            
            #construct WEIBO RSA Publickey using n and e above, note that n is a hex string
            key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)
            
            #get encrypted password
            encropy_pwd = rsa.encrypt(message, key)
            #trun back encrypted password binaries to hex string
            return binascii.b2a_hex(encropy_pwd)

        def getTimeStamp(self,timeStr):
            timeArray = time.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            return timeStamp
            
        def get_user(self,username):
            username_ = urllib.quote(username)
            username = base64.encodestring(username_)[:-1]
            return username


         
        def formatTime(self,starttime):
            return datetime.datetime.fromtimestamp(time.mktime(time.strptime(starttime, '%a %b %d %H:%M:%S +0800 %Y')))
            
            
        def send_text_pic2(self,text=None,filepath=None):
        		if filepath==None:
        			sys.exit(0)
        		if len(filepath)>1:
        			for i in range(len(filepath)):
        				content=open(filepath[i],'rb').read()
        				#print base64.encodestring(content)
        				headers2={"Cookie":cook,"Host":"picupload.service.weibo.com",\
        				"Referer":"http://weibo.com/6103983087/profile?topnav=1&wvr=6&is_all=1",\
        				"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
        				params1={'b64_data':base64.b64encode(content)}
        				data=urllib.urlencode(params1)
        				r=requests.post(get_pic_url,headers=headers2,data=data,allow_redirects=False)
        				print  r.status_code
        				print r.text
        				#text=r.text.decode('utf-8').encode('utf-8')
        				#print text
        				#d=re.search(r'{.*}}',text).group(0)
        				#result=json.loads(d)
        				#p=result['data']['pics']['pic_1']
        				break
        				#print p
        					
        			#self.client.statuses.upload.post(status=text,pic=temp)
                
        def send_text_pic(self, text=None,filepath=None):
        		if filepath==None:
        			print "Error, file is none"
        			sys.exit(0)
        		if os.path.isfile(filepath):		
        			f=open(filepath,"rb")
        			self.client.statuses.upload.post(status=text,pic=f)
        			f.close()
        		else:
        			print "file not exist"

if __name__ == "__main__":
    wb=WeiboAPI()
    text="hello world"
    utext = unicode(text, "UTF-8")
    filepath="../../test/demo.png"
    try:
    	wb.send_text_pic(utext, filepath)
    except:
	print "send failed"

