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

while True:
    ip_confim = input('要配置的ip：' + str(ips) + ' 如果不对请手动输入，以逗号分割ip\n')

    if '.' in ip_confim:
        ips = ip_confim.split(',')
    else:
        break

# service_location = '/etc/systemd/system/'
service_location = '/etc/systemd/system/'
config_location = '/usr/local/etc/v2ray/'

templet = '''{
	"log": {
		"access": "/var/log/v2ray/access.log",
		"error": "/var/log/v2ray/error.log",
		"loglevel": "error"
	},
	"inbounds": [
		{
            "port": {{port}},
            "listen": "{{ip}}",
			"protocol": "vmess",
			"settings": {
				"clients": [
					{
						"id": "{{uuid}}",
						"level": 1,
						"alterId": {{alterId}}
					}
				]
			},
			"streamSettings": {
				"network": "tcp"
			},
			"sniffing": {
				"enabled": true,
				"destOverride": [
					"http",
					"tls"
				]
			}
		}
		//include_ss
		//include_socks
		//include_mtproto
		//include_in_config
		//
	],
	"outbounds": [
		{
            "sendThrough": "{{ip}}",
			"protocol": "freedom",
			"settings": {
				"domainStrategy": "UseIP"
			},
			"tag": "direct"
		},
		{
			"protocol": "blackhole",
			"settings": {},
			"tag": "blocked"
        },
		{
			"protocol": "mtproto",
			"settings": {},
			"tag": "tg-out"
		}
		//include_out_config
		//
	],
	"dns": {
		"servers": [
			"https+local://cloudflare-dns.com/dns-query",
			"1.1.1.1",
			"1.0.0.1",
			"8.8.8.8",
			"8.8.4.4",
			"localhost"
		]
	},
	"routing": {
		"domainStrategy": "IPOnDemand",	
		"rules": [
			{
				"type": "field",
				"ip": [
					"0.0.0.0/8",
					"10.0.0.0/8",
					"100.64.0.0/10",
					"127.0.0.0/8",
					"169.254.0.0/16",
					"172.16.0.0/12",
					"192.0.0.0/24",
					"192.0.2.0/24",
					"192.168.0.0/16",
					"198.18.0.0/15",
					"198.51.100.0/24",
					"203.0.113.0/24",
					"::1/128",
					"fc00::/7",
					"fe80::/10"
				],
				"outboundTag": "blocked"
			},
			{
				"type": "field",
				"inboundTag": ["tg-in"],
				"outboundTag": "tg-out"
			}
			,
			{
				"type": "field",
				"domain": [
					"domain:epochtimes.com",
					"domain:epochtimes.com.tw",
					"domain:epochtimes.fr",
					"domain:epochtimes.de",
					"domain:epochtimes.jp",
					"domain:epochtimes.ru",
					"domain:epochtimes.co.il",
					"domain:epochtimes.co.kr",
					"domain:epochtimes-romania.com",
					"domain:erabaru.net",
					"domain:lagranepoca.com",
					"domain:theepochtimes.com",
					"domain:ntdtv.com",
					"domain:ntd.tv",
					"domain:ntdtv-dc.com",
					"domain:ntdtv.com.tw",
					"domain:minghui.org",
					"domain:renminbao.com",
					"domain:dafahao.com",
					"domain:dongtaiwang.com",
					"domain:falundafa.org",
					"domain:wujieliulan.com",
					"domain:ninecommentaries.com",
					"domain:shenyun.com"
				],
				"outboundTag": "blocked"
			}			,
                {
                    "type": "field",
                    "protocol": [
                        "bittorrent"
                    ],
                    "outboundTag": "blocked"
                }
			//include_ban_ad
			//include_rules
			//
		]
	},
	"transport": {
		"kcpSettings": {
            "uplinkCapacity": 100,
            "downlinkCapacity": 100,
            "congestion": true
        }
    }
}'''

f = open(service_location + "v2ray.service", "r")
service_templet = '''[Unit]
Description=V2Ray Service
Documentation=https://www.v2fly.org/
After=network.target nss-lookup.target

[Service]
User=nobody
CapabilityBoundingSet=~
AmbientCapabilities=
NoNewPrivileges=true
ExecStart=/usr/local/bin/v2ray -config /usr/local/etc/v2ray/config.json
Restart=on-failure
RestartPreventExitStatus=23

[Install]
WantedBy=multi-user.target'''

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
    config_f = open(config_location + config_name, "w")
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
