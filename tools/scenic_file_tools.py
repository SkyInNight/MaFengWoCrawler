# -*- coding: utf-8 -*-
import json


def check_inside_scenic(scenic_, dir_list):
    for index_ in dir_list:
        inside_scenic_list = index_['inside_scenic']
        for inside_scenic in inside_scenic_list:
            if scenic_['title'] == inside_scenic['title']:
                print('景点{0},为景点{1}的内部景点'.format(inside_scenic['title'], index_['title']))
                scenic_['type'] = index_['title']
    return scenic_


def set_inside_scenic(city_name):
    with open('../data/all_scenic_info/' + city_name + '.json', 'r', encoding='utf-8') as f:
        scenic_info_list = json.loads(f.read())
    for index_ in range(0, len(scenic_info_list)):
        scenic_info_list[index_] = check_inside_scenic(scenic_info_list[index_], scenic_info_list)
    with open('../data/scenic_info/' + city_name + '.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(scenic_info_list))


def scenic_callback(arg):
    city_name = arg[len(arg) - 1]['city']
    with open('../data/all/' + city_name + '.json', 'a+', encoding='utf-8') as output:
        output.write(json.dumps(arg) + "\n")


def scenic_info_callback(arg):
    with open('../data/all_scenic_info/' + arg['city'] + '.json', 'a+', encoding='utf-8') as output:
        output.write(json.dumps(arg['scenic_info_list']) + "\n")


def save_top_five_scenic(arg):
    file_name = ""
    for index_ in arg:
        file_name = index_['city']
        break
    current_url_list = []
    with open('../data/' + file_name + '.json', 'w', encoding="utf-8") as output:
        scenic_info_list = []
        for index_ in range(len(arg)):
            """
            if index_ == len(arg) - 1:
            current_url_list = arg[index_]['current_url_list']
                break
            """
            scenic_info_list.append(arg[index_])
        output.write(json.dumps(scenic_info_list) + '\n')
    # with open('../data/exist_url.json', 'a+', encoding='utf-8') as output:
    #     output.write(json.dumps(current_url_list))


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
    all_info = []
    for city in city_list:
        for key in city.keys():
            city_name = key
        # set_inside_scenic(city_name)
        with open('../data/scenic_info/' + city_name + '.json', 'r', encoding='utf-8') as f:
            scenic_info = json.loads(f.read())
        for scenic in scenic_info:
            all_info.append(scenic)
    with open('../data/all_info.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(all_info))
    print(len(all_info))
