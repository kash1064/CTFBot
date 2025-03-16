# Discord bot

## 利用方法

1. developers portalにアクセス。
https://discord.com/developers/applications
2. New Application > CreateでBotを作る。
3. OAuth2 > SCOPESでbotを選択
4. Bot PERMISSIONSで、`Manage Roles`, `Manage Channels`, `View Channels`を選択。
5. Generated URLにアクセスを行い、自身のサーバにBotを入れてあげる。
6. Bot画面
   7. TOKENを取得し、.envに`TOKEN=<値>`と書き込む
   8. Privileged Gateway Intent部分の以下の箇所にチェックを入れる。
      - Server Members Intent
      - Message Content Intent

## /get_event

### event登録
直近で開催されるCTF Eventを5つ取得し、表示してくれます。
(現在開催中のCTFは含みません。)

![](image/2025-03-16-15-29-30.png)

![](image/2025-03-16-15-30-10.png)

いずれかを選択すると、以下のように情報が出ます。

![](image/2025-03-16-15-30-44.png)

「送信」を押下すると、private categoryが作成されます。

![](image/2025-03-16-15-32-54.png)

### event参加

CTF 参加者は、Botが発言した「registered xxxCTF」のメッセージに対して何らかのリアクションを押すと、Botがカテゴリへの参加権を与えてくれます。

## /set_event <id>

`/set_event`は任意のeventを設定可能なコマンドです。

### id指定する方法

例えば、`SECCON CTF 13 Quals`は、CTFTimeのURLは`https://ctftime.org/event/2478`です。
この時、`2478`がidとなります。

![](image/2025-03-16-15-41-25.png)

このように入力すると、CTFTimeからいい感じに情報を取得してくれます。

![](image/2025-03-16-15-41-51.png)

### id指定しない方法

`/set_event`を入力するだけです。
以下のような画面出ます。

![](image/2025-03-16-15-44-03.png)

CTF Timeに登録されていないやつを登録するために存在しています。
