# BTC Signal Bot (MACD + EMA + RSI)

A crypto trading signal bot that uses EMA crossover, MACD histogram, and RSI to send long/short signals on BTCUSDT via Telegram.

## 🔧 How It Works
- Gets OHLCV data from Binance
- Calculates EMA(50), EMA(200), MACD(12,26,9), and RSI(14)
- Sends alerts to Telegram when:
  - 📈 Long: EMA50 > EMA200, MACD > Signal, RSI rising under 80
  - 📉 Short: EMA50 < EMA200, MACD < Signal, RSI falling over 20

## 🚀 Deploy to Render
1. Fork this repo to your GitHub
2. Go to [https://render.com](https://render.com)
3. Create a new **cron job**
4. Set the schedule to `0 * * * *` (every hour)
5. Add environment variables:
   - `BOT_TOKEN`: your Telegram bot token
   - `CHAT_ID`: your Telegram chat ID

## 🔗 Telegram Setup
- Create a bot via [@BotFather](https://t.me/botfather)
- Get your chat ID via [@userinfobot](https://t.me/userinfobot)

---

✅ Done! You’ll now get signals to Telegram every hour.
