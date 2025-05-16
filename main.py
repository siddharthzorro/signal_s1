import os
import requests
import pandas as pd
import ta
from datetime import datetime

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

def get_binance_ohlcv(symbol, interval='4h', limit=200):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def check_signal(symbol):
    df = get_binance_ohlcv(symbol)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['ema200'] = ta.trend.ema_indicator(df['close'], window=200)
    macd_line = ta.trend.macd(df['close'], window_slow=26, window_fast=12)
    macd_signal = ta.trend.macd_signal(df['close'], window_slow=26, window_fast=12, window_sign=9)
    rsi = ta.momentum.rsi(df['close'], window=14)

    df['macd'] = macd_line
    df['macd_signal'] = macd_signal
    df['rsi'] = rsi

    last = df.iloc[-1]
    prev = df.iloc[-2]

    long_entry = last['ema50'] > last['ema200'] and last['macd'] > last['macd_signal'] and last['rsi'] > prev['rsi'] and last['rsi'] < 80
    short_entry = last['ema50'] < last['ema200'] and last['macd'] < last['macd_signal'] and last['rsi'] < prev['rsi'] and last['rsi'] > 20

    symbol_readable = symbol.replace('USDT', '')
    if long_entry:
        send_telegram(f"📈 LONG Signal - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")
    elif short_entry:
        send_telegram(f"📉 SHORT Signal - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")

if __name__ == "__main__":
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        check_signal(symbol)
