import ccxt
import telepot
import requests
import random

from os import environ, getcwd
from pivotbot.logger import get_logger
from pivotbot.jokes import jokes
from ccxt.base.exchange import Exchange
from typing import Dict
from string import Template

USER_AGENT = environ.get('USER_AGENT', 'PivotBot')
TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN', '472836801:AAGQgDhB0dg471Nvqc9RjqiXZJ4K2qnieHQ')
TELEGRAM_USER_ID = environ.get('TELEGRAM_USER_ID', '-1001351609280')

logger = get_logger()


def get_ccxt_client(exchange: str, api_key: str = None, api_secret: str = None, testnet: bool = True) -> Exchange:
    try:
        exc = getattr(ccxt, exchange)
    except AttributeError:
        raise AttributeError(f'The exchange {exchange} is not supported')

    current_path = getcwd()
    with open(f'{current_path}/version.txt', 'r') as f:
        version = f.readline()

    headers = {
        'User-Agent': f'{USER_AGENT}/v{version}'
    }

    if api_key and api_secret:
        exchange = exc({
            'apiKey': api_key,
            'secret': api_secret,
            'headers': headers
        })
    else:
        exchange = exc({
            'headers': headers
        })

    if testnet:
        if 'test' in exchange.urls:
            exchange.urls['api'] = exchange.urls['test']
        else:
            raise NotImplementedError('Testnet is wanted but the exchange does not support testnet')

    return exchange


async def get_pivot_points(exchange: str, symbol: str) -> Dict:
    client = get_ccxt_client(exchange=exchange,
                             testnet=False)
    logger.info(f'Exchange: {exchange}')
    logger.info(f'Symbol: {symbol}')

    if not client.has['fetchOHLCV']:
        raise NotImplementedError('This exchange does not implement OHLCV feature')

    ohlcv = client.fetchOHLCV(symbol=symbol,
                              timeframe='1d',
                              limit=10)
    yesterday = ohlcv[-2]

    prices = {
        'open': float(yesterday[1]),
        'high': float(yesterday[2]),
        'low': float(yesterday[3]),
        'close': float(yesterday[4]),
    }

    pp = (prices.get('high') + prices.get('low') + prices.get('close')) / 3

    pivot = {
        'exchange': exchange,
        'symbol': symbol,
        'r4': f"{pp + (prices.get('high') - prices.get('low')) * 3:.2f}",
        'mpr3': f"{((pp + (prices.get('high') - prices.get('low')) * 3) + (prices.get('high') + 2 * (pp - prices.get('low')))) / 2:.2f}",
        'r3': f"{prices.get('high') + 2 * (pp - prices.get('low')):.2f}",
        'mpr2': f"{((prices.get('high') + 2 * (pp - prices.get('low'))) + (pp + (prices.get('high') - prices.get('low')))) / 2:.2f}",
        'r2': f"{pp + (prices.get('high') - prices.get('low')):.2f}",
        'mpr1': f"{((pp + (prices.get('high') - prices.get('low'))) + ((2 * pp) - prices.get('low'))) / 2:.2f}",
        'r1': f"{(2 * pp) - prices.get('low'):.2f}",
        'mpr0': f"{(((2 * pp) - prices.get('low')) + pp) / 2:.2f}",
        'pp': f"{pp:.2f}",
        'mps0': f"{(pp + (2 * pp) - prices.get('high')) / 2:.2f}",
        's1': f"{(2 * pp) - prices.get('high'):.2f}",
        'mps1': f"{(((2 * pp) - prices.get('high')) + (pp - (prices.get('high') - prices.get('low')))) / 2:.2f}",
        's2': f"{pp - (prices.get('high') - prices.get('low')):.2f}",
        'mps2': f"{((pp - (prices.get('high') - prices.get('low'))) + (prices.get('low') - 2 * (prices.get('high') - pp))) / 2:.2f}",
        's3': f"{prices.get('low') - 2 * (prices.get('high') - pp):.2f}",
        'mps3': f"{((prices.get('low') - 2 * (prices.get('high') - pp)) + (pp - (prices.get('high') - prices.get('low')) * 3)) / 2:.2f}",
        's4': f"{pp - (prices.get('high') - prices.get('low')) * 3:.2f}",
    }
    logger.info(f'R4: ${pivot.get("r4")}')
    logger.info(f'MP: ${pivot.get("mpr3")}')
    logger.info(f'R3: ${pivot.get("r3")}')
    logger.info(f'MP: ${pivot.get("mpr2")}')
    logger.info(f'R2: ${pivot.get("r2")}')
    logger.info(f'MP: ${pivot.get("mpr1")}')
    logger.info(f'R1: ${pivot.get("r1")}')
    logger.info(f'MP: ${pivot.get("mpr0")}')
    logger.info(f'PP: ${pivot.get("pp")}')
    logger.info(f'MP: ${pivot.get("mps0")}')
    logger.info(f'S1: ${pivot.get("s1")}')
    logger.info(f'MP: ${pivot.get("mps1")}')
    logger.info(f'S2: ${pivot.get("s2")}')
    logger.info(f'MP: ${pivot.get("mps2")}')
    logger.info(f'S3: ${pivot.get("s3")}')
    logger.info(f'MP: ${pivot.get("mps3")}')
    logger.info(f'S4: ${pivot.get("s4")}')

    return pivot


async def chucknorris() -> str:
    url = 'https://api.chucknorris.io/jokes/random'

    try:
        resp = requests.get(url)
        json = resp.json()
        joke = json.get('value')
        return joke
    except requests.exceptions.RequestException:
        return random.choice(jokes)


async def send_telegram_msg(pivots: list):
    bot = telepot.Bot(token=TELEGRAM_TOKEN)

    def transform_pivot_to_message_entry(pivot: Dict) -> str:
        with open('pivotbot/templates/pivot-entry.txt', 'r') as f:
            src = Template(f.read())
            values = {
                'exchange': pivot.get('exchange'),
                'symbol': pivot.get('symbol'),
                'r4': pivot.get('r4'),
                'mpr3': pivot.get('mpr3'),
                'r3': pivot.get('r3'),
                'mpr2': pivot.get('mpr2'),
                'r2': pivot.get('r2'),
                'mpr1': pivot.get('mpr1'),
                'r1': pivot.get('r1'),
                'mpr0': pivot.get('mpr0'),
                'pp': pivot.get('pp'),
                'mps0': pivot.get('mps0'),
                's1': pivot.get('s1'),
                'mps1': pivot.get('mps1'),
                's2': pivot.get('s2'),
                'mps2': pivot.get('mps2'),
                's3': pivot.get('s3'),
                'mps3': pivot.get('mps3'),
                's4': pivot.get('s4'),
            }

            return src.substitute(values)

    pivots = [transform_pivot_to_message_entry(pivot) for pivot in pivots]

    async def get_full_message(pvs) -> str:
        with open('pivotbot/templates/pivot-whole-msg.txt', 'r') as f:
            src = Template(f.read())
            entry_messages = ''.join(pvs)
            values = {
                'pivots': entry_messages,
                'chucknorris': await chucknorris(),
            }

            return src.substitute(values)

    message = await get_full_message(pivots)

    bot.sendMessage(chat_id=TELEGRAM_USER_ID,
                    text=message,
                    parse_mode='HTML')


async def tick():
    exchanges = [
        ['kucoin', 'BTC/USDT'],
        ['bitmex', 'BTC/USD'],
        ['bybit', 'BTC/USD'],
        ['binance', 'BTC/USDT'],
    ]

    pivots = [await get_pivot_points(x[0], x[1]) for x in exchanges]

    await send_telegram_msg(pivots=pivots)

