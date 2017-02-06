notification_error = ['you have an error in your sql syntax', \
                'mysqli error','mysql failed', \
                'query failed']

from bs4 import BeautifulSoup, SoupStrainer
import urllib
from urlparse import urlparse, urljoin , parse_qsl
import re
import requests

from payload.payload_sql import payload_sql
from config import COOKIE_NAME_DVWA, COOKIE_VALUE_DVWA
from scan.util import get_scheme, get_hostname


cookies = {COOKIE_NAME_DVWA: COOKIE_VALUE_DVWA}


def get_paras_in_url(url):
    # http://example.com/?q=abc&p=123
    parsed = urlparse(url)
    params = parse_qsl(parsed.query)
    return params

def convert_tag(form):
    try:
        string=str(form).replace('<','&lt;').replace('>','&gt;')
        return string
    except:
        return None

def get_info_form(form, payload):
    try:
        data = {}
        for input in form.findChildren({'input'},{'type': 'password'}):        
            if input.get('type').lower() == 'password':
                 return
        for input in form.findChildren({'input'},{'type': 'text'}):        
            if input.get('type').lower() == 'text':
                 data[str(input.get('name'))] = payload
        for input in form.findChildren({'input'},{'type': 'submit'}):
            if input.get('type').lower() == 'submit':
                if input.has_attr('name'):
                    data[str(input.get('name'))] = input.get('value')
                else:
                    data['submit'] = input.get('value')
        for input in form.findChildren({'textarea'}):
            if input:
                data[str(input['name'])] = payload
        info_form = {}
        info_form['method'] = str(form.get('method',''))
        info_form['action'] = str(form.get('action',''))
        info_form['data'] = data
        return info_form
    except: 
        return
def convert_tag(form):
    try:
        string=str(form).replace('<','&lt;').replace('>','&gt;')
        return string
    except:
        return None

def scan_url_sql(session, url, params, payload):
    parsed = urlparse(url)
    query = '&'.join([k+'='+payload for k,v in params])
    url_scan = parsed.scheme + '://' + parsed.netloc + parsed.path \
            + '?' + query
    req = session.get(url_scan)
    for error in notification_error:
        if error.lower() in req.content.lower():
            return url
    
    return
def scan_form_sql(session, url, data_form, payload):
    try:
        action = data_form.get('action', None)
        if action != '#' and action != '':
            pass
            url = get_scheme(url)+ '://' + get_hostname(url) + '/' +action.rstrip('?')
        elif action == None: 
            pass
        else:
            url = url + '/' + action.rstrip('?')
        method = data_form.get('method', '')    
        try:
            if method.lower() == 'get':
                
                re = session.get(url, params = data_form['data'], cookies=cookies)
            elif method.lower() == 'post':
                
                re = session.post(url, data = data_form['data'], cookies=cookies)
        except:
            return
        for error in notification_error:
            if error.lower() in re.content.lower():
                return True
    except:
        return
    

def scan_sql(session, url, list_href):    
    sql_vul = {'url': {'list':[], 'level': ''
                },
                'form': {'list': [], 'level': '', 'url': []
                }
            }
    for href in list_href:
        flag_level = 0
        for level in ['high', 'medium', 'low']:

            payloads = payload_sql[level]['payload']
            for payload in payloads:
                #
                # proess url
                #
                params = get_paras_in_url(href)
                result_url = scan_url_sql(session, href, params, payload)
                if result_url and result_url not in sql_vul['url']['list']:
                    print 'payload sql:' + payload
                    sql_vul['url']['list'].append(result_url)
                    if len(sql_vul['url']['list']) > 0:
                        sql_vul['url']['level'] = level
                    flag_level = 1                    
                #
                # process form
                #
                req_sql = session.get(href, cookies=cookies)
                soup = BeautifulSoup(req_sql.content,'html.parser')
                form = soup.find('form')
                data_form = get_info_form(form, payload)
                if data_form:
                    result_form = scan_form_sql(session, href, data_form, payload)
                    if result_form and convert_tag(form) not in sql_vul['form']['list']:
                        print 'payload sql:' + payload
                        print level
                        sql_vul['form']['list'].append(convert_tag(form))
                        sql_vul['form']['url'].append(href)

                        if len(sql_vul['form']['list']) > 0:
                            sql_vul['form']['level'] = level
                        flag_level = 1
                        break        

            if flag_level == 1:
                break
    sql_vul['url']['total'] = len(sql_vul['url']['list'])
    sql_vul['form']['total'] = len(sql_vul['form']['list'])

    sql_vul['total_vul'] = len(sql_vul['url']['list']) + len(sql_vul['form']['list'])
    return sql_vul
