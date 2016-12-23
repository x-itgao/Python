# -*- coding:utf-8 -*-

"""
@author:itgao
@file: entity_gen.py
@time: 2016/12/6 20:24
根据 MAP 生成Entity文件
"""

from SQL import getTableInfo
import setting

package = 'package '+setting.ENTITY_TARGET_PACKAGE+';'
class_name = 'public class '+setting.ENTITY_NAME+'{'
tab = '\t'
nextLine = '\n'
setter = 'public void set{0}{\n\tthis.{1} = {2};\n}'
getter = 'public {0} get{1}{'+nextLine+tab+'return {1};'+nextLine+'}'
item = 'private {0} {1};'


def generate():
    content = package+nextLine+nextLine+class_name+nextLine+nextLine
    maps = getTableInfo()
    items = []
    getters = []
    setters = []
    for map in maps.values():
        it = map.keys()[0]
        type = map.values()[0]
        items.append(item.format(type,it))
        setters.append('public void set'+it[0].upper()+it[1:]+'('+type+' '+it+') '+'{\n\t\tthis.'+it+' = '+it+';\n\t}')
        getters.append('public '+type+' get'+it[0].upper()+it[1:]+'(){'+nextLine+tab+tab+'return '+it+';\n\t}')
    for data in items:
        content += tab+data+nextLine

    for set,get in zip(setters,getters):
        content += tab+set+nextLine+tab+get+nextLine
    return content+nextLine+'}'



if __name__ == '__main__':
    print generate()

