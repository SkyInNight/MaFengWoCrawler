# -*- coding: utf-8 -*-
import queue
import socket
import time
import json
import requests
from requests import exceptions
import configparser

cf = configparser.ConfigParser()
cf.read("../config/config.conf")


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
    """
    { code: "0", msg: "ok", obj: [ { port: "28635", ip: "113.94.123.104" }, { port: "40782", ip: "36.22.79.124" }, { port: "42269", ip: "117.69.151.229" } ], errno: 0, data: [ null ] }
    url = '
    """

    def __init__(self, max_size):
        self.__max_size = max_size
        self.__ip_queue = queue.Queue(max_size)
        status = self.request_ip(max_size)
        if status == "wait":
            print("ip地址获取出错，请保存数据退出")
        elif status == "success":
            ip = self.__ip_queue.get()
            self.__ip_queue.put(ip)
            print("获取ip地址成功{0}".format(ip))

    def get_proxy(self):
        if self.__ip_queue.empty():
            status = self.request_ip(self.__max_size)
            if status == "wait":
                print("ip地址获取出错，请保存数据退出")
                return "error"
            elif status == "success":
                print("获取ip地址成功")
        ip_ = self.__ip_queue.get()
        if is_open(ip_['ip'], ip_['port']):
            proxy = {'http': ip_['ip'] + ":" + ip_['port']}
            self.__ip_queue.put(ip_)
            return proxy
        else:
            self.get_proxy()

    def request_ip(self, num):
        # 为了防止获取上一次的ip地址，这里强制在获取地址前先休眠1秒钟
        time.sleep(1)
        if num > 50 or num < 1:
            num = 10
        url = cf.get('proxy', 'url') + str(num)
        try:
            response = requests.get(url)
            if response.status_code == 112:
                time.sleep(1)
                self.request_ip(num)
            elif response.status_code == 108:
                print("订单已经用完，请充值")
                return "wait"
            elif response.status_code == 110:
                print("订单申请过于频繁，请等3分钟后重试")
                return "wait"
            response.raise_for_status()
            data = json.loads(response.text)
            message = data['msg']
            if message == "请求数量超过限制，请前往续费或者购买":
                print(message)
                return "wait"
            elif message == "超过并发限制":
                print(message)
                return "wait"
            ip_list = data['obj']
            for ip_ in ip_list:
                self.__ip_queue.put(ip_)
            return "success"
        except exceptions.HTTPError as e:
            print(e)
            return "wait"


if __name__ == '__main__':
    # print(cf.get('proxy', 'url'))
    ip_pool = ProxyPool(1)
    for i in range(0, 100):
        print(ip_pool.get_proxy())
    # ip = '117.81.190.56'
    # port = '40659'
    # print(is_open(ip, port))
