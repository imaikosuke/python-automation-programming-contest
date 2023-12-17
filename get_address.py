# suumo上のURLから物件情報を取得してくる

from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import csv
import re

def get_address(base_url):

	@retry(tries=3, delay=10, backoff=2)
	def get_html(url):
		try:
			r = requests.get(url)
			r.raise_for_status()  # HTTPリクエストのステータスチェック
			soup = BeautifulSoup(r.content, "html.parser")
			return soup
		except requests.exceptions.RequestException as e:  # リクエストエラーのキャッチ
			print(f"リクエストエラー: {e}")
			return None  # エラーが発生した場合、Noneを返す

	all_data = []
	max_page = 1 # SUUMOで検索するページ数
	max_item = 3 # SUUMOで検索する1ページごとの物件数

	for page in range(1, max_page+1):
		url = base_url.format(page)                            # URLを定義
		soup = get_html(url)                                   # HTMLを取得
		if soup is None:                                       # soupがNoneの場合、次のページへスキップ
			continue
		items = soup.findAll("div", {"class": "cassetteitem"}) # 全ての項目を抽出する

		# 異なる建物の情報
		for index, item in enumerate(items):
			if index < max_item:
				stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
				
				# 異なる最寄駅の情報
				for index, station in enumerate(stations):
					if index % 3 == 0:
						base_data = {}

						# ベースの情報
						property_name = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
						base_data["名称"] = property_name.replace('　', ' ')
						base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
						base_data["アクセス"] = station.getText().strip()
						# 同じ建物の異なる部屋の情報（今回のシステムとしては建物の場所が分かれば良いから部屋の違いだけなら省略）
						tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
						
						for index, tbody in enumerate(tbodys):
							if index == 0:
								data = base_data.copy()

								data["階数"] = tbody.findAll("td")[2].getText().strip()
								data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
								data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")
								all_data.append(data)

	df = pd.DataFrame(all_data)  # データフレームに変換
	try:
		df.to_csv("property_information.csv") # CSVとして出力
	except Exception as e:  # 追加: ファイル操作のエラーをキャッチ
		print(f"ファイル書き込みエラー: {e}")
		return None

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
	try:
		with open("property_information.csv", mode='r', newline='', encoding='utf-8') as file:
			reader = csv.reader(file)

			# ヘッダー行をスキップ
			next(reader)

			# 物件情報を保存する配列(物件名, 駅名, 駅徒歩時間)
			property_info = []

			# 各行に対して処理を行う
			for row in reader:
				walk_minutes = re.search(r'歩(\d+)分', row[3])
				walk_minutes = int(walk_minutes.group(1)) if walk_minutes else None

				# walk_minutesがNoneでない場合のみ処理を続ける
				if walk_minutes is not None:
					name = row[1].replace('　', ' ')
					names.append(name)        # 名称
					addresses.append(row[2])  # アドレス
					accesses.append(row[3])   # アクセス
					floors.append(row[4])     # 階数
					rents.append(row[5])      # 家賃
					urls.append(row[6])       # URL

					# 最寄り駅と最寄りまでの歩行時間の結果を格納
					station_name = row[3].split("駅")[0] + "駅"
					stations.append(station_name)
					walk_times.append(walk_minutes)
	except Exception as e:  # ファイル読み込みエラーのキャッチ
		print(f"ファイル読み込みエラー: {e}")
		return None

	#物件情報を保存する配列(物件名, 駅名,　駅徒歩時間)
	property_info = [names, stations, walk_times]

	# 結果を表示（テスト用）
	# print("名称:", names)
	# print("アドレス:", addresses)
	# print("アクセス:", accesses)
	# print("階数:", floors)
	# print("家賃:", rents)
	# print("URL:", urls)
	# print("stations:", stations)
	# print("walk_times:", walk_times)

	return(property_info)