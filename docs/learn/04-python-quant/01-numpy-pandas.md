# 4.1 NumPy 与 Pandas 基础

> 本章目标：掌握量化金融中最重要的两个 Python 库——NumPy 和 Pandas。这不是泛泛的 Python 教程，而是**带着金融数据**学。

## 一句话

NumPy 做数学运算，Pandas 做数据管理——两个库加起来就是量化分析的"手脚"。

## 学习目标

学完本章你能：
- 用 NumPy 进行向量化金融计算（收益率、协方差、组合收益）
- 用 Pandas 管理时间序列数据（合并、对齐、滚动窗口）
- 用真实金融数据完成数据探索

## 核心内容

### 1. NumPy 向量化金融计算

```python
import numpy as np

# 两股票的三天收益率（两个向量）
aapl = np.array([0.01, -0.005, 0.02])    # AAPL 3天收益率
goog = np.array([0.008, 0.01, -0.003])   # GOOG 3天收益率

# 向量加法 = 等权组合的收益率
equal_weight = (aapl + goog) / 2
print(f"等权组合日收益: {equal_weight}")

# 点积 = 给定权重下的组合收益
weights = np.array([0.6, 0.4])  # 60% AAPL, 40% GOOG
portfolio_returns = aapl * weights[0] + goog * weights[1]
# 等价于：
portfolio_returns_v2 = np.dot(np.array([aapl, goog]).T, weights)
print(f"组合日收益(点积): {portfolio_returns}")

# 矩阵乘法：多期多资产
np.random.seed(42)
n_days = 10
n_stocks = 4
returns_matrix = np.random.randn(n_days, n_stocks) * 0.02  # 日收益率
weights = np.array([0.25, 0.25, 0.25, 0.25])
portfolio_daily = returns_matrix @ weights

print(f"组合10天收益:\n{portfolio_daily}")
print(f"年化波动率: {portfolio_daily.std() * np.sqrt(252):.2%}")

# 协方差矩阵
cov = np.cov(returns_matrix, rowvar=False)

# 特征值分解用于 PCA
eigenvalues, eigenvectors = np.linalg.eig(cov)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]
explained_ratio = eigenvalues / eigenvalues.sum()
print(f"第一主成分解释方差: {explained_ratio[0]:.2%}")
```

### 2. Pandas 金融数据处理

```python
import pandas as pd
import numpy as np
import yfinance as yf

# 下载 AAPL 数据
aapl = yf.download('AAPL', start='2024-01-01', end='2024-12-31')
print(aapl.head())
print(f"数据形状: {aapl.shape}")

# 核心操作：使用 Adj Close
prices = aapl['Adj Close']

# 收益率计算
returns = prices.pct_change().dropna()
print(f"平均日收益: {returns.mean():.4%}")
print(f"日波动率: {returns.std():.4%}")

# 年化指标
print(f"年化收益率: {returns.mean() * 252:.2%}")
print(f"年化波动率: {returns.std() * np.sqrt(252):.2%}")

# 滚动窗口
ma_20 = prices.rolling(20).mean()
ma_60 = prices.rolling(60).mean()

# 多股票 DataFrame
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
data = yf.download(tickers, start='2024-01-01', end='2024-12-31')['Adj Close']
print(data.head())

# 归一化比较
normalized = data / data.iloc[0] * 100
print(normalized.tail())

# 相关系数矩阵
print(data.pct_change().dropna().corr().round(3))
```

### 3. 金融数据速查表

| 操作 | NumPy | Pandas |
|------|-------|--------|
| 收益率 | `np.diff(p) / p[:-1]` | `df.pct_change()` |
| 协方差 | `np.cov(X)` | `df.cov()` |
| 相关系数 | `np.corrcoef(X)` | `df.corr()` |
| 滚动均线 | 手动循环 | `df.rolling(n).mean()` |
| 滞后 | 切片 | `df.shift(k)` |
| 日期索引 | 不支持 | `df.loc['2024-01']` |
| 合并 | 不支持 | `pd.concat()`, `pd.merge()` |

## 深度阅读

- Wiki → [NumPy 基础](/prerequisite-math/01-python/1.1-numpy-basics)
- Wiki → [Pandas 时间序列](/prerequisite-math/01-python/1.2-pandas-timeseries)

## 练习

### 选择题

1. `np.array([1,2,3]) @ np.array([4,5,6])` 的结果是：
   - A. 32
   - B. [4,10,18]
   - C. 数组形状不匹配
   - D. 6

2. Pandas 中 `shift(1)` 的作用是：
   - A. 将数据向前移动 1 行
   - B. 将数据向后移动 1 行
   - C. 删除第一行
   - D. 计算差分

3. 年化波动率的计算公式是：
   - A. 日收益率标准差 × √252
   - B. 日收益率均值 × 252
   - C. 日收益率标准差 × 252
   - D. 日收益率最大值 × √252

4. `rolling(20).mean()` 计算的是：
   - A. 20 个时间点的累加平均
   - B. 过去 20 个时间点的移动平均
   - C. 未来 20 个时间点的预测
   - D. 20 个时间点的中位数

### 编程题

**题目：** 下载 5 只股票（AAPL, MSFT, GOOGL, AMZN, META）2024 年数据，计算它们的年化收益率和年化波动率，并找出夏普比率最高的一只（假设无风险利率 5%）。

```python
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

# 你的代码
```

### 填空题

NumPy 进行向量化运算时，`a @ b` 代表 \\_\\_\\_\\_ 运算。Pandas 中处理缺失值的常用方法包括 `.fillna()` 和 \_\_\_\_ 。

## 掌握检查
