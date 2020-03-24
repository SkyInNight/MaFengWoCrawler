# -*- coding: utf-8 -*-
import queue
import os
import sys
import json
import time
from fake_useragent import UserAgent
from multiprocessing import Process, Pool, freeze_support
import requests
from html_parser.mafengwo_parser import TopFiveCityParser, AllScenicParser
from tools.proxy_pool import ProxyPool, ProxyManager
from tools.read_js import read_js


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


def post_crawler(url, proxy_pool_=None, headers=None, data=None):
    proxy_ = None
    if proxy_pool_ is not None:
        if proxy_pool_.is_empty():
            return None
        proxy_ = proxy_pool_.get_proxy()
        # print(proxy)
    try:
        response = requests.post(
            url,
            headers=headers,
            proxies=proxy_,
            data=data,
            timeout=3)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        return response
    except Exception as e:
        print(e)
        if proxy_pool_ is not None:
            proxy_pool_.drop_current_ip()
            return post_crawler(url, proxy_pool_, headers)
        else:
            return None


def top_five_city_crawler(city_, parser_, open_proxy=False, default_proxy=2):
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
    proxy_manager_ = None
    if open_proxy:
        proxy_pool_ = ProxyPool(default_proxy)
        proxy_manager_ = ProxyManager(proxy_pool_.get_ip_list(default_proxy))
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
    current_url_list = []
    with open('../data/' + file_name + '.json', 'w', encoding="utf-8") as output:
        scenic_info_list = []
        for index_ in range(len(arg)):
            """
            if index_ == len(arg) - 1:
                current_url_list = arg[index_]['current_url_list']
                break
            """
            scenic_info_list.append(arg[index_])
        output.write(json.dumps(scenic_info_list) + '\n')
    # with open('../data/exist_url.json', 'a+', encoding='utf-8') as output:
    #     output.write(json.dumps(current_url_list))


def all_scenic_crawler(city_, parser_ ,open_proxy=False, default_proxy=2):
    city_id = ""
    city_name = ""
    for index_ in city_.keys():
        city_name = index_
        city_id = city_[index_]
    url = r'http://www.mafengwo.cn/ajax/router.php'
    scenic_list = []
    for index_ in range(1, 21):
        data = {
            'sAct': 'KMdd_StructWebAjax|GetPoisByTag',
            'iMddid': city_id,
            'iTagId': 0,
            'iPage': index_,
            "_ts": int(time.time() * 1000)
        }
        data = read_js(data)
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
            # "Accept-Encoding": "gzip, deflate"
        }
        response = post_crawler(url, headers=headers, data=data)
        if response is None:
            with open('../data/error.log', 'a+', encoding='utf-8') as output:
                output.write('城市：{0}，页数{1}，下载失败'.format(city_id, index_) + '\n')
            continue
        html = json.loads(response.text)['data']['list']
        result = parser_.parser(html)
        for j in result:
            for key in j.keys():
                if key != 'current_url_list':
                    j['city'] = city_name
                    break
        scenic_list.append(result)
    scenic_list.append({'city': city_name})
    return scenic_list


def scenic_callback(arg):
    city_name = arg[len(arg) - 1]['city']
    with open('../data/all/' + city_name + '.json', 'a+', encoding='utf-8') as output:
        output.write(json.dumps(arg) + "\n")


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
    city_parser = AllScenicParser()
    # proxy_list = []
    """
    # proxy_manager = ProxyManager(proxy_list)
    for index in city_list:
        # proxy_pool = ProxyPool(1)
        print(top_five_city_crawler(index, city_parser))
    """
    # """ 多进程获取，获取top5和热门景点
    # proxy = ProxyPool(70)
    pool = Pool(processes=14)
    for city in city_list:
        pool.apply_async(
            func=all_scenic_crawler,
            args=(city,city_parser),
            callback=scenic_callback)
    pool.close()
    pool.join()
    # """
