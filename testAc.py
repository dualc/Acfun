#coding:utf8
import urllib
import urllib2
import cookielib
import time
import logging
import json
import os
import chardet
import smtplib  
from email.mime.text import MIMEText  

LOGIN_URL = 'http://passport.acfun.tv/login.aspx'
SIGN_CARD = 'http://webapi.acfun.tv/record/actions/signin?channel=0&date='
ISOTIMEFORMAT='%Y-%m-%d %X'


def set_log():
	logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)

def get_browser_header():
    user_agent = 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                 ' Chrome/41.0.2272.101 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Referer' : "http://translate.google.cn/"}
    return headers

def get_opener():
	#声明一个CookieJar对象实例来保存cookie
	cookie = cookielib.CookieJar()
	#利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
	handler=urllib2.HTTPCookieProcessor(cookie)
	#通过handler来构建opener
	opener = urllib2.build_opener(handler)
	#此处的open方法同urllib2的urlopen方法，也可以传入request
	#response = opener.open('http://www.baidu.com')
	return opener

def get_user_info(user_info={},conf={}):
	data = ''
	config_path = os.path.join(os.getcwd(),'config').replace('\\','/')
	# config_path = os.path.abspath('.')+'\\config.json'
	try:
		with open(config_path,'r') as f:
			data = f.read()
			config = json.loads(data)
			for info in config['info']:
				user_info[info['usr']]=info['pwd']
			conf['email'] = config['email']
			conf['use_email']= config['use_email']=='True'
	except Exception,ex:
		logging.error('fail to read config ,%s' % ex)
		return False
	else:
		return True

def is_success(auth_ret=''):
	info = json.loads(auth_ret)
	if 'success' in info.keys():
		return info['success']
	elif 'data' in info.keys():
		return info['data'] == True

def sign_card(username = '',pwd = '',send_email = False):
	opener = get_opener()
	values = {'username':username,'password':pwd}
	data = urllib.urlencode(values)
	req = urllib2.Request(LOGIN_URL, data,get_browser_header())
	response = opener.open(req)
	auth_ret = response.read()
	logging.info(auth_ret)
	if is_success(auth_ret):
		response = opener.open(SIGN_CARD+str(int((lambda x:x*1000)(time.time()))))
		sign_ret = response.read()
		logging.info(sign_ret)
		if is_success(sign_ret):
			return True
	else:
		return False

if __name__ == '__main__':
	set_log()
	user_list = {}
	conf = {}
	get_user_info(user_list,conf)
	for k,v in user_list.items():
		if sign_card(k.encode('utf8'),v.encode('utf8')):
			logging.info("%s %s sign_card success" %(k,time.strftime( ISOTIMEFORMAT, time.localtime() )))