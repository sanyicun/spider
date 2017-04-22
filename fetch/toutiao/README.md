# auto-spider
test-mysql.py  用于创建mysql数据库表  其中有一些测试代码

news-toutiao.py  主要负责爬取数据存入数据库

tornado web   是一个基于tornado的web服务器 

news-get-top.py  获取标签中的处于前几位的标签
注意事项:
  mysql数据库   先创建数据库test    表调用test-mysql.py来创建  数据库 表的字符集是utf8
  安装tornado  pip install tornado
  
  运行:
   1 创建一个test数据库  
   2 python test-mysql.py创建表
   3 cd tornado web  执行python web监听本机8999端口 
   
