# 3.7 时间序列分析

> 对应 MIT 18.S096 L8: Time Series + L11: Statistical Arbitrage + L12: Pairs Trading
>
> 🎬 [看 L8 视频](https://youtu.be/oYvOHC68bQw) → 🎬 [看 L11 视频](https://youtu.be/YpV2HEbH2XU) → 🎬 [看 L12 视频](https://youtu.be/1Sj2GTi9QZQ) → 然后学本章代码

## 一句话

时间序列分析让你能回答"这个序列有记忆吗？"和"两个看似随机游走的资产之间是否存在统计套利关系？"——从 ARIMA 预测到配对交易的协整检验，是量化策略的统计地基。

## 学习目标

学完本章你能：
- 区分平稳与非平稳时间序列，理解单位根的含义
- 用 ACF 和 PACF 图判断 AR/MA 阶数，拟合 ARIMA 模型做预测
- 用 ADF 检验验证序列的平稳性
- 理解协整（Cointegration）并用它进行配对交易
- 做季节性分解（Seasonal Decomposition）

## 核心内容

### 1. 时间序列基础——平稳性与自相关

**平稳性（Stationarity）** 是时间序列分析的起点。一个时间序列 $y_t$ 如果满足：

1. **均值恒定**：$\mathbb{E}[y_t] = \mu$（不随时间变化）
2. **方差恒定**：$\text{Var}(y_t) = \sigma^2$（不随时间变化）
3. **协方差仅依赖滞后**：$\text{Cov}(y_t, y_{t-k}) = \gamma_k$（只与时间差 k 有关）

就称它为**弱平稳**（Weak Stationary），量化金融里通常简称"平稳"。

**股票价格 vs 收益率：** 价格通常是非平稳的（随机游走），而日收益率通常是平稳的。

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 下载真实数据
aapl = yf.download('AAPL', start='2023-01-01', end='2024-12-31')['Adj Close']
returns = aapl.pct_change().dropna()

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# 价格 vs 收益率
axes[0, 0].plot(aapl.index, aapl.values, color='steelblue')
axes[0, 0].set_title('AAPL 价格——非平稳（有趋势）')
axes[0, 0].set_ylabel('Price ($)')

axes[0, 1].plot(returns.index, returns.values, color='coral', alpha=0.7)
axes[0, 1].set_title('AAPL 日收益率——平稳（均值≈0）')
axes[0, 1].set_ylabel('Returns')
axes[0, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# ACF：价格（非平稳 → ACF 缓慢衰减）
plot_acf(aapl.dropna(), lags=40, ax=axes[1, 0])
axes[1, 0].set_title('ACF: 价格——自相关缓慢衰减（非平稳特征）')

# ACF：收益率（平稳 → 快速截尾）
plot_acf(returns, lags=40, ax=axes[1, 1])
axes[1, 1].set_title('ACF: 收益率——快速衰减（平稳特征）')

plt.tight_layout()
plt.show()
```

**关键观察：**
- 价格的 ACF 在滞后很多期后仍然显著——这是非平稳的标志
- 收益率的 ACF 快速衰减到置信区间内——这是平稳的标志

**ACF vs PACF：**
- **ACF（自相关函数）**：衡量 $y_t$ 和 $y_{t-k}$ 之间的总相关性（包含中间滞后的间接影响）
- **PACF（偏自相关函数）**：衡量 $y_t$ 和 $y_{t-k}$ 之间的**净**相关性（剔除了中间滞后的影响）

### 2. ARIMA 模型

#### AR(p)——自回归模型

$$y_t = c + \phi_1 y_{t-1} + \phi_2 y_{t-2} + \dots + \phi_p y_{t-p} + \varepsilon_t$$

AR 模型假设**过去 p 期的值**可以预测当前值。

```python
from statsmodels.tsa.arima.model import ARIMA

# 模拟一个 AR(2) 过程
np.random.seed(42)
n = 500
phi1, phi2 = 0.6, 0.2
eps = np.random.randn(n)
y_ar = np.zeros(n)
for t in range(2, n):
    y_ar[t] = 0.5 + phi1 * y_ar[t-1] + phi2 * y_ar[t-2] + eps[t]

# 用 PACF 判断 AR 阶数
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(y_ar, lags=30, ax=axes[0])
plot_pacf(y_ar, lags=30, ax=axes[1])
plt.show()
# PACF 在 lag>2 后截尾 → AR(2)
```

**经验法则：** PACF 在 lag>p 后截尾 → AR(p)

#### MA(q)——移动平均模型

$$y_t = c + \varepsilon_t + \theta_1 \varepsilon_{t-1} + \dots + \theta_q \varepsilon_{t-q}$$

MA 模型假设过去 q 期的**随机冲击**影响当前值。

```python
# 模拟一个 MA(2) 过程
theta1, theta2 = 0.5, 0.3
eps = np.random.randn(n)
y_ma = np.zeros(n)
for t in range(2, n):
    y_ma[t] = 1.0 + eps[t] + theta1 * eps[t-1] + theta2 * eps[t-2]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(y_ma, lags=30, ax=axes[0])
plot_pacf(y_ma, lags=30, ax=axes[1])
plt.show()
# ACF 在 lag>2 后截尾 → MA(2)
```

**经验法则：** ACF 在 lag>q 后截尾 → MA(q)

#### ARIMA(p,d,q)——集成模型

ARIMA = AR(p) + 差分(d) + MA(q)

- **d** = 需要差分的次数，使序列变平稳
- 差分运算：$\Delta y_t = y_t - y_{t-1}$
- 一阶差分通常足以让金融价格序列变平稳（因为价格≈随机游走，一阶差分=收益率）

```python
# 用真实数据拟合 ARIMA(1,1,1)
aapl = yf.download('AAPL', start='2023-01-01', end='2024-12-31')['Adj Close']

# 注意 d=1（对价格做一阶差分使其平稳）
model = ARIMA(aapl, order=(1, 1, 1))
result = model.fit()
print(result.summary())

# 预测未来 10 天
forecast = result.forecast(steps=10)
print("\n未来 10 天价格预测：")
print(forecast)

# 可视化
plt.figure(figsize=(12, 5))
plt.plot(aapl.index[-100:], aapl.values[-100:], label='历史价格', color='steelblue')
future_idx = pd.date_range(start=aapl.index[-1] + pd.Timedelta(days=1), periods=10, freq='B')
plt.plot(future_idx, forecast, label='预测', color='red', marker='o')
plt.fill_between(
    future_idx,
    forecast - 1.96 * np.sqrt(result.params.get('sigma2', 0.001)) * np.arange(1, 11),
    forecast + 1.96 * np.sqrt(result.params.get('sigma2', 0.001)) * np.arange(1, 11),
    alpha=0.2, color='red', label='95% 置信区间'
)
plt.title('ARIMA(1,1,1) 对 AAPL 价格的 10 日预测')
plt.legend()
plt.show()
```

**ARIMA 选择指南：**

| 步骤 | 方法 |
|------|------|
| 判断是否需要差分 (d) | ADF 检验（p>0.05 → 需要差分） |
| 判断 AR 阶数 (p) | PACF 在 lag p 后截尾 |
| 判断 MA 阶数 (q) | ACF 在 lag q 后截尾 |
| 模型诊断 | 检查残差是否白噪声（Ljung-Box 检验） |

### 3. 单位根检验（ADF）

#### 为什么叫"单位根"？

考虑 AR(1) 模型：

$$y_t = \phi y_{t-1} + \varepsilon_t$$

- 如果 $|\phi| < 1$：序列是平稳的（冲击随时间衰减）
- 如果 $|\phi| = 1$：**单位根**（随机游走，冲击永久保留）
- 如果 $|\phi| > 1$：爆炸性序列（不常见于金融数据）

ADF（Augmented Dickey-Fuller）检验的假设：

- $H_0$：序列有一个单位根（**非平稳**）
- $H_1$：序列是平稳的

```python
from statsmodels.tsa.stattools import adfuller

# 对价格做 ADF 检验
price_adf = adfuller(aapl.dropna())
print("=== 价格序列 ADF 检验 ===")
print(f"ADF 统计量: {price_adf[0]:.4f}")
print(f"p-value: {price_adf[1]:.6f}")
print(f"临界值 (5%): {price_adf[4]['5%']:.4f}")
print(f"结论: {'非平稳（有单位根）' if price_adf[1] > 0.05 else '平稳'}")
print()

# 对收益率做 ADF 检验
return_adf = adfuller(returns.dropna())
print("=== 收益率序列 ADF 检验 ===")
print(f"ADF 统计量: {return_adf[0]:.4f}")
print(f"p-value: {return_adf[1]:.6f}")
print(f"临界值 (5%): {return_adf[4]['5%']:.4f}")
print(f"结论: {'非平稳（有单位根）' if return_adf[1] > 0.05 else '平稳'}")
```

**输出解读：**
- 价格 ADF：p-value 通常 > 0.05（有时接近 0.5-0.9）→ **有单位根，不平稳**
- 收益率 ADF：p-value 通常 ≈ 0（远小于 0.05）→ **没有单位根，平稳**

**实操指南：**

```
p-value > 0.05  →  序列有单位根  →  需要差分 (d=1)，然后再检验
p-value ≤ 0.05  →  序列平稳     →  可以直接建模
```

**为什么这很重要？** 用非平稳序列做回归会导致**伪回归**（Spurious Regression）——两个毫无关系的随机游走序列回归的 R² 可能很高，t 统计量看似显著，但完全是假的相关性（Granger & Newbold 1974 经典论文）。

### 4. 协整与配对交易（L11 + L12）

#### 协整的核心洞察

协整（Cointegration）的精髓在下面这句话里理解：

> 一个醉汉牵着一条狗散步——单独看，两个都是随机游走（非平稳），但它们之间的距离（价差）是平稳的，因为狗绳把它们拉在一起。

**数学定义：** 如果两个（或多个）非平稳序列 $y_t, x_t$ 存在线性组合 $z_t = y_t - \beta x_t$ 是平稳的，就称它们**协整**。

```python
from statsmodels.tsa.stattools import coint, adfuller
import yfinance as yf

# 下载两只股票——传统配对：XOM (Exxon) vs CVX (Chevron)
xom = yf.download('XOM', start='2023-01-01', end='2024-12-31')['Adj Close']
cvx = yf.download('CVX', start='2023-01-01', end='2024-12-31')['Adj Close']

# 对齐数据
prices = pd.concat({'XOM': xom, 'CVX': cvx}, axis=1).dropna()

# 1. 先验证每只股票都是非平稳的
for col in prices.columns:
    adf = adfuller(prices[col].dropna())
    print(f"{col}: ADF p-value = {adf[1]:.6f} → {'非平稳' if adf[1] > 0.05 else '平稳'}")

print()

# 2. 协整检验
score, pvalue, _ = coint(prices['XOM'], prices['CVX'])
print(f"协整检验 p-value = {pvalue:.6f}")
print(f"结论: {'存在协整关系 ✓' if pvalue < 0.05 else '不存在协整关系 ✗'}")

# 3. 可视化价差（Spread）
# 用 OLS 估计 hedge ratio
import statsmodels.api as sm

X = sm.add_constant(prices['CVX'])
model = sm.OLS(prices['XOM'], X).fit()
hedge_ratio = model.params['CVX']
print(f"Hedge Ratio (β) = {hedge_ratio:.4f}")

# 计算价差
spread = prices['XOM'] - hedge_ratio * prices['CVX']

# 验证价差的平稳性
spread_adf = adfuller(spread.dropna())
print(f"价差 ADF p-value = {spread_adf[1]:.6f}")
print(f"价差是否平稳？{'是 ✓' if spread_adf[1] < 0.05 else '否 ✗'}")

# 可视化
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

axes[0].plot(prices.index, prices['XOM'], label='XOM', color='navy')
axes[0].plot(prices.index, prices['CVX'], label='CVX', color='darkgreen')
axes[0].set_title('XOM vs CVX——两只非平稳股票')
axes[0].legend()

axes[1].plot(prices.index, spread, color='purple')
axes[1].axhline(y=spread.mean(), color='red', linestyle='--', label='均值')
axes[1].axhline(y=spread.mean() + 2*spread.std(), color='orange', linestyle=':', label='±2σ')
axes[1].axhline(y=spread.mean() - 2*spread.std(), color='orange', linestyle=':', label='')
axes[1].set_title('价差 —— 平稳的！均值回归特征')
axes[1].legend()

plot_acf(spread.dropna(), lags=40, ax=axes[2])
axes[2].set_title('价差 ACF —— 快速衰减（平稳特征）')

plt.tight_layout()
plt.show()
```

#### 配对交易策略逻辑

```
当价差偏离到 ±2σ 以上时：
  如果价差 > +2σ：卖 XOM，买 CVX（预期价差回归）
  如果价差 < -2σ：买 XOM，卖 CVX（预期价差回归）
  在价差回归到均值附近时平仓
```

这就是**统计套利（Statistical Arbitrage）** 的核心——不依赖方向性预测，只依赖价差的均值回归性质。

#### 协整 vs 相关性

| | 相关性 | 协整 |
|--|--------|------|
| 衡量 | 线性关系的方向和强度 | 是否存在平稳的线性组合 |
| 时间维度 | 静态（无记忆） | 动态（长期均衡关系） |
| 伪相关风险 | 高——两个随机游走也可能相关 | 低——检验了均衡关系的持久性 |
| 量化应用 | 因子筛选 | 配对交易、统计套利 |

**经典误解：** 高相关 ≠ 协整！两只完全不相关的股票因为同向趋势而高度相关，但价差可能发散。

### 5. 季节性分解

很多金融时间序列有**季节性模式**（例如：月底效应、季度财报周期、商品期货的季节性库存变化）。

```python
from statsmodels.tsa.seasonal import seasonal_decompose

# 使用高频数据演示（这里用模拟+真实组合）
# 实际中，可以用某个周期性明显的 ETF 或商品
prices = yf.download('XLE', start='2022-01-01', end='2024-12-31')['Adj Close']

# 季节性分解（日数据，一年约 252 个交易日）
decomposition = seasonal_decompose(prices, model='multiplicative', period=252)

fig = decomposition.plot()
fig.set_size_inches(14, 10)
plt.show()
```

**分解的三个成分：**
- **趋势（Trend）**：长期方向（如能源板块的长期价格趋势）
- **季节性（Seasonal）**：固定周期的重复模式（如每年冬季取暖需求推高能源价格）
- **残差（Residual）**：不能被趋势和季节性解释的部分——通常是随机噪声或异常事件

**适用场景：**
- 商品期货：有明显的收获/消费季节性
- 宏观经济指标：GDP、CPI 有季度/年度周期
- 交易量：有日内和周内模式
- 波动率：有日内的 U 型模式

## 深度阅读

- Wiki → [时间序列基础](/prerequisite-math/04-statistics/4.5-time-series)
- Wiki → [统计套利](/quant-finance/2.3-statistical-arbitrage)
- 经典论文：Engle & Granger (1987) "Co-Integration and Error Correction: Representation, Estimation, and Testing"
- 经典论文：Granger & Newbold (1974) "Spurious Regressions in Econometrics"

## 练习

### 选择题

1. 一个 AR(1) 模型 $y_t = 0.8 y_{t-1} + \varepsilon_t$ 的 PACF 图应该是：
   - A. PACF 在所有滞后都显著
   - B. PACF 在 lag 1 显著，之后截尾
   - C. PACF 在 lag 2 显著，之后截尾
   - D. PACF 在 lag 1 之后线性衰减

2. ADF 检验的 p-value = 0.32 意味着：
   - A. 序列是平稳的，可以进行回归分析
   - B. 序列有单位根，差分前不宜直接建模
   - C. 序列有强季节性
   - D. 模型拟合良好

3. 两只股票 $X_t$ 和 $Y_t$ 都是 I(1)，如果存在 $\beta$ 使得 $Y_t - \beta X_t$ 是 I(0)，那么：
   - A. $X_t$ 和 $Y_t$ 高度相关
   - B. $X_t$ 和 $Y_t$ 协整，价差可以用于配对交易
   - C. $X_t$ 和 $Y_t$ 协方差很大
   - D. 两只股票来自同一行业

4. ARIMA(p,d,q) 中 d=1 的作用是：
   - A. 增加模型复杂度以提高拟合度
   - B. 通过一次差分使非平稳序列变平稳
   - C. 减少参数数量
   - D. 消除自相关

### 编程题

**题目：** 找到一对协整的股票，检验价差的平稳性，并用 ARIMA 模型预测未来 5 天的价差。

要求：
1. 从 yfinance 选择两只你认为可能协整的股票（不同行业也可以，试试 SPY 和 IVV？或者你的创意）
2. 用 `coint()` 检验协整
3. 如果协整，计算 hedge ratio（用 OLS），计算价差
4. 用 ADF 检验验证价差的平稳性
5. 用 ARIMA(1,0,1) 拟合价差（因为价差应该是平稳的，d=0），预测未来 5 天价差并可视化

```python
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.tsa.arima.model import ARIMA

# 你的代码
```

### 填空题

时间序列的平稳性要求均值 \\_\\_\\_\\_、方差 \\_\\_\\_\\_、协方差只与 \\_\\_\\_\\_ 有关。ARIMA 中 d 代表 \\_\\_\\_\\_ 次数。如果 ADF 检验的 p-value \\_\\_\\_\\_ 0.05，则拒绝单位根假设。两只 I(1) 序列如果存在线性组合是 I(0)，则称它们 \\_\\_\\_\\_。配对交易的核心假设是价差的 \\_\\_\\_\\_ 性质。

## 掌握检查

- [ ] 我能解释平稳时间序列的三个条件，并能从 ACF 图判断序列是否平稳
- [ ] 我能用 PACF 和 ACF 判断 AR 和 MA 的阶数
- [ ] 我能用 ARIMA 模型对股价进行预测
- [ ] 我能用 ADF 检验判断一个序列是否有单位根
- [ ] 我能解释协整的含义，以及它和相关的区别
- [ ] 我能找到一对协整的股票，计算价差，并用 ARIMA 预测价差
- [ ] 我能进行季节性分解并解读趋势/季节/残差分量
