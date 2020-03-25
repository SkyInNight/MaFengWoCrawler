# -*- coding: utf-8 -*-
import execjs
import re

with open('../data/function.js', 'r', encoding='utf-8') as f:
    js = f.read()


def read_js(data, ):
    ctx = execjs.compile(js, cwd=r"C:\Users\ASUS\AppData\Roaming\npm\node_modules")
    sn = ctx.call("_0xe7fex35", data)
    # print(sn)
    data['_sn'] = sn
    return data


def parse_js(html):
    # 提取js加密函数
    js_string = re.search('<script>(.*?)</script>', html).group(1)
    # 修改js数据，将eval改为return
    func_return = js_string.replace('eval', 'return').replace('try{',"").replace(';break}',"").replace('catch(_){}',"")
    content = execjs.compile(func_return)
    evaled_func = content.call('f')
    function_name = re.search('var (.*?)=function',evaled_func).group(1)
    mode_func = evaled_func. \
        replace('return return', 'return eval'). \
        replace('while(window._phantom||window.__phantomas){};', ''). \
        replace('document.cookie=', 'return'). \
        replace(';if((function(){try{return !!window.addEventListener;}', ''). \
        replace("catch(e){return false;}})()){document.addEventListener('DOMContentLoaded',"+function_name+",false)}", ''). \
        replace("else{document.attachEvent('onreadystatechange',"+function_name+")}", '').replace(
        r"setTimeout('location.href=location.pathname+location.search.replace(/[\?|&]captcha-challenge/,\'\')',1500);",
        '')
    mode_func = 'const jsdom = require("jsdom"); \n \
    const { JSDOM } = jsdom;const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`); \n \
    window = dom.window; \n \
    document = window.document; \n \
    XMLHttpRequest = window.XMLHttpRequest; \n ' + mode_func
    content = execjs.compile(mode_func, cwd=r'C:\Users\ASUS\AppData\Roaming\npm\node_modules')
    cookies = content.call(function_name)
    __jsl_clearance = cookies.split(';')[0]
    return __jsl_clearance


if __name__ == '__main__':
    with open('../data/cookie.js', 'r', encoding='utf-8') as f:
        html = f.read()
    print(parse_js(html))
