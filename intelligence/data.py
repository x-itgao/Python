# -*- coding:utf-8 -*-

"""
@author:itgao
@file: data.py
@time: 2016/12/20 21:09
"""
from math import sqrt
critics = {'Lisa Rose':
               {'Lady in the Water':2.5,'Snakes on a Plane':3.5,'Just My Luck':3.0,'Superman Retruns':3.5,'You,Me and Dupree':2.5,'The Night Listener':3.0},
           'Gene Seymour':
               {'Lady in the Water':3.0,'Snakes on a Plane':3.5,'Just My Luck':1.5,'Superman Retruns':5.0,'The Night Listener':3.0,'You,Me and Dupree':3.5},
           'Michael Phillips':
               {'Lady in the Water':2.5,'Snakes on a Plane':3.0,'Superman Retruns':3.5,'The Night Listener':4.0},
           'Claudia Puig':
               {'Snakes on a Plane':3.5,'Just My Luck':3.0,'The Night Listener':4.5,'Superman Retruns':4.0,'You,Me and Dupree':2.5},
           'Mick LaSalle':
               {'Lady in the Water':3.0,'Snake on a Plane':4.0,'Just My Luck':2.0,'Superman Retruns':3.0,'The Night Listener':3.0,'You,Me and Dupree':2.0},
           'Jack Matthews':
               {'Lady in the Water':3.0,'Snakes on a Plane':4.0,'The Night Listener':3.0,'Superman Retruns':5.0,'You,Me and Dupree':3.5},
           'Toby':
               {'Snakes on a Plane':4.5,'You,Me and Dupree':1.0,'Superman Retruns':4.0}}


# 欧几里得距离评价
# 返回一个有关person1和person2的基于距离的相似度评价
def sim_distance(prefs,person1,person2):
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    # 如果两者没有共同之处，返回0
    if len(si) == 0:
        return 0

    # 计算所有差值的平方和
    sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sqrt(sum_of_squares))


# 皮尔逊相关度评价
# 相关系数是判断两组数据与某一直线拟合程度的一种度量
def sim_pearson(prefs,p1,p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    # 得到列表元素的个数
    n = len(si)
    if n == 0:
        return 1

    # 对所有偏好求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # 求平方和
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    # 求乘积之和
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])

    # 计算皮尔逊评价值
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den == 0:
        return 0
    r = num / den
    return r


# 寻找接近的匹配者
def top_matches(prefs,person, n = 5, similarity = sim_pearson):
    # 排除自己
    scores = [(similarity(prefs, person, other),other)
              for other in prefs if other != person]
    # 对列表进行排序，评价值最高者排在最前面
    scores.sort()
    scores.reverse()
    return scores[0:n]


# 利用所有他人评价值的加权平均，为某人提供建议
def get_recommenddations(prefs, person, similarity=sim_pearson):
    totals = {}
    sim_sums = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs,person,other)
        if sim <= 0:
            continue
        for item in prefs[other]:
            # 只对自己还没看过的影片进行评价
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item,0)
                # 所有影片评价加权
                totals[item] += prefs[other][item]*sim
                sim_sums.setdefault(item,0)
                #
                sim_sums[item] += sim
        # 建立一个归一化的列表
        rankings = [(total/sim_sums[item],item) for item,total in totals.items()]

        rankings.sort()
        rankings.reverse()
        return rankings


# 将人员和物品调换
def trans_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item]
    return result


# 构造物品比较数据集，找到每个物品各自最接近的集合
def calc_sim_items(prefs,n = 10):
    result = {}
    # 倒置处理
    item_prefs = trans_prefs(prefs)
    c = 0
    for item in item_prefs:
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c,len(item_prefs))
        # 找到最接近的
        scores = top_matches(item_prefs,item,n=n,similarity=sim_distance)
        result[item] = scores
    return result


# 评分结果
def get_recom_items(prefs,item_match,user):
    user_ratings = prefs[user]
    scores = {}
    total_sim = {}
    # 循环遍历与当前用户评分的物品
    for (item,rating) in user_ratings.items():
        for (similarity,item2) in item_match[item]:
            if item2 in user_ratings:
                continue
            scores.setdefault(item2,0)
            scores[item2] += similarity*rating

            #全部相似度之和
            total_sim.setdefault(item2,0)
            total_sim[item2] += similarity
    rankings = [(score/total_sim[item],item) for item,score in scores.items()]
    # 按照从高到低的顺序返回
    rankings.sort()
    rankings.reverse()
    return rankings


# 加载数据
def load_movies(path="./data"):

    # 获取影片标题
    movies = {}
    for line in open(path+'/u.item'):
        (id,title) = line.split('|')[0:2]
        movies[id] = title
    # 加载
    prefs = {}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts) = line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]] = float(rating)
    return prefs
if __name__ == '__main__':
    # print sim_distance(critics,'Lisa Rose','Gene Seymour')
    # print sim_pearson(critics,'Lisa Rose','Gene Seymour')
    # print topMatches(critics,'Toby',n=3)
    # print get_recommenddations(critics,'Toby',similarity=sim_distance)
    # movies = trans_prefs(critics)
    # print top_matches(movies,'Superman Retruns')
    # print get_recommenddations(movies, 'Just My Luck')
    # print pydelicious.get_popular(tag='programming')
    print calc_sim_items(critics)
    # print get_recom_items(critics,itemsim,'Toby')
    # prefs = load_movies()
    # print get_recommenddations(prefs,'87')[0:30]
    # itemsim = calc_sim_items(prefs,n = 50)
    # print get_recom_items(prefs,itemsim,'87')[0:30]