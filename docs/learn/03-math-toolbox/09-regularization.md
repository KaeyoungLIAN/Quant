# 3.9 正则化与风险模型

> MIT 18.S096 L10: Regularized Models
>
> 🎬 [看 L10 视频](https://youtu.be/wkysaQKAN00) → 然后学本章代码

## 一句话

当特征数量接近甚至超过样本数量时，普通最小二乘法会失效——系数爆炸、预测崩溃；正则化通过给目标函数加一个"惩罚项"，牺牲一点偏差换取方差的大幅下降，是量化中处理高维数据（几百个因子、几千只股票）的标配工具。

## 学习目标

学完本章你能：
- 理解为什么高维回归不加正则化会灾难性过拟合（系数爆炸）
- 用岭回归（Ridge / L2）处理多重共线性，通过交叉验证选择惩罚强度 λ
- 用 Lasso（L1）做因子选择——让不重要的系数精确归零
- 用弹性网（ElasticNet）结合 L1 和 L2 的优点
- 将正则化思想应用到协方差矩阵估计（收缩估计）和因子选择

> 📐 **前置数学**: 正则化的惩罚项本质是带约束的优化——
> 岭回归 = OLS + $||\beta||_2^2 \leq t$，Lasso = OLS + $||\beta||_1 \leq t$，
> 拉格朗日乘数法将约束变成惩罚项。如果这块不熟悉，复习 [拉格朗日乘数法](/prerequisite-math/05-optimization/5.2-lagrange-multiplier)。

## 核心内容

### 1. 过拟合回顾——为什么需要正则化

#### 高维灾难

假设你有 **50 个样本**（交易日），但尝试拟合 **20 个特征**（因子）。OLS 公式：

$$\hat{\beta} = (X^\top X)^{-1} X^\top y$$

当 $p \approx n$ 时，$X^\top X$ 接近奇异（行列式几乎为 0），求逆爆炸——$\hat{\beta}$ 的系数可以大到几万甚至几十万。模型在训练集上完美拟合（R² ≈ 1），但在新数据上表现极差。

#### 直观演示

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler

np.random.seed(42)

# ── 10 个真实相关特征 + 10 个噪声特征 —— 共 20 个特征 ──
n, p, p_true = 50, 20, 10
X = np.random.randn(n, p)
# 前 10 个特征有真实信号
true_beta = np.array([2, -1, 0.5, 0, 0, 0, 1.5, -0.8, 0.3, 0] + [0]*10)
y = X @ true_beta + np.random.randn(n) * 0.5

# OLS —— 系数爆炸
ols = LinearRegression()
ols.fit(X, y)

# 对比真实系数 vs OLS 估计
coef_comparison = pd.DataFrame({
    'True β': true_beta,
    'OLS β': np.round(ols.coef_, 4),
    '|OLS|': np.round(np.abs(ols.coef_), 4)
})
print("OLS 系数（部分展示）:")
print(coef_comparison.head(15))
print(f"\nOLS 系数绝对值的最大值: {np.abs(ols.coef_).max():.2f}")
print(f"OLS 训练集 R²: {ols.score(X, y):.4f}")
```

> **预期结果：** OLS 的系数绝对值可以达到几十甚至上百（取决于随机种子），训练集 R² 接近 1.0，但这是虚假的完美。

### 2. 岭回归（Ridge / L2）

#### 数学原理

岭回归在 OLS 损失函数上加一个 **L2 惩罚项**：

$$\hat{\beta}_{\text{ridge}} = \arg\min_\beta \left\{ \sum_{i=1}^n (y_i - X_i\beta)^2 + \lambda \sum_{j=1}^p \beta_j^2 \right\}$$

等价于带约束的优化：$\min ||y - X\beta||^2$ 且 $||\beta||_2^2 \leq t$。

**关键性质：**
- 把系数向零"收缩"，但**永远不会精确到零**
- 保留了所有特征——适合所有特征都有一定预测能力的情况
- 解析解：$\hat{\beta}_{\text{ridge}} = (X^\top X + \lambda I)^{-1} X^\top y$
- $\lambda$ 越大，收缩越强。$\lambda = 0$ 退化为 OLS

#### 与 OLS 系数对比

```python
# ── 标准化（岭回归要求特征尺度一致）──
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 不同 λ 下的岭回归
lambdas = [0, 0.1, 1, 10, 100]
ridge_coefs = []

for lam in lambdas:
    ridge = Ridge(alpha=lam)
    ridge.fit(X_scaled, y)
    ridge_coefs.append(ridge.coef_)

ridge_df = pd.DataFrame(
    ridge_coefs,
    index=[f'λ={l}' for l in lambdas],
    columns=[f'X{j+1}' for j in range(p)]
).T

print("岭回归系数（随 λ 增大而收缩）:")
print(ridge_df.round(4))
print(f"\nλ=0 (OLS) 系数范数: {np.linalg.norm(ridge_coefs[0]):.2f}")
print(f"λ=100 系数范数: {np.linalg.norm(ridge_coefs[-1]):.2f}")
```

#### 用交叉验证选择 λ

```python
from sklearn.linear_model import RidgeCV

# RidgeCV 自动做交叉验证选 λ
alphas = np.logspace(-3, 3, 50)  # λ 从 0.001 到 1000
ridge_cv = RidgeCV(alphas=alphas, scoring='neg_mean_squared_error', cv=5)
ridge_cv.fit(X_scaled, y)

print(f"最优 λ = {ridge_cv.alpha_:.4f}")
print(f"最优 Ridge 的测试 R² = {ridge_cv.score(X_scaled, y):.4f}")
print(f"最优 Ridge 的系数范数: {np.linalg.norm(ridge_cv.coef_):.2f}")
```

> **岭回归的量化应用：** 当你有 50～200 个宏观经济或风格因子时，很多因子都包含一些信息但都不算"决定性"——岭回归适合这种情况，因为它不会丢掉任何因子，只是对每个因子做稳健收缩。

### 3. Lasso（L1）

#### 数学原理

Lasso（Least Absolute Shrinkage and Selection Operator）在 OLS 上加 **L1 惩罚项**：

$$\hat{\beta}_{\text{lasso}} = \arg\min_\beta \left\{ \sum_{i=1}^n (y_i - X_i\beta)^2 + \lambda \sum_{j=1}^p |\beta_j| \right\}$$

**关键性质：**
- 系数可以**精确归零**——自动做特征选择
- L1 的几何形状（菱形）导致最优解往往落在坐标轴上（某些系数 = 0）
- 没有解析解（因为 L1 不可导），用**坐标下降法**（coordinate descent）求解
- $\lambda$ 越大，更多系数被压缩到 0

#### 正则化路径

```python
from sklearn.linear_model import lasso_path

# ── 计算 Lasso 的正则化路径 ──
alphas_lasso, coefs_lasso, _ = lasso_path(X_scaled, y, alphas=np.logspace(-2, 2, 100))

# 可视化：每个 λ 下，20 个系数的变化轨迹
plt.figure(figsize=(10, 6))
for i in range(p):
    plt.semilogx(alphas_lasso, coefs_lasso[i], label=f'X{i+1}')
plt.axvline(x=0.1, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('λ (log scale)')
plt.ylabel('系数值')
plt.title('Lasso 正则化路径——λ 越大，越多系数归零')
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
plt.grid(alpha=0.3)
# plt.show()  # 取消注释查看

print("正则化路径端点:")
print(f"λ 最小时 (λ={alphas_lasso[0]:.4f}) 非零系数量: {np.sum(coefs_lasso[:, 0] != 0)}")
print(f"λ 最大时 (λ={alphas_lasso[-1]:.4f}) 非零系数量: {np.sum(coefs_lasso[:, -1] != 0)}")

# ── 交叉验证选 λ ──
from sklearn.linear_model import LassoCV

lasso_cv = LassoCV(alphas=np.logspace(-3, 1, 100), cv=5, random_state=42)
lasso_cv.fit(X_scaled, y)

selected = np.sum(lasso_cv.coef_ != 0)
print(f"\n最优 λ (LassoCV) = {lasso_cv.alpha_:.4f}")
print(f"选中的特征数: {selected} / {p}")
print(f"非零系数的索引: {np.where(lasso_cv.coef_ != 0)[0]}")

# 对比真实特征（前 10 个有信号）
true_signals = set(range(10))
selected_indices = set(np.where(lasso_cv.coef_ != 0)[0])
print(f"正确选中的真实信号: {len(true_signals & selected_indices)} / {p_true}")
```

> **Lasso 的量化应用：** 因子选择。你有 100+ 个技术指标，但只有少数几个真正的预测信号。Lasso 帮你选出那少数几个关键因子。后续章节的因子模型中，Lasso 也是 Top 工具。

### 4. 弹性网（ElasticNet）

#### 混合惩罚

弹性网结合 L1 和 L2，拿了两头的好处：

$$\hat{\beta}_{\text{enet}} = \arg\min_\beta \left\{ \sum_{i=1}^n (y_i - X_i\beta)^2 + \lambda \left( \alpha ||\beta||_1 + \frac{1-\alpha}{2} ||\beta||_2^2 \right) \right\}$$

其中 $\alpha \in [0, 1]$ 控制 L1 和 L2 的比例：
- $\alpha = 1$ → 纯 Lasso
- $\alpha = 0$ → 纯 Ridge
- $\alpha = 0.5$ → 各一半

**为什么需要弹性网？**
- Lasso 在高度相关的特征组中只会随机选一个（不稳健）
- 弹性网的 L2 项让相关特征"组进组出"（group selection）
- Lasso 最多能选 n 个特征（样本数限制），弹性网可以突破这个限制

```python
# ── ElasticNet 对比不同 α ──
from sklearn.linear_model import ElasticNetCV

# l1_ratio = α 就是我们公式里的 α
enet_cv = ElasticNetCV(
    l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0],
    alphas=np.logspace(-3, 1, 50),
    cv=5,
    random_state=42
)
enet_cv.fit(X_scaled, y)

print(f"ElasticNet 最优 α (l1_ratio) = {enet_cv.l1_ratio_:.2f}")
print(f"ElasticNet 最优 λ = {enet_cv.alpha_:.4f}")
print(f"选中的特征数: {np.sum(enet_cv.coef_ != 0)} / {p}")

# ── 三种方法对比 ──
print("\n=== 三种正则化的 5 折交叉验证 MSE ===")
print(f"{'方法':<15} {'CV MSE':>10} {'非零系数':>10}")
print("-" * 35)

# OLS
ols_cv_scores = cross_val_score(LinearRegression(), X_scaled, y, cv=5,
                                 scoring='neg_mean_squared_error')
print(f"{'OLS':<15} {-ols_cv_scores.mean():>10.4f} {p:>10d}")

# Ridge
ridge_cv_scores = cross_val_score(Ridge(alpha=ridge_cv.alpha_), X_scaled, y, cv=5,
                                   scoring='neg_mean_squared_error')
print(f"{'Ridge':<15} {-ridge_cv_scores.mean():>10.4f} {p:>10d}")

# Lasso
lasso_cv_scores = cross_val_score(Lasso(alpha=lasso_cv.alpha_), X_scaled, y, cv=5,
                                   scoring='neg_mean_squared_error')
print(f"{'Lasso':<15} {-lasso_cv_scores.mean():>10.4f} {np.sum(lasso_cv.coef_ != 0):>10d}")

# ElasticNet
enet_cv_scores = cross_val_score(
    ElasticNet(alpha=enet_cv.alpha_, l1_ratio=enet_cv.l1_ratio_),
    X_scaled, y, cv=5, scoring='neg_mean_squared_error'
)
print(f"{'ElasticNet':<15} {-enet_cv_scores.mean():>10.4f} {np.sum(enet_cv.coef_ != 0):>10d}")
```

### 5. 量化中的正则化

#### 5.1 协方差矩阵收缩——风险模型

**问题：** 样本协方差矩阵 $\hat{\Sigma} = \frac{1}{n} \sum (r_t - \bar{r})(r_t - \bar{r})^\top$ 在 $p > n$ 时是奇异的，即使 $p \approx n$ 也极度不稳定——极端的相关系数只是噪声。

**解决方案：收缩估计（Shrinkage）**。将样本协方差向一个"结构化目标"收缩：

$$\hat{\Sigma}_{\text{shrink}} = \delta F + (1 - \delta) \hat{\Sigma}$$

其中 $F$ 是一个结构化模型（如常数相关系数模型），$\delta \in [0, 1]$ 是收缩强度。

```python
from sklearn.covariance import LedoitWolf, ShrunkCovariance

# ── 多资产数据 ──
import yfinance as yf

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
           'V', 'JNJ', 'WMT', 'PG', 'XOM', 'CVX', 'UNH']
data = yf.download(tickers, start='2023-01-01', end='2024-12-31')['Adj Close']
returns = data.pct_change().dropna()

print(f"样本数: {len(returns)}, 资产数: {len(tickers)}")
print(f"样本/资产比: {len(returns) / len(tickers):.1f}")

# 样本协方差（不稳定）
sample_cov = returns.cov().values
print(f"\n样本协方差矩阵条件数: {np.linalg.cond(sample_cov):.2f}")

# Ledoit-Wolf 收缩（最优收缩）
lw = LedoitWolf().fit(returns)
lw_cov = lw.covariance_
print(f"Ledoit-Wolf 协方差条件数: {np.linalg.cond(lw_cov):.2f}")
print(f"Ledoit-Wolf 收缩强度 (δ): {lw.shrinkage_:.4f}")

# 经典 ShrunkCovariance
shrink = ShrunkCovariance(shrinkage=0.5).fit(returns)
shrink_cov = shrink.covariance_
print(f"Shrunk (δ=0.5) 协方差条件数: {np.linalg.cond(shrink_cov):.2f}")

# 对比
print(f"\n样本协方差奇异？ {np.linalg.matrix_rank(sample_cov) < len(tickers)}")
print(f"Ledoit-Wolf 奇异？ {np.linalg.matrix_rank(lw_cov) < len(tickers)}")

# 最小方差组合权重（使用不同协方差估计）
from scipy.optimize import minimize

def min_var_weights(cov):
    """最小方差组合（无做空限制）"""
    n = cov.shape[0]
    def portfolio_var(w):
        return w @ cov @ w
    cons = {'type': 'eq', 'fun': lambda w: w.sum() - 1}
    bounds = [(0, 1)] * n
    res = minimize(portfolio_var, np.ones(n)/n, bounds=bounds, constraints=cons)
    return res.x

w_sample = min_var_weights(sample_cov)
w_lw = min_var_weights(lw_cov)

print(f"\n=== 最小方差组合权重 ===")
weight_df = pd.DataFrame({
    'Ticker': tickers,
    'Sample Cov': np.round(w_sample, 4),
    'Ledoit-Wolf': np.round(w_lw, 4)
})
print(weight_df.to_string(index=False))
print(f"\n样本协方差→极端权重（最大权重: {w_sample.max():.4f}, 集中度: {(w_sample**2).sum():.4f}）")
print(f"Ledoit-Wolf→更均匀（最大权重: {w_lw.max():.4f}, 集中度: {(w_lw**2).sum():.4f}）")
```

> **关键洞察：** 收缩协方差矩阵的投资组合权重比样本协方差更稳定、更分散——这是正则化在风险模型中的直接体现。

#### 5.2 因子选择——用 Lasso 挑因子

在量化因子模型中，我们有几十上百个候选因子，但真正有预测力的可能只有几个。Lasso 可以自动完成因子选择。

```python
# ── 模拟因子预测收益率 ──
np.random.seed(42)
n_days = 500
n_factors = 30

# 构造 30 个因子，只有 F1、F5、F12、F20 是真实有预测力的
factor_returns = np.random.randn(n_days, n_factors)
true_factor_betas = np.zeros(n_factors)
true_factor_betas[[0, 4, 11, 19]] = [0.03, -0.02, 0.015, -0.01]

y_returns = factor_returns @ true_factor_betas + np.random.randn(n_days) * 0.02

# Lasso 因子选择
scaler = StandardScaler()
X_factors = scaler.fit_transform(factor_returns)

lasso_factor = LassoCV(cv=5, random_state=42)
lasso_factor.fit(X_factors, y_returns)

selected_factors = np.where(lasso_factor.coef_ != 0)[0]
print(f"真实有效因子: {[0, 4, 11, 19]}")
print(f"Lasso 选中的因子索引: {selected_factors}")
print(f"选中的正确因子: {len(set([0, 4, 11, 19]) & set(selected_factors))} / 4")

# 因子系数对比
factor_df = pd.DataFrame({
    '因子索引': range(n_factors),
    '真实 β': true_factor_betas,
    'Lasso β': np.round(lasso_factor.coef_, 6)
})
print("\n所有因子系数:")
print(factor_df[factor_df['Lasso β'] != 0].to_string(index=False))
```

### 三方法总结

| 方法 | 惩罚项 | 系数行为 | 何时用 |
|------|--------|----------|--------|
| **Ridge (L2)** | $\lambda \sum \beta_j^2$ | 收缩但不归零 | 多重共线性，所有特征都有信息 |
| **Lasso (L1)** | $\lambda \sum |\beta_j|$ | 可以精确归零（自动选特征） | 因子选择，稀疏建模 |
| **ElasticNet** | $\lambda(\alpha||\beta||_1 + \frac{1-\alpha}{2}||\beta||_2^2)$ | 组选+收缩 | 高度相关特征存在时 |

> 💡 **实战准则：** 不确定时先用 ElasticNet 或 RidgeCV（自动 CV 选 λ）；如果你相信只有少数几个因子起作用，用 Lasso。

## 深度阅读

| 资源 | 链接 |
|------|------|
| 拉格朗日乘数法（理解惩罚项的数学本质） | [5.2 拉格朗日乘数法](/prerequisite-math/05-optimization/5.2-lagrange-multiplier) |
| scikit-learn 官方文档——Lasso 路径 | [Lasso Path Example](https://scikit-learn.org/stable/auto_examples/linear_model/plot_lasso_lars.html) |
| sklearn 协方差收缩 | [Shrunk Covariance](https://scikit-learn.org/stable/modules/covariance.html#shrunk-covariance) |
| 论文（Ledoit & Wolf, 2004） | [A Well-Conditioned Estimator for Large-Dimensional Covariance Matrices](https://www.ledoit.net/honey.pdf) |
| ESL（统计学习导论）第 6 章 | [An Introduction to Statistical Learning](https://www.statlearning.com/) |

## 练习

### 判断题 / 选择题

**Q1.** 岭回归的 L2 惩罚可以自动将不重要的特征的系数压缩到恰好为 0。

<details>
<summary>A.</summary>
❌ 错。L2 惩罚会让系数收缩但永远不会精确为零——那是 Lasso (L1) 的特性。
</details>

**Q2.** 当你有 100 个候选因子但只有 5 个真正有效时，Lasso 是比 Ridge 更合适的选择。

<details>
<summary>A.</summary>
✅ 对。Lasso 自动做特征选择，把不重要的特征系数变为 0，适合稀疏场景。
</details>

**Q3.** 在协方差矩阵收缩中，Ledoit-Wolf 方法会自动选择一个最优的收缩强度 δ，使得估计量在统计上是可逆（非奇异）的。

<details>
<summary>A.</summary>
✅ 对。Ledoit-Wolf 通过最小化 MSE 自动确定 δ，且收缩后的协方差矩阵总是满秩的。
</details>

**Q4.** ElasticNet 的 L1 项可以处理特征组（group of correlated features）效应，而纯 Lasso 做不到这一点。

<details>
<summary>A.</summary>
❌ 不准确。ElasticNet 的 L2 项（不是 L1 项）帮助处理相关特征组——让相关特征"组进组出"。纯 Lasso 在高度相关的特征中只会随机选一个。
</details>

### 编程练习

**用 Lasso 从 12 个技术指标中选出真正预测 SPY 收益率的关键因子。**

```python
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

# 下载数据
spy = yf.download('SPY', start='2020-01-01', end='2024-12-31')['Adj Close']
returns = spy.pct_change().dropna()

# ── 构造 12 个技术指标特征 ──
# （这些指标有些是真实信号，大部分是噪音）
close = spy.values
n = len(close)

# 特征 1-5：常见的滞后收益率（可能有预测力）
f1 = pd.Series(returns.shift(1), name='lag1')
f2 = pd.Series(returns.shift(2), name='lag2')
f3 = pd.Series(returns.shift(3), name='lag3')
f4 = pd.Series(returns.shift(5), name='lag5')
f5 = pd.Series(returns.shift(10), name='lag10')

# 特征 6-8：简单移动平均价差
ma5  = pd.Series(spy.rolling(5).mean(), name='ma5')
ma20 = pd.Series(spy.rolling(20).mean(), name='ma20')
f6 = pd.Series((close / ma5 - 1) * 100, name='ma5_pct')      # 价格偏离 MA5%
f7 = pd.Series((close / ma20 - 1) * 100, name='ma20_pct')    # 价格偏离 MA20%

# 特征 8：RSI（相对强弱指标）
delta = close[1:] - close[:-1]
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)
avg_gain = pd.Series(gain).rolling(14).mean()
avg_loss = pd.Series(loss).rolling(14).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
f8 = pd.Series(np.concatenate([[np.nan], rsi.values]), name='rsi')
f8.index = spy.index

# 特征 9-10：波动率相关
vol5  = pd.Series(returns.rolling(5).std(), name='vol5')
vol20 = pd.Series(returns.rolling(20).std(), name='vol20')
f9 = pd.Series(vol5 / vol20, name='vol_ratio')

# 特征 11-12：随机噪音（应该被 Lasso 排除）
rng = np.random.RandomState(42)
f11 = pd.Series(rng.randn(len(returns)), index=returns.index, name='noise1')
f12 = pd.Series(rng.randn(len(returns)), index=returns.index, name='noise2')

# ── 合并特征 ──
features = pd.concat([f1, f2, f3, f4, f5, f6, f7, f8, f9, f11, f12], axis=1)
features.index = returns.index

# 去掉 NaN
data = pd.concat([returns.shift(-1).rename('next_return'), features], axis=1).dropna()

y_next = data['next_return']
X_tech = data.drop('next_return', axis=1)

print(f"样本数: {len(y_next)}")
print(f"特征数: {X_tech.shape[1]}")
print(f"特征列表: {list(X_tech.columns)}")

# ── 你的任务 ──
# 1. 用 StandardScaler 标准化特征
# 2. 用 LassoCV(cv=5, random_state=42) 拟合
# 3. 输出选择的因子和对应的系数
# 4. 解释：哪些因子被选中了？噪声变量被排除了吗？
# === 从这开始写你的代码 ===

# 参考答案（隐藏——自己写完后对比）：
# 1. 标准化
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X_tech)
# 2. Lasso with CV
# lasso = LassoCV(cv=5, random_state=42)
# lasso.fit(X_scaled, y_next)
# 3. 结果
# selected = X_tech.columns[lasso.coef_ != 0]
# print(f"选中的因子: {list(selected)}")
# print(f"系数: {dict(zip(selected, lasso.coef_[lasso.coef_ != 0]))}")
```

### 完形填空

> 岭回归对目标函数添加 **____（①）** 惩罚项，使得系数向零 **____（②）**但不会精确归零；Lasso 添加 **____（③）** 惩罚项，可以让系数 **____（④）**。弹性网结合两者，用超参数 **____（⑤）** 控制 L1 与 L2 的比例。在协方差矩阵估计中，**____（⑥）** 方法可以自动选择最优的收缩强度，使得协方差矩阵总是 **____（⑦）** 的。

<details>
<summary>答案</summary>
① L2 (或 $\|\beta\|_2^2$)  
② 收缩  
③ L1 (或 $\|\beta\|_1$)  
④ 精确归零（做特征选择）  
⑤ $\alpha$ (或 l1_ratio)  
⑥ Ledoit-Wolf  
⑦ 非奇异（满秩 / 可逆）
</details>

## 掌握检查

学完本章后你应该能回答这些问题。如果不能，请回顾对应章节：

1. ❓ 为什么 p ≈ n 时 OLS 会失效？（→ 1. 过拟合回顾）
2. ❓ 岭回归的惩罚项是什么？它和 OLS 的解析解有何不同？（→ 2. Ridge）
3. ❓ Lasso 为什么可以自动做特征选择？L1 惩罚的几何解释是什么？（→ 3. Lasso）
4. ❓ 为什么当特征高度相关时 ElasticNet 比 Lasso 更稳健？（→ 4. ElasticNet）
5. ❓ 协方差矩阵收缩如何降低了投资组合权重的极端性？（→ 5.1 风险模型）
6. ❓ 什么时候该用 Ridge 而不是 Lasso，反之亦然？（→ 总结表）
