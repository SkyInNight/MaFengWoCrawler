# -*- coding: utf-8 -*-
import json


def check_inside_scenic(scenic, dir_list):
    for index_ in dir_list:
        inside_scenic_list = index_['inside_scenic']
        for inside_scenic in inside_scenic_list:
            if scenic['title'] == inside_scenic['title']:
                print('景点{0},为景点{1}的内部景点'.format(inside_scenic['title'],index_['title']))
                scenic['type'] = index_['title']
    return scenic


def set_inside_scenic(city_name):
    with open('../data/all_scenic_info/' + city_name + '.json', 'r', encoding='utf-8') as f:
        scenic_info_list = json.loads(f.read())
    for index_ in range(0, len(scenic_info_list)):
        scenic_info_list[index_] = check_inside_scenic(scenic_info_list[index_], scenic_info_list)
    with open('../data/scenic_info/' + city_name + '.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(scenic_info_list))


if __name__ == '__main__':
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
        # set_inside_scenic(city_name)
        with open('../data/scenic_info/' + city_name + '.json', 'r', encoding='utf-8') as f:
            scenic_info = json.loads(f.read())
        print('城市{0}的景点个数为{1}'.format(city_name,len(scenic_info)))