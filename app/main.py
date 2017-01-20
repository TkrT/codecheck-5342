#!/usr/bin/env python3
# coding: utf-8
import sys
import os
import urllib.parse
import xml.etree.ElementTree as ET
import json
import numpy
import datetime
import asyncio
import aiohttp

#週数の取得
def getWeekNum(startDate, endDate):
    dateNum = (endDate - startDate).days + 1
    return (dateNum // 7)

#Webページの取得
@asyncio.coroutine
def get(url):
    response = yield from aiohttp.request('GET', url)
    return (yield from response.text())

#XMLを解析して件数を取得
def analyzeAsahiXML(page):
    root = ET.fromstring(page)
    result = root.find('.//result')
    return (int(result.get('numFound')))

#週ごとに記事件数の取得
@asyncio.coroutine
def getArticleNumber(index, numbersArray, prefix, keywords, startDate):
    #検索日付の設定
    weekStartDate = startDate + datetime.timedelta(days = 7 * index[1])
    weekEndDate = weekStartDate + datetime.timedelta(days = 6)

    #URLの作成と読み込み
    q = 'Body:' + keywords[index[0]] + ' AND ' + 'ReleaseDate:[' + weekStartDate.strftime('%Y-%m-%d') + ' TO ' + weekEndDate.strftime('%Y-%m-%d') + ']'
    url = prefix + 'q=' +  urllib.parse.quote(q.encode('utf-8'))
    page = yield from get(url)

    #XMLを解析して件数を取得
    numbersArray[index[0]][index[1]] = analyzeAsahiXML(page)

#相関係数の計算 (総件数が0ならNaNを返す)
def calcCoefficients(coefficientsArray, numbersArray, keywordNumber):
    #各キーワードの総件数の計算
    totalNumbersArray = numpy.zeros(keywordNumber, numpy.int)
    for i in range(0, keywordNumber):
        totalNumbersArray[i] = numbersArray[i].sum()

    #相関係数の計算
    index = 0
    for i in range(0, keywordNumber):
        for j in range(0, i):
            if ((totalNumbersArray[i] != 0) and (totalNumbersArray[j] != 0)):
                coefficientsArray[index] = numpy.corrcoef(numbersArray[i], numbersArray[j])[0, 1]
            else:
                coefficientsArray[index] = numpy.NaN
            index += 1

#XMLを解析して品詞リストを取得
def analyzePOSXML(posArray, page):
    root = ET.fromstring(page)
    for e in root.getiterator('{urn:yahoo:jp:jlp}word'):
        pos = e.find('.//{urn:yahoo:jp:jlp}pos')
        if (pos.text != '特殊'):
            posArray.append(pos.text)

#品詞が全て等しいかを調べる
@asyncio.coroutine
def checkPOS(prefix, keywords, keywordNumber):
    #形態要素解析
    posArray = []

    #URLの作成と読み込み
    sentence = keywords[0]
    for i in range(1, keywordNumber):
        sentence += ',' + keywords[i]
    url = prefix + 'sentence=' + urllib.parse.quote(sentence)
    page = yield from get(url)

    #XMLを解析して品詞リストを取得
    analyzePOSXML(posArray, page)

    #品詞がすべて等しいかを確認
    posChecker = True
    for pos in posArray:
        if (pos != posArray[0]):
            posChecker = False
    
    return (posChecker)

def main(argv):
    #jsonを用いてキーワードをパース
    jsonString = '{"keywords":' + os.fsencode(argv[0]).decode('utf-8') + '}'
    jsonComponent = json.loads(jsonString)
    keywordNumber = len(jsonComponent['keywords'])
 
    #キーワードリストを作成
    Keywords = []
    for i in range(0, keywordNumber):
        Keywords.append(jsonComponent['keywords'][i])

    #開始日時と終了日時をパース
    startDate = datetime.datetime.strptime(os.fsencode(argv[1]).decode('utf-8'), '%Y-%m-%d')
    endDate = datetime.datetime.strptime(os.fsencode(argv[2]).decode('utf-8'), '%Y-%m-%d')

    #週数を取得
    weekNum = getWeekNum(startDate, endDate)

    #件数保存用の配列を初期化
    numbersArray = numpy.ones([keywordNumber, weekNum], numpy.int)

    #記事検索用のプレフィックスを作成
    prefix = 'http://54.92.123.84/search?'
    query = [
        ('ackey', '869388c0968ae503614699f99e09d960f9ad3e12'),
        ('rows', '1'),
    ]
    for item in query:
        prefix += item[0] + "=" + item[1] + "&"

    #記事検索
    indexList = []
    for i in range(0, keywordNumber):
        for j in range(0, weekNum):
            indexList.append((i, j))

    loop = asyncio.get_event_loop()
    f = asyncio.wait([getArticleNumber(i, numbersArray, prefix, Keywords, startDate) for i in indexList])
    loop.run_until_complete(f)

    #相関係数保存用の配列を初期化
    coefficientsArrayNumber = (1 + keywordNumber) * keywordNumber // 2
    coefficientsArray = numpy.empty(coefficientsArrayNumber, numpy.double)

    #相関係数の計算
    calcCoefficients(coefficientsArray, numbersArray, keywordNumber)

    #形態要素解析用のプレフィックスを作成
    prefix = 'http://jlp.yahooapis.jp/MAService/V1/parse?'
    query = [
        ('appid', 'dj0zaiZpPU84QnlScDdxM1p5NSZzPWNvbnN1bWVyc2VjcmV0Jng9MjY-'),
        ('results', 'ma'),
    ]
    for item in query:
        prefix += item[0] + "=" + item[1] + "&"

    #品詞が全て等しいかを調べる
    posChecker = loop.run_until_complete(checkPOS(prefix, Keywords, keywordNumber))

    #出力を整形
    string = '{"coefficients":['

    #相関係数を出力
    indexstart = 0
    for i in range(0, keywordNumber):
        string += '['
        index = indexstart

        #i > j
        for j in range(0, i):
            if (not numpy.isnan(round(coefficientsArray[index],3))):
                string += str(round(coefficientsArray[index],3))
            else:
                string += 'null'
            string += ','
            index += 1

        #i = j
        string += "1" + ','
        index += indexstart + i

        #i < j
        for j in range(i + 1, keywordNumber):
            if (not numpy.isnan(round(coefficientsArray[index],3))):
                string += str(round(coefficientsArray[index],3))
            else:
                string += 'null'
            string += ','
            index += j

        string = string[:-1]
        string += '],'
        indexstart += i

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
