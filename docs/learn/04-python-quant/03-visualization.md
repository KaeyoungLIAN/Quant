# 4.3 K 线图与可视化

> 本章目标：用 mplfinance 画出专业的 K 线图和成交量图，从图表中读懂市场信息。

## 一句话

K 线图是量化交易者的"X 光片"——一图胜千言，体+影就能判断市场情绪。

## 学习目标

学完本章你能：
- 用 mplfinance 画 K 线图和成交量图
- 叠加均线、成交量指标
- 从 K 线图中识别趋势和模式
- 做多股票归一化比较可视化

## 核心内容

### 1. 画 K 线图

```python
import yfinance as yf
import mplfinance as mpf

# 下载数据
aapl = yf.download('AAPL', start='2024-01-01', end='2024-12-31')

# 取最近 30 天
data_30d = aapl.tail(30)

# 画 K 线图
mpf.plot(data_30d, type='candle', volume=True,
         title='AAPL 30日K线', style='charles',
         mav=(5, 10, 20))  # 叠加均线
```

**你的第一个量化分析工具！** 每天打开看看几只看好的股票——这是培养"市场感觉"最直接的方法。

### 2. K 线语言

只用体+影就能判断市场情绪：
- 长阳线 + 短上影 = 买方主导，强势
- 长阴线 + 短下影 = 卖方主导，弱势
- 十字星 = 多空平衡，变盘信号
- 长上影 = 卖方在高位反击

### 3. 计算基础指标的可视化

```python
import numpy as np
import matplotlib.pyplot as plt

# 收益率和波动率
returns = aapl['Adj Close'].pct_change().dropna()
print(f"年化收益率: {returns.mean() * 252:.2%}")
print(f"年化波动率: {returns.std() * np.sqrt(252):.2%}")
print(f"最大单日涨幅: {returns.max():.2%}")
print(f"最大单日跌幅: {returns.min():.2%}")

# 滚动均线
prices = aapl['Adj Close']
prices_ma20 = prices.rolling(20).mean()
prices_ma60 = prices.rolling(60).mean()

# 成交量指标
volume_ma20 = aapl['Volume'].rolling(20).mean()
print(f"\n平均成交量: {aapl['Volume'].mean():,.0f}")
print(f"成交量放大倍数: {(aapl['Volume'] / volume_ma20).tail(5).round(2).tolist()}")
```

### 4. 多股票比较

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

### 5. 可视化净值曲线

```python
# 策略回测净值曲线
def plot_equity_curve(strategy_returns, buy_hold_returns, title="策略对比"):
    """画策略净值曲线 vs 买入持有"""
    plt.figure(figsize=(12, 6))
    plt.plot(strategy_returns.index, (1 + strategy_returns).cumprod(), 
             label='策略', linewidth=2)
    plt.plot(buy_hold_returns.index, (1 + buy_hold_returns).cumprod(), 
             label='买入持有', linewidth=1, alpha=0.7)
    plt.title(title)
    plt.xlabel('日期')
    plt.ylabel('净值')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

## 深度阅读

- Wiki → [mplfinance 用法](/prerequisite-math/01-python/1.3-visualization)

## 练习

### 选择题

1. 十字星 K 线通常表示什么？
   - A. 强力上涨
   - B. 强力下跌
   - C. 多空平衡，变盘信号
   - D. 成交量异常

2. mplfinance 中 `mav=(5, 10, 20)` 的作用是：
   - A. 画 5, 10, 20 日均线
   - B. 设置图表大小
   - C. 调整颜色
   - D. 设置时间范围

3. 长上影线表示：
   - A. 买方完全主导
   - B. 卖方在高位反击，上涨遇到阻力
   - C. 趋势确立
   - D. 成交量放大

### 编程题

**题目：** 取 QQQ（纳斯达克 100 ETF）2024 年数据，画最后 60 个交易日的 K 线图，叠加 10 日和 30 日均线。

```python
import yfinance as yf
import mplfinance as mpf

# 你的代码
```

### 填空题

K 线图由 \\_\\_\\_\\_ 和 \\_\\_\\_\\_ 组成，实体表示开盘价和 \\_\\_\\_\\_ 之间的差。

## 掌握检查
