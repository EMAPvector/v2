#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import uuid
import random
import re



#获取ip
f = os.popen('ip addr')
ip_txt = f.read()
f.close()

p = re.compile(r'\binet (?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

all_ip = p.findall(ip_txt)

ips = []
for sour_ip in all_ip:
    if 'inet 127.0.0.1' != sour_ip:
        ips.append(sour_ip.replace('inet ',''))

print('要配置的ip：' + str(ips))

# service_location = '/etc/systemd/system/'
service_location = '/etc/systemd/system/'

f = open("config.jsonc", "r")
templet = f.read()
f.close()

f = open(service_location + "v2ray.service", "r")
service_templet = f.read()
f.close()

for ip in ips:
    ip_short = ip.split('.')[3]
    port = str(random.randint(5000,6000))
    alterId = str(random.randint(5,60))
    uuid_s = str(uuid.uuid1())
    config = templet.replace('{{ip}}',ip)
    print('IP: '+ip)
    config = config.replace('{{port}}',port)
    print('port: '+port)
    config = config.replace('{{uuid}}',uuid_s)
    print('uuid: '+uuid_s)
    config = config.replace('{{alterId}}',alterId)
    print('alterId: '+alterId)

    config_name = 'config_' + ip_short + '.json'
    config_f = open(config_name, "w")
    config_f.write(config)
    config_f.close()

    service_name = 'config_' + ip_short + '.json'
    service_path = service_location + 'vpn' + ip_short + '.service'
    service_f = open(service_path, "w")
    service_f.write(service_templet.replace('config.json',service_name))
    service_f.close()

    os.system('firewall-cmd --permanent --add-port=' + port + '/tcp')
    os.system('firewall-cmd --permanent --add-port=' + port + '/udp')
    os.system('systemctl start vpn' + ip_short)

    print('=====================================')

os.system('firewall-cmd --reload')