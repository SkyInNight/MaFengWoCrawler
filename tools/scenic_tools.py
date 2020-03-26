# -*- coding: utf-8 -*-
import json


def check_name_in_dir(name, dir_list):
    for scenic in dir_list:
        if scenic is not None and scenic['title'] == name:
            return True
    return False


def check_download(city_name):
    list = get_scenic_url(city_name)
    scenic_list = list['scenic_list']
    with open('../data/all_scenic_info/'+city_name+'.json', 'r', encoding='utf-8') as f:
        download_data = f.read()
    download_list = json.loads(download_data)
    fault_list = []
    for scenic in scenic_list:
        if not check_name_in_dir(scenic['title'], download_list):
            fault_list.append(scenic)
    print('城市{0},下载失败景点个数{1}，全部景点个数{2}'.format(city_name, len(fault_list), len(scenic_list)))
    with open('../data/fault_download/'+city_name+'.json', 'a+', encoding='utf-8') as f:
        f.write(json.dumps(fault_list))


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
    # print(get_scenic_url('长沙'))
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
    for city in city_list:
        for key in city.keys():
            city_name = key
        # print(city_name)
        check_download(city_name)
