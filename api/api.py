from flask import Flask, jsonify, make_response, request,abort
import requests
import json
from urlparse import urlparse
import time
import datetime

#
# own package
#
from common import get_string_time
from scan.util import info_website, check_login, get_href, bypass_login
from config import COOKIE_NAME_DVWA, COOKIE_VALUE_DVWA
from scan.scan_xss import scan_xss
from scan.scan_port import scan_port
from scan.scan_sql import scan_sql
from scan.scan_sql_blind import scan_sql_blind
from scan.scan_file_upload import scan_file_upload

scan_sql
app = Flask(__name__)

@app.route('/')
def index():
	return 'welcome'

@app.route('/scan',methods=['POST'])
def audit():
	result = {}
	session = requests.Session()

	duration = int(time.time())
	# get time : 2016-11-26 15:00:00
	string_start = get_string_time()
	#
	# lay thong webapp gui len
	#
	req_dict = request.form
	list_scan = req_dict.getlist('list_scan')
	if list_scan == None:
		list_scan = ['xss', 'sql_injection', 'sql_blind_injection', 'file_upload', 'port_scan']
	#list_scan = ['xss', 'sql_injection', 'port_scan', 'file_upload']
	#list_scan = ['xss', 'sql_injection', 'file_upload']
	#list_scan = ['port_scan']
	url = req_dict.getlist('url')[0]

	print url
	print list_scan	

	info = info_website(session, url)
	
	result['info'] = info
	# khoi tao global variable
	xss_vul = {}
	sql_vul = {}
	sql_blind_vul = {}
	fi_vul = {}
	file_upload_vul = {}
	port_vul = {}
	ssl_vul = {}
	csrf = {}
	_404 = {}
	#
	# process pentest
	#

	cookies = {COOKIE_NAME_DVWA: COOKIE_VALUE_DVWA}
	is_login = check_login(session, url)
	if is_login:
		# neu phai login de scan
		print 'login'
		if bypass_login(session, url, cookies) == 0:
			print 'cannot scan'
		# khong can login de scan

	list_href = get_href(session, url)
	print list_href
	for scan in list_scan:
		if scan == 'xss':
			bypass_login(session, url, cookies)
			print 'scan_xss ...'
			xss_vul = scan_xss(session=session, url=url, list_href=list_href)
			result['xss'] = xss_vul
			print '#'*100
			#print xss
		elif scan == 'sql_injection':
			bypass_login(session, url, cookies)
			print 'scan_sql ...'
			sql_vul = scan_sql(session=session, url=url, list_href=list_href)
			result['sql'] = sql_vul
			print result
		elif scan == 'sql_blind_injection':
			bypass_login(session, url, cookies)
			print 'scan_sql_blind ...'
			sql_blind_vul = scan_sql_blind(session=session, url=url, list_href=list_href)
			result['sql_blind'] = sql_blind_vul
			print result
			print '#'*100
		elif scan == 'file_upload':
			bypass_login(session, url, cookies)
			print 'scan_file_upload ...'
			file_upload_vul = scan_file_upload(session=session, url=url, list_href=list_href)
			result['file_upload'] = file_upload_vul
			print result
		elif scan == 'port_scan':
			port_vul = scan_port(session=session, name=info['host'], url=url)
			result['port'] = port_vul
			pass	
	print '#'*100
	print 'xss:'
	print xss_vul
	print '*'*10
	print 'sql:'
	print sql_vul
	print '='*10
	print 'sql_blind:'
	print sql_blind_vul
	print '='*10
	print 'file_upload:'
	print file_upload_vul
	print '='*10
	print 'port_scan:'
	print port_vul

	duration = int(time.time()) - duration
	string_end = get_string_time()

	info['string_start'] = string_start
	info['string_end'] = string_end
	info['duration'] = duration
	print result
	return jsonify({'result':result})

@app.route('/test')
def test():
	return jsonify({'result': 'test'})	

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9999)
    
