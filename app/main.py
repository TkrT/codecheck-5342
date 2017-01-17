#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import json
import datetime
from datetime import datetime as dt
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import numpy
import asyncio
import aiohttp

#Webページの取得
@asyncio.coroutine
def get(url):
    response = yield from aiohttp.request('GET', url)
    return (yield from response.text())

#週ごとに記事件数の取得
@asyncio.coroutine
def getArticleNumber(data):
    global Keywords
    global startDate
    global numbersArray
    global AsahiURLPrefix

    #検索日付の設定
    weekStartDate = startDate + datetime.timedelta(days = 7 * data[1])
    weekEndDate = weekStartDate + datetime.timedelta(days = 6)

    #URLの作成と読み込み
    query = 'q=Body%3A' + Keywords[data[0]] + '%20AND%20ReleaseDate%3A%5B' + weekStartDate.strftime('%Y-%m-%d') + '%20TO%20' + weekEndDate.strftime('%Y-%m-%d') + '%5D'
    url = AsahiURLPrefix + query
    page = yield from get(url)

    #XMLを解析して件数を取得
    root = ET.fromstring(page)
    result = root.find('.//result')
    numbersArray[data[0]][data[1]] = int(result.get('numFound'))

def main(argv):
    #global変数の定義
    global Keywords
    global startDate
    global numbersArray
    global AsahiURLPrefix

    #jsonを用いてキーワードをパース
    jsonString = '{"keywords":' + os.fsencode(argv[0]).decode('utf-8') + '}'
    jsonComponent = json.loads(jsonString)
    keywordNumber = len(jsonComponent['keywords'])
 
    #UTF-8かつURLエンコード済みのキーワードリストを作成
    Keywords = []
    for i in range(0, keywordNumber):
        Keywords.append(urllib.parse.quote(jsonComponent['keywords'][i].encode('utf-8')))

    #開始日時と終了日時をパース
    startDate = dt.strptime(os.fsencode(argv[1]).decode('utf-8'), '%Y-%m-%d')
    endDate = dt.strptime(os.fsencode(argv[2]).decode('utf-8'), '%Y-%m-%d')

    #日数を取得
    dateNum = (endDate - startDate).days + 1

    #端数を削除し、週数を取得
    dateFraction = dateNum % 7
    endDate = endDate - datetime.timedelta(days=dateFraction)
    dateNum -= dateFraction
    weekNum = dateNum // 7

    #件数保存用の配列を初期化
    totalNumbersArray = numpy.zeros(keywordNumber, numpy.int)
    numbersArray = numpy.ones([keywordNumber, weekNum], numpy.int)

    #記事検索用のプレフィックスを作成
    AsahiURLPrefix = 'http://54.92.123.84/search?'
    query = [
        ('ackey', '869388c0968ae503614699f99e09d960f9ad3e12'),
        ('rows', '1'),
    ]
    for item in query:
        AsahiURLPrefix += item[0] + "=" + item[1] + "&"

    #記事検索
    httpList = []
    for i in range(0, keywordNumber):
        for j in range(0, weekNum):
            httpList.append((i, j))

    loop = asyncio.get_event_loop()
    f = asyncio.wait([getArticleNumber(d) for d in httpList])
    loop.run_until_complete(f)

    #総数の取得
    for i in range(0, keywordNumber):
        totalNumbersArray[i] = numbersArray[i].sum()

    #相関係数保存用の配列を初期化
    coefficientsArray = numpy.empty([keywordNumber, keywordNumber], numpy.double)

    #相関係数の計算
    for i in range(0, keywordNumber):
        for j in range(0, keywordNumber):
            if (i <= j):
                if ((totalNumbersArray[i] != 0) and (totalNumbersArray[j] != 0)):
                    if (i != j):
                        coefficientsArray[i][j] = numpy.corrcoef(numbersArray[i], numbersArray[j])[0, 1]
                    else:
                        coefficientsArray[i][j] = 1
                else:
                    coefficientsArray[i][j] = 0
            else:
                coefficientsArray[i][j] = coefficientsArray[j][i]

    #形態要素解析
    posArray = []

    #キーワードからクエリを作成
    urlprefix = "http://jlp.yahooapis.jp/MAService/V1/parse?"
    sentence = Keywords[0]
    for i in range(1, keywordNumber):
        sentence += ',' + Keywords[i]
    query = [
        ('appid', 'dj0zaiZpPU84QnlScDdxM1p5NSZzPWNvbnN1bWVyc2VjcmV0Jng9MjY-'),
        ('results', 'ma'),
        ('sentence', sentence)
    ]

    #URLの形に整形
    url = urlprefix
    for item in query:
        url += item[0] + "=" + item[1] + "&"
    url = url[:-1]

    #レスポンスを取得
    response = urllib.request.urlopen(url)
    resdata = response.read()

    #XMLを解析して品詞を取得
    root = ET.fromstring(resdata)
    for e in root.getiterator('{urn:yahoo:jp:jlp}word'):
        pos = e.find('.//{urn:yahoo:jp:jlp}pos')
        if (pos.text != '特殊'):
            posArray.append(pos.text)

    #品詞がすべて等しいかを確認
    posChecker = True
    for pos in posArray:
        if (posArray[0] != pos):
            posChecker = False

    #出力を整形
    string = '{"coefficients":['
    for i in range(0, keywordNumber):
        string += '['
        for j in range(0, keywordNumber):
            if ((totalNumbersArray[i] != 0) and (totalNumbersArray[j] != 0)):
                if (i == j):
                    #同じ要素なら"1"を出力
                    string += "1"
                else:
                    #違う要素なら相関係数を小数点以下3桁で出力
                    string += str(round(coefficientsArray[i][j],3))
            else:
                #どちらかが0ならnull
                string += 'null'
            string += ','
        string    = string[:-1]
        string += '],'
    string    = string[:-1]
    string += '],"posChecker":'
    #品詞がすべて等しいかを出力
    if (posChecker):
        string += 'true'
    else:
        string += 'false'
    string += '}'

    #出力
    print(string)
    