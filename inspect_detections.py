import getpass
import json
import urllib.parse
import urllib.request
import re
import datetime
import os

class API:
    def __init__(self, url, detection_url):
        self.url = url
        self.detection_url = detection_url
        self.access_token = None
        self.refresh_token = None

#ユーザ名チェック
    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

#認証
    def authenticate(self, username, password):
        auth_url = self.url + "/oauth/token"
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
        req = urllib.request.Request(auth_url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.status
                if status_code == 200:
                    print(status_code)
                    response_data = response.read().decode("utf-8")
                    response_json = json.loads(response_data)
                    self.access_token = response_json.get("access_token")
                    self.refresh_token = response_json.get("refresh_token")
                    print("アクセストークンを取得しました")
                else:
                    print(f"エラー: ステータスコード {status_code}")

#APIキー
    def get_api_key(self):
        return "Bearer " + self.access_token

def main():
    url = "https://jpn.business-account.iam.eset.systems/"
    detection_url = "https://jpn.incident-management.eset.systems/v1/detections?pageSize=10000"

    eset_api = API(url, detection_url)

    print("APIの実行権があるユーザーアカウントのユーザー名とパスワードを入力してください")
    for attempt in range(3):
        username = input("ユーザ名を入力してください: ")
        if eset_api.validate_email(username):
            break
        else:
            print(f"正しいメールアドレスを入力してください。残り試行回数: {2 - attempt}")
    else:
        raise Exception("Error: 正しいユーザー名を確認し、最初からやり直してください")

    password = getpass.getpass("パスワード：")

    eset_api.authenticate(username, password)
    api_key = eset_api.get_api_key()
    print("処理中です...少々お待ちください")

    # Acquiring detection log
    headers = {
        'accept': 'application/json',
        'Authorization': api_key
    }

    request = urllib.request.Request(detection_url, headers=headers)
    response = urllib.request.urlopen(request)

    # Saving detection logs
    now = datetime.datetime.now()
    json_data = json.load(response)
    filename = f"Inspect_detctions_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False, indent=4)
    current_path = os.getcwd()
    print("検知ログの取得に成功しました")
    print(f"検知ログは {current_path} の直下に {filename} で保存されました。")

if __name__ == "__main__":
    main()
