# -*- coding:utf-8 -*-

"""
@author:itgao
@file: clusters.py
@time: 2016/12/21 19:23
"""
from math import sqrt
from PIL import Image,ImageDraw

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


# 算法
def hcluster(rows,distance=pearson):
    distances = {}
    currentclustid = -1

    # 最开始的聚类就是数据集中的行
    clust = [bicluster(rows[i],id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestpair = (0,1)
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
        newcluster = bicluster(mergevec,left=clust[lowestpair[0]],
                               right=clust[lowestpair[1]],distance=closest,id=currentclustid)
        # 不在原始集合中的聚类，其id为负数
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]


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
        printclust(clust.left,labels=labels,n = n+1)
    if clust.right:
        printclust(clust.right,labels=labels,n = n+1)


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
    clust = hcluster(data)
    # printclust(clust,labels=blognames)
    drawdendrogram(clust,blognames,jpeg='data/bligclust.jpg')