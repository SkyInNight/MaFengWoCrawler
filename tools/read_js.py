# -*- coding: utf-8 -*-
import execjs

with open('../data/function.js', 'r', encoding='utf-8') as f:
    js = f.read()


def read_js(data,):
    ctx = execjs.compile(js, cwd=r"C:\Users\ASUS\AppData\Roaming\npm\node_modules")
    sn = ctx.call("_0xe7fex35", data)
    # print(sn)
    data['_sn'] = sn
    return data
