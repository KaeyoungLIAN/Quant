# 0.4 随机过程与布朗运动

> 对应 MIT 18.S096 L5: Stochastic Processes I
>
> 🎬 [看 L5 视频](https://youtu.be/OQuxlEjhOGo) → 然后学本章代码

## 一句话

随机过程描述价格如何在时间中演化——布朗运动是它的"原子"，任何资产价格模型都建立在随机过程的数学之上。

## 学习目标

学完本章你能：
- 用随机游走模拟资产价格的离散路径
- 理解布朗运动（Wiener Process）的定义与性质
- 实现几何布朗运动（GBM）并模拟多路径
- 理解伊藤引理的直觉——为什么 `d(log S)` 有修正项

## 核心内容

### 1. 随机游走——最基础的随机过程

随机游走 = 每一步 ±1，累积求和。股价的"随机漫步"与此几乎一样：

```python
import numpy as np
import matplotlib.pyplot as plt

# 简单随机游走：抛硬币决定 ±1
np.random.seed(42)
steps = np.random.choice([-1, 1], size=500)
positions = np.cumsum(steps)  # 累积位置

# 加上漂移（drift）——股价有长期上涨趋势
drift = 0.05
n = 500
steps_with_drift = np.random.choice([-1, 1], size=n) + drift
positions_with_drift = np.cumsum(steps_with_drift)

# 模拟"股价"：S_t = exp(随机游走 + drift)
price_simple = 100 * np.exp(0.01 * positions_with_drift)

print(f"最终价格: {price_simple[-1]:.2f}")
print(f"日收益率标准差: {np.std(np.diff(np.log(price_simple))):.4f}")
```

随机游走有两个关键元素：**漂移（drift）**——长期趋势方向；**噪声（noise）**——每日随机波动。股价 = 漂移 + 噪声。

### 2. 布朗运动（Wiener Process）

布朗运动 $W(t)$ 是连续时间版本的随机游走，定义：

- $W(0) = 0$
- 独立增量：$W(t) - W(s)$ 与过去无关
- 正态增量：$W(t) - W(s) \sim N(0, t-s)$

```python
# 模拟一条布朗运动路径
def brownian_motion(T, N):
    """T=总时间, N=步数"""
    dt = T / N
    # 每个时间步的增量 ~ N(0, dt)
    dW = np.sqrt(dt) * np.random.randn(N)
    # 累积得到路径
    W = np.cumsum(dW)
    W = np.insert(W, 0, 0)  # W(0) = 0
    return W

# 时间分辨率逐步提高——观察极限行为
for N in [10, 100, 1000]:
    W = brownian_motion(1.0, N)
    t = np.linspace(0, 1, N + 1)
    print(f"N={N:5d} → W(1) = {W[-1]:.3f}, var ≈ {W[-1]**2:.3f} (理论: 1.0)")

# 关键性质：方差随时间线性增长
np.random.seed(42)
n_paths = 5
T, N = 1.0, 500
dt = T / N
t = np.linspace(0, T, N + 1)

# 画 5 条路径
for i in range(n_paths):
    W = brownian_motion(T, N)
    # plt.plot(t, W, lw=0.8, label=f'Path {i+1}')

# 验证 Var[W(t)] = t
W_end = np.array([brownian_motion(T, 1000)[-1] for _ in range(10000)])
print(f"\nVar[W(1)] = {np.var(W_end):.4f} (理论: 1.0)")
print(f"E[W(1)]  = {np.mean(W_end):.4f} (理论: 0.0)")
```

**关键直觉**：布朗运动路径处处连续但处处不可导——它的"瞬时导数"相当于白噪声。这就是为什么股票日收益率仿佛是随机的。

### 3. 几何布朗运动（GBM）——标准股价模型

GBM 是金融中最基础的股价模型：

$$dS = \mu S\,dt + \sigma S\,dW$$

离散化（Euler 方法）：

$$S_{t+dt} = S_t \exp\left( (\mu - \frac{\sigma^2}{2})dt + \sigma \sqrt{dt}\,\varepsilon \right)$$

```python
# GBM 模拟器
def gbm_path(S0, mu, sigma, T, N):
    """生成一条 GBM 路径"""
    dt = T / N
    # 标准正态随机数
    eps = np.random.randn(N)
    # 对数收益率的演化
    log_ret = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * eps
    # 累积 → 价格路径
    S = S0 * np.exp(np.cumsum(log_ret))
    S = np.insert(S, 0, S0)
    return S

# 参数
S0, mu, sigma, T = 100, 0.10, 0.25, 1.0
N = 252  # 交易日

# 模拟多条路径
np.random.seed(42)
n_paths = 10
paths = np.zeros((n_paths, N + 1))
for i in range(n_paths):
    paths[i] = gbm_path(S0, mu, sigma, T, N)

# 检查终值分布
final_prices = paths[:, -1]
print(f"S_T 均值: {final_prices.mean():.2f}")
print(f"理论期望: {S0 * np.exp(mu * T):.2f}")
print(f"S_T 中位数: {np.median(final_prices):.2f}")
print(f"理论中位数: {S0 * np.exp((mu - 0.5*sigma**2) * T):.2f}")

# 与真实数据对比
import yfinance as yf
spy = yf.download('SPY', start='2023-01-01', end='2023-12-31')['Adj Close']
spy_returns = np.log(spy / spy.shift(1)).dropna()
spy_mu = spy_returns.mean() * 252  # 年化
spy_sigma = spy_returns.std() * np.sqrt(252)

print(f"\nSPY 实际年化漂移: {spy_mu:.2%}")
print(f"SPY 实际年化波动率: {spy_sigma:.2%}")
```

**为什么 GBM 是好模型？** 价格永远非负（对数正态），收益率近似正态，且方差随持有期线性增长——与市场数据大致相符。

### 4. Ito 引理直觉——为什么"对数"这么好用？

Ito 引理告诉你：如果 $S$ 是随机过程，$f(S)$ 的微分公式不是普通的链式法则。

最经典的例子：$f(S) = \log S$。

普通微积分告诉你：$d(\log S) = \frac{1}{S} dS$

但 Ito 引理说（把 $dS = \mu S dt + \sigma S dW$ 代入）：

$$d(\log S) = \left(\mu - \frac{\sigma^2}{2}\right)dt + \sigma\,dW$$

多了一个 $-\frac{\sigma^2}{2}$ 项！

```python
# 直观验证 Ito 修正项
np.random.seed(42)
S0, mu, sigma, T, N = 100, 0.10, 0.25, 1.0, 100000
dt = T / N

# 用 GBM 模拟一条极长路径
eps = np.random.randn(N)
S = S0 * np.exp(np.cumsum((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*eps))

# 计算实际对数收益率
log_returns = np.diff(np.log(np.insert(S, 0, S0)))
actual_mean_log_ret = log_returns.mean() / dt
theoretical_mean_log_ret = mu - 0.5 * sigma**2

print(f"实际 d(log S) 年平均: {actual_mean_log_ret:.4f}")
print(f"理论 (μ - σ²/2) = {theoretical_mean_log_ret:.4f}")
print(f"如不用 Ito 修正: {mu:.4f} ← 会高估")

# 为什么这很重要？
# 因为 S_T 是对数正态分布：
# log(S_T) ~ N(log(S0) + (μ - σ²/2)T, σ²T)
# 这个 "σ²/2" 修正了 "波动率拖累" (volatility drag)
# 高波动 → 长期的复利收益被拉低
print(f"\n波动率拖累效应:")
low_vol = 0.10
high_vol = 0.40
drag_low = 0.5 * low_vol**2
drag_high = 0.5 * high_vol**2
print(f"  低波动(σ=10%): μ 损失 {drag_low:.2%}")
print(f"  高波动(σ=40%): μ 损失 {drag_high:.2%}")
```

**核心直觉**：波动率本身就降低长期收益率——这就是"波动率拖累"(volatility drag)。Ito 引理中的 $-\sigma^2/2$ 项量化了这个效应。

## 深度阅读

- Wiki → [随机过程基础](/prerequisite-math/06-stochastic-processes/6.1-basics)
- Wiki → [布朗运动](/prerequisite-math/06-stochastic-processes/6.3-brownian-motion)

## 练习

### 选择题

1. 布朗运动 W(t) 的增量分布是：
   - A. W(t) - W(s) ~ N(0, t-s)
   - B. W(t) - W(s) ~ N(0, t+s)
   - C. W(t) - W(s) ~ Uniform(-1, 1)
   - D. W(t) - W(s) 与时间无关

2. 几何布朗运动模拟股价时，最终价格 S_T 服从什么分布？
   - A. 正态分布
   - B. 对数正态分布
   - C. 泊松分布
   - D. 均匀分布

3. Ito 引理中 d(log S) 比链式法则多出一项。这是因为：
   - A. 布朗运动的二次变分不为零
   - B. 数学家在故意搞复杂
   - C. 对数函数不连续
   - D. 随机过程不可微

4. 波动率拖累 (volatility drag) 的数值是：
   - A. σ
   - B. σ²/2
   - C. μ - σ
   - D. σ√dt

### 编程题

**题目：** 用 GBM 模拟 10,000 条路径，定价一个欧式看涨期权。

假设：S₀=100, K=105, T=1年, r=5%, σ=25%。

期权 payoff = max(S_T - K, 0)，折现价格 = e^{-rT} × 平均 payoff。

```python
import numpy as np

S0, K, T, r, sigma = 100, 105, 1, 0.05, 0.25
n_simulations = 10000
N = 252  # 每年交易日

# 你的代码：模拟 10000 条 GBM 路径，计算期权价格
# 提示：
# dt = T/N
# S_T = S0 * exp((r - 0.5*sigma^2) * T + sigma * sqrt(T) * Z)
# payoff = max(S_T - K, 0)
# price = exp(-r*T) * mean(payoff)
```

通过 Black-Scholes 公式验证结果是否大致在 9.3 左右。

### 填空题

连续时间下的随机游走称为 \_\_\_\_，其路径处处 \_\_\_\_（可导/不可导）。GBM 中价格永远 \_\_\_\_（可以为负/非负）。Ito 引理中 d(log S) 的漂移项修正了 \_\_\_\_ 效应。

## 掌握检查
