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
        if proxy_pool_.is_empty():
            return None
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
        if proxy_pool_ is not None:
            proxy_pool_.drop_current_ip()
            return crawler(url, proxy_pool_, headers)
        else:
            return None


def city_crawler(city_,parser_):
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
    # proxy_manager_ = None
    # if proxy_pool_ is not None:
    proxy_pool_ = ProxyPool(2)
    proxy_manager_ = ProxyManager(proxy_pool_.get_ip_list(2))
    # try:
    response = crawler(url, proxy_manager_, headers)
    result = parser_.parser(response.text)
    for index_ in result:
        for key in index_.keys():
            if key != 'current_url_list':
                index_['city'] = city_name
                break
    return result


def callbacks(arg):
    file_name = ""
    for index_ in arg:
        file_name = index_['city']
        break
    with open('../data/' + file_name + '.json', 'a+', encoding="utf-8") as output:
        for index_ in arg:
            output.write(json.dumps(index_) + '\n')


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
    city_parser = CityParser()
    # proxy_list = []

    """
    """
    # proxy_manager = ProxyManager(proxy_list)
    # for index in city_list:
    #     # proxy_pool = ProxyPool(1)
    #     print(city_crawler(index, proxy_manager))

    """ 获取top5和热门景点
        """
    # proxy = ProxyPool(70)
    pool = Pool(processes=5)
    for index in range(0, 2):
        city = city_list[index]
        # for city in city_list:
        # proxy_pool = ProxyPool(1)
        # proxy_pool = None
        # list_ = []
        # for i in range(0, 6):
        #     list_.append(proxy_list.pop())
        # print(list_)
        # proxy_manager = ProxyManager(list_)
        pool.apply_async(
            func=city_crawler,
            args=(city, city_parser),
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
