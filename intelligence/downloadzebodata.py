# -*- coding:utf-8 -*-

"""
@author:itgao
@file: downloadzebodata.py
@time: 2016/12/22 11:50
"""

from bs4 import BeautifulSoup
import urllib2
import re

pattern = re.compile(r'[!-\.&]')
item_owners = {}

# 要去除的单词
drop_words = ['a','new','some','more','my','own','the','many','other','another']

current_user = 0
for i in range(1,51):
    # 搜索“用户希望拥有的物品” 所对应的URL
    c = urllib2.urlopen('http://member.zebo.com/Main?event_key=USERSEARCHE&wiowiw=wiw&keyword=car&page=%d' % (i))
    soup = BeautifulSoup(c.read())
    for td in soup('td'):
        # 寻找带有bgverdansmall类的表格单元格
        if 'class' in dict(td.attrs) and td['class'] == 'bgverdanasmall':
            items = [re.sub(pattern,'',a.contents[0].lower()).strip()
                     for a in td('a')]
            for item in items:
                # 去除多余的单词
                txt = ' '.join([t for t in item.split(' ') if t not in drop_words])
                if len(txt) < 2:
                    continue
                item_owners.setdefault(txt,{})
                item_owners[txt][current_user] = 1
            current_user += 1

with open('data/zebo.txt','w') as file:
    file.write('Item')
    for user in range(0,current_user):
        file.write('\tU%d' % user)
    file.write('\n\r')
    for item,owers in item_owners.items():
        if len(owers) > 10:
            file.write(item)
            for user in range(0,current_user):
                if user in owers:
                    file.write('\t1')
                else:
                    file.write('\t0')
            file.write('\n')