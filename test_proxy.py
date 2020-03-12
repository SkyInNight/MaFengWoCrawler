# -*- coding: utf-8 -*-
import configparser

import requests
import json


def test_proxy():
    proxy_list = [
        {'http': '163.179.206.102:48585'},
        {'http': '113.65.232.120:43052'},
        {'http': '39.72.145.0:45905'},
        {'http': '36.6.241.115:45398'},
        {'http': '180.114.196.24:44003'},
        {'http': '121.8.28.30:36863'},
        {'http': '119.114.77.53:42985'},
        {'http': '121.230.226.77:43417'},
        {'http': '106.9.169.149:47435'}
    ]
    try:
        response = requests.get(
            "http://www.baidu.com", proxies=proxy_list[3], timeout=5)
        response.raise_for_status()
        print(response.status_code)
    except requests.exceptions.HTTPError as e:
        print(e)
    except Exception as e:
        print(e)


def test_conf():
    cf = configparser.ConfigParser()
    cf.read("config\\config.conf")
    url_list = json.loads(cf.get('proxy', 'url'))
    for url in url_list:
        print(url)


if __name__ == '__main__':
    # for i in range(1, 1000):
    #     test_proxy()
    test_conf()
