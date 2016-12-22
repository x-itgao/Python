# -*- coding:utf-8 -*-

"""
@author:itgao
@file: clusters.py
@time: 2016/12/21 19:23
"""
from math import sqrt
from PIL import Image,ImageDraw
import random


def readfile(filename):
    lines = [line for line in file(filename)]

    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # 每行的第一列是行名
        rownames.append(p[0].decode('utf-8'))
        # 剩余部分是该行对应的数据
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data


# 利用皮尔逊相关度进行计算，返回两个列表的相关度分值
def pearson(v1,v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1_sq = sum([pow(v,2) for v in v1])
    sum2_sq = sum([pow(v,2) for v in v2])

    p_sum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = p_sum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1_sq-pow(sum1,2)/len(v1))*(sum2_sq-pow(sum2,2)/len(v1)))
    if den == 0:
        return 0
    # 皮尔逊相关度在两者完全匹配的情况下为1.0，毫无关系的情况下为0.0
    return 1.0 - num / den


# 分级聚类算法
class bicluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance
'''
    分类聚类算法以一组对应于原始数据项的聚类开始，主循环部分会尝试每一组可能的配对
    并计算他们的相关度，以此找出最佳配对，然后合并成一个新的聚类，这一过程持续重复下去，
    直到剩下一个聚类
'''


# 算法,找到相互匹配的，保存的是一个节点，删掉了两个分支
def h_cluster(rows,distance=pearson):
    distances = {}
    currentclustid = -1

    # 最开始的聚类就是数据集中的行，原始数据
    clust = [bicluster(rows[i],id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestpair = (0,1)
        # 当前最佳配对
        closest = distance(clust[0].vec,clust[1].vec)
        # 遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                # 用distances来缓存距离的计算器
                if(clust[i].id,clust[j].id) not in distances:
                    distances[(clust[i].id,clust[j].id)] = distance(clust[i].vec,clust[j].vec)

                d = distances[(clust[i].id,clust[j].id)]
                # 记录相关值，及位置 i,j
                if d < closest:
                    closest = d
                    lowestpair = (i,j)
        # 计算两个聚类的平均值
        mergevec = [
            (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))
        ]
        # 建立新的聚类
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]],
                               right=clust[lowestpair[1]], distance=closest, id=currentclustid)
        # 不在原始集合中的聚类，其id为负数
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]


# K-均值聚类过程
def k_cluster(rows,distance=pearson,k=4):
    # 确定每个点的最大值和最小值
    ranges = [(min([row[i] for row in rows]),max([row[i] for row in rows]))
              for i in range(len(rows[0]))]
    # 随机创建k个中心点
    clusters = [[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)]
    last_matches = None
    for t in range(100):
        print 'Iteration %d' % t
        best_matches = [[] for i in range(k)]
        # 在每一行中寻找距离最近的中心点
        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(clusters[i],row)
                if d < distance(clusters[best_match],row):
                    best_match = i
            best_matches[best_match].append(j)
        # 如果结果与上次相同，则整个过程结束
        if best_matches == last_matches:
            break
        last_matches = best_matches
        # 把中心点移到其他成员的平均位置处
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(best_matches[i]) > 0:
                for row_id in best_matches[i]:
                    for m in range(len(rows[row_id])):
                        avgs[m] += rows[row_id][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(best_matches[i])
                clusters[i] = avgs
    return best_matches


# Tanimoto系数 度量，代表的是交集(只包含那些在两个集合都出现的项)与并集(包含所有出现在任一集合的项)的比率
def tanimoto(v1,v2):
    c1,c2,shr = 0,0,0
    for i in range(len(v1)):
        if v1[i] != 0:
            c1 += 1
        if v2[i] != 0:
            c2 += 1
        if v1[i] != 0 and v2[i] != 0:
            shr +=1
    return 1.0 - (float(shr) / (c1+c2-shr))


# 多维缩放
def scale_down(data,distance=pearson,rate=0.01):
    n = len(data)

    # 每一对数据项之间真实距离
    real_dist = [[distance(data[i],data[j]) for j in range(n)] for i in range(0,n)]

    outer_num = 0.0
    # 随机初始化节点在二维空间中的起始位置
    loc = [[random.random(),random.random()] for i in range(n)]
    fake_dist = [[0.0 for j in range(n)] for i in range(n)]

    last_error = None
    for m in range(0,1000):
        # 寻找投影后的距离
        for i in range(n):
            for j in range(n):
                fake_dist[i][j] = sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))
        # 移动节点
        grad = [[0.0,0.0] for i in range(n)]
        total_error = 0
        for k in range(n):
            for j in range(n):
                if j == k:
                    continue
                # 该误差值等于目标距离与当前距离之间差值的百分比
                error_term = (fake_dist[j][k] - real_dist[j][k]) / real_dist[j][k]
                grad[k][0] += ((loc[k][0]-loc[j][0]) / fake_dist[j][k]) * error_term
                grad[k][1] += ((loc[k][1]-loc[j][1]) / fake_dist[j][k]) * error_term
                # 记录总的误差值
                total_error += abs(error_term)
        # 如果节点移动后情况变得更糟则程序结束
        if last_error and last_error < total_error:
            break
        last_error = total_error
    return loc


# 二维
def draw2d(data,labels,jpeg='data/mds2d.jpg'):
    img = Image.new('RGB',(2000,2000),(255,255,255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x,y),labels[i],(0,0,0))

    img.save(jpeg,'JPEG')


# 打印
def printclust(clust,labels=None,n=0):
    # 用缩进来建立层级布局
    for i in range(n):
        print ' ',
    if clust.id < 0:
        print '-'
    else:
        if not labels:
            print clust.id
        else:
            print labels[clust.id]
    if clust.left:
        printclust(clust.left,labels=labels, n=n+1)
    if clust.right:
        printclust(clust.right,labels=labels, n=n+1)


# 将整个数据集转置，每一行代表 一个单词对应出现次数
def rotate_matrix(data):
    new_data = []
    for i in range(len(data)):
        new_row = [data[j][i] for j in range(len(data))]
        new_data.append(new_row)
    return new_data


# 绘制树状图
# 如果是叶节点 高度为1，否则高度为其子节点的总和
def getheight(clust):
    if not (clust.left or clust.right):
        return 1
    return getheight(clust.left) + getheight(clust.right)


# 一个节点的误差深度等于其所属的每个分支的最大可能误差
def getdepth(clust):
    if not(clust.left or clust.right):
        return 0
    return max(getdepth(clust.left),getheight(clust.right))+clust.distance


# 为每一个最终生成的聚类创建一个高度为20像素、宽度固定的图片
# 其中的缩放因子是由固定宽度除以总的深度值得到的
def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
    h = getheight(clust)*20
    w = 1200
    depth = getdepth(clust)

    #由于宽度是固定的，因此我们要对距离值做相应的调整
    scaling = float(w-150) / depth
    # 新建一个白色背景的图片
    img = Image.new('RGB',(w,h),(255,255,255))
    draw = ImageDraw.Draw(img)

    draw.line((0,h/2,10,h/2),fill=(255,0,0))

    # 画第一个节点
    drawnode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling,labels):
    if clust.id < 0:
        h1 = getheight(clust.left)*20
        h2 = getheight(clust.right)*20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        ll = clust.distance*scaling
        # 聚类到其子节点的垂直线
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))
        # 连接左侧节点的水平线
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))
        # 连接右侧节点的水平线
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))
        # 调用函数绘制左右节点
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
    else:
        # 如果是叶节点，绘制节点的标签
        draw.text((x+5,y-7),labels[clust.id],(0,0,0))
if __name__ == '__main__':
    blognames,words,data = readfile('data/blogdata.txt')
    # clust = hcluster(data)
    # printclust(clust,labels=blognames)
    #　绘制博客树状图
    # drawdendrogram(clust,blognames,jpeg='data/bligclust.jpg')
    # 绘制单词树状图
    # r_data = rotate_matrix(data)
    # word_clust = h_cluster(r_data)
    # drawdendrogram(word_clust,labels=words,jpeg='data/wordclust.jpg')
    # k-聚类
    # k_clust = k_cluster(data,k=5)
    # print k_clust
    # print [blognames[r] for r in k_clust[0]]
    # print [blognames[r] for r in k_clust[1]]
    # wants,people,data = readfile('data/zebo.txt')
    # clust = h_cluster(data,distance=tanimoto)
    # drawdendrogram(clust,wants,'data/clusters.jpg')
    coords = scale_down(data)
    draw2d(coords,blognames)
