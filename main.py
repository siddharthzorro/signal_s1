import os
import requests
import pandas as pd
import ta
from datetime import datetime

BOT_TOKEN = '8161960481:AAGnBkojjGDKqU1Qz-UxL6u4VGCoTUWXKFo'
CHAT_ID = '5340848858'

# In-memory position tracking (reset each time script runs)
positions = {}

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

    macd_cross_down = prev['macd'] > prev['macd_signal'] and last['macd'] < last['macd_signal']
    macd_cross_up   = prev['macd'] < prev['macd_signal'] and last['macd'] > last['macd_signal']

    symbol_readable = symbol.replace('USDT', '')
    position = positions.get(symbol, "none")

    # === Entry logic ===
    if position == "none":
        if long_entry:
            send_telegram(f"📈 LONG Entry - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")
            positions[symbol] = "long"
        elif short_entry:
            send_telegram(f"📉 SHORT Entry - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")
            positions[symbol] = "short"

    # === Exit logic ===
    elif position == "long" and macd_cross_down:
        send_telegram(f"❌ LONG Exit (MACD Cross Down) - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")
        positions[symbol] = "none"
    elif position == "short" and macd_cross_up:
        send_telegram(f"❌ SHORT Exit (MACD Cross Up) - {symbol_readable}\nPrice: {last['close']:.2f}\nTime: {datetime.utcnow()} UTC")
        positions[symbol] = "none"

if __name__ == "__main__":
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        check_signal(symbol)
