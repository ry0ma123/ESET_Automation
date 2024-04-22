#!/usr/bin/env python3
import getpass, json, urllib.parse, urllib.request, re, datetime, os

#Replace here to your own region
url = "https://jpn.business-account.iam.eset.systems/" 
detection_url = "https://jpn.incident-management.eset.systems/v1/detections?pageSize=10000"

#ユーザ名チェック関数
def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    else:
        return False

# Username, Password
print("APIの実行権があるユーザーアカウントのユーザー名とパスワードを入力してください")
for attempt in range(3):
    username = input("ユーザ名を入力してください: ")
    if validate_email(username):
        print(f"パスワードを入力してください")
        break
    else:print(f"正しいメールアドレスを入力してください。残り試行回数: {2 - attempt}")
else:
    raise Exception('Error:'"正しいユーザー名を確認し、最初からやり直してください")

password = getpass.getpass("パスワード：")

# 認証
auth = url + "/oauth/token"
headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}
data = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "client_id": "", 
    "client_secret": "",  
    "refresh_token": "",  
}

data = urllib.parse.urlencode(data).encode("utf-8")
req = urllib.request.Request(auth, data=data, headers=headers)
with urllib.request.urlopen(req) as response:
    status_code = response.status
    if status_code != 200:
        raise Exception(f"Error: 認証に失敗しました、ユーザ名とパスワード、ネットワーク接続状況をご確認ください:{{'error code': {status_code}}}")
    else:
        response_data = response.read().decode("utf-8")
        response_json = json.loads(response_data)
        access_token = response_json.get("access_token")
        refresh_token = response_json.get("refresh_token")

print("access_tokenの取得が完了しました")
print("処理中です...少々お待ちください")
api_key = "Bearer "+ access_token
#print(api_key)

#検知ログを取得
headers = {
    'accept': 'application/json',
    'Authorization': api_key}

request = urllib.request.Request(detection_url, headers=headers)
response = urllib.request.urlopen(request)

# レスポンスの内容を表示
now = datetime.datetime.now()
json_data = json.load(response)
filename = f"Inspect_detctions_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"

# 検知ログを保存
with open(filename, 'w', encoding='utf-8') as outfile:
    json.dump(json_data, outfile, ensure_ascii=False, indent=4)
current_path = os.getcwd()
print("検知ログの取得に成功しました")
print(f"検知ログは {current_path}の直下に{filename} で保存されました。")
