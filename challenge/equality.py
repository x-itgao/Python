# -*- coding:utf-8 -*-

"""
@author:itgao
@file: equality.py
@time: 2016/12/20 11:14
"""

import re
# equality.data 数据
# One small letter, surrounded by EXACTLY three big bodyguards on each of its sides.

with open('data/equality.data','r') as file:
    page_data = file.read()
file.close()
page_data = ''.join(page_data)
data = re.findall(r'[^A-Z][A-Z]{3}([a-z])[A-Z]{3}[^A-Z]',page_data)
print ''.join(data)


