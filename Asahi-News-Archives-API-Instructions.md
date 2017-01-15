
朝日新聞アーカイブ記事API 利用方法

## 1. 問合せURL
http://54.92.123.84/search?［検索パラメータ］

## 2. 検索パラメータ
- 「ackey」(必須）：アクセスキー
- 「q」（必須）：検索条件
- 「sort」：検索結果の並び順を指定
- 「start」：検索結果に含める最初のレコード（デフォルトは1件目から）
- 「rows」：検索結果に含めるレコードの件数（デフォルトは10件）
- 「wt」：検索結果のフォーマットを指定(デフォルトはxml）

## 3. パラメータ詳細

##### ackeyパラメータ（必須）  
朝日新聞アーカイブ記事APIにリクエストを送る際に必要なアクセスキー(ackey)は以下の文字数列です:
```
869388c0968ae503614699f99e09d960f9ad3e12
```

##### qパラメータ（必須）  
 - 検索クエリ「q=検索条件」で指定してください。  
※検索条件指定方法は、フィールド名:値  
※複数の条件を指定する場合は「 AND 」や「 OR 」で条件を結合。範囲指定は「TO」  
※クエリは必須のため、検索条件を指定しない場合には「q=*:*」として指定。  
※検索クエリはurlエンコード。

- 検索対象フィールドとデータ
 - `フィールド`: 内容
 - `Id`: 記事ID（記事ごとにユニークなID）
 - `PageName`: 掲載面名
 - `Title`: 記事見出し
 - `Body`: 記事本文
 - `Category`: カテゴリ（掲載面を元にした大カテゴリ）
 - `SubCategory`: サブカテゴリ（掲載面を元にしたサブカテゴリ）
 - `Keyword`: キーワード
 - `PublicationKind`: 朝刊・夕刊種別（M or E)
 - `ReleaseDate`: 掲載日
 - `WordCount`: 本文に含まれる文字数
 - `Page`: 掲載頁


- 検索例
 - (例１)記事IDで検索する「q=Id:記事ID」    
   `http://54.92.123.84/search?q=Id:A1001120160420E002204-005&ackey=［アクセスキー］`
 - (例２)見出し、本文をAND検索 「q=Title:地方 AND Body:神奈川」    
   `http://54.92.123.84/search?q=Title:地方 AND Body:神奈川&ackey=［アクセスキー］`
 - (例３)日付を範囲で指定  「ReleaseDate:［日付 TO 日付］」    
   `http://54.92.123.84/search?q=Title:* AND ReleaseDate:[2016-03-31 TO 2016-04-30]&ackey=［アクセスキー］`
 - (例４)カテゴリを指定して検索 「Category:地方」  
   `http://54.92.123.84/search?q= Category:地方&ackey=［アクセスキー］  `
 - (例５)文字数の範囲を指定して検索 「WordCount:[20 TO% 100]」    
   ` http://54.92.123.84/search?q=WordCount:[20 TO 100]&ackey=［アクセスキー］`
 - (例６）見出しとカテゴリのAND検索 「Title:横浜 AND Category:地方」    
   `http://54.92.123.84/search?q= Title:横浜 AND Category:地方&ackey=［アクセスキー］`

##### 「sort」パラメータ
 - 検索結果の並び順を指定  
「sort=フィールド名 asc|desc」  
※複数のフィールドを使用する場合、カンマ区切り  

 - (例）  
`http://54.92.123.84/search?q=*:*&sort=ReleaseDate descPage desc&ackey=［アクセスキー］`


##### 「start」パラメータ
 - 検索結果に含める最初のレコード（デフォルトは1件目から）  

 - (例）検索結果の11件目から返す場合「start=10」  
`http://54.92.123.84/search?q=*:*&start=10&ackey=［アクセスキー］`

##### 「rows」パラメータ
 - 検索結果に含めるレコードの件数（デフォルトは10件最大１００件まで）  

 - (例）検索結果を20件取得する場合「rows=20」  
`http://54.92.123.84/select?q=*:*&rows=20&ackey=［アクセスキー］`

##### 「wt」
 - 検索結果のフォーマットを指定（デフォルトはxml)  
「wt=xml」(デフォルト)  
「wt=json」  

 - (例）jsonで取得  
`http://54.92.123.84/search?q=*:*&wt=json&ackey=［アクセスキー］`


## ４. レスポンス

- レスポンス [内容]

```
<response> [XMLヘッダー（固定）]
　　<status>Data</status>[リクエストに対する実行結果の成否。OKかNGで返却。]
　　<code>Data</code>[実行結果のステータスコード]
　　<result numFound=""Data"" start=""Data"">[リクエストに対する結果。次の属性を持つ。]  
           [numFound：マッチした記事の総数。]
           [start：返却した検索結果に含まれる記事の最初のポジション]
　　　　<doc>
　　　　　　<Id>Data</Id>[記事ID（記事ごとにユニークなID）]
　　　　　　<PageName>Data</PageName>[掲載面名]
　　　　　　<Title>Data</Title>[記事見出し]
　　　　　　<Body>Data</Body>[記事本文]
　　　　　　<Category>Data</Category>[カテゴリ（掲載面を元にした大カテゴリ）]
　　　　　　<SubCategory>Data</SubCategory>[サブカテゴリ（掲載面を元にしたサブカテゴリ）]
　　　　　　<Keyword>Data</Keyword>[キーワード]
　　　　　　<PublicationKind>Data</PublicationKind>[朝刊・夕刊種別（M or E)]
　　　　　　<ReleaseDate>Data</ReleaseDate>[掲載日]
　　　　　　<WordCount>Data</WordCount>[記事本文の文字数（文字数が多いほど扱いが大きい記事）]
　　　　　　<Page>Data</Page>掲載頁
　　　　</doc>
　　</result>
</response>
```

※記事の見出し・本文に含まれるデータでは、アルファベット、数字は全角で登録されています

- エラーレスポンス [内容]
```
<response>[XMLヘッダー（固定）]
　　<status>Data</status>[リクエストに対する実行結果の成否。OKかNGで返却。]
　　<code>Data</code>[実行結果のステータスコード]
　　<errstr>Data</errstr>[サーバーからのメッセージ]
</response>
```

５.利用制限

ＡＰＩへの極端な集中アクセスは控えてください。  
そのようなアクセスがあった場合、該当のアクセスキーからのＡＰＩ利用を制限させていただく場合があります。
