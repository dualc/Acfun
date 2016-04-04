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
import random
from progressbar import *
from email.mime.text import MIMEText  

LOGIN_URL = 'http://passport.acfun.tv/login.aspx'
SIGN_CARD = 'http://www.acfun.tv/member/checkin.aspx'
#'http://webapi.acfun.tv/record/actions/signin?channel=0&date='
ISOTIMEFORMAT='%Y-%m-%d %X'
COMMENT = 'http://www.acfun.tv/comment.aspx'
COMMENT_REFER = 'http://www.acfun.tv/a/ac2644286'
COMMENT_LIST = 'http://www.acfun.tv/comment_list_json.aspx?contentId=2644286&currentPage=1'
COMMENT_FORM = '为种子而奋斗。[emot=ac,%d/]'
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

def get_browser_header(refer = "http://www.acfun.tv/member/"):
    user_agent = 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                 ' Chrome/41.0.2272.101 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Referer' : refer}
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

def is_get_succed(comment_ret,userName,floor_list):
	info = json.loads(comment_ret)
	comment_list = info['data']['commentContentArr']
	for i in comment_list:
		floor_list.append(comment_list[i]['count'])
		if comment_list[i]['userName'].encode('utf-8')==userName:
			print  comment_list[i]['count'],
			if comment_list[i]['count']%100 == False:
				print 'get success'
				return True
	else:
		return False


def sign_card(username = '',pwd = '',send_email = False):
	opener = get_opener()
	values = {'username':username,'password':pwd}
	data = urllib.urlencode(values)
	req = urllib2.Request(LOGIN_URL, data,get_browser_header())
	response = opener.open(req)
	auth_ret = response.read()
	logging.info(auth_ret)
	if is_success(auth_ret):
		# response = opener.open(SIGN_CARD+str(int((lambda x:x*1000)(time.time()))))
		response = opener.open(SIGN_CARD)
		sign_ret = response.read()
		logging.info(sign_ret)
		if is_success(sign_ret):
			return True
	else:
		return False

        
def sign_comment(username = '',pwd = '',send_email = False):
	opener = get_opener()
	values = {'username':username,'password':pwd}
	data = urllib.urlencode(values)
	req = urllib2.Request(LOGIN_URL, data,get_browser_header(COMMENT_REFER))
	response = opener.open(req)
	auth_ret = response.read()
	form ={'name':'name','token':'mimiko','quoteId':0,
			'text':'种子。。。。。。。[emot=ac,01/]',
			'cooldown':5000,
			'contentId':2644286,
			'quoteName':''} 
	logging.info(auth_ret)
	interval = 1
	count  = 0;
	if is_success(auth_ret):
		# response = opener.open(SIGN_CARD+str(int((lambda x:x*1000)(time.time()))))
		while True:
			emotionid = random.randint(1, 54)
			form['text']= COMMENT_FORM % emotionid
			print form['text'].decode('utf-8')
			data = urllib.urlencode(form)
			progress = ProgressBar()
			print 'current wait time %d' % interval
			for i in progress(range(interval)):
  				time.sleep(1)
			response = opener.open(COMMENT_LIST)
			list_ret = response.read()
			floor_list = [];
			if is_get_succed(list_ret,username,floor_list):
				count+=1
				print "get %d" % count
			else:
				max_id =int(max(floor_list))
				print "max floor %d ,interval %d,wait" % (max_id,interval)
				if (100 - max_id%100) < 10:
					interval = 2 
					print "post 10 times to get floor"
					for i in range(10):
						emotionid = random.randint(1, 54)
						response = opener.open(COMMENT,data)
						sign_ret = response.read()
						print sign_ret.decode('utf-8')
				else:
					interval =(100 - max_id%100)/2

if __name__ == '__main__':
	set_log()
	user_list = {}
	conf = {}
	get_user_info(user_list,conf)
	for k,v in user_list.items():
		if sign_comment(k.encode('utf8'),v.encode('utf8')):
			logging.info("%s %s sign_card success" %(k,time.strftime( ISOTIMEFORMAT, time.localtime() )))
