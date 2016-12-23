# -*- coding:utf-8 -*-

"""
@author:itgao
@file: main.py
@time: 2016/12/6 19:34
将数据库中对应表的对应字段和类型以Java中MyBatis要求的格式
生成 Entity、Dao、Mapper文件，简化了mybatis的重复操作
"""

import os
import setting
import dao_gen,entity_gen,mapper_gen


def main():

    entity_file = os.path.join(setting.ENTITY_TARGET_PROJECT,setting.ENTITY_NAME+'.java')
    dao_file = os.path.join(setting.DAO_TARGET_PROJECT,setting.ENTITY_NAME+'Dao.java')
    mapper_file = os.path.join(setting.MAPPER_TARGET_PROJECT,setting.ENTITY_NAME+'Mapper.xml')
    print entity_file,dao_file,mapper_file
    with open(entity_file,'w') as file:
        file.write(entity_gen.generate())
    with open(dao_file,'w') as file:
        file.write(dao_gen.generate())
    with open(mapper_file,'w') as file:
        file.write(mapper_gen.generate())
    file.close()

if __name__ == '__main__':
    main()

