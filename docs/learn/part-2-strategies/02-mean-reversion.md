# 2.2 均值回归策略

> 本章目标：理解"涨多必跌，跌多必涨"的量化实现——趋势的对立面。

## 一句话

**均值回归**假设价格会"弹回"平均值——偏离越远，回归概率越大。

## 学习目标

学完本章你能：
- 理解均值回归与趋势跟踪的数学区别
- 实现布林带、RSI 两种经典均值回归策略
- 用平稳性检验判断一只股票是否适合均值回归

## 核心内容

### 1. 两种世界观

```
趋势跟踪：趋势是我的朋友 → 追涨杀跌
均值回归：万物皆归平均 → 高抛低吸
```

没有谁对谁错——不同时间尺度适用不同策略。**日级别趋势为主，分钟级别均值回归为主。**

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('AAPL', start='2020-01-01', end='2024-12-31')
close = data['Adj Close']

# 看不同时间尺度下的自相关
for lag in [1, 5, 20, 60]:
    ac = close.pct_change().dropna().autocorr(lag=lag)
    print(f"{lag}日自相关: {ac:.4f} {'→ 趋势' if ac > 0.02 else ('→ 均值回归' if ac < -0.02 else '→ 随机')}")
```

**关键洞察：** 短期（1-5天）可能微弱趋势，中期（20-60天）可能均值回归。不同时间尺度有不同的"性格"。

### 2. 布林带策略——最直观的均值回归

```python
import numpy as np
import pandas as pd

def bollinger_strategy(close, window=20, std_mult=2):
    """
    布林带均值回归
    价格 > 上轨 → 卖出（偏高，会回来）
    价格 < 下轨 → 买入（偏低，会回去）
    """
    ma = close.rolling(window).mean()
    std = close.rolling(window).std()
    
    upper = ma + std_mult * std
    lower = ma - std_mult * std
    
    # 信号
    signal = pd.Series(0, index=close.index)
    signal[close > upper] = -1   # 做空
    signal[close < lower] = 1    # 做多
    # 回到均值区间 → 平仓
    signal[(close <= upper) & (close >= lower)] = 0
    
    return signal, upper, lower, ma

# 测试
signal, upper, lower, ma = bollinger_strategy(close)
returns = close.pct_change()
strategy_rets = signal.shift(1) * returns

print(f"布林带策略总收益: {(1 + strategy_rets.dropna()).prod() - 1:.2%}")
print(f"交易次数: {(signal.diff().abs() > 0).sum() // 2}")
```

**关键点：** 布林带策略在**震荡市**中表现好——价格反复触碰上下轨。在**单边牛市**中会反复做空被"打死"。

### 3. RSI 策略——相对强弱指标

RSI 衡量"上涨动能相对于下跌动能的强弱"：

$$\text{RSI} = 100 - \frac{100}{1 + \text{RS}}$$

其中 $\text{RS} = \frac{\text{平均涨幅}}{\text{平均跌幅}}$（通常用 14 日）。

```python
import numpy as np
import pandas as pd

def rsi_strategy(close, window=14, oversold=30, overbought=70):
    """
    RSI 均值回归策略
    RSI < 30 → 超卖 → 买入
    RSI > 70 → 超买 → 卖出
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    signal = pd.Series(0, index=close.index)
    signal[rsi < oversold] = 1    # 买入
    signal[rsi > overbought] = -1 # 卖出
    # 离开极端区域时平仓
    signal[(rsi >= oversold) & (rsi <= overbought)] = 0
    
    return signal, rsi

signal_rsi, rsi = rsi_strategy(close)
returns = close.pct_change()
strategy_rets = signal_rsi.shift(1) * returns

print(f"RSI策略总收益: {(1 + strategy_rets.dropna()).prod() - 1:.2%}")
print(f"当前RSI值: {rsi.iloc[-1]:.1f}")
```

### 4. 平稳性检验——你选的股票适合均值回归吗？

不是所有股票都适合均值回归。用**ADF 检验**判断：

```python
import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller

def check_mean_reversion(ticker):
    """检查一只股票是否适合均值回归策略"""
    data = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    close = data['Adj Close']
    
    # ADF 检验
    result = adfuller(close.dropna())
    adf_stat = result[0]
    p_value = result[1]
    
    # p < 0.05 → 平稳 → 适合均值回归
    # p > 0.05 → 非平稳 → 不适合均值回归（有趋势成分）
    
    # 但直观地说：看价格是否"反复回到某个区间"
    zscore = (close - close.rolling(60).mean()) / close.rolling(60).std()
    mean_reversion_score = (zscore.abs() > 2).mean()  # 历史上"偏离"的比例
    
    print(f"{ticker}:")
    print(f"  ADF p-value: {p_value:.4f} ({'适合均值回归' if p_value < 0.05 else '不太适合'})")
    print(f"  偏离2σ以上比例: {mean_reversion_score:.2%}")
    
# 测试不同类型
for t in ['SPY', 'TLT', 'XLP', 'TSLA']:
    try:
        check_mean_reversion(t)
    except:
        pass
```

**经验法则：**
- 宽基指数（SPY）— 长期向上，不太适合纯均值回归
- 债券（TLT）— 来回波动，适合均值回归
- 消费股（XLP）— 较稳定，适合
- 科技成长股（TSLA）— 趋势性强，不太适合

### 5. 趋势 vs 均值回归——什么时候用哪个？

```python
import numpy as np
import pandas as pd

# 一个简单的混合信号：看价格在均线哪侧
def regime_detector(close, window=60):
    """判断当前市场状态：趋势还是震荡"""
    ma = close.rolling(window).mean()
    std = close.rolling(window).std()
    
    # 一段时间内的价格路线长度 / 净变化
    # 路线长 + 净变化小 = 震荡
    # 路线长 + 净变化大 = 趋势
    path_length = close.diff().abs().rolling(window).sum()
    net_change = (close - close.shift(window)).abs()
    
    efficiency = net_change / path_length  # 效率比：接近 1 = 趋势，接近 0 = 震荡
    return efficiency

eff = regime_detector(close)
print(f"当前效率比: {eff.iloc[-1]:.3f}")
print(f"结论: {'趋势市场 ↑ 用趋势策略' if eff.iloc[-1] > 0.3 else '震荡市场 ↔ 用均值回归'}")
```

## 深度阅读

## 练习

### 选择题

1. 均值回归策略在什么市场中最赚钱？
   - A. 单边上涨
   - B. 震荡市场
   - C. 单边下跌
   - D. 高波动市场

2. 布林带策略中，价格突破上轨时的信号是：
   - A. 买入
   - B. 卖出/做空
   - C. 平仓
   - D. 加仓

3. RSI < 30 通常被解释为：
   - A. 超买，应该卖出
   - B. 超卖，应该买入
   - C. 正常范围
   - D. 趋势形成

4. ADF 检验的 p-value < 0.05 意味着：
   - A. 序列非平稳
   - B. 序列平稳
   - C. 有趋势
   - D. A 和 C

5. 效率比接近 1 表示：
   - A. 市场在震荡
   - B. 市场在趋势
   - C. 无法判断
   - D. 需要更多数据

### 编程题

**作业：** 对 TLT（20年以上国债 ETF）做布林带 + RSI 双策略对比回测。哪个在 TLT 上表现更好？画出净值曲线对比。

### 填空题

布林带的上轨计算公式是：中轨 + 倍数 × \_\_\_\_。

## 掌握检查
