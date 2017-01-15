# コマンドラインアプリケーション(CLI アプリ)作成用テンプレート(Python2.x)

[main.py](app/main.py)を編集して、CLIアプリを実装してください。  
チャレンジ内でファイルの作成が許可されていれば、可読性等のためにファイルを分割する事も可能です。

## コマンドライン引数の取得方法
[main.py](app/main.py)内で定義されている、`main`という関数から、 `argv` の名前で取得可能です。  

``` python
def main(argv):
    # code to run
```

ここでの `argv` は [index.py](index.py) から渡されるもので、`sys.argv` の内容からスクリプト名の情報を抜いたデータが入ります。


## コマンド実行結果の標準出力への出力
`stdout`への出力は標準の`print`メソッドが使用可能です。

``` python
print(result)
```

## 外部ライブラリの追加方法
外部ライブラリを使用する場合は以下の手順で実施してください。

- [requirements.txt](requirements.txt)にライブラリ名とバージョンを記述
