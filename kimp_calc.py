# -*- coding:utf8 -*-

from rich.console import Console
from rich.table import Table
from rich.live import Live

from time import sleep

import requests
import ccxt
import pyupbit

version = '1.0.0'
headers = {'User-Agent': 'Mozilla/5.0 '
                         '(Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/90.0.4430.85 Safari/537.36'}

# dunamu(upbit) USD <-> KRW exchange rate open api
exchange_rate_api_url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
console = Console()


def get_exchange_rate(usd):
    exchange = requests.get(exchange_rate_api_url, headers=headers).json()

    return round(float(exchange[0]['basePrice']) * usd)


def calculate_kimp() -> (float, float, float, float, float, bool):
    ccxt_binance = ccxt.binance()
    binance_btc_ticker = ccxt_binance.fetch_ticker('BTC/USDT')
    btc_usd = float(binance_btc_ticker['close'])  # Get realtime Binance USD price
    btc_binance_krw = get_exchange_rate(btc_usd)  # Convert Binance USD exchange KRW price use realtime exchange_rate
    btc_upbit_krw = pyupbit.get_current_price('KRW-BTC')  # Get realtime Upbit KRW price
    is_kimp = btc_upbit_krw >= btc_binance_krw  # Check current state is Kimchi Premium or Yeok Premium
    btc_subtract = \
        btc_upbit_krw - btc_binance_krw if is_kimp else btc_binance_krw - btc_upbit_krw  # high price - low_price

    btc_percentage = btc_upbit_krw / btc_binance_krw if is_kimp else btc_binance_krw / btc_upbit_krw
    btc_percentage = round((btc_percentage - 1) * 100.0, 2)  # Get percentage

    if not is_kimp:
        btc_percentage *= -1

    return btc_usd, btc_binance_krw, round(btc_upbit_krw), round(btc_subtract), btc_percentage, is_kimp


def generate_kimp_table(result: tuple) -> Table:
    btc_usd, btc_binance_krw, btc_upbit_krw, btc_subtract, btc_percentage, is_kimp = result

    kimp_table = Table(border_style='#FF6CEB')
    kimp_table.add_column('Binance USDT', header_style='bold #F2CB61', style='bold #EAEAEA', justify='center')
    kimp_table.add_column('Binance KRW', header_style='bold #F2CB61', style='bold #EAEAEA', justify='center')
    kimp_table.add_column('Upbit KRW', header_style='bold #5587ED', style='bold #EAEAEA', justify='center')
    kimp_table.add_column('Subtract KRW', header_style='bold deep_pink3',
                          style='bold #47C83E' if is_kimp else 'bold #FF4848', justify='center')
    kimp_table.add_column('Percentage', header_style='bold dark_violet',
                          style='bold #47C83E' if is_kimp else 'bold #FF4848', justify='center')
    kimp_table.add_row(f'$ {format(btc_usd, ",")}', f'{format(btc_binance_krw, ",")} KRW',
                       f'{format(btc_upbit_krw, ",")} KRW', f'{format(btc_subtract, ",")} KRW',
                       f'{format(btc_percentage, ",")} %')

    return kimp_table


def main():
    with Live(generate_kimp_table(calculate_kimp()), auto_refresh=False, transient=True) as live:
        live.console.print(f'[*] Kimp Calculator v{version}', style='bold #47C83E')
        live.console.print('[*] If you exit calculator -> ctrl + C', style='bold #47C83E')

        while True:
            sleep(1)
            live.update(generate_kimp_table(calculate_kimp()), refresh=True)


if __name__ == '__main__':
    main()
