# -*- coding: utf-8 -*-


def get_scenic_info(scenic_url):
    scenic_id = scenic_url.split('/')[len(scenic_url.split('/')) - 1].split('.')[0]
    return scenic_id
