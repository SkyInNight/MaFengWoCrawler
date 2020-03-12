# -*- coding: utf-8 -*-
import queue
import os
import sys
import json
import time
from fake_useragent import UserAgent
from multiprocessing import Process, Pool, freeze_support
import requests
from html_parser.mafengwo_parser import CityParser
from tools.proxy_pool import ProxyPool, ProxyManager


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 当前程序上上一级目录
# sys.path.append(BASE_DIR)  # 添加环境变量


def crawler(url, proxy_pool_=None, headers=None):
    proxy_ = None
    if proxy_pool_ is not None:
        proxy_ = proxy_pool_.get_proxy()
        # print(proxy)
    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxy_,
            timeout=3)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        return response
    except Exception as e:
        print(e)
        # if proxy is not None:
        #     print(proxy)
        proxy_pool_.drop_current_ip()
        return crawler(url, proxy_pool_, headers)


def city_crawler(city_, proxy_manager_=None):
    city_id = ""
    city_name = ""
    for index_ in city_.keys():
        city_name = index_
        city_id = city_[index_]
    url = r'http://www.mafengwo.cn/jd/' + city_id + r'/gonglve.html'
    ua = UserAgent()
    headers = {
        "Origin": url,
        'User-Agent': ua.random,
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "text/html; charset=utf-8",
    }
    # try:
    response = crawler(url, proxy_manager_, headers)
    city_parser = CityParser()
    result = city_parser.parser(response.text)
    for index_ in result:
        for key in index_.keys():
            if key != 'current_url_list':
                index_['city'] = city_name
                break
    return result


def callbacks(arg):
    file_name = ""
    for index in arg:
        file_name = index['city']
        break
    with open('../data/' + file_name + '.json', 'a+', encoding="utf-8") as output:
        for index in arg:
            output.write(json.dumps(index) + '\n')


def senic_crawler(city_, proxy_pool_=None):
    pass


def post_request(city_id, proxy_pool_=None, page_num=None):
    url = r'http://www.mafengwo.cn/ajax/router.php'
    data = {
        'sAct': 'KMdd_StructWebAjax|GetPoisByTag',
        'iMddid': city_id,
        'iTagId': 0,
        'iPage': page_num,
        "_ts": str(int(time.time()))
    }
    ua = UserAgent()
    headers = {
        "Host": "www.mafengwo.cn",
        "Origin": "http://www.mafengwo.cn",
        "Connection": "keep-alive",
        "Referer": "http://www.mafengwo.cn/jd/" + city_id + "/gonglve.html",
        # "Origin":url,
        'User-Agent': ua.random,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.6",
        "Content-Length": "101",
        # "Accept-Encoding":"gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Encoding": "gzip, deflate"
    }
    try:
        if page_num is None:
            data['iPage'] = 1
        if proxy_pool_ is not None:
            ip = proxy_pool_.get_ip()
            proxy = {'http': ip['ip'] + ":" + ip['port']}
            response = requests.post(
                url, headers=headers, data=data, proxies=proxy, timeout=5)
            print("网页响应码为：{0}".format(response.status_code))
            response.raise_for_status()
            proxy_pool_.put_current_ip()
        else:
            response = requests.post(
                url, headers=headers, data=data, timeout=1)
            response.raise_for_status()
        response.encoding = response.apparent_encoding
        return json.dumps(response.text)
    except requests.exceptions.HTTPError as e:
        print("网页响应错误：".format(e))


if __name__ == '__main__':
    # common : http://www.mafengwo.cn/jd/id/gonglve.html
    city_list = [
        {"长沙": r'10466'},
        {"株洲": r'21916'},
        {"湘潭": r"34888"},
        {"衡阳": r'10398'},
        {"邵阳": r'15540'},
        {"岳阳": r'14104'},
        {"常德": r'17070'},
        {"张家界": r'10267'},
        {"益阳": r'15393'},
        {"郴州": r'10792'},
        {"永州": r'22460'},
        {"怀化": r'23078'},
        {"娄底": r'17363'},
        {"湘西": r'13287'}
    ]
    proxy_list = [
        {
            'port': '24695', 'ip': '117.67.41.133'}, {
            'port': '24975', 'ip': '114.226.160.26'}, {
                'port': '42297', 'ip': '59.62.165.249'}, {
                    'port': '48623', 'ip': '58.253.13.231'}, {
                        'port': '33679', 'ip': '115.151.7.125'}, {
                            'port': '28240', 'ip': '113.117.39.25'}, {
                                'port': '26107', 'ip': '119.140.183.189'}, {
                                    'port': '14275', 'ip': '36.57.87.3'}, {
                                        'port': '15159', 'ip': '114.104.139.90'}, {
                                            'port': '47675', 'ip': '218.64.152.136'}, {
                                                'port': '46582', 'ip': '125.89.22.141'}, {
                                                    'port': '46635', 'ip': '223.214.171.254'}]

    """
    """
    # proxy_manager = ProxyManager(proxy_list)
    # for index in city_list:
    #     # proxy_pool = ProxyPool(1)
    #     print(city_crawler(index, proxy_manager))

    """ 获取top5和热门景点
        """
    # proxy = ProxyPool(70)
    pool = Pool(processes=2)
    for index in range(0, 2):
        city = city_list[index]
        # for city in city_list:
        # proxy_pool = ProxyPool(1)
        # proxy_pool = None
        list_ = []
        for i in range(0, 6):
            list_.append(proxy_list.pop())
        # print(list_)
        proxy_manager = ProxyManager(list_)
        pool.apply_async(
            func=city_crawler,
            args=(
                city,
                proxy_manager),
            callback=callbacks)
    pool.close()
    pool.join()

    """
    sAct: KMdd_StructWebAjax|GetPoisByTag
iMddid: 10466
iTagId: 0
iPage: 1
_ts: 1583850982764
_sn: e4ae66965c

sAct: KMdd_StructWebAjax|GetPoisByTag
iMddid: 10466
iTagId: 0
iPage: 1
_ts: 1583856069548
_sn: 21454efe08

    """
