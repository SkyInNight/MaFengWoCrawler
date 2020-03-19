# -*- coding: utf-8 -*-
import configparser

import requests
import json

from tools.proxy_pool import ProxyManager


def test_proxy():
    proxy_list = [
            {'port': '23640', 'ip': '120.9.140.19'}, {
                'port': '18803', 'ip': '117.69.153.100'}, {
                    'port': '32777', 'ip': '113.85.46.139'}, {
                        'port': '20156', 'ip': '58.253.11.130'}, {
                            'port': '46042', 'ip': '171.8.10.129'}]
    proxy_manager = ProxyManager(proxy_list)
    try:
        response = requests.get(
            "http://konachan.com/post", proxies=proxy_manager.get_proxy(), timeout=5)
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
    for i in range(1, 10):
        test_proxy()
    # test_conf()
