# PivotBot

This bot's only purpose is to send Pivot Points at UTC 00:00:30 to a telegram channel or chat.

## Exchanges

At the moment, these are the exchanges supported implemented using [ccxt](https://github.com/ccxt/ccxt):

* Kucoin - BTC/USD
* Bitmex - BTC/USD
* Bybit - BTC/USD
* Binance - BTC/USDT

## Running

```
$ python3 -m virtualenv env
$ . env/bin/activate
$ pip install -r requirements.txt
$ export TELEGRAM_TOKEN=your_bot_token_from_botfather
$ export TELEGRAM_USER_ID=also_known_as_chat_id
$ python app.py
```

### Docker

```
$ docker pull tistaharahap/pivotbot:latest
$ docker run --name pivotbot -e TELEGRAM_TOKEN=your_bot_token_from_botfather -e TELEGRAM_USER_ID=also_known_as_chat_id tistaharahap/pivotbot:latest
```
