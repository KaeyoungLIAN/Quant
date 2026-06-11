# 5.3 统计套利

> 本章目标：利用两只或多只股票之间的"价差规律"赚钱——不关心涨跌，只关心它们之间是否"跑偏"了。

## 一句话

**统计套利** = 找到两只同向运动但偶尔走散的股票，在走散时赌它们会走回来。

## 学习目标

学完本章你能：
- 理解协整关系的含义和检验方法
- 实现配对交易（Pairs Trading）策略
- 理解"对冲"的本质：不赌方向，赌关系

## 核心内容

### 1. 协整 vs 相关——关键区别

```
相关性：A涨10%，B有80%概率也涨    → 表面关系
协整性：A和B的价差稳定在±2%内    → 深层绑定
```

```python
import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import coint

# 下载两只有名的配对
a = yf.download('XOM', start='2020-01-01', end='2024-12-31')['Adj Close']
b = yf.download('CVX', start='2020-01-01', end='2024-12-31')['Adj Close']

# 相关性
corr = a.corr(b)
print(f"相关性: {corr:.4f}")

# 协整检验
score, p_value, _ = coint(a, b)
print(f"协整检验 p-value: {p_value:.4f}")
print(f"结论: {'协整关系成立' if p_value < 0.05 else '不成立'}")
```

**直观理解：** 两条狗在散步。相关性 = 它们是否朝同一方向跑；协整性 = 它们之间的绳子（价差）不会无限拉长。

### 2. 配对交易策略

```python
import numpy as np
import pandas as pd

def pairs_trading(price_a, price_b, window=60, entry_z=2, exit_z=0.5):
    """
    配对交易策略
    
    核心逻辑：
    1. 计算价差 spread = ln(price_a) - β × ln(price_b)
    2. 价差标准化为 Z-score
    3. |Z| > entry_z → 开仓（偏离太多，赌回归）
    4. |Z| < exit_z → 平仓（回归了）
    """
    # 计算对冲比率 β（用滚动回归）
    log_a = np.log(price_a)
    log_b = np.log(price_b)
    
    # 简单方法：价差 = a - b（假设对冲比率=1）
    # 更精确：用滚动回归求 β
    spread = log_a - log_b
    
    # Z-score 标准化
    spread_mean = spread.rolling(window).mean()
    spread_std = spread.rolling(window).std()
    zscore = (spread - spread_mean) / spread_std
    
    # 信号
    position_a = pd.Series(0, index=price_a.index)
    position_b = pd.Series(0, index=price_a.index)
    
    # 当 Z > entry_z → 做空 A，做多 B（价差会缩小）
    position_a[zscore > entry_z] = -1
    position_b[zscore > entry_z] = 1
    
    # 当 Z < -entry_z → 做多 A，做空 B
    position_a[zscore < -entry_z] = 1
    position_b[zscore < -entry_z] = -1
    
    # 回到 Z-score 0 附近 → 平仓
    position_a[zscore.abs() < exit_z] = 0
    position_b[zscore.abs() < exit_z] = 0
    
    return position_a, position_b, zscore

pos_a, pos_b, zscore = pairs_trading(a, b)

rets_a = a.pct_change()
rets_b = b.pct_change()

# 组合收益（多空对冲）
strategy_rets = (pos_a.shift(1) * rets_a + pos_b.shift(1) * rets_b) / 2

cumulative = (1 + strategy_rets.dropna()).cumprod()
print(f"配对交易总收益: {cumulative.iloc[-1] - 1:.2%}")

# 与买入持有对比
print(f"XOM 买入持有: {a.iloc[-1] / a.iloc[0] - 1:.2%}")
print(f"CVX 买入持有: {b.iloc[-1] / b.iloc[0] - 1:.2%}")
```

**关键洞察：** 配对交易是**市场中性的**——大盘涨跌都可以赚钱，只看价差是否回归。

### 3. 寻找可配对的股票

```python
import numpy as np
import pandas as pd
import itertools
import yfinance as yf
from statsmodels.tsa.stattools import coint

# 候选池：同业股票
energy_stocks = ['XOM', 'CVX', 'COP', 'EOG', 'OXY', 'PSX', 'VLO']

# 下载所有
data = {}
for t in energy_stocks:
    try:
        data[t] = yf.download(t, start='2020-01-01', end='2024-12-31')['Adj Close']
    except:
        pass

# 对所有组合做协整检验
pairs_df = yf.download(energy_stocks, start='2020-01-01', end='2024-12-31')['Adj Close']
prices = pairs_df.dropna(how='any')

results = []
for s1, s2 in itertools.combinations(prices.columns, 2):
    score, p_value, _ = coint(prices[s1], prices[s2])
    if p_value < 0.05:  # 只保留协整成立的
        results.append({
            'pair': f'{s1}-{s2}',
            'coint_p': p_value,
            'corr': prices[s1].corr(prices[s2]),
        })

results_df = pd.DataFrame(results).sort_values('coint_p')
print("协整成立的配对:")
print(results_df.to_string())
```

### 4. 配对交易 vs 纯方向交易

| 对比维度 | 趋势/均线策略 | 配对交易 |
|---------|-------------|---------|
| 市场方向 | 依赖 | 中性（多空对冲） |
| 风险来源  | 大盘波动 | 价差异常 |
| 最大回撤 | 可能很大（崩盘） | 较小（价差回归） |
| 交易频率 | 中等 | 较高 |
| 胜率 | 40-50% | 50-70% |

### 5. 实战注意事项

```python
import numpy as np
import pandas as pd

# 一、滑点成本是关键
# 配对交易交易频繁，每笔的交易成本会吃掉利润
# 模拟手续费：
def after_cost_returns(strategy_rets, cost_per_trade=0.001, position_changes=None):
    """考虑交易成本后的收益"""
    if position_changes is None:
        position_changes = (pos_a.diff().abs() + pos_b.diff().abs()) > 0
    trade_cost = position_changes * cost_per_trade / 2  # 双边成本
    return strategy_rets - trade_cost.shift(1).fillna(0)

# 二、协整关系不是永恒的
# 定期重新检验协整性——3个月一次
```

## 深度阅读

## 练习

### 选择题

1. 协整和相关的关键区别是：
   - A. 协整需要线性关系，相关不需要
   - B. 协整检验长期的平衡关系，相关只看短期
   - C. 协整关注价差是否稳定，相关关注是否同向运动
   - D. 两者没有区别

2. 配对交易中，当 Z-score > 2 时你应该：
   - A. 做多 A，做空 B
   - B. 做空 A，做多 B
   - C. 同时做多
   - D. 同时做空

3. 配对交易是市场中性的，意思是：
   - A. 不需要预测市场方向
   - B. 没有风险
   - C. 不赚钱
   - D. 只做空

4. 配对交易的最大风险是：
   - A. 协整关系断裂
   - B. 交易成本太高
   - C. A 和 B
   - D. 没有风险

5. 对冲比率 β 在配对交易中用于：
   - A. 决定开仓大小
   - B. 核算一个单位的 A 用多少 B 对冲
   - C. 计算总收益
   - D. 做回归

### 编程题

**作业：** 选择**不同行业**的两只股票（比如 JPM 银行 + XOM 能源），检验它们是否协整。如果协整，做回测；如果不协整，解释为什么。

### 填空题

配对交易中，Z-score 表示当前价差偏离 \_\_\_\_ 的 \_\_\_\_ 倍标准差。

## 掌握检查
