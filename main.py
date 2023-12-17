import re
import google_map
import config
import get_address


# https://suumo.jp/chintai/tokyo/city/
# このサイトから住みたい物件の条件を指定して検索したURLを base_url に入力する

# 2件hitのurlサンプル
# base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ek=000520110&ra=013&cb=8.5&ct=9.0&md=02&et=5&mb=0&mt=9999999&cn=9999999&fw2="

try:
	base_url = input("SUUMOの検索結果URLを入力してください: ")
	if not base_url.startswith("https://suumo.jp/"):
		raise ValueError("間違ったURL形式です。")
except ValueError as e:
	print(f"エラー: {e}")
	exit()

#物件情報が保存される配列 (駅名, 駅徒歩)
try:
	property_info = get_address.get_address(base_url)
except Exception as e:
	print(f"物件情報取得時のエラー: {e}")
	exit()

if len(property_info[0]) == 0:
	print("物件情報が見つかりませんでした。")
	exit()

for i in range(len(property_info[0])):
	point_x = property_info[0][i]   #物件名
	station = property_info[1][i]   #最寄り駅
	walk_time = property_info[2][i] #駅までの徒歩時間

	print(f'# {point_x} (最寄り駅: {station}から徒歩{walk_time}分) までの経路情報 ↓')
	for address in config.addresses:
		try:
			info = google_map.get_route_info(address[1], station)
			sum_time = walk_time + int(re.sub(r"\D", "", info["time"]))
			print(f'  - {address[0]} までの所要時間は {sum_time} 分、交通費は {info["fare"]} です。')
		except Exception as e:
			print(f"経路情報取得時のエラー: {e}")
	print("\n")