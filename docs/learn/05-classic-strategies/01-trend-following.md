# 5.1 趋势跟踪策略

> 本章目标：实现并理解量化策略中最大的一类——趋势跟踪。

## 一句话

**趋势跟踪**——"涨了买更多，跌了卖"，假设市场的动量会持续。

## 学习目标

学完本章你能：
- 理解动量因子和趋势跟踪的核心逻辑
- 实现双均线、MACD、动量三种趋势策略
- 用"分组回测"验证策略是否真正有效
- 写出策略作业：选定一只股票，三种趋势策略对比

## 核心内容

### 1. 趋势跟踪的底层逻辑

趋势跟踪赚钱的基础：**市场不是完全随机的——趋势存在。**

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('AAPL', start='2020-01-01', end='2024-12-31')
close = data['Adj Close']

# 证明趋势存在：自相关检验
# 如果今天的收益率和明天的收益率正相关 → 趋势存在
returns = close.pct_change().dropna()
autocorr_1d = returns.autocorr(lag=1)
autocorr_5d = returns.autocorr(lag=5)

print(f"1日自相关: {autocorr_1d:.4f}")
print(f"5日自相关: {autocorr_5d:.4f}")
print(f"结论: {'存在短期趋势' if autocorr_1d > 0.02 else '趋势不明显'}")
```

**真实情况：** 日收益率自相关很低。趋势跟踪赚的是"一两个月的趋势"，不是一两天。

### 2. 动量策略——最简单的趋势

```python
import numpy as np
import pandas as pd

def momentum_strategy(close, lookback=60, holding=20):
    """
    动量策略：用过去 N 天涨幅预测未来 M 天
    每月调仓一次
    """
    # 过去 lookback 天的收益率
    momentum = close.pct_change(lookback)
    
    # 信号：动量 > 0 做多，< 0 做空
    signal = pd.Series(0, index=close.index)
    signal[momentum > 0] = 1    # 做多
    signal[momentum < 0] = -1   # 做空
    
    # 每 holding 天调仓一次
    rebalance = signal.resample(f'{holding}D').last()  # 调仓日
    signal_rebalanced = signal.copy()
    signal_rebalanced[:] = np.nan
    signal_rebalanced[rebalance.index] = rebalance
    signal_rebalanced = signal_rebalanced.ffill()  # 在两个调仓日之间保持持仓
    
    return signal_rebalanced

# 测试
signal = momentum_strategy(close, lookback=60, holding=20)
returns = close.pct_change()
strategy_rets = signal.shift(1) * returns

cumulative = (1 + strategy_rets).cumprod()
print(f"动量策略总收益: {cumulative.iloc[-1] - 1:.2%}")
print(f"买入持有: {close.iloc[-1] / close.iloc[0] - 1:.2%}")
```

### 3. MACD——交易员最常用的趋势指标

```python
import numpy as np
import pandas as pd

def macd_strategy(close, fast=12, slow=26, signal_line=9):
    """
    MACD 策略
    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(MACD, signal_line)
    金叉（MACD上穿Signal）→ 买入
    死叉（MACD下穿Signal）→ 卖出
    """
    # 计算EMA
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_line, adjust=False).mean()
    histogram = macd - signal
    
    # 双轨信号
    position = pd.Series(0, index=close.index)
    position[macd > signal] = 1
    
    return position, macd, signal, histogram

pos, macd, sig, hist = macd_strategy(close)
rets = close.pct_change()
strategy_rets = pos.shift(1) * rets

print(f"MACD策略总收益: {(1 + strategy_rets.dropna()).prod() - 1:.2%}")
```

### 4. 海龟交易法则

经典趋势策略——突破 N 日高点买入，跌破 N 日低点卖出。

```python
import numpy as np
import pandas as pd

def turtle_strategy(high, low, close, entry_window=20, exit_window=10):
    """
    海龟交易法则简化版
    """
    # 入场信号：价格突破20日高点
    entry_high = high.rolling(entry_window).max()
    entry_signal = close > entry_high.shift(1)
    
    # 出场信号：价格跌破10日低点
    exit_low = low.rolling(exit_window).min()
    exit_signal = close < exit_low.shift(1)
    
    # 持仓状态
    position = pd.Series(0, index=close.index)
    in_position = False
    
    for i in range(1, len(close)):
        if not in_position and entry_signal.iloc[i]:
            position.iloc[i] = 1
            in_position = True
        elif in_position and exit_signal.iloc[i]:
            position.iloc[i] = 0
            in_position = False
        elif in_position:
            position.iloc[i] = 1
            
    return position

pos_turtle = turtle_strategy(data['High'], data['Low'], close)
rets = close.pct_change()
strategy_rets = pos_turtle.shift(1) * rets
print(f"海龟策略总收益: {(1 + strategy_rets.dropna()).prod() - 1:.2%}")
```

### 5. 分组回测——检验策略是否真有效

单一股票上的好表现可能是运气。分组回测：**在所有股票上跑一遍，看胜率统计。**

```python
import numpy as np
import pandas as pd
import yfinance as yf

# 用多只股票验证趋势策略
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM']
results = []

for ticker in tickers:
    try:
        d = yf.download(ticker, start='2020-01-01', end='2024-12-31')
        c = d['Adj Close']
        
        # 动量策略
        sig = momentum_strategy(c, lookback=60, holding=20)
        r = c.pct_change()
        sr = sig.shift(1) * r
        total_ret = (1 + sr.dropna()).prod() - 1
        
        bh = c.iloc[-1] / c.iloc[0] - 1
        results.append({
            'ticker': ticker,
            'strategy_ret': total_ret,
            'buy_hold_ret': bh,
            'excess': total_ret - bh,
        })
    except Exception as e:
        print(f"{ticker}: {e}")

results_df = pd.DataFrame(results)
print("\n分组回测结果:")
print(results_df[['ticker', 'strategy_ret', 'buy_hold_ret', 'excess']].to_string())
print(f"\n跑赢基准比例: {(results_df['excess'] > 0).mean():.0%}")
```

## 深度阅读

## 练习

### 选择题

1. 趋势跟踪策略的核心假设是：
   - A. 市场永远随机
   - B. 过去的趋势会延续
   - C. 价格回归均值
   - D. 技术面比基本面重要

2. MACD 金叉是指：
   - A. MACD 线上穿 Signal 线
   - B. MACD 线下穿 Signal 线
   - C. 价格上穿 MACD
   - D. Signal 线上穿 MACD

3. 海龟交易法则的入场条件是：
   - A. 价格突破 N 日高点
   - B. 均线金叉
   - C. MACD 金叉
   - D. 成交量放大

4. 分组回测的目的是：
   - A. 增加交易次数
   - B. 验证策略在不同股票上是否都有效
   - C. 提高夏普比率
   - D. 减少回撤

5. 动量策略中 `lookback=60, holding=20` 的含义是：
   - A. 看过去60天，每20天调仓
   - B. 看过去20天，每60天调仓
   - C. 持有60天，卖出后等20天
   - D. 20日均线穿过60日均线

### 编程题

**作业：** 选择一个趋势策略（动量/MACD/海龟），对 SPY（标普 500 ETF）做回测，画出净值曲线 + 买入持有对比，计算夏普比率和最大回撤。

### 填空题

趋势跟踪在 \_\_\_\_ 市场中表现最好，在 \_\_\_\_ 市场中表现最差（横盘震荡/单边上涨/单边下跌）。

## 掌握检查
