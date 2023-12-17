# suumo上のURLから物件情報を取得してくる

from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import csv
import re

# https://suumo.jp/chintai/tokyo/city/
# このサイトから住みたい物件の条件を指定して検索したURLを base_url に入力する
base_url = input("SUUMOの検索結果URLを入力してください: ")

@retry(tries=3, delay=10, backoff=2)
def get_html(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	return soup

all_data = []
max_page = 1

# ここで検索する物件数を設定できます
max_item = 3

for page in range(1, max_page+1):
	# URLを定義 
	url = base_url.format(page)
	
	# HTMLを取得
	soup = get_html(url)
	
	# すべての項目を抽出する
	items = soup.findAll("div", {"class": "cassetteitem"})
	print("page", page, "items", len(items))
	
	# 異なる建物の情報
	for index, item in enumerate(items):
		if index < max_item:
			stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
			
			# 異なる最寄駅の情報
			for index, station in enumerate(stations):
				if index % 3 == 0:
					base_data = {}

					# ベースの情報
					base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
					base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
					base_data["アクセス"] = station.getText().strip()
					# base_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
					# base_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
					# base_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()
					
					# 同じ建物の異なる部屋の情報（今回のシステムとしては建物の場所が分かれば良いから部屋の違いだけなら省略）
					tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
					
					for index, tbody in enumerate(tbodys):
						if index == 0:
							data = base_data.copy()

							data["階数"] = tbody.findAll("td")[2].getText().strip()
							data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
							# data["管理費"] = tbody.findAll("td")[3].findAll("li")[1].getText().strip()
							# data["敷金"] = tbody.findAll("td")[4].findAll("li")[0].getText().strip()
							# data["礼金"] = tbody.findAll("td")[4].findAll("li")[1].getText().strip()
							# data["間取り"] = tbody.findAll("td")[5].findAll("li")[0].getText().strip()
							# data["面積"] = tbody.findAll("td")[5].findAll("li")[1].getText().strip()
							
							data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")
							
							all_data.append(data)

# データフレームに変換
df = pd.DataFrame(all_data)

# CSVとして出力
df.to_csv("property_information.csv")

# 各列の値を格納するための配列
names = []
addresses = []
accesses = []
floors = []
rents = []
urls = []
stations = []
walk_times = []

# CSVファイルを開いてデータを読み込む
with open("property_information.csv", mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)

    # ヘッダー行をスキップ
    next(reader)

    # 各行に対して処理を行う
    for row in reader:
        name = row[1].replace('　', ' ')
        names.append(name)     # 名称
        addresses.append(row[2]) # アドレス
        accesses.append(row[3])  # アクセス
        floors.append(row[4])    # 階数
        rents.append(row[5])     # 家賃
        urls.append(row[6])      # URL

# 最寄り駅と最寄りまでの歩行時間の結果を格納するための配列
for text in accesses:
    # "駅"までの文字列を取得
    station_name = text.split("駅")[0] + "駅"
    stations.append(station_name)

    # "歩"と"分"の間の整数を抽出
    walk_minutes = re.search(r'歩(\d+)分', text)
    walk_minutes = int(walk_minutes.group(1)) if walk_minutes else None
    walk_times.append(walk_minutes)

# 結果を表示（テスト用）
print("名称:", names)
print("アドレス:", addresses)
print("アクセス:", accesses)
print("階数:", floors)
print("家賃:", rents)
print("URL:", urls)
print("stations:", stations)
print("walk_times:", walk_times)
