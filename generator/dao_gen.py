# -*- coding:utf-8 -*-

"""
@author:itgao
@file: dao_gen.py
@time: 2016/12/6 23:16
根据 MAP 生成DAO文件
"""

import setting
from SQL import getTableInfo


package = 'package '+setting.DAO_TARGET_PACKAGE+';'
im = '\nimport '+setting.ENTITY_TARGET_PACKAGE+'.'+setting.ENTITY_NAME+';'
start = '\npublic interface '+setting.ENTITY_NAME+'Dao{\n'
save = '\n\tpublic void save('+setting.ENTITY_NAME+' '+setting.ENTITY_NAME[0].lower()+setting.ENTITY_NAME[1:]+');'
update = '\n\tpublic void update('+setting.ENTITY_NAME+' '+setting.ENTITY_NAME[0].lower()+setting.ENTITY_NAME[1:]+');'
select = '\n\tpublic '+setting.ENTITY_NAME+' select(int id);'
delete = '\n\tpublic void delete(int id);'


def generate():
    content = package+im+start+save+update+select+delete+'\n}'
    return content


if __name__ == '__main__':
    print generate()