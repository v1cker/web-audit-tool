from bs4 import BeautifulSoup
import urllib
from urlparse import urlparse, urljoin
import re
import requests
import socket
import ssl

def get_href(session, url):
    list_href = []
    #
    # url = http://google.com
    #
    print ('get href')
    html_context = session.get(url)
    soup = BeautifulSoup(html_context.content,'html.parser')
    
    list_a = soup.find_all('a')
    parsed_url = urlparse(url)
    for a in list_a:
        href = a.get('href')
        
        url_a = urljoin(url, href)
        
        parsed_url_a = urlparse(url_a)
        #
        # neu dung dinh dang url va cung 1 hostname
        # insert vo list href
        #
        if bool(parsed_url_a.scheme) and \
            parsed_url.hostname == parsed_url_a.hostname and \
            str(url_a) not in list_href and \
            url_a != url and url_a != '':
                
            list_href.append(str(url_a))
            
            html_context_url_a = session.get(url_a)
            soup_url_a = BeautifulSoup(html_context_url_a.content,'html.parser')
            list_child_url_a = soup_url_a.find_all('a')
                        
            for child_a in list_child_url_a:
                href_child_a = child_a.get('href')
                url_child_a = urljoin(url, href_child_a)
                
                parsed_child_url_a = urlparse(url_child_a)
                
                if bool(parsed_child_url_a.scheme) and \
                    parsed_child_url_a.hostname == parsed_url_a.hostname and \
                    str(url_child_a) not in list_href and \
                    url_child_a != url and url_child_a != '':
                        
                        list_href.append(str(url_child_a))
                else:
                    
                    pass               
        else:
            
            pass
    return list_href
    

def find_data_login(session, url, user, password):
    form = {'action': '', 'data':{}}
    data = form.get('data')
    req = session.get(url)
    soup = BeautifulSoup(req.content,'html.parser')
    if soup.findChild('input',{'type':'password'}):
        form_action = soup.find('form')
        action = form_action.get('action', '')
        method = form_action.get('method', '')
        form['action'] = action
        form['method'] = method

        for input in soup.find_all('input'):
            if input.has_attr('name'):
                if input.get('type').lower() == 'submit':
                    if input.has_attr('name'):
                        data[str(input.get('name'))] = str(input.get('value'))
                    else:
                        data[str(input.get('name'))] = 'submit'
                elif input.get('type').lower() == 'password':
                    data[str(input.get('name'))] = password
                elif input.get('type').lower() == 'text' and input.get('value') == None:
                    data[str(input.get('name'))] = user
                else:
                    data[str(input.get('name'))] = str(input.get('value'))  
    return form
def bypass_login(session, url, cookies):
    user = 'admin'
    password = 'password'
    print cookies
    form = find_data_login(session=session, url=url, user=user, password=password)
    print form['data']
    try:
        if form['action'] and form['action'] != '#':
            url = url +'/'+form['action']
        if form.get('method').lower() == 'post':
            req = session.post(url, data=form['data'], cookies=cookies)
        elif form.get('method').lower() == 'get':
            req = session.get(url, params=form['data'], cookies=cookies)
        else:
            return 0
    except:
        return
    return
def check_login(session, url):
    req = session.get(url)
    soup = BeautifulSoup(req.content,'html.parser')
    if soup.findChild('input',{'type':'password'}):
        return True
    return False

def info_website(session, url):
    domain = get_hostname(url)
    host = get_host_by_name(domain)
    x_powered_url = ''
    server_url = ''
    try:
        req = session.get(url)
        server_url = req.headers.get('server', 'n/a')
        x_powered_url = req.headers.get('x-powered-by', 'n/a')
        
    except:
        server_url = 'n/a'
        

    info = {'total': 4, 'host': host, 'domain': domain, \
            'server_url': server_url, 'x_powered_url': x_powered_url}
    return info

def get_hostname(url):
    #hostname: localhost | dvwa.vn | 
    try:
        o = urlparse(url)
    except:
        o = 'n/a'
    return o.hostname

def get_scheme(url):
    # scheme : http | https
    try:
        o = urlparse(url)
    except:
        o = 'n/a'
    return o.scheme


def get_host_by_name(url):
    # host : 127.0.0.1
    try:
        host = socket.gethostbyname(url)
    except:
        host = 'n/a'
    return host