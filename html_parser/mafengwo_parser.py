# -*- coding: utf-8 -*-
from html_parser.html_parser import HtmlParserInterface
from bs4 import BeautifulSoup
import re


class CityParser(HtmlParserInterface):

    def parser(self, context):
        """ 解析马蜂窝城市景点首页

        :param context: 需要进行解析的网页文本
        :return: 返回当前首页中的top5景点和热门景点
        """
        scenic_list = []
        current_url_list = []
        soup = BeautifulSoup(context, 'lxml')
        # 1. 获取当前页面的top5景点
        top_list = soup.select('div.row-top5 > div > div > div > div')
        for div in top_list:

            # 1.1 因为通过select调用返回必定是列表，所以需要通过提取列表中第一个元素来提取a标签
            a = div.select('h3 > a')[0]
            # 1.2 获取当前景点的url

            if r'http://www.mafengwo.cn' + a['href'] in current_url_list:
                continue
            # 1.3 为了快速去重，所以这里临时建立url列表，用来去除重复景点
            current_url_list.append(r'http://www.mafengwo.cn' + a['href'])
            # 1.4 获取当前景点的title
            scenic = {'href': r'http://www.mafengwo.cn' + a['href'],
                      'title': a['title'],
                      'type': 'top_' + str(div.find('span', {"class": "num"}).contents[0])}
            """
            # 1.6 如果当前景点有内部景点，则遍历循环当前景点的内部景点
            link_list = div.select('div.links > a')
            if link_list is not None:
                inside_scenic_list = []
                for link in link_list:
                    inside_scenic = {'href': r'http://www.mafengwo.cn' + \
                                             link['href'],
                                     'title': link.get_text()
                                     }
                    current_url_list.append(
                        r'http://www.mafengwo.cn' + link['href'])
                    inside_scenic_list.append(inside_scenic)
                scenic['inside_scenic_list'] = inside_scenic_list
                """
            scenic_list.append(scenic)
        # 2 获取当前页面的热门页面
        hot_list = soup.select(
            'div.row-hotScenic > div > div > div > div.figure')
        for div in hot_list:
            # 2.1 获取热门景点的url
            a = div.select('a')[0]
            href = r'http://www.mafengwo.cn' + a['href']
            if href in current_url_list:
                continue
            scenic = {'href': href, 'title': a['title'], 'type': 'hot_scenic'}
            current_url_list.append(href)
            scenic_list.append(scenic)
        scenic_list.append({'current_url_list': current_url_list})
        return scenic_list


class ScenicListParser(HtmlParserInterface):

    def parser(self, context):
        scenic_list = []
        soup = BeautifulSoup(context, 'lxml')
        all_list = soup.select('div.row-allScenic > div > div.bd > ul > li > a')
        for link in all_list:
            scenic = {
                'href': r'http://www.mafengwo.cn' + link['href'],
                'title': link['title'],
                'type': 'common_scenic'}
            scenic_list.append(scenic)
        return scenic_list
