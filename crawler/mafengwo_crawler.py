# -*- coding: utf-8 -*-
from html_parser.mafengwo_parser import CityParser
import queue
import json
import time
from fake_useragent import UserAgent
from multiprocessing import Process, Pool, freeze_support
from tools.proxy_pool import ProxyPool
import requests


def crawler(url, proxy_pool_=None, headers=None):
    proxy = None
    if proxy_pool_ is not None:
        proxy = proxy_pool_.get_proxy()
    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxy,
            timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response
    except Exception as e:
        print(e)
        proxy_pool_.drop_current_ip()
        return crawler(url, proxy_pool_, headers)


def city_crawler(city_, open_proxy_=0):
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
    proxy_pool_ = None
    if open_proxy_ > 0:
        proxy_pool_ = ProxyPool(open_proxy_)
    response = crawler(url, proxy_pool_, headers)
    city_parser = CityParser()
    result = city_parser.parser(response.text)
    for index_ in result:
        for key in index_.keys():
            if key != 'current_url_list':
                index_['city'] = city_name
                break
    return result
    # except requests.exceptions.HTTPError as e:
    #     print(e)
    #     proxy_pool.drop_current_ip()
    #     city_crawler(city_, proxy_pool_)
    # except requests.exceptions.ReadTimeout as e:
    #     print(e)
    #     proxy_pool.drop_current_ip()
    #     city_crawler(city_, proxy_pool_)
    # except Exception as e:
    #     print(e)
    #     proxy_pool.drop_current_ip()
    #     city_crawler(city_, proxy_pool_)


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
    """
        
    for index in city_list:
        # proxy_pool = ProxyPool(1)
        print(city_crawler(index, 1))

    """
    """ 获取top5和热门景点
    """
    pool = Pool(processes=14)
    for city in city_list:
        # proxy_pool = ProxyPool(1)
        # proxy_pool = None
        open_proxy = 1
        pool.apply_async(
            func=city_crawler,
            args=(
                city,
                open_proxy),
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


_ts: 1583856197164
_sn: d9b5b2a2d4

sAct: KMdd_StructWebAjax|GetPoisByTag
iMddid: 10466
iTagId: 0
iPage: 1
_ts: 1583856069548
_sn: 21454efe08

sAct: KMdd_StructWebAjax|GetPoisByTag
iMddid: 10267
iTagId: 0
iPage: 1
_ts: 1583852948325
_sn: 2253754add
    """
