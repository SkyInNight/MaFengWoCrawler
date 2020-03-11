# -*- coding: utf-8 -*-
from html_parser.mafengwo_parser import CityParser
import queue
import json
import time
from fake_useragent import UserAgent
from multiprocessing import Process, Pool, freeze_support
from tools.proxy_pool import ProxyPool
import requests


def city_crawler(city_, proxy_pool_=None):
    city_id = ""
    city_name = ""
    for index in city_.keys():
        city_name = index
        city_id = city_[index]
    url = r'http://www.mafengwo.cn/jd/' + city_id + r'/gonglve.html'
    ua = UserAgent()
    headers = {
        "Origin": url,
        'User-Agent': ua.random,
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "text/html; charset=utf-8",
    }
    try:
        proxy = None
        if proxy_pool_ is not None:
            proxy = proxy_pool_.get_proxy()
        response = requests.get(
            url,
            headers=headers,
            proxies=proxy,
            timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        city_parser = CityParser()
        result = city_parser.parser(response.text)
        for index in result:
            for key in index.keys():
                if key != 'current_url_list':
                    index['city'] = city_name
                    break
        return result
    except requests.exceptions.HTTPError as e:
        print(e)
        return "HTTPError"


def callbacks(arg):
    file_name = ""
    for index in arg:
        file_name = index['city']
        break
    with open('../data/' + file_name + '.json', 'a+', encoding="utf-8") as output:
        for index in arg:
            output.write(json.dumps(index) + '\n')


def post_request(city_id, proxy_pool=None, page_num=None):
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
        "Cookie": r'mfw_uuid=5e192805-c454-2e52-c102-7ffb02526b95; _r=baidu; '
                  r'_rp=a%3A2%3A%7Bs%3A1%3A%22p%22%3Bs%3A18%3A%22www.baidu.com%2Flink%22%3Bs%3A1%3A%22t%22%3Bi'
                  r'%3A1578706949%3B%7D; '
                  r'UM_distinctid=16f9244592e538-052da684b576f-7e657564-144000-16f9244592f80f; '
                  r'uva=s%3A366%3A%22a%3A4%3A%7Bs%3A13%3A%22host_pre_time%22%3Bs%3A10%3A%222020-01-11%22%3Bs%3A2'
                  r'%3A%22lt%22%3Bi%3A1578706950%3Bs%3A10%3A%22last_refer%22%3Bs%3A239%3A%22https%3A%2F%2Fwww'
                  r'.baidu.com%2Flink%3Furl%3DkK7RaPV9EJhX0fspPeKz3vYnAV4N38eI5-ng4CD5sXKb'
                  r'-DdciijTyKeuwm7pfurFGFjX4jLoVRFXCkpIcWoqMLIVfonZsiPl2sYyPit2fzy%26ck%3D4525.9.82.427.586.365'
                  r'.330.1%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26eqid%3Dfbe44466001f45b9000000065e1927e9'
                  r'%22%3Bs%3A5%3A%22rhost%22%3Bs%3A13%3A%22www.baidu.com%22%3B%7D%22%3B; '
                  r'__mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1578706950%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A13'
                  r'%3A%22www.baidu.com%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; '
                  r'__mfwuuid=5e192805-c454-2e52-c102-7ffb02526b95; __mfwc=direct; '
                  r'__jsluid_h=caccec0dce5b950ba7baa82954bf198e; __omc_chl=; __omc_r=; '
                  r'oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo'
                  r'.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222020-03-04+21%3A14%3A42%22%3B%7D; '
                  r'PHPSESSID=emslnfbif7c2fr3djtjbl70bt3; Hm_lvt_8288b2ed37e5bc9b4c9f7008798d2de0=1583657294,'
                  r'1583720769,1583760286,1583831883; __mfwlv=1583850835; __mfwvn=10; '
                  r'Hm_lpvt_8288b2ed37e5bc9b4c9f7008798d2de0=1583852948; '
                  r'CNZZDATA30065558=cnzz_eid%3D1067883239-1578703684-https%253A%252F%252Fwww.baidu.com%252F'
                  r'%26ntime%3D1583851556; __mfwb=3bffc37bc2af.1.direct; '
                  r'__mfwa=1578706950191.28777.14.1583852948261.1583856069490; __mfwlt=1583856069',
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
        if proxy_pool is not None:
            ip = proxy_pool.get_ip()
            proxy = {'http': ip['ip'] + ":" + ip['port']}
            response = requests.post(
                url, headers=headers, data=data, proxies=proxy, timeout=5)
            print("网页响应码为：{0}".format(response.status_code))
            response.raise_for_status()
            proxy_pool.put_current_ip()
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
    # proxy_pool = ProxyPool(1)
    # callbacks(city_crawler(city_list[0], proxy_pool))

    pool = Pool(processes=14)
    for city in city_list:
        # proxy_pool = ProxyPool(1)
        proxy_pool = None
        pool.apply_async(
            func=city_crawler,
            args=(
                city,
                proxy_pool),
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
