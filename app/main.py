# coding: utf-8
import sys
import json
import datetime
from datetime import datetime as dt
import urllib
import urllib2
import xml.etree.ElementTree as ET
import numpy

def main(argv):
    #jsonを用いてキーワードをパース
    jsonString = u'{"keywords":' + argv[0].decode('utf-8') + u'}'
    jsonComponent = json.loads(jsonString)
    keywordNumber = len(jsonComponent[u'keywords'])
 
    #UTF-8のキーワードリストを作成
    Keywords = []
    for i in range(0, keywordNumber):
        Keywords.append(jsonComponent[u'keywords'][i].encode('utf-8'))

    #開始日時と終了日時をパース
    startDate = dt.strptime(argv[1], u'%Y-%m-%d')
    endDate = dt.strptime(argv[2], u'%Y-%m-%d')

    #日数を取得
    dateNum = (endDate - startDate).days + 1

    #端数を削除し、週数を取得
    dateFraction = dateNum % 7
    endDate = endDate - datetime.timedelta(days=dateFraction)
    dateNum -= dateFraction
    weekNum = dateNum // 7

    #件数保存用の配列を初期化
    numbersArray = []
    for i in range(0, keywordNumber):
        numbersArray.append([])
        for j in range(0, weekNum):
            numbersArray[i].append(0)

    #クエリのプレフィックスを作成
    q = 'Body:' + Keywords[0]
    for i in range(1, keywordNumber):
        q += ' OR Body:' + Keywords[i]
    q += ' AND ReleaseDate:[' + startDate.strftime('%Y-%m-%d') + ' TO ' + endDate.strftime('%Y-%m-%d') + ']'
    urlprefix  = 'http://54.92.123.84/search?'
    urlprefix += 'ackey=869388c0968ae503614699f99e09d960f9ad3e12&'
    urlprefix += 'q=' + urllib.quote(q) + '&'
    urlprefix += 'rows=100&'

    #件数を取得
    number = -1
    index = 0
    while True:
        #クエリを作成
        url = urlprefix + 'start=' + str(index)

        #レスポンスを取得
        response = urllib2.urlopen(url)
        resdata = response.read()

        #XMLを解析して件数を取得
        root = ET.fromstring(resdata)
        if (number == -1):
            result = root.find('.//result')
            number = int(result.get('numFound'))

        #XMLを解析して週別の件数を取得
        for e in root.getiterator('doc'):
            rd = e.find('.//ReleaseDate')
            releseDate = dt.strptime(rd.text, u'%Y-%m-%d')
            week = (releseDate - startDate).days // 7

            body = e.find('.//Body')
            for i in range(0, keywordNumber):
                if (Keywords[i] in body.text):
                    numbersArray[i][week] += 1

        #インデックスを更新
        if (index > number):
            break
        index += 100

    #相関係数保存用の配列を初期化
    coefficientsArray = []
    for i in range(0, keywordNumber):
        coefficientsArray.append([])

    #相関係数の計算
    for i in range(0, keywordNumber):
        for j in range(0, keywordNumber):
            if (i != j):
                coefficientsArray[i].append(numpy.corrcoef(numbersArray[i], numbersArray[j])[0, 1])
            else:
                coefficientsArray[i].append(1)


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
        ('sentence', urllib.quote(sentence.encode('utf-8')))
    ]

    #URLの形に整形
    url = urlprefix
    for item in query:
        url += item[0] + "=" + item[1] + "&"
    url = url[:-1]

    #レスポンスを取得
    response = urllib2.urlopen(url)
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
            if (i == j):
                #同じ要素なら"1"を出力
                string += "1"
            else:
                #違う要素なら相関係数を小数点以下3桁で出力
                string += str(round(coefficientsArray[i][j],3))
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
    