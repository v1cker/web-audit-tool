import requests
from bs4 import BeautifulSoup, SoupStrainer
from os.path import basename

from payload.payload_file_upload import payload_file_upload
from config import COOKIE_NAME_DVWA, COOKIE_VALUE_DVWA


cookies = {COOKIE_NAME_DVWA: COOKIE_VALUE_DVWA}
print cookies

def convert_tag(form):
    try:
        string=str(form).replace('<','&lt;').replace('>','&gt;')
        return string
    except:
        return None

def get_info_form(soup):
    data = {}
    for input in soup.findChildren({'input'},{'type': 'password'}):        
        if input.get('type').lower() == 'password':
             return
    for input in soup.findChildren({'input'},{'type': 'file'}):        
        if input.get('type').lower() == 'file':
             data['file'] = str(input.get('name'))
    for input in soup.findChildren({'input'},{'type': 'submit'}):
        if input.get('type').lower() == 'submit':
            if input.has_attr('name'):
                data[str(input.get('name'))] = str(input.get('value'))
            else:
                data['submit'] = str(input.get('value'))
    
    info_form = {}
    info_form['method'] = str(info_form.get('method',''))
    info_form['action'] = str(info_form.get('action',''))
    info_form['data'] = data
    return info_form
 

def get_content_upload_success(session, url, files, data_form):
    if files:
        file_name = basename(files)
        print file_name
        files = {data_form['data']['file']:open(files, 'rb')}
        if data_form['method'].lower() == 'post':
            print url
            req = session.post(url, files=files, data=data_form['data'], cookies=cookies)
            content = req.content.replace(file_name, 'nguyenhainam_test_file_upload')
            return content
            
        elif data_form['method'].lower() == 'get':
            req = session.get(url, files=files, params=data_form['data'], cookies=cookies)
            content = req.content.replace(file_name, 'nguyenhainam_test_file_upload')
            return content
    return

def scan_file_upload(session, url, list_href):
    file_upload_vul = {'url': {'list':[], 'level': ''
                },
                'form': {'list': [], 'level': ''
                }
            }
    for href in list_href:
        flag_level = 0
        for level in ['high', 'medium', 'low']:
            
            upload_normal = payload_file_upload[level]['payload']['upload_normal']
            upload_shell = payload_file_upload[level]['payload']['upload_shell']
            upload_large_mb = payload_file_upload[level]['payload']['upload_large_mb']

            req = session.get(href, cookies=cookies)
            soup = BeautifulSoup(req.content,'html.parser')
            form = soup.find('form')
            if form:
                if form.get('enctype', '') == 'multipart/form-data':
                    print level
                    data_form = get_info_form(soup)
                    data_form['method'] = str(form.get('method'))
                    print data_form
                    content_upload_success = get_content_upload_success(session, href, upload_normal, data_form)
                    content_upload_shell = get_content_upload_success(session, href, upload_normal, data_form)
                    content_upload_large_mb = get_content_upload_success(session, href, upload_normal, data_form)
                    if content_upload_success and content_upload_shell and content_upload_large_mb:
                        if content_upload_success.lower() == content_upload_shell.lower():
                            print 'shell'
                            print level
                            if convert_tag(form) not in file_upload_vul['form']['list']:
                                file_upload_vul['form']['list'].append(convert_tag(form))
                                file_upload_vul['url']['list'].append(href)
                                
                                if len(file_upload_vul['form']['list']) > 0:
                                    file_upload_vul['form']['level'] = level
                                flag_level = 1
                        if content_upload_success.lower() == content_upload_large_mb.lower():
                            print 'large mb'
                            print level
                            if convert_tag(form) not in file_upload_vul['form']['list']:
                                file_upload_vul['form']['list'].append(convert_tag(form))

                                if len(file_upload_vul['form']['list']) > 0:
                                    file_upload_vul['form']['level'] = level
                                flag_level = 1

            if flag_level == 1:
                break
    file_upload_vul['total_vul'] = len(file_upload_vul['url']['list']) +\
                                    len(file_upload_vul['form']['list']) 
    return file_upload_vul
