# -*- coding:utf-8 -*-
import arcpy
import sys
from arcpy import env
import numpy as np
import math

reload(sys)
sys.setdefaultencoding('utf-8')
env.overwriteOutput = True

# 读取一个shapefile, 用户自定义
# input a shapefile customized by user
shp = r'C:\Users\Lenovo\Desktop\11111\polygon.shp'


# 从.shp文件中获取多边形顶点坐标列表
# access the nodes' coordinate of each single feature
def getPolyXY(shape):
    with arcpy.da.SearchCursor(shape, ["SHAPE@"]) as cursor:
        polygons = []
        for row in cursor:
            coordXY = row[0].getPart()
            record = []
            for v in range(row[0].pointCount - 1):
                pnt = coordXY.getObject(0).getObject(v)
                record.append([pnt.X, pnt.Y])
            polygons.append(record)
            # record = []
        #     for part in row[0]:
        #         for pnt in part[0:len(part)-1]:
        #             record.append([pnt.X, pnt.Y])
        #         polygons.append(record)
        return polygons


class Douglas(object):
    def __init__(self):
        self.pts_seq = list()
        self.flag = list()
        self.sigma = 20
        self.head = 0
        self.rear = 0

    def update(self, pts_seq):
        self.pts_seq = pts_seq
        length = len(pts_seq)
        self.rear = length - 1
        self.flag = [False] * length

    def max_dis(self, head, rear):
        x0, y0 = self.pts_seq[head][0], self.pts_seq[head][1]
        x1, y1 = self.pts_seq[rear][0], self.pts_seq[rear][1]
        a = y1 - y0
        b = x0 - x1
        c = x0 * (y0 - y1) + y0 * (x1 - x0)
        max_d = 0
        index = 0
        for i in range(head + 1, rear):
            pt = self.pts_seq[i]
            di = np.abs(a * pt[0] + b * pt[1] + c) / np.sqrt(a ** 2 + b ** 2)
            if di > max_d:
                max_d = di
                index = i
        return max_d, index

    def compress(self, head, rear):
        if rear - head > 1:
            max_d, index = self.max_dis(head, rear)
            if max_d <= self.sigma:
                self.flag[head] = True
                self.flag[rear] = True
            else:
                self.compress(head, index)
                self.compress(index, rear)
        else:
            self.flag[head] = True
            self.flag[rear] = True

    def draw_polygon(self):
        polygon = []
        for i, bool_value in enumerate(self.flag):
            if bool_value:
                polygon.append(self.pts_seq[i])
        return polygon


def main():
    polygons = getPolyXY(shp)
    dgls = Douglas()
    dgls.sigma = input('请输入容差/plz input the threshold:')
    plg_out = []
    for plg in polygons:
        dgls.update(plg)
        dgls.compress(dgls.head, dgls.rear)
        plg_out.append(dgls.draw_polygon())

    # customize output file path&name
    out_path = r'C:\Users\Lenovo\Desktop\11111'
    out_name = 'polygon_cps.shp'
    fc = out_path + '\\' + out_name
    shp_plg = arcpy.CreateFeatureclass_management(out_path,
                                                  out_name,
                                                  geometry_type='POLYGON')
    cursor = arcpy.InsertCursor(fc)
    for plg in plg_out:
        array = arcpy.Array()
        point = arcpy.Point()
        for pt in plg:
            point.X = pt[0]
            point.Y = pt[1]
            array.add(point)
        new_plg = arcpy.Polygon(array)
        row = cursor.newRow()
        row.shape = new_plg
        cursor.insertRow(row)


if __name__ == '__main__':
    main()
