"""
VOO 每日开盘异动监控
逻辑：用「今日开盘价」相对「昨日收盘价」的涨跌幅，
      与过去 N 日收益率的标准差（波动率基准）比较，
      超过 K 倍标准差则通过 Telegram 推送提醒。

环境变量：
  TICKER               股票代码，默认 VOO
  WINDOW               计算波动率基准的历史天数，默认 20
  K_MULTIPLIER         触发阈值的标准差倍数，默认 2.0
  TELEGRAM_BOT_TOKEN   Telegram Bot Token
  TELEGRAM_CHAT_ID     Telegram Chat ID
  STATE_FILE           状态文件路径，默认 state.json（防止同一天重复推送）
"""

import os
import sys
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import yfinance as yf
import requests

TICKER = os.environ.get("TICKER", "VOO")
WINDOW = int(os.environ.get("WINDOW", "20"))
K_MULTIPLIER = float(os.environ.get("K_MULTIPLIER", "2.0"))
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = os.environ.get("STATE_FILE", "state.json")

NY_TZ = ZoneInfo("America/New_York")


def get_ny_today_str():
    return datetime.now(NY_TZ).strftime("%Y-%m-%d")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_telegram(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[WARN] 未配置 Telegram，跳过推送，仅打印消息：")
        print(message)
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] Telegram 发送失败: {resp.status_code} {resp.text}")
    else:
        print("[INFO] Telegram 消息已发送")


def main():
    today_ny = get_ny_today_str()
    state = load_state()

    if state.get("last_checked_date") == today_ny:
        print(f"[INFO] {today_ny} 已经检查过，跳过本次运行。")
        return

    df = yf.download(TICKER, period="3mo", interval="1d", progress=False)
    if df.empty or len(df) < WINDOW + 2:
        print("[WARN] 数据不足，跳过本次检查。")
        return

    last_row_date = df.index[-1].strftime("%Y-%m-%d")
    if last_row_date != today_ny:
        print(
            f"[INFO] 尚未获取到今日（{today_ny}）行情数据"
            f"（最新数据日期为 {last_row_date}），可能是非交易日或尚未开盘。"
        )
        return

    today_open = float(df["Open"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])

    # 历史每日收益率（收盘对收盘），不含今天这一行（今天还未收盘）
    hist_close = df["Close"].iloc[:-1]
    daily_returns = hist_close.pct_change().dropna()
    rolling_std = float(daily_returns.tail(WINDOW).std())

    change_pct = (today_open - prev_close) / prev_close
    threshold = K_MULTIPLIER * rolling_std
    sigma_multiple = abs(change_pct) / rolling_std if rolling_std > 0 else 0

    print(f"[INFO] {TICKER} {today_ny}")
    print(f"  昨日收盘: {prev_close:.2f}")
    print(f"  今日开盘: {today_open:.2f}")
    print(f"  开盘涨跌幅: {change_pct*100:.2f}%")
    print(f"  过去{WINDOW}日波动率(标准差): {rolling_std*100:.2f}%")
    print(f"  触发阈值(±{K_MULTIPLIER}倍标准差): ±{threshold*100:.2f}%")
    print(f"  当前偏离: {sigma_multiple:.2f} 倍标准差")

    if abs(change_pct) > threshold:
        direction = "📈 大幅高开" if change_pct > 0 else "📉 大幅低开"
        message = (
            f"⚠️ *{TICKER} 异常波动提醒*\n\n"
            f"{direction}\n"
            f"日期: {today_ny}\n"
            f"昨收: {prev_close:.2f} → 今开: {today_open:.2f}\n"
            f"涨跌幅: *{change_pct*100:+.2f}%*\n"
            f"过去{WINDOW}日波动率: {rolling_std*100:.2f}%\n"
            f"偏离倍数: {sigma_multiple:.2f}σ (阈值 {K_MULTIPLIER}σ)"
        )
        send_telegram(message)
    else:
        print("[INFO] 波动在正常范围内，不触发提醒。")

    state["last_checked_date"] = today_ny
    save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] 运行失败: {e}")
        sys.exit(1)
