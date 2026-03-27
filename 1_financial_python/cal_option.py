#!pip install yfinance numpy scipy pandas
import yfinance as yf
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime

# ===== 参数 =====
ticker = "OXY"   # 改成你的股票代码
strike = 65
expiration = "2025-08-21"
risk_free_rate = 0.045

# ===== Black-Scholes 定价 =====
def bs_call_price(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

# ===== 计算隐含波动率 =====
def implied_volatility(market_price, S, K, T, r):
    func = lambda sigma: bs_call_price(S, K, T, r, sigma) - market_price
    return brentq(func, 1e-6, 5)

# ===== 获取市场数据 =====
stock = yf.Ticker(ticker)
S0 = stock.history(period="1d")["Close"].iloc[-1]

option_chain = stock.option_chain(expiration)
calls = option_chain.calls
call_option = calls[calls["strike"] == strike].iloc[0]

market_price = call_option["lastPrice"]

# ===== 时间到期 =====
today = datetime.today()
expiry = datetime.strptime(expiration, "%Y-%m-%d")
T = (expiry - today).days / 365

# ===== 计算 IV =====
iv = implied_volatility(market_price, S0, strike, T, risk_free_rate)

# ===== Covered Call 年化收益 =====
premium = market_price
capital = S0 - premium   # 实际成本基础
return_pct = premium / capital
annualized_return = return_pct * (365 / ((expiry - today).days))

# ===== 输出 =====
print("当前股价:", round(S0, 2))
print("Call 市场价格:", market_price)
print("隐含波动率 IV:", round(iv * 100, 2), "%")
print("权利金收益率:", round(return_pct * 100, 2), "%")
print("年化收益率:", round(annualized_return * 100, 2), "%")
