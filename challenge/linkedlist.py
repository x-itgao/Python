# -*- coding:utf-8 -*-

"""
@author:itgao
@file: linkedlist.py
@time: 2016/12/20 12:10
"""
import re
import urllib

next = "8022"
url = ""
response = ""
while True:
    url = "http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing="+next
    res = urllib.urlopen(url)
    response = res.read()

    if re.findall(r'\.html$', response):
        break

    code = re.findall(r'\d+$', response)

    if(code):
        next = code[0]
    else:
        next = str (int (next) / 2 )

    print url
    print response