from bs4 import BeautifulSoup
import re


class HtmlParserInterface:
    def parser(self, context):
        '''
        自定义html文本解析格式
        - param context：传入需要解析的文本
        - return: 文本解析后的结果
        '''

# html解析


class HtmlParser(HtmlParserInterface):

    def __init__(self, head):
        self.__head = head

    def parser(self, context):
        soup = BeautifulSoup(context, 'lxml')
        spots_list = soup.find_all(
            'a', {"class": "photo_link"})  # 查找所有class为指定值的啊标签
        url_list = []
        for i in spots_list:
            temp = self.__head + i.get('href')
            url_list.append(temp)
        return url_list
