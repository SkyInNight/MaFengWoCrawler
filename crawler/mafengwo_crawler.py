# -*- coding: utf-8 -*-
import json
import time
from multiprocessing.pool import Pool

import requests
from fake_useragent import UserAgent

from html_parser.mafengwo_parser import ScenicInfoParser
from tools import scenic_tools, scenic_file_tools
from tools.proxy_pool import ProxyPool, ProxyManager
from tools.read_js import read_js, parse_js


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 当前程序上上一级目录
# sys.path.append(BASE_DIR)  # 添加环境变量


def crawler(url_, proxy_pool_=None, headers=None, data=None):
    proxy_ = None
    if proxy_pool_ is not None:
        if proxy_pool_.is_empty():
            return None
        proxy_ = proxy_pool_.get_proxy()
        # print(proxy)
    try:
        response = requests.get(
            url_,
            headers=headers,
            proxies=proxy_,
            params=data,
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
            return crawler(url_, proxy_pool_, headers, data)
        else:
            return None


def post_crawler(url_, proxy_pool_=None, headers=None, data=None):
    proxy_ = None
    if proxy_pool_ is not None:
        if proxy_pool_.is_empty():
            return None
        proxy_ = proxy_pool_.get_proxy()
        # print(proxy)
    try:
        response = requests.post(
            url_,
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
            return post_crawler(url_, proxy_pool_, headers)
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
    result = parser_.top_five_city_parser(response.text)
    for index_ in result:
        for key in index_.keys():
            if key != 'current_url_list':
                index_['city'] = city_name
                break
    return result


def all_scenic_crawler(city_, parser_, open_proxy=False, default_proxy=2):
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
            'User-Agent': ua.random,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.6",
            "Content-Length": "101",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        response = post_crawler(url, headers=headers, data=data)
        if response is None:
            with open('../data/error.log', 'a+', encoding='utf-8') as output:
                output.write('城市：{0}，页数{1}，下载失败'.format(city_id, index_) + '\n')
            continue
        html = json.loads(response.text)['data']['list']
        result = parser_.scenic_list_parser(html)
        for j in result:
            for key in j.keys():
                if key != 'current_url_list':
                    j['city'] = city_name
                    break
        scenic_list.append(result)
    scenic_list.append({'city': city_name})
    return scenic_list


def scenic_location_crawler(scenic_id):
    # 获取景点的地理位置。
    url_location = r'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi'
    ua = UserAgent()
    headers = {
        'Host': 'pagelet.mafengwo.cn',
        'Referer': 'http://www.mafengwo.cn/poi/' + scenic_id + '.html',
        "Connection": "keep-alive",
        'User-Agent': ua.random,
        "Accept": "*/*",
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
    }
    data = read_js({'_ts': str(int(time.time() * 1000)), 'params': '{"poi_id":"' + scenic_id + '"}'})
    response = crawler(url_location, headers=headers, data=data)
    result = json.loads(response.text)['data']['controller_data']['poi']
    location = {'北纬': result['lat'], '东经': result['lng']}
    return location


def scenic_summary_crawler(scenic_url, scenic_info_parser):
    while True:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.mafengwo.cn',
            'Referer': 'http://www.mafengwo.cn/jd/10466/gonglve.html',
            'Upgrade-Insecure-Requests': '1',
        }
        session = requests.session()
        response = session.get(scenic_url, headers=headers)
        # cookies = response.cookies
        # cookies = '; '.join(['='.join(item) for item in cookies.items()])
        if response.status_code == 521:
            cookie = parse_js(response.text)
            if cookie is None:
                continue
            session.cookies['__jsl_clearance'] = cookie.split('=')[1]
            # print(session.cookies)
            response = session.get(scenic_url, headers=headers)
            # print(response.status_code)
            return scenic_info_parser.summary_parser(response.text)


def scenic_img_crawler(scenic_id, scenic_info_parser):
    url = r'http://www.mafengwo.cn/mdd/ajax_photolist.php'
    data = {
        'act': 'getPoiPhotoList',
        'poiid': scenic_id,
        'page': '1'
    }
    ua = UserAgent()
    headers = {
        'Host': 'www.mafengwo.cn',
        'Referer': r'http://www.mafengwo.cn/photo/poi/' + scenic_id + '.html',
        'User-Agent': ua.random
    }
    response = requests.get(url, headers=headers, params=data)
    return scenic_info_parser.photo_parser(response.text)


def scenic_info_crawler(scenic, scenic_info_parser, time=0):
    print('正在获取景点：{0}的信息'.format(scenic['title']))
    scenic_id = scenic_tools.get_scenic_info(scenic['href'])
    try:
        scenic['location'] = scenic_location_crawler(scenic_id)
        scenic['summary'] = scenic_summary_crawler(scenic['href'], scenic_info_parser)
        scenic['photos'] = scenic_img_crawler(scenic_id, scenic_info_parser)
        scenic['inside_scenic'] = inside_scenic_crawler(scenic_id, scenic_info_parser)
        return scenic
    except Exception as e:
        print(e)
        if time > 30:
            return scenic
        scenic_info_crawler(scenic, scenic_info_parser, time + 1)


def inside_scenic_crawler(scenic_id, scenic_info_parser):
    url = r'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi'
    ua = UserAgent()
    headers = {
        'Host': 'pagelet.mafengwo.cn',
        'Referer': r'http://www.mafengwo.cn/poi/' + scenic_id + '.html',
        'User-Agent': ua.random
    }
    page_num = 1
    insider_scenic_list = []
    while True:
        data = read_js({'_ts': str(int(time.time() * 1000)),
                        'params': '{"poi_id":"' + scenic_id + '", "page":' + str(page_num) + '}'})
        page_num += 1
        response = crawler(url, headers=headers, data=data)
        html = json.loads(response.text)['data']['html']
        if html == "":
            break
        scenic_list = scenic_info_parser.inside_scenic_parser(html)
        for scenic in scenic_list:
            insider_scenic_list.append(scenic)
    return insider_scenic_list


def city_scenic_crawler(city_, scenic_info_parser, top_scenic_list, all_scenic_list):
    city_ = scenic_tools.get_city_info(city_)
    # scenic_list = scenic_tools.get_scenic_url(city_['city_name'])
    scenic_list = scenic_tools.combine_scenic_url(top_scenic_list, all_scenic_list)
    scenic_info_list = scenic_list['scenic_list']
    for index_ in range(0, len(scenic_info_list)):
        scenic_info_list[index_] = scenic_info_crawler(scenic_info_list[index_], scenic_info_parser)
    return {'scenic_info_list': scenic_info_list, 'city': city_['city_name']}


def fault_scenic_download(city_name, scenic_info_parser):
    print('正在下载城市{0}的景点'.format(city_name))
    with open('../data/fault_download/' + city_name + '.json', 'r', encoding='utf-8') as f:
        scenic_list = json.loads(f.read())
    for index_ in range(0, len(scenic_list)):
        scenic_list[index_] = scenic_info_crawler(scenic_list[index_], scenic_info_parser)
    output = {'city_name': city_name, 'scenic_list': scenic_list}
    return output


def fault_download_callback(arg):
    city_ = arg['city_name']
    with open('../data/fault_download/' + city_ + '_success.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(arg['scenic_list']))


def get_city_scenic(city_, scenic_info_parser):
    print('正在爬取当前城市{0}的top five景点'.format(city_))
    top_scenic_list = top_five_city_crawler(city_, scenic_info_parser)
    print('正在爬取当前城市{0}的全部景点'.format(city_))
    all_scenic_list = all_scenic_crawler(city_, scenic_info_parser)
    result = city_scenic_crawler(city_, scenic_info_parser, top_scenic_list, all_scenic_list)
    return result


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
    city_parser = ScenicInfoParser()
    for city in city_list:
        get_city_scenic(city, city_parser)
    """
    url = r'http://www.mafengwo.cn/poi/321.html?type=3'
    print(json.dumps(city_scenic_crawler(city_list[0])))
    """

    # proxy_list = []
    """
    # proxy_manager = ProxyManager(proxy_list)
    for index in city_list:
        # proxy_pool = ProxyPool(1)
        print(top_five_city_crawler(index, city_parser))
    """
    """ 多进程获取，获取top5和热门景点
    # proxy = ProxyPool(70)
    pool = Pool(processes=14)
    for city in city_list:
        for key in city.keys():
            city_name = key
        # scenic_info_callback(city_scenic_crawler(city, city_parser))
        pool.apply_async(
            func=get_city_scenic,
            args=(city, city_parser),
            callback=scenic_file_tools.scenic_info_callback)
    pool.close()
    pool.join()
    """
