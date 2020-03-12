# -*- coding: utf-8 -*-
import queue
import socket
import time
import json
import requests
import configparser


def is_open(ip_, port_):
    """
    检测端口是否打开
    :param ip_:
    :param port_:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip_, int(port_)))
        s.shutdown(1)
        return True
    except BaseException:
        return False


class ProxyPool(object):

    def __init__(self, max_size=50):
        self.__cf = configparser.ConfigParser()
        self.__cf.read("..\\config\\config.conf")
        if max_size < 1 or max_size > 200:
            max_size = 50
        self.__max_size = max_size
        self.__ip_queue = queue.Queue(max_size)
        self.__current_ip = None

    @property
    def ip_queue(self):
        if self.__ip_queue.empty():
            result = self.allocate_proxy(self.__max_size)
            if result == "wait":
                return None
        return self.__ip_queue

    def allocate_proxy(self, num_):
        url_list = json.loads(self.__cf.get('proxy', 'url'))
        if len(url_list) == 0:
            return "wait"
        # 单个api最多允许一次请求50条如果平均分摊超过最大上限，则自动降低要求。
        if num_ > len(url_list) * 50:
            num_ = len(url_list) * 30
        if num_ / len(url_list) == 0:
            return self.request_ip(url_list[0], num_)
        else:
            half = int(num_ / len(url_list))
            for url in url_list:
                print(url)
                result = self.request_ip(url, half)
                if result == "wait":
                    url_list.remove(url)
            if len(url_list) == 0:
                return "wait"
            return "success"

    def get_proxy(self):
        if self.__current_ip is not None:
            self.__ip_queue.put(self.__current_ip)
            self.__current_ip = None
        if self.__ip_queue.empty():
            status = self.allocate_proxy(self.__max_size)
            if status == "wait":
                print("ip地址获取出错，请保存数据退出")
                return "error"
            elif status == "success":
                print("获取ip地址成功")
        ip_ = self.__ip_queue.get()
        if is_open(ip_['ip'], ip_['port']):
            proxy = {'http': ip_['ip'] + ":" + ip_['port']}
            self.__current_ip = ip_
            return proxy
        else:
            return self.get_proxy()

    def drop_current_ip(self):
        self.__current_ip = None

    def request_ip(self, url, num, error_num=0):
        # 为了防止获取上一次的ip地址，这里强制在获取地址前先休眠1秒钟
        time.sleep(1)
        if num > self.__max_size or num < 1:
            num = self.__max_size
        url = url + str(num)
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = json.loads(response.text)
            message = data['msg']
            if message != "ok":
                print(message)
                return "wait"
            ip_list = data['obj']
            for ip_ in ip_list:
                self.__ip_queue.put(ip_)
            return "success"
        except Exception as e:
            print(e)
            if error_num < 3:
                error_num += 1
                return self.request_ip(num, error_num)
            else:
                return "wait"


if __name__ == '__main__':
    # print(cf.get('proxy', 'url'))
    ip_pool = ProxyPool(10)
    for i in range(0, 100):
        print(ip_pool.get_proxy())
    # ip = '117.81.190.56'
    # port = '40659'
    # print(is_open(ip, port))
