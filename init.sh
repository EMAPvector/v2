#!/bin/bash

if [ ! -d "/etc/v2ray/hwx" ]; then
  mkdir /etc/v2ray/hwx
fi
rm -rf /etc/v2ray/hwx/*

cat >/etc/v2ray/hwx/00config.json <<-EOF
{
  "log": {
    "access": "none",
    "error": "/var/log/v2ray/error.log",
    "loglevel": "error"
  },
  "dns": {
    "servers": [
      "https+local://dns.google/dns-query",
      "8.8.8.8",
      "1.1.1.1",
      "localhost"
    ]
  },
  "outbounds": [
    {
      "protocol": "blackhole",
      "settings": {
        "response": {
          "type": "http",
          "description": "禁止访问"
        }
      },
      "tag": "blocked"
    },
    {
      "settings": {},
      "protocol": "freedom"
    }
  ],
  "transport": {
    "kcpSettings": {
      "uplinkCapacity": 100,
      "downlinkCapacity": 100,
      "congestion": true
    }
  }
}
EOF

cat >/etc/v2ray/hwx/templete.json <<-EOF
{
  "inbounds": [
    {
        "listen": "tag-ip",
        "port": 8089,
        "streamSettings": {
            "network": "ws",
            "wsSettings":{
                "path": "/chat/tag-path"
            }
        },
        "settings": {
            "clients": [
                {
                    "id": "uuid",
                    "alterId": 64
                }
            ]
        },
        "tag":"tag-in",
        "protocol": "vmess"
    }
],
  "routing": {
    "rules": [
      {
        "inboundTag": ["tag-in"],
        "outboundTag": "tag-out",
        "type": "field"
      }
    ]
  },
  "outbounds": [
    {
        "sendThrough": "tag-ip",
        "protocol": "freedom",
        "settings": {
            "domainStrategy": "AsIs"
        },
        "tag": "tag-out"
    }
  ]
}
EOF

ips=$(ifconfig | grep -E 'inet [0-9]' | awk '{print $2}' | grep -v '127.0.0.1')
for ip in $ips
do
  uuid=$(cat /proc/sys/kernel/random/uuid)
  short_ip=$(echo $ip | awk -F. '{print $NF}')
  cp /etc/v2ray/hwx/templete.json /etc/v2ray/hwx/$short_ip.json

  sed -i "s/uuid/$uuid/" /etc/v2ray/hwx/$short_ip.json
  sed -i "s/tag-ip/$ip/" /etc/v2ray/hwx/$short_ip.json
  sed -i "s/tag-in/tag-in-$short_ip/" /etc/v2ray/hwx/$short_ip.json
  sed -i "s/tag-out/tag-out-$short_ip/" /etc/v2ray/hwx/$short_ip.json
  sed -i "s/tag-path/$short_ip/" /etc/v2ray/hwx/$short_ip.json
  cat >/etc/v2ray/hwx/vmess_qr.json <<-EOF
{
  "v": "2",
  "ps": "tag-ip",
  "add": "tag-ip",
  "port": "8089",
  "id": "uuid",
  "aid": "64",
  "net": "ws",
  "type": "none",
  "host": "tag-ip",
  "path": "/chat/tag-path",
  "tls": ""
}
EOF

  sed -i "s/tag-ip/$ip/" /etc/v2ray/hwx/vmess_qr.json
  sed -i "s/uuid/$uuid/" /etc/v2ray/hwx/vmess_qr.json
  sed -i "s/tag-path/$short_ip/" /etc/v2ray/hwx/vmess_qr.json
  echo "vmess://$(cat /etc/v2ray/hwx/vmess_qr.json | base64 -w 0)"

done

service v2ray stop
rm -f /etc/v2ray/hwx/templete.json
rm -f /etc/v2ray/hwx/vmess_qr.json

sed -i "s#-config /etc/v2ray/config.json#-d /etc/v2ray/hwx#" /usr/lib/systemd/system/v2ray.service

systemctl daemon-reload
service v2ray start