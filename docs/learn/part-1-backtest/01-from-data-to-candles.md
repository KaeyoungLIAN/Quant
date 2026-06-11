# 1.1 从数据到 K 线

> 本章目标：获取真实市场数据，理解 OHLCV 结构，用 K 线图"看"市场。

## 一句话

量化分析的第一步永远是把价格数据变成你熟悉的格式——OHLCV 是全世界通用的价格语言。

## 学习目标

学完本章你能：
- 用 yfinance 获取任意股票的历史数据
- 理解 OHLCV 每列的含义
- 用 mplfinance 画 K 线图和成交量图
- 从 K 线图中识别趋势和模式

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

**K 线语言**（只用体+影就能判断市场情绪）：
- 长阳线 + 短上影 = 买方主导，强势
- 长阴线 + 短下影 = 卖方主导，弱势
- 十字星 = 多空平衡，变盘信号
- 长上影 = 卖方在高位反击

### 3. 画 K 线图

```python
import mplfinance as mpf

# 取最近 30 天
data_30d = aapl.tail(30)

# 画 K 线图
mpf.plot(data_30d, type='candle', volume=True,
         title='AAPL 30日K线', style='charles',
         mav=(5, 10, 20))  # 叠加均线
```

**你的第一个量化分析工具！** 每天打开看看几只看好的股票——这是培养"市场感觉"最直接的方法。

### 4. 计算基础指标

```python
# 收益率
returns = prices.pct_change().dropna()
print(f"年化收益率: {returns.mean() * 252:.2%}")
print(f"年化波动率: {returns.std() * np.sqrt(252):.2%}")
print(f"最大单日涨幅: {returns.max():.2%}")
print(f"最大单日跌幅: {returns.min():.2%}")

# 滚动均线
prices_ma20 = prices.rolling(20).mean()
prices_ma60 = prices.rolling(60).mean()

# 成交量指标
volume_ma20 = aapl['Volume'].rolling(20).mean()
print(f"\n平均成交量: {aapl['Volume'].mean():,.0f}")
print(f"成交量放大倍数: {(aapl['Volume'] / volume_ma20).tail(5).round(2).tolist()}")
```

### 5. 多股票比较

```python
# 获取多只股票
tickers = ['AAPL', 'GOOGL', 'MSFT', 'SPY']
data = yf.download(tickers, start='2024-01-01', end='2024-12-31')['Adj Close']

# 归一化比较（都从 100 开始）
normalized = data / data.iloc[0] * 100
print(normalized.head())

# 看谁涨得最好
print(f"\n2024年涨幅:")
print((normalized.iloc[-1] - 100).round(2))
```

## 深度阅读

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

5. 十字星 K 线通常表示什么？
   - A. 强力上涨
   - B. 强力下跌
   - C. 多空平衡，变盘信号
   - D. 成交量异常

### 编程题

**题目：** 下载 SPY（标普 500 ETF）近一年的数据，找到**最大单日涨跌幅**的日期，并打印那天的 OHLC 数据。

```python
import yfinance as yf

spy = yf.download('SPY', start='2024-01-01', end='2024-12-31')

# 你的代码：找出收益率绝对值最大的那天
```

### 填空题

一个长阳线 + 短上影线表示 \_\_\_\_ 主导市场，方向 \_\_\_\_ 。

## 掌握检查
