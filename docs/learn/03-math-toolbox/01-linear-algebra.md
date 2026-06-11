# 3.1 线性代数与 Python 向量化

> 对应 MIT 18.S096 L1 (Introduction, Financial Terms) + L2 (Linear Algebra)
>
> 🎬 [先看 L1](https://youtu.be/msa8jv0_17U) → [再看 L2](https://youtu.be/cg2W0geU7E8) → 然后学本章代码

## 一句话

金融中一切量化分析最终都变成**向量和矩阵的运算**——用 Python 实现就是一行 `a @ b` 的事。

## 学习目标

学完本章你能：
- 用 NumPy 向量/矩阵表达金融概念（收益率、组合市值、协方差）
- 理解矩阵乘法在量化中的实际含义
- 从线性代数的视角理解 PCA（主成分分析）——L2 的核心应用

## 核心内容

### 1. 向量：用 Python 理解 L2 的向量空间

MIT L2 讲的向量空间、线性无关、基——在 Python 里就是数组操作：

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
```

**L2 核心概念 → Python 映射：**
- 向量 = `np.array`
- 线性组合 = `w1 * v1 + w2 * v2`
- 点积 = `np.dot(a, b)` 或 `a @ b`
- 线性无关 = `np.linalg.matrix_rank(A)` = 独立的列数

### 2. 矩阵乘法：L2 最核心的运算

```python
# 构建收益率矩阵（10天 × 4只股票）
np.random.seed(42)
n_days = 10
n_stocks = 4
returns_matrix = np.random.randn(n_days, n_stocks) * 0.02  # 日收益率

# 权重向量（单期）
weights = np.array([0.25, 0.25, 0.25, 0.25])
# 组合每日收益 = 收益率矩阵 × 权重向量
portfolio_daily = returns_matrix @ weights

print(f"组合10天收益:\n{portfolio_daily}")
print(f"年化波动率: {portfolio_daily.std() * np.sqrt(252):.2%}")
```

### 3. 特诊值分解与 PCA（L2 的高潮）

MIT L2 讲特征值和特征向量的金融应用——PCA 降维：

```python
# 计算协方差矩阵（L2 说要特征分解的东西）
cov = np.cov(returns_matrix, rowvar=False)

# 特征值分解
eigenvalues, eigenvectors = np.linalg.eig(cov)

# 按特征值从大到小排序
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# 解释方差比例
explained_ratio = eigenvalues / eigenvalues.sum()
print("各主成分解释方差比例:")
for i, ratio in enumerate(explained_ratio):
    print(f"  PC{i+1}: {ratio:.2%}")

# 第一个主成分 = 市场因子（所有股票同向变动）
print(f"\n第一主成分（市场因子）权重:\n{eigenvectors[:, 0]}")
```

**关键洞察：** 如果第一主成分解释了 60%+ 的方差，说明这些股票主要由一个共同因子驱动——就是市场。

### 4. 金融术语速查（L1 内容）

| 术语 | 数学表示 | Python |
|------|---------|--------|
| 收益率 | $r_t = (P_t - P_{t-1}) / P_{t-1}$ | `pct_change()` |
| 年化波动率 | $\sigma \times \sqrt{252}$ | `rets.std() * np.sqrt(252)` |
| 组合方差 | $w^T \Sigma w$ | `w @ cov @ w` |
| Beta | $\beta = \text{Cov}(r_i, r_m) / \text{Var}(r_m)$ | 见下面的代码 |

```python
def beta(stock_returns, market_returns):
    """计算股票相对市场的 Beta"""
    cov = np.cov(stock_returns, market_returns)[0, 1]
    var_market = np.var(market_returns)
    return cov / var_market

# 示例：AAPL vs SPY
import yfinance as yf
spy = yf.download('SPY', start='2024-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()
aapl = yf.download('AAPL', start='2024-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()

aapl_beta = beta(aapl, spy)
print(f"AAPL Beta to SPY: {aapl_beta:.2f}")
```

## 练习

### 选择题

1. 向量 $a = [1,2]$, $b = [3,4]$，$a \cdot b$ 的值是：
   - A. 10
   - B. 11
   - C. 3
   - D. 7

2. 矩阵 A 的形状是 (5, 3)，向量 v 的形状是 (3,)，A@v 的结果形状是：
   - A. (5, 3)
   - B. (5,)
   - C. (3,)
   - D. (5, 3)

3. PCA 中第一主成分解释方差比例最高，意味着：
   - A. 数据主要由一个方向的变化驱动
   - B. 数据是随机的
   - C. 特征值都等于 1
   - D. 需要更多主成分

4. Beta > 1 意味着：
   - A. 股票比市场波动大
   - B. 股票比市场波动小
   - C. 股票与市场无关
   - D. 股票收益率高于市场

5. 特征值分解中，较大的特征值对应的特征向量是：
   - A. 方差贡献最小的方向
   - B. 方差贡献最大的方向
   - C. 随机方向
   - D. 零向量

### 编程题

**题目：** 下载 5 只科技股（AAPL, MSFT, GOOGL, AMZN, META）1 年数据，计算收益率协方差矩阵，做 PCA。第一主成分解释了多少方差？这个主成分对应什么因子？

```python
import numpy as np
import yfinance as yf

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

# 你的代码
```

### 填空题

组合方差的计算公式是 $w^T \_\_\_\_ w$，其中中间的矩阵是 \_\_\_\_ 矩阵。

## 掌握检查
