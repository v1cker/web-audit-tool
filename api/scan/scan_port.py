import socket
import nmap

from util import get_host_by_name, get_hostname

list_port_secure = [80, 8080, 25565, 3306, 27017, 1433, 5432, 1521, 587, \
                    22, 21, 990, 443, 110, 995, 143, 995, 25, 465, 9042]

def scan_port(session, name, url):
    hostname = get_hostname(url)
    host = get_host_by_name(hostname)
    nm = nmap.PortScanner()
    ports_scan = nm.scan(host, '1-1000') # 1-65535

    host_port_secure = []
    host_port_insecure = []
    ports = ports_scan['scan'][host]['tcp']

    for port in ports:
        print port
        if port in list_port_secure:
            host_port_secure.append({'port': port, 'name': ports[port]['name']})
        else:
            host_port_insecure.append({'port': port, 'name': ports[port]['name']})

    list_port = {'info':{'total_secure': len(host_port_secure), 'total_insecure': len(host_port_insecure), 'host': host},\
                'detail':{'secure': host_port_secure, 'insecure': host_port_insecure},\
                'level': {'insecure': 'low'}
                }

    return list_port