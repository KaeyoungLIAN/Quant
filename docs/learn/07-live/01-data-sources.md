# 7.1 数据源与 API

> 本章目标：知道怎么获取真实市场数据——不再是 yfinance 的模拟，而是真实交易场景。

## 一句话

**数据源** = 策略的"水管"——没水（数据）哪里都去不了。本章让你知道有哪些水源、怎么接。

## 学习目标

学完本章你能：
- 列出主要的免费/付费数据源及其区别
- 用 API 获取行情和财务数据
- 理解不同数据频次的用途

## 核心内容

### 1. 数据源对比

| 数据源 | 覆盖范围 | 费用 | 延迟 | 易用性 | 推荐场景 |
|--------|---------|------|------|--------|---------|
| **yfinance** | 全球股票 | 免费 | T+1 | ★★★★★ | 学习、研究 |
| **Alpha Vantage** | 全球股票/外汇/加密货币 | 免费(5/min) | 15min | ★★★★ | 小项目 |
| **Polygon.io** | 美国股票/期权 | $29/月起 | 实时 | ★★★★ | 实盘 |
| **Free API (tushare)** | A股 | 免费(需积分) | T+1 | ★★★ | A股研究 |
| **IBKR API** | 全球 | 需开户 | 实时 | ★★ | 实盘交易 |

```python
import os
import pandas as pd

# yfinance 你已会了——但对于多只股票、多年数据，它很慢

# 更好的方式：用缓存
CACHE_DIR = 'data_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_data(ticker, start, end):
    """带缓存的 yfinance 下载"""
    cache_file = f'{CACHE_DIR}/{ticker}_{start}_{end}.parquet'
    
    if os.path.exists(cache_file):
        return pd.read_parquet(cache_file)
    
    import yfinance as yf
    data = yf.download(ticker, start=start, end=end)
    data.to_parquet(cache_file)
    return data

# 这样同一个数据只需要下载一次
```

### 2. 历史数据 vs 实时数据

```python
"""
历史数据用于回测——需要：
- 精确的 OHLCV
- 复权处理
- 分红拆股信息

实时数据用于交易——需要：
- 低延迟（毫秒级）
- 实时推送（WebSocket）
- 盘口深度（Level 2）

学习阶段只需要历史数据。
"""
```

### 3. 数据清洗

```python
import numpy as np
import pandas as pd

# 真实数据从不完美
def clean_market_data(data):
    """常见数据清洗步骤"""
    df = data.copy()
    
    # 1. 处理缺失值
    print(f"原始缺失值: {df.isnull().sum().sum()}")
    df = df.ffill()  # 用前值填充
    df = df.dropna()
    
    # 2. 异常值检测
    # 超过 5 倍标准差的价格变动可能是数据错误
    returns = df['Adj Close'].pct_change()
    outliers = returns.abs() > returns.std() * 5
    if outliers.any():
        print(f"发现 {outliers.sum()} 个异常收益率，已剔除")
        df = df[~outliers]
    
    # 3. 校验 OHLC 关系
    # Open <= High, Low <= Close 等
    bad_ohlc = (
        (df['High'] < df['Low']) |
        (df['High'] < df['Open']) |
        (df['Low'] > df['Close'])
    )
    if bad_ohlc.any():
        print(f"发现 {bad_ohlc.sum()} 行 OHLC 异常，已剔除")
        df = df[~bad_ohlc]
    
    return df
```

### 4. 数据频率选择

```python
"""
选择数据频率取决于你的策略持仓期：

持仓期    推荐频率    原因
1天以内    分钟/ tick   高频交易
1-5天     日线        短线策略
1-4周     日线        中期趋势
1个月+     周线        长线投资
1年+       月线        资产配置

规则：不要用比你的持仓期更高的频率
- 日线策略不需要分钟数据（增加噪声）
- 月线策略不需要日线数据（过拟合风险）
"""
```

## 深度阅读

## 练习

### 选择题

1. 回测最需要的数据精度是：
   - A. 实时 tick
   - B. 精确的历史 OHLCV
   - C. 任意数据
   - D. 只需要收盘价

2. 数据清洗时需要检查 OHLC 关系是因为：
   - A. 数据格式要求
   - B. 数据供应商可能出错
   - C. 为了美观
   - D. 不需要检查

3. 持仓 3 个月的策略应该用：
   - A. 分钟数据
   - B. 日线数据
   - C. 周线数据
   - D. B 或 C

### 填空题

下载数据时添加 \_\_\_\_ 机制可以避免重复下载相同的数据。

## 掌握检查
