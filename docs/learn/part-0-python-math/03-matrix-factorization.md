# 0.3 矩阵分解与 SVD

> 对应 MIT 18.S096 L4: Matrix Primer（Morgan Stanley 矩阵团队）
>
> 🎬 [看 L4 视频](https://youtu.be/6XxrL0odXmY) → 然后学本章代码

## 一句话

矩阵分解 = 把一个大矩阵拆成几个简单矩阵的乘积——降维、降噪、找结构。PCA、因子模型、风险模型都建立在这之上。

## 学习目标

学完本章你能：
- 理解矩阵分解（SVD、Cholesky）在量化中的用途
- 用 SVD 做 PCA 降维
- 用 Cholesky 分解生成相关随机序列

## 核心内容

### 1. SVD——最通用的矩阵分解

```python
import numpy as np
import yfinance as yf

# 取 10 只股票 1 年收益率
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
           'TSLA', 'NVDA', 'JPM', 'V', 'JNJ']
data = yf.download(tickers, start='2024-01-01', end='2024-12-31')['Adj Close']
returns = data.pct_change().dropna()

# 中心化
returns_centered = returns - returns.mean(axis=0)

# SVD
U, S, Vt = np.linalg.svd(returns_centered, full_matrices=False)

print(f"U 形状: {U.shape}")  # (天数, 天)
print(f"S (奇异值): {S[:5].round(2)}")
print(f"Vt 形状: {Vt.shape}")  # (10, 10)

# 奇异值平方 = 解释方差
var_explained = (S**2) / (S**2).sum()
print(f"\n前3个奇异值解释方差: {var_explained[:3].sum():.2%}")
```

### 2. PCA = SVD 的另一种视角

```python
# 用 Vt 的行作为主成分权重
pc1 = Vt[0]  # 第一主成分 = 各股票的权重
pc2 = Vt[1]  # 第二主成分

print("第一主成分（市场因子）权重:")
for ticker, weight in zip(tickers, pc1):
    print(f"  {ticker}: {weight:.3f}")

print("\n第二主成分（可能是行业因子）权重:")
for ticker, weight in zip(tickers, pc2):
    print(f"  {ticker}: {weight:.3f}")
```

### 3. Cholesky 分解——生成相关随机序列

要模拟多个相关资产的路径——用 Cholesky：

```python
# 生成两个相关的正态序列
correlation = 0.7  # 期望的相关系数
cov_matrix = np.array([[1.0, correlation],
                        [correlation, 1.0]])

# Cholesky 分解
L = np.linalg.cholesky(cov_matrix)

# 生成独立随机数 → 转换为相关
np.random.seed(42)
independent = np.random.randn(1000, 2)
correlated = independent @ L.T

print(f"生成的序列相关系数: {np.corrcoef(correlated.T)[0,1]:.3f}")
print(f"期望相关系数: {correlation}")

# 量化应用：生成多个相关资产的价格路径
S0 = np.array([100, 80])
sigma = np.array([0.2, 0.25])
dt = 1/252

# 每天的随机冲击
z = np.random.randn(1, 2) @ L.T
# 代入每个资产的 SDE
dS = S0 * (0.05 * dt + sigma * np.sqrt(dt) * z)
```

### 4. 矩阵求逆与正则化

```python
# 在回归和风险模型中，你需要求 (X'X)^{-1}
# 但如果 X'X 近似奇异（多重共线性），数值不稳定

from numpy.linalg import inv, cond

# 构造一个近奇异的矩阵
X = np.random.randn(100, 3)
X[:, 2] = X[:, 0] * 0.99 + X[:, 1] * 0.01 + np.random.randn(100) * 0.01  # 近似线性相关

XtX = X.T @ X
print(f"条件数: {cond(XtX):.2f}")
print(f"条件数 > 1000 → 矩阵近奇异，求逆不稳定")

# 正则化：在 X'X 上加一个小扰动
lambda_reg = 0.1
XtX_reg = XtX + lambda_reg * np.eye(3)
print(f"正则化后条件数: {cond(XtX_reg):.2f}")
```

## 深度阅读

- Wiki → [SVD 与 PCA](/prerequisite-math/02-linear-algebra/2.4-eigen-decomposition)

## 练习

### 选择题

1. SVD 分解 UΣV^T 中，V 的列代表：
   - A. 时间模式
   - B. 资产权重（主成分方向）
   - C. 奇异值
   - D. 残差

2. Cholesky 分解要求输入矩阵：
   - A. 对称正定
   - B. 可逆
   - C. 对角矩阵
   - D. 正交矩阵

3. 条件数大的矩阵在求逆时会：
   - A. 更快
   - B. 数值不稳定
   - C. 总是失败
   - D. 精度更高

4. 正则化通过在 X'X 上加什么来改善条件数？
   - A. 单位矩阵乘以 λ
   - B. 全 1 矩阵
   - C. 零矩阵
   - D. 对角矩阵

### 编程题

**题目：** 取 SPY + TLT + GLD（股票、债券、黄金）1 年数据，做 PCA。三大类资产的第一主成分是什么？它如何解释三类资产的关系？

### 填空题

SVD 将矩阵 A 分解为 $A = U \_\_\_\_ V^T$，其中中间的矩阵是对角矩阵，元素称为 \_\_\_\_。

## 掌握检查
