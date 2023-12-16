# suumo上のURLから住居情報を取得してくる

from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd 

# https://suumo.jp/chintai/tokyo/city/
# このサイトから住みたい物件の条件を指定して検索したURLを base_url に入力する
#　いまは定数になってるけど、コマンドラインから手動でURLを入力するようにする必要があります
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rsnflg=1&rn=0005&rn=0395&ek=000519670&ek=039502890&ek=000505050&ra=013&cb=0.0&ct=3.0&et=9999999&mb=0&mt=9999999&cn=9999999&fw2="

@retry(tries=3, delay=10, backoff=2)
def get_html(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	return soup

all_data = []
max_page = 1

for page in range(1, max_page+1):
	# URLを定義 
	url = base_url.format(page)
	
	# HTMLを取得
	soup = get_html(url)
	
	# すべての項目を抽出する
	items = soup.findAll("div", {"class": "cassetteitem"})
	print("page", page, "items", len(items))
	
	# 異なる建物の情報
	for item in items:
		stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
		
		# 異なる最寄駅の情報
		for index, station in enumerate(stations):
			if index % 3 == 0:
				base_data = {}

				# ベースの情報
				base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
				# base_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
				base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
				base_data["アクセス"] = station.getText().strip()
				# base_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
				# base_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()
				
				# 同じ建物の異なる部屋の情報（今回のシステムとしては建物の場所が分かれば良いから部屋の違いだけなら省略）
				tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
				
				for index, tbody in enumerate(tbodys):
					if index % 3 == 0:
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
