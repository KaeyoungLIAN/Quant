# 4.2 数据获取与预处理

> 本章目标：获取真实市场数据，理解 OHLCV 结构，处理数据中的各种"脏"问题。

## 一句话

量化分析的第一步永远是把价格数据变成你熟悉的格式——OHLCV 是全世界通用的价格语言。

## 学习目标

学完本章你能：
- 用 yfinance 获取任意股票的历史数据
- 理解 OHLCV 每列的含义
- 处理缺失值、复权、时间对齐问题
- 做数据清洗和异常值检测

## 核心内容

### 1. 获取数据

```python
import yfinance as yf
import pandas as pd

# 下载 AAPL 近一年数据
aapl = yf.download('AAPL', start='2024-01-01', end='2024-12-31')
print(aapl.head())
print("\n数据信息:", aapl.shape)
```

输出会是一个 6 列 DataFrame，索引是日期，列是：
- **Open** — 开盘价（当天第一笔成交）
- **High** — 最高价（当天最高）
- **Low** — 最低价（当天最低）
- **Close** — 收盘价（当天最后一笔）
- **Volume** — 成交量（成交股数）
- **Adj Close** — 复权收盘价（考虑了分红和拆股）

```python
# 实际分析中绝大多数情况用 Adj Close
prices = aapl['Adj Close']
```

### 2. 理解 OHLCV

每一根 K 线 = 一天的交易"故事"。

```python
# 从 OHLC 中你可以读出的信息
day1 = aapl.iloc[0]
print(f"开盘: ${day1['Open']:.2f}")
print(f"最高: ${day1['High']:.2f}")
print(f"最低: ${day1['Low']:.2f}")
print(f"收盘: ${day1['Close']:.2f}")
print(f"实体方向: {'阳线📈' if day1['Close'] > day1['Open'] else '阴线📉'}")
print(f"上影线: {day1['High'] - max(day1['Open'], day1['Close']):.2f}")
print(f"下影线: {min(day1['Open'], day1['Close']) - day1['Low']:.2f}")
```

### 3. 数据预处理

```python
import numpy as np
import pandas as pd

def clean_market_data(data):
    """常见数据清洗步骤"""
    df = data.copy()
    
    # 1. 处理缺失值
    print(f"原始缺失值: {df.isnull().sum().sum()}")
    df = df.ffill()  # 用前值填充
    df = df.dropna()
    
    # 2. 异常值检测
    returns = df['Adj Close'].pct_change()
    outliers = returns.abs() > returns.std() * 5
    if outliers.any():
        print(f"发现 {outliers.sum()} 个异常收益率，已剔除")
        df = df[~outliers]
    
    # 3. 校验 OHLC 关系
    bad_ohlc = (
        (df['High'] < df['Low']) |
        (df['High'] < df['Open']) |
        (df['Low'] > df['Close'])
    )
    if bad_ohlc.any():
        print(f"发现 {bad_ohlc.sum()} 行 OHLC 异常，已剔除")
        df = df[~bad_ohlc]
    
    return df

# 多股票比较
tickers = ['AAPL', 'GOOGL', 'MSFT', 'SPY']
data = yf.download(tickers, start='2024-01-01', end='2024-12-31')['Adj Close']

# 归一化比较（都从 100 开始）
normalized = data / data.iloc[0] * 100
print("2024年涨幅:")
print((normalized.iloc[-1] - 100).round(2))
```

### 4. 带缓存的数据获取

```python
import os

CACHE_DIR = 'data_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_data(ticker, start, end):
    """带缓存的 yfinance 下载"""
    cache_file = f'{CACHE_DIR}/{ticker}_{start}_{end}.parquet'
    
    if os.path.exists(cache_file):
        return pd.read_parquet(cache_file)
    
    data = yf.download(ticker, start=start, end=end)
    data.to_parquet(cache_file)
    return data

# 这样同一个数据只需要下载一次
```

### 5. 数据频率选择

```
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
```

## 深度阅读

- Wiki → [Pandas 时间序列](/prerequisite-math/01-python/1.2-pandas-timeseries)

## 练习

### 选择题

1. OHLCV 中的 O 代表：
   - A. 收盘价
   - B. 开盘价
   - C. 最高价
   - D. 成交量

2. K 线图中的"阳线"表示：
   - A. Close < Open
   - B. Close > Open
   - C. High > Low
   - D. Volume 增加

3. 复权收盘价（Adj Close）是考虑了什么？
   - A. 通货膨胀
   - B. 分红和拆股
   - C. 手续费
   - D. 市场情绪

4. 年化波动率的计算公式是：
   - A. 日收益率标准差 × √252
   - B. 日收益率均值 × 252
   - C. 日收益率标准差 × 252
   - D. 日收益率最大值

### 编程题

**题目：** 下载 SPY（标普 500 ETF）近一年的数据，找到**最大单日涨跌幅**的日期，并打印那天的 OHLC 数据。

```python
import yfinance as yf

spy = yf.download('SPY', start='2024-01-01', end='2024-12-31')

# 你的代码：找出收益率绝对值最大的那天
```

### 填空题

一个长阳线 + 短上影线表示 \\_\\_\\_\\_ 主导市场，方向 \\_\\_\\_\\_ 。数据清洗中，`ffill()` 是用 \\_\\_\\_\\_ 值填充缺失值。

## 掌握检查
