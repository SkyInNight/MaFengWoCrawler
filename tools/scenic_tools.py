# -*- coding: utf-8 -*-
import json


def get_city_info(city_):
    city_id = ""
    city_name = ""
    for index_ in city_.keys():
        city_name = index_
        city_id = city_[index_]
    return {'city_id': city_id, 'city_name': city_name}


def get_scenic_info(scenic_url):
    scenic_id = scenic_url.split('/')[len(scenic_url.split('/')) - 1].split('.')[0]
    return scenic_id


def get_scenic_url(city_name):
    all_url_list = []
    top_scenic_list = []
    all_scenic_list = []
    result_scenic_list = []
    with open('../data/' + city_name + '.json', 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().replace('\n', '')
            if line is None or line == "":
                break
            top_scenic_list.append(json.loads(line))
    with open('../data/all/' + city_name + '.json', 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().replace('\n', '')
            if line is None or line == "":
                break
            all_scenic_list.append(json.loads(line))
    for top_scenic in top_scenic_list:
        for scenic in top_scenic:
            if 'current_url_list' in scenic:
                for url in scenic['current_url_list']:
                    all_url_list.append(url)
                continue
            result_scenic_list.append(scenic)
    for all_scenic in all_scenic_list:
        for scenic_list in all_scenic:
            for scenic in scenic_list:
                if 'current_url_list' in scenic:
                    if len(scenic['current_url_list']) == 0:
                        break
                    for url in scenic['current_url_list']:
                        if url in all_url_list:
                            continue
                        all_url_list.append(url)
                    continue
                if 'href' in scenic and scenic['href'] not in all_url_list:
                    result_scenic_list.append(scenic)
    return {'scenic_list': result_scenic_list, 'url_list': all_url_list}


if __name__ == '__main__':
    print(get_scenic_url('长沙'))
