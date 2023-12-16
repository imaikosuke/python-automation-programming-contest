# python-automation-programming-contest
このPythonコードは、SUUMOのウェブサイトから特定の物件情報を収集し、それをCSVファイルに保存するプログラムです。以下は、それぞれのブロックについてChatGPTによって解説したものです。

### 1. インポートとベースURLの設定

```python
from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd 

base_url = input("SUUMOの検索結果URLを入力してください: ")
```

- `retry`, `requests`, `BeautifulSoup`, `pandas` というライブラリをインポートします。
- `base_url` はユーザーから入力されるSUUMOの検索結果ページのURLです。

### 2. HTML取得関数

```python
@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup
```

- `get_html` 関数は、指定されたURLからHTMLを取得し、BeautifulSoupオブジェクトに変換して返します。
- `retry` デコレータは、失敗した場合に最大3回までリトライし、リトライ間の遅延は10秒、リトライ毎に遅延を2倍に増やします。

### 3. データ収集ループ

```python
all_data = []
max_page = 1

for page in range(1, max_page+1):
    url = base_url.format(page)
    soup = get_html(url)
    items = soup.findAll("div", {"class": "cassetteitem"})
    print("page", page, "items", len(items))
    ...
```

- この部分では、指定されたページ数（ここでは1ページのみ）にわたって物件データを収集します。
- `base_url` にページ番号をフォーマットしてURLを生成し、そのページのHTMLを取得します。
- その後、ページ内のすべての物件を表す要素を取得します。

### 4. 各物件の詳細データ収集

```python
for item in items:
    stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
    for index, station in enumerate(stations):
        if index % 3 == 0:
            base_data = {}
            base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
            base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
            base_data["アクセス"] = station.getText().strip()
            tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
            ...
```

- 各物件に対して、最寄り駅や物件の基本情報（名称、アドレス、アクセス）を収集します。
- このコードでは一部の情報（例：カテゴリー、築年数、構造）はコメントアウトされており、収集されません。

### 5. 各部屋の詳細データ収集

```python
for index, tbody in enumerate(tbodys):
    if index == 0:
        data = base_data.copy()
        data["階数"] = tbody.findAll("td")[2].getText().strip()
        data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
        data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")
        all_data.append(data)
```

- 同じ建物内の異なる部屋の情報（階数、家賃）を収集します。部屋ごとの詳細な情報（管理費、敷金、礼金、間取り、面積）は省略されています。
-

 各部屋の詳細ページへのURLも収集されます。

### 6. CSVへの出力

```python
df = pd.DataFrame(all_data)
df.to_csv("property_information.csv")
```

- 収集したデータをPandasのデータフレームに変換し、CSVファイルとして保存します。