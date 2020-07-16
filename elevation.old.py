# please download elevation model from https://fgd.gsi.go.jp/download/menu.php (login required)

# code based on https://www.gis-py.com/entry/2016/01/10/163027

import re
import numpy as np
from os.path import join,relpath
from glob import glob
import shelve

elevation_data = []

def float2(str):
    lc = ""
    for i in range(len(str)):
        c = str[i]
        if c == lc:
            renzoku += 1
            if renzoku == 6:
                return float(str[:i+1] + c * 10)
        else:
            lc = c
            renzoku = 1
        return float(str)

#XMLを格納するフォルダ
path = "./DL"
#ファイル名取得
files = [relpath(x,path) for x in glob(join(path,'**/*.xml'))]

# 検索パターンをコンパイル
r1 = re.compile("<gml:lowerCorner>(.+) (.+)</gml:lowerCorner>")
r2 = re.compile("<gml:upperCorner>(.+) (.+)</gml:upperCorner>")
r3 = re.compile("<gml:high>(.+) (.+)</gml:high>")
r4 = re.compile("<gml:startPoint>(.+) (.+)</gml:startPoint>")

for index_files, fl in enumerate(files):
    xmlFile = join(path,fl)
    #XMLを開く
    with open(xmlFile, "r", encoding = "utf-8") as f:
        for ln in f:
            m = r1.search(ln)
            #検索パターンとマッチした場合、スタートポジションを格納
            if m != None:
                lry = float2(m.group(1))
                ulx = float2(m.group(2))
                break


        for ln in f:
            m = r2.search(ln)

            #検索パターンとマッチした場合、スタートポジションを格納
            if m != None:
                uly = float2(m.group(1))
                lrx = float2(m.group(2))
                break


        for ln in f:
            m = r3.search(ln)
            #検索パターンとマッチした場合、縦横の領域を格納
            if m != None:
                xlen = int(m.group(1)) + 1
                ylen = int(m.group(2)) + 1
                break

        startx = starty = 0

        for ln in f:
            m = r4.search(ln)
            #検索パターンとマッチした場合、スタートポジションを格納
            if m != None:
                startx = int(m.group(1))
                starty = int(m.group(2))
                break

    #numpy用にデータを格納しておく
    with open(xmlFile, "r", encoding = "utf-8") as f:
        src_document = f.read()
        lines = src_document.split("\n")
        num_lines = len(lines)
        l1 = None
        l2 = None
        for i in range(num_lines):
            if lines[i].find("<gml:tupleList>") != -1:
                l1 = i + 1
                break
        for i in range(num_lines - 1, -1, -1):
            if lines[i].find("</gml:tupleList>") != -1:
                l2 = i - 1
                break

    #セルのサイズを算出
    psize_x = (lrx - ulx) / xlen
    psize_y = (uly - lry) / ylen
    
    narray = np.empty((ylen, xlen), np.float32)
    narray.fill(0)

    num_tuples = l2 - l1 + 1

    #スタートポジションを算出
    start_pos = starty*xlen + startx

    i = 0
    sx = startx

    #標高を格納
    for y in range(starty, ylen):
        for x in range(sx, xlen):
            if i < num_tuples:
                vals = lines[i + l1].split(",")
                if len(vals) == 2 and vals[1].find("-99") == -1:
                    narray[y][x] = float(vals[1])
                i += 1
            else:
                break
        if i == num_tuples: break
        sx = 0
    
    elevation_data.append([ulx, uly, psize_x, psize_y, narray])
    print("%s/%s startx%s starty%s sizex%s sizey%s" % (index_files, len(files) - 1, ulx, uly, psize_x, psize_y))

shel = shelve.open('elevation.shel')
shel['elevation'] = elevation_data
shel.close()
