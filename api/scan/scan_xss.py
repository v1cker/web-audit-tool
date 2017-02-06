from bs4 import BeautifulSoup, SoupStrainer
import urllib
from urlparse import urlparse, urljoin , parse_qsl
import re
import requests

from payload.payload_xss import payload_xss
from config import COOKIE_NAME_DVWA, COOKIE_VALUE_DVWA
from scan.util import get_scheme, get_hostname


cookies = {COOKIE_NAME_DVWA: COOKIE_VALUE_DVWA}


def get_paras_in_url(url):
    # http://example.com/?q=abc&p=123
    parsed = urlparse(url)
    params = parse_qsl(parsed.query)
    return params


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

def scan_url_xss(session, url, params, payload):
    parsed = urlparse(url)
    query = '&'.join([k+'='+payload for k,v in params])
    url_scan = parsed.scheme + '://' + parsed.netloc + parsed.path \
            + '?' + query
    req = session.get(url_scan)
    soup = BeautifulSoup(req.content,'html.parser')
    for script in soup.find_all('script'):
        if payload.lower() == str(script).lower():
            return url
    return
def scan_form_xss(session, url, data_form, payload):
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
        if payload.lower() in re.content.lower():
            return True
    except:
        return
def re_request(session, url, payload, cookies=cookies):
    req = session.get(url, cookies=cookies)
    print 'check xss_s'
    soup = BeautifulSoup(req.content,'html.parser')
    for script in soup.find_all('script'):
        if payload.lower() == str(script).lower():            
            return True
    return False
def scan_xss(session, url, list_href):
    #list_href = ['http://dvwa.vn/vulnerabilities/xss_r/']
    xss_vul = {'xss_r': {'url': [], 
                        'form': [],
                        'level':''
                }, 
                'xss_s': {'url': [], 
                        'form': [],
                        'level':''
                }
            }
    for href in list_href:
        flag_level = 0
        for level in ['high', 'medium', 'low']:

            payloads = payload_xss[level]['payload']
            for payload in payloads:
                #
                # proess url
                #
                #params = get_paras_in_url(href)
                #result_url = scan_url_xss(session, href, params, payload)
                #if result_url and result_url not in xss_vul['xss_s']['url']:
                #    print 'payload xss:' + payload
                #    xss_vul['url']['list'].append(result_url)
                #    if len(xss_vul['url']['list']) > 0:
                #        xss_vul['url']['level'] = level
                #    flag_level = 1
                    
                #
                # process form
                #
                req_xss = session.get(href, cookies=cookies)
                soup = BeautifulSoup(req_xss.content,'html.parser')
                form = soup.find('form')
                data_form = get_info_form(form, payload)
                if data_form:
                    result_form = scan_form_xss(session, href, data_form, payload)
                    if result_form :
                        print 'payload xss:' + payload                   
                        if re_request(session, href, payload, cookies):
                            print level
                            if convert_tag(form) not in xss_vul['xss_s']['form']:
                                xss_vul['xss_s']['form'].append(convert_tag(form))
                                xss_vul['xss_s']['url'].append(href)
                        else:
                            print level
                            if convert_tag(form) not in xss_vul['xss_r']['form']:
                                xss_vul['xss_r']['form'].append(convert_tag(form))
                                xss_vul['xss_r']['url'].append(href)

                        if len(xss_vul['xss_s']['form']) > 0:
                            xss_vul['xss_s']['level'] = level

                        if len(xss_vul['xss_r']['form']) > 0:
                            xss_vul['xss_r']['level'] = level
                        flag_level = 1
                        break        

            if flag_level == 1:
                break
    xss_vul['xss_s']['total'] = len(xss_vul['xss_s']['form']) + \
                                len(xss_vul['xss_s']['url'])

    xss_vul['xss_r']['total'] = len(xss_vul['xss_r']['form']) + \
                                len(xss_vul['xss_r']['url'])
    total_vul = xss_vul['xss_r']['total'] + xss_vul['xss_s']['total']
    xss_vul['total_vul'] = total_vul
    return xss_vul