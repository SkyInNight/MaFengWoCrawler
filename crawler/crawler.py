# -*- coding: utf-8 -*-
import requests


class CrawlerInterface:

    def set_request(
            self,
            url,
            params=None,
            data=None,
            headers=None,
            cookies=None):
        """

        :param cookies:
        :param headers: 自定义请求头
        :param url: 网页url
        :param params: url后附加的参数
        :param data: url中通过内部发送的数据

        :return:
        """
        request = requests.Request(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            data=data)
        return request

    def get(self, url, timeout=2, proxies=None, parser=None):
        """  通用get方法，通过将其他复杂步骤封装进此方法中，减少爬虫代码框架搭建步骤

        :param parser:
        :param url: 网页url
        :param timeout: 连接超时时间
        :param proxies: 代理信息
        :return:
        """
        try:
            request = self.set_request(url)
            response = requests.get(request, timeout=timeout, proxies=proxies)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            if parser is not None:
                result = parser.parse(response.text)
            else:
                result = response.text
            return result
        except requests.exceptions.HTTPError as e:
            print(e)
            return "HTTPError"

    def post(self, url, timeout=2, proxies=None, parser=None):
        """  通用get方法，通过将其他复杂步骤封装进此方法中，减少爬虫代码框架搭建步骤

        :param parser:
        :param url: 网页url
        :param timeout: 连接超时时间
        :param proxies: 代理信息
        :return:
        """
        try:
            request = self.set_request(url)
            response = requests.post(request, timeout=timeout, proxies=proxies)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            if parser is not None:
                result = parser.parse(response.text)
            else:
                result = response.text
            return result
        except requests.exceptions.HTTPError as e:
            print(e)
            return "HTTPError"

