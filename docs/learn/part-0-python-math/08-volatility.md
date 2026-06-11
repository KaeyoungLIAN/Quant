# 0.8 波动率建模

> MIT 18.S096 L9: Volatility Modeling
>
> 🎬 [看 L9 视频](https://youtu.be/YR4psBSD60E) → 然后学本章代码

## 一句话

波动率不是常数——大的波动之后常常跟着大的波动（波动率聚集），而 ARCH/GARCH 模型正是捕捉这种"波动的记忆性"的工具，是量化风险管理（VaR、Risk Parity、Volatility Targeting）的计量基石。

## 学习目标

学完本章你能：
- 理解波动率聚集（Volatility Clustering）现象，并用平方收益率的 ACF 验证它
- 理解 ARCH 模型如何刻画条件异方差性
- 用 GARCH(1,1) 模型拟合收益率序列，提取条件波动率
- 解释 α+β 接近 1 的经济含义（高持续性）
- 将波动率模型应用于风险平配、波动率目标化和期权定价

## 核心内容

### 1. 波动率聚集（Volatility Clustering）

**现象：** 金融资产的大幅波动（无论是涨还是跌）往往聚集在一起——平静期之后还是平静期，风暴之后接着风暴。

**实证验证：**

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

# ── 先安装 arch 包 ──
# pip install arch

# 下载 SPY 日数据
spy = yf.download('SPY', start='2015-01-01', end='2024-12-31')['Adj Close']
returns = spy.pct_change().dropna()  # 日收益率

# 平方收益率——波动率的代理变量
squared_returns = returns ** 2

fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 1. 收益率序列（看到波动率聚集）
axes[0].plot(returns.index, returns.values, color='steelblue', linewidth=0.5)
axes[0].set_title('SPY 日收益率——平静期与风暴期交替出现')
axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
axes[0].set_ylabel('Returns')

# 2. 平方收益率（波动率代理）
axes[1].plot(squared_returns.index, squared_returns.values,
             color='coral', linewidth=0.5, alpha=0.7)
axes[1].set_title('SPY 平方收益率——大幅波动聚集出现')
axes[1].set_ylabel('Squared Returns')

# 3. 平方收益率的 ACF——波动率的自相关性
plot_acf(squared_returns.dropna(), lags=50, ax=axes[2])
axes[2].set_title('ACF of Squared Returns——波动率有显著的自相关性')

plt.tight_layout()
plt.show()
```

**关键观察：**
- 收益率本身看起来近似白噪声（无自相关）
- 但**平方收益率**的 ACF 在多个滞后期仍显著——说明波动率（方差）有记忆
- 这就是**条件异方差性（Conditional Heteroskedasticity）**：方差不是常数，而是时变的

### 2. ARCH 模型

#### 直觉

ARCH（Autoregressive Conditional Heteroskedasticity）模型由 Engle（1982，诺贝尔奖）提出。核心思想：

> 今天的**方差**取决于昨天的**冲击**（残差平方）。

#### ARCH(1) 数学表达

$$r_t = \mu + \varepsilon_t, \quad \varepsilon_t = \sigma_t z_t, \quad z_t \sim N(0,1)$$

$$\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2$$

其中：
- $\sigma_t^2$ 是条件方差（今天的波动率）
- $\omega > 0$ 是基线方差
- $\alpha \geq 0$ 控制新冲击对波动率的影响强度
- $\varepsilon_{t-1}^2$ 是昨天的残差平方

```python
from arch import arch_model

# 模拟一个 ARCH(1) 过程
np.random.seed(42)
n = 1000
omega, alpha = 0.01, 0.3
sigma2 = np.zeros(n)
eps = np.zeros(n)
z = np.random.normal(0, 1, n)

sigma2[0] = omega / (1 - alpha)  # 无条件方差
eps[0] = np.sqrt(sigma2[0]) * z[0]

for t in range(1, n):
    sigma2[t] = omega + alpha * eps[t-1]**2
    eps[t] = np.sqrt(sigma2[t]) * z[t]

plt.figure(figsize=(14, 6))
plt.plot(eps, color='darkgreen', linewidth=0.5)
plt.title(f'模拟 ARCH(1): ω={omega}, α={alpha}——冲击有记忆')
plt.ylabel('Return')
plt.show()
```

#### 拟合真实数据——ARCH(1)

```python
# 拟合 SPY 的 ARCH(1) 模型
model_arch = arch_model(returns * 100, vol='ARCH', p=1)
result_arch = model_arch.fit(disp='off')
print(result_arch.summary())
```

> **注意：** 我们给收益率乘以 100（百分数形式），这样参数值更易读。

### 3. GARCH(1,1)——泛化的 ARCH

#### 为什么需要 GARCH？

ARCH(1) 只用**一期的冲击**来预测方差。但如果波动率的记忆很长（ACF 缓慢衰减），就需要很多阶的 ARCH 项。GARCH（Bollerslev, 1986）用**过去的方差本身**作为一个额外的预测变量——更简洁、更强大。

#### GARCH(1,1) 数学表达

$$\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

新增的 $\beta \sigma_{t-1}^2$ 项让模型记住"昨天的波动率水平"。

#### 直观理解

| 参数 | 控制 | 越大意味着 |
|------|------|-----------|
| $\omega$ | 长期平均方差 | 基线波动率水平 |
| $\alpha$ | 对新冲击的反应 | 新的好消息/坏消息 → 波动率快速跳升 |
| $\beta$ | 波动率的持续性 | 冲击的衰减速度慢（记忆长） |
| $\alpha + \beta$ | 持久性 | **接近 1 → 波动率近乎单位根过程（IGARCH）** |

```python
# 拟合 GARCH(1,1)
model_garch = arch_model(returns * 100, vol='GARCH', p=1, q=1)
result_garch = model_garch.fit(disp='off')
print(result_garch.summary())

# 提取条件波动率
cond_vol = result_garch.conditional_volatility / 100  # 恢复原始尺度

# 可视化
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# 收益率叠加条件波动率（±1σ 带）
axes[0].plot(returns.index, returns.values, color='steelblue', linewidth=0.5, alpha=0.6)
axes[0].plot(returns.index, cond_vol, color='red', linewidth=1, label='GARCH 条件波动率')
axes[0].plot(returns.index, -cond_vol, color='red', linewidth=1)
axes[0].fill_between(returns.index, -cond_vol, cond_vol, alpha=0.1, color='red')
axes[0].set_title('SPY 收益率 + GARCH(1,1) 条件波动率带')
axes[0].legend()
axes[0].set_ylabel('Returns')

# 条件波动率单独看
axes[1].plot(returns.index, cond_vol, color='darkred', linewidth=0.8)
axes[1].set_title('GARCH(1,1) 条件波动率——波动率本身有清晰的时变模式')
axes[1].set_ylabel('Conditional Vol (daily)')
axes[1].fill_between(returns.index, 0, cond_vol, alpha=0.2, color='darkred')

plt.tight_layout()
plt.show()

# 检查持久性
alpha = result_garch.params['alpha[1]']
beta = result_garch.params['beta[1]']
print(f"α = {alpha:.4f}, β = {beta:.4f}, α+β = {alpha + beta:.4f}")
print(f"结论: {'高持续性（接近 IGARCH）' if alpha + beta > 0.97 else '中等持久性'}")
```

**典型结果（SPY 日数据）：**
```
α = 0.09, β = 0.90, α+β = 0.99
```

α 小、β 大 ——> 新冲击对波动率影响有限，但一旦波动率升高，它会**很慢地衰减**。这就是金融波动率的典型特征。

#### GARCH(1,1) 的方差预测

未来 k 天的条件方差预测：

$$\mathbb{E}[\sigma_{t+k}^2 \mid \mathcal{F}_t] = \bar{\sigma}^2 + (\alpha + \beta)^{k-1}(\sigma_{t+1}^2 - \bar{\sigma}^2)$$

其中 $\bar{\sigma}^2 = \frac{\omega}{1 - \alpha - \beta}$ 是无条件方差。

当 $\alpha + \beta < 1$ 时，长期预测收敛到无条件方差。当 $\alpha + \beta = 1$（IGARCH）时，波动率冲击永久存在。

### 4. 波动率在量化中的应用

#### 4.1 Risk Parity（风险平配）

**思想：** 给定一个资产组合，按每类资产的**波动率倒数**分配资金，使每类资产对总风险的贡献相等。

```python
# 简化示例：SPY（股票）vs TLT（国债）
spy = yf.download('SPY', start='2020-01-01', end='2024-12-31')['Adj Close']
tlt = yf.download('TLT', start='2020-01-01', end='2024-12-31')['Adj Close']

returns = pd.DataFrame({
    'SPY': spy.pct_change().dropna(),
    'TLT': tlt.pct_change().dropna()
})

# 用 GARCH(1,1) 估计各自的波动率
vols = {}
for col in returns.columns:
    res = arch_model(returns[col] * 100, vol='GARCH', p=1, q=1).fit(disp='off')
    vols[col] = res.conditional_volatility.iloc[-1] / 100  # 最新条件波动率

latest_vols = pd.Series(vols)
risk_parity_weights = (1 / latest_vols) / (1 / latest_vols).sum()
print(f"最新条件波动率:\n{latest_vols}\n")
print(f"风险平配权重:\n{risk_parity_weights}\n")
print(f"等权波动率贡献:{'SPY=' + str(risk_parity_weights['SPY'] * latest_vols['SPY']:.2%):<20}{'TLT=' + str(risk_parity_weights['TLT'] * latest_vols['TLT']:.2%)}")
```

#### 4.2 Volatility Targeting（波动率目标化）

**思想：** 当波动率升高时缩小仓位，波动率降低时扩大仓位——让策略的**波动率保持恒定**。

$$\text{仓位调整因子} = \frac{\sigma_{\text{target}}}{\sigma_{\text{current}}}$$

```python
# 用 GARCH 估计当前波动率，动态调整仓位
sigma_target = 0.15 / np.sqrt(252)  # 目标年化 15% → 日波动率

# 获取 GARCH 条件波动率序列
res_spy = arch_model(returns['SPY'] * 100, vol='GARCH', p=1, q=1).fit(disp='off')
current_daily_vol = res_spy.conditional_volatility / 100

# 仓位调整因子
position_factor = sigma_target / current_daily_vol
position_factor = position_factor.clip(upper=2.0, lower=0.0)  # 限制最大 2 倍杠杆

plt.figure(figsize=(14, 6))
plt.plot(position_factor.index, position_factor.values, color='purple', linewidth=0.8)
plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='全仓（杠杆=1）')
plt.title(f'Volatility Targeting 仓位因子（目标年化 {0.15:.0%}）')
plt.ylabel('仓位调整因子')
plt.legend()
plt.show()
```

#### 4.3 期权定价

GARCH 模型可以生成波动率期限结构，作为 Black-Scholes 的输入：

```python
# 预测未来 30 天的波动率
forecasts = result_garch.forecast(horizon=30)
# forecasts.variance 是未来 30 天的条件方差预测
# 转换为年化波动率（假设 252 交易日）
predicted_vols = np.sqrt(forecasts.variance.iloc[-1] / 10000) * np.sqrt(252)

plt.figure(figsize=(10, 5))
plt.plot(range(1, 31), predicted_vols.values, marker='o', color='darkgreen')
plt.title('GARCH(1,1) 预测的波动率期限结构')
plt.xlabel('未来天数')
plt.ylabel('年化波动率')
plt.axhline(y=np.sqrt(forecasts.variance.iloc[-1].mean() / 10000) * np.sqrt(252),
            color='gray', linestyle='--', label='平均预测值')
plt.legend()
plt.show()
```

## 深度阅读

- Wiki → [时间序列基础](/prerequisite-math/04-statistics/4.5-time-series)
- Engle, R. (1982). "Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation." *Econometrica*, 50(4), 987-1007. — ARCH 开创论文
- Bollerslev, T. (1986). "Generalized Autoregressive Conditional Heteroskedasticity." *Journal of Econometrics*, 31(3), 307-327. — GARCH 开创论文
- 进阶阅读：RiskMetrics (1996) 的技术文档——用 EWMA 作为 GARCH 的简化替代方案

## 练习

### 选择题

1. 观察 SPY 日收益率的平方值的 ACF 图，如果 ACF 在多个滞后期显著不为零，这说明：
   - A. 收益率本身有自相关性
   - B. 收益率是平稳的
   - C. 收益率的**方差**有自相关性（波动率聚集）
   - D. 收益率存在季节性

2. GARCH(1,1) 模型 $\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$ 中，如果 $\alpha + \beta = 0.99$，这表示：
   - A. 波动率几乎没有记忆
   - B. 新冲击对波动率的影响很快消失
   - C. 波动率有很强的持久性，冲击衰减很慢
   - D. 模型参数不显著

3. 在 Volatility Targeting 策略中，如果 GARCH 模型估计的当前日波动率是 0.02，目标年化波动率是 16%，那么仓位调整因子（假设 252 交易日/年）大约是：
   - A. 0.5
   - B. 1.0
   - C. 1.6
   - D. 2.0

4. Risk Parity 的核心思路是：
   - A. 让每类资产的权重相等
   - B. 让每类资产的波动率相等
   - C. 让每类资产对总风险的贡献相等
   - D. 让组合的夏普比率最大化

### 编程题

**题目：** 下载 SPY 从 2018-01-01 到 2024-12-31 的日数据，拟合 GARCH(1,1) 模型，回答以下问题：

1. 条件波动率的最高值出现在哪一天？当时的波动率是多少？
2. 在 COVID 暴跌期间（2020 年 2 月-3 月），条件波动率从低点上升到峰值花了多少个交易日？
3. α 和 β 分别是多少？α+β 是否接近 1？

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from arch import arch_model

# ── 你的代码 ──
```

### 填空题

波动率 \\_\\_\\_\\_ 现象指大幅波动之后倾向于跟随大幅波动，这可以用 \\_\\_\\_\\_ 收益率 \\_\\_\\_\\_ 图的滞后相关性来验证。ARCH 模型假设今天的 \\_\\_\\_\\_ 取决于昨天的 \\_\\_\\_\\_。GARCH(1,1) 相比 ARCH(1) 多了一个 \\_\\_\\_\\_ 项。如果 GARCH(1,1) 的 α+β 接近 1，说明波动率的 \\_\\_\\_\\_ 很高。在 Risk Parity 中，资金分配到每个资产的权重与资产的 \\_\\_\\_\\_ 成反比。

## 掌握检查

- [ ] 我能解释什么是波动率聚集，并用平方收益率的 ACF 验证它
- [ ] 我能写出 ARCH(1) 和 GARCH(1,1) 的数学表达式
- [ ] 我能用 `arch` 包拟合 GARCH(1,1) 并提取条件波动率
- [ ] 我能解释 α 和 β 的经济含义
- [ ] 我能解释 α+β 接近 1 意味着什么
- [ ] 我能将 GARCH 应用于 Risk Parity 和 Volatility Targeting
- [ ] 我能用 GARCH 预测波动率的期限结构
