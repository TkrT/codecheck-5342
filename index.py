# coding: utf-8

import sys
from app.main import main

#デフォルトのエンコーディングをUTF-8に設定
reload(sys)
sys.setdefaultencoding('utf-8')

#実行
main(sys.argv[1:])
