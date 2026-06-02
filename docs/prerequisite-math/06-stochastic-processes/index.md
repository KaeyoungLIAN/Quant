---
title: "06 随机过程"
description: "随机过程定义、随机游走、布朗运动、鞅的定义与手算实例，以及量化金融中的 GBM 与期权定价"
---

# 06 随机过程

> 随机过程是量化金融的灵魂——资产价格、利率、波动率在时间维度上的不确定性，全部由随机过程建模。Black-Scholes 模型的核心正是假设股票价格遵循几何布朗运动。

---

## 一、随机过程的基本概念

### 1.1 定义

**随机过程**是一族随机变量 $\{X_t\}_{t \in \mathcal{T}}$，其中 $t$ 是时间参数。对于每个固定的 $t$，$X_t$ 是一个随机变量；对于每个固定的 $\omega$（样本点），$t \mapsto X_t(\omega)$ 是一条**样本路径**。

| 类型 | 时间参数 | 状态空间 | 示例 |
|------|----------|----------|------|
| 离散时间、离散状态 | $t = 0, 1, 2, \dots$ | 可数集 | 随机游走 |
| 离散时间、连续状态 | $t = 0, 1, 2, \dots$ | $\mathbb{R}$ | AR(1) 时间序列 |
| 连续时间、连续状态 | $t \in [0, \infty)$ | $\mathbb{R}$ | 布朗运动 |

### 1.2 过滤（Filtration）

**过滤** $\{\mathcal{F}_t\}_{t \ge 0}$ 是 $\sigma$-代数的递增序列，表示截至时间 $t$ 的所有已知信息：

$$
\mathcal{F}_s \subseteq \mathcal{F}_t \quad \text{对 } \forall s \le t
$$

- $\mathcal{F}_t$ 包含所有到时间 $t$ 为止的事件
- 称随机过程 $X_t$ 是 $\mathcal{F}_t$**适应的**，若 $X_t$ 对每个 $t$ 都是 $\mathcal{F}_t$-可测的（即 $t$ 时刻的值由当时已知信息决定）

> **Quant Link**：在衍生品定价中，**风险中性测度** $Q$ 下的资产价格过程必须是一个 $\mathcal{F}_t$-鞅。过滤 $\mathcal{F}_t$ 代表了交易者拥有的全部市场信息（历史价格、成交量等）。

---

## 二、随机游走（Random Walk）

### 2.1 定义

最经典的离散时间随机过程：设 $\{\varepsilon_t\}_{t=1}^\infty$ 为 i.i.d. 随机变量，$P(\varepsilon_t = +1) = P(\varepsilon_t = -1) = 0.5$。定义：

$$
S_n = \sum_{t=1}^n \varepsilon_t, \quad S_0 = 0
$$

**性质**：
- $\mathbb{E}[S_n] = 0$（公平游戏）
- $\text{Var}(S_n) = n$
- $\mathbb{E}[S_n^2] = n$（均方位移）

### 2.2 手算实例：3 步后的位置分布

抛硬币 3 次，正面 $+1$，反面 $-1$。$S_3$ 的可能取值及概率。

所有 $2^3 = 8$ 条等概率路径：

| 序列 | $S_1$ | $S_2$ | $S_3$ |
|------|-------|-------|-------|
| HHH | 1 | 2 | 3 |
| HHT | 1 | 2 | 1 |
| HTH | 1 | 0 | 1 |
| HTT | 1 | 0 | -1 |
| THH | -1 | 0 | 1 |
| THT | -1 | 0 | -1 |
| TTH | -1 | -2 | -1 |
| TTT | -1 | -2 | -3 |

**$S_3$ 的概率分布**：

| 位置 $k$ | 路径数 | 概率 $P(S_3 = k)$ | 组合数公式 |
|----------|--------|-------------------|-----------|
| $3$ | 1 (HHH) | $1/8$ | $\binom{3}{3}/8$ |
| $1$ | 3 (HHT, HTH, THH) | $3/8$ | $\binom{3}{2}/8$ |
| $-1$ | 3 (HTT, THT, TTH) | $3/8$ | $\binom{3}{1}/8$ |
| $-3$ | 1 (TTT) | $1/8$ | $\binom{3}{0}/8$ |

**通式**：$n$ 步后位置为 $k$ 的条件是 $n + k$ 为偶数且 $-n \le k \le n$：

$$
P(S_n = k) = \binom{n}{\frac{n+k}{2}} \cdot \frac{1}{2^n}
$$

**期望位置**：

$$
\mathbb{E}[S_3] = 3 \cdot \frac{1}{8} + 1 \cdot \frac{3}{8} + (-1) \cdot \frac{3}{8} + (-3) \cdot \frac{1}{8} = 0
$$

验证了 $\mathbb{E}[S_n] = 0$。一般地，$\mathbb{E}[S_n] = n \cdot \mathbb{E}[\varepsilon_1] = n \cdot 0 = 0$。

> **Quant Link**：随机游走是**有效市场假说（EMH）**的数学基础——如果价格已反映所有公开信息，那么价格变化 $\Delta P_t$ 应是不相关的随机游走。但实证发现收益率存在**动量效应**和**均值回归**，与纯随机游走不完全一致。

---

## 三、布朗运动（Brownian Motion）

### 3.1 定义

**标准布朗运动**（Wiener 过程）$\{W_t\}_{t \ge 0}$ 满足：

1. $W_0 = 0$ a.s.
2. $W_t$ 有独立增量：对 $0 \le s < t$，$W_t - W_s$ 与 $\mathcal{F}_s$ 独立
3. $W_t - W_s \sim \mathcal{N}(0, t - s)$（正态增量）
4. 样本路径几乎处处连续

### 3.2 为什么 $dW_t \sim \mathcal{N}(0, dt)$？

考虑时间区间 $[0, T]$，分割为 $n$ 等份，每段 $\Delta t = T/n$。定义：

$$
W_T = \sum_{i=1}^n \Delta W_i,\quad \Delta W_i \sim \mathcal{N}(0, \Delta t)
$$

对任意 $\Delta t$，$\Delta W_i$ 的方差恰好等于 $\Delta t$：

| 性质 | 推导 | 意义 |
|------|------|------|
| $\mathbb{E}[\Delta W] = 0$ | 正态分布对称 | 增量无偏 |
| $\text{Var}(\Delta W) = \Delta t$ | $\mathbb{E}[(\Delta W)^2] = \Delta t$ | 方差与时间步长成正比 |
| $\text{Var}(W_T) = n \cdot \Delta t = T$ | 独立增量方差可加 | 总方差等于总时间 |

因此，**增量 $dW_t$ 的方差无穷小，与时间微分成正比**。这恰是随机微积分（Itô 积分）的核心：

$$
(dW_t)^2 = dt \quad \text{(在均方意义下)}
$$

### 3.3 布朗运动性质一览

| 性质 | 描述 |
|------|------|
| 连续性 | 路径几乎处处连续，但处处不可微 |
| 二次变分 | $\sum (\Delta W)^2 \to T$，不为零 |
| 自相似性 | $W_{at} \stackrel{d}{=} \sqrt{a} W_t$ |
| 鞅性 | $W_t$ 是一个 $\mathcal{F}_t$-鞅 |

> **Quant Link**：**几何布朗运动（GBM）** 是 Black-Scholes 模型的基础假设：
> $$ dS_t = \mu S_t dt + \sigma S_t dW_t $$
> 其中 $\mu$ 是漂移率（预期收益率），$\sigma$ 是波动率。解为：
> $$ S_T = S_0 \exp\left((\mu - \frac{\sigma^2}{2})T + \sigma W_T\right) $$
> 即 $S_T$ 服从**对数正态分布**，这正是期权定价中风险中性世界的关键假设。

---

## 四、鞅（Martingale）

### 4.1 定义

随机过程 $\{M_t\}_{t \ge 0}$ 关于过滤 $\{\mathcal{F}_t\}$ 是一个**鞅**，如果：

1. $\mathbb{E}[|M_t|] < \infty$ 对所有 $t$（可积）
2. $M_t$ 是 $\mathcal{F}_t$-适应的
3. **鞅性质**：$\mathbb{E}[M_T \mid \mathcal{F}_t] = M_t$ 对 $\forall t \le T$

通俗理解：**给定当前信息，未来期望值等于当前值**——即"公平游戏"。

### 4.2 手算实例：公平游戏期望

考虑一个赌局：每轮掷一枚公平硬币。若正面，你赢 $\$1$；若反面，你输 $\$1$。设 $M_n$ 为 $n$ 轮后的累计财富，$M_0 = 0$。

**问题**：验证 $M_n$ 是鞅。

**第一步**：验证可积性——$|M_n| \le n$，显然可积。

**第二步**：验证 $\mathbb{E}[M_{n+1} \mid \mathcal{F}_n] = M_n$。

已知 $M_{n+1} = M_n + \varepsilon_{n+1}$，其中 $\varepsilon_{n+1} = \pm 1$ 各概率 $1/2$。

| 步骤 | 计算 |
|------|------|
| 给定 $\mathcal{F}_n$（历史信息） | $M_n$ 已知 |
| 下一轮期望增量 | $\mathbb{E}[\varepsilon_{n+1} \mid \mathcal{F}_n] = 1 \cdot 0.5 + (-1) \cdot 0.5 = 0$ |
| 条件期望 | $\mathbb{E}[M_{n+1} \mid \mathcal{F}_n] = M_n + 0 = M_n$ ✅ |

**验证通过**！$M_n$ 确实是一个鞅。

**数值验证**：假设前 2 轮结果是 HT（正面、反面），$M_2 = 0$。

$$
\mathbb{E}[M_3 \mid \mathcal{F}_2] = 0.5 \times (0 + 1) + 0.5 \times (0 - 1) = 0 = M_2
$$

**子鞅和上鞅**：

| 类型 | 条件 | 含义 |
|------|------|------|
| 鞅（Martingale） | $\mathbb{E}[M_T \mid \mathcal{F}_t] = M_t$ | 公平游戏 |
| 子鞅（Submartingale） | $\mathbb{E}[M_T \mid \mathcal{F}_t] \ge M_t$ | 有利趋势（如带正漂移的 GBM） |
| 上鞅（Supermartingale） | $\mathbb{E}[M_T \mid \mathcal{F}_t] \le M_t$ | 不利趋势 |

> **Quant Link**：在**风险中性定价**框架下，贴现资产价格 $\tilde{S}_t = e^{-rt} S_t$ 必须是风险中性测度 $Q$ 下的鞅：
> $$ \mathbb{E}^Q[e^{-rT} S_T \mid \mathcal{F}_t] = e^{-rt} S_t $$
> 这正是 Black-Scholes 模型定价公式的基础。任何与鞅性质的偏离都意味着套利机会。

---

## 五、Quant Link：期权定价模型

### 5.1 几何布朗运动与 Black-Scholes

Black-Scholes 模型的核心假设：

1. **股票价格**遵循 GBM：$dS_t = \mu S_t dt + \sigma S_t dW_t$
2. **无交易成本**、无税收、连续交易
3. **无风险利率** $r$ 恒定
4. **波动率** $\sigma$ 恒定（这是最受质疑的假设）

在风险中性测度 $Q$ 下，$dS_t = r S_t dt + \sigma S_t dW_t^Q$，欧式看涨期权定价公式：

$$
C(S, t) = S_t \Phi(d_1) - Ke^{-r(T-t)} \Phi(d_2)
$$

其中：
$$
d_1 = \frac{\ln(S_t/K) + (r + \sigma^2/2)(T-t)}{\sigma\sqrt{T-t}},\quad d_2 = d_1 - \sigma\sqrt{T-t}
$$

### 5.2 从 Black-Scholes 到 Heston 模型

BS 模型假设常数波动率，但实证发现**波动率微笑**——隐含波动率随执行价格变化。Heston 模型引入随机波动率：

$$
\begin{aligned}
dS_t &= \mu S_t dt + \sqrt{v_t} S_t dW_t^S \\
dv_t &= \kappa(\theta - v_t)dt + \sigma_v \sqrt{v_t} dW_t^v
\end{aligned}
$$

| 特征 | Black-Scholes | Heston |
|------|---------------|--------|
| 波动率 | 常数 $\sigma$ | 随机过程 $v_t$ |
| 参数 | 1 个波动率参数 | $\kappa, \theta, \sigma_v, \rho$ |
| 波动率微笑 | 无法捕获 | 通过 $\rho$（价格-波动相关性）捕获 |
| 解析解 | 有封闭解 | 半解析（特征函数方法） |

> **"波动率是金融中最不随机的常数"** —— 这正是 BS 模型的最大局限，也是 Heston 等随机波动率模型的价值所在。

---

## 六、Python：模拟布朗运动路径

```python
import numpy as np
import matplotlib.pyplot as plt

def simulate_brownian(T=1.0, n_steps=1000, n_paths=5):
    """
    模拟标准布朗运动路径
    Parameters:
        T: 总时间
        n_steps: 时间步数
        n_paths: 模拟路径数
    Returns:
        t: 时间点数组
        W: 布朗运动路径矩阵 (n_paths, n_steps+1)
    """
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)

    # 正态随机增量 ~ N(0, dt)
    dW = np.random.normal(0, np.sqrt(dt), size=(n_paths, n_steps))

    # 累加得到布朗运动路径
    W = np.zeros((n_paths, n_steps + 1))
    W[:, 1:] = np.cumsum(dW, axis=1)

    return t, W

# 模拟 5 条路径
t, W = simulate_brownian(T=1.0, n_steps=1000, n_paths=5)

# 验证 W_1 的分布
_, W_many = simulate_brownian(T=1.0, n_steps=500, n_paths=10000)
W_1 = W_many[:, -1]
print(f"理论值: E[W_1] = 0, Var[W_1] = 1")
print(f"模拟值: E[W_1] = {W_1.mean():.4f}, Var[W_1] = {W_1.var():.4f}")

# GBM 模拟
def simulate_gbm(S0=100, mu=0.05, sigma=0.2, T=1.0, n_steps=252):
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)
    dW = np.random.normal(0, np.sqrt(dt), size=n_steps)
    W = np.cumsum(dW)
    S = S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * np.insert(W, 0, 0))
    return t, S

t_gbm, S_gbm = simulate_gbm()
print(f"GBM 最终价格: S_T = {S_gbm[-1]:.2f}")
```

---

## 小结

| 概念 | 核心公式/性质 | 量化金融应用 |
|------|-------------|-------------|
| 过滤 $\mathcal{F}_t$ | 信息流的代数结构 | 风险管理、条件期望 |
| 随机游走 $S_n$ | $\mathbb{E}[S_n] = 0,\; \text{Var}(S_n) = n$ | 有效市场检验 |
| 布朗运动 $W_t$ | $W_t \sim \mathcal{N}(0, t),\; (dW)^2 = dt$ | GBM 的随机驱动项 |
| 鞅 $M_t$ | $\mathbb{E}[M_T \mid \mathcal{F}_t] = M_t$ | 风险中性定价、无套利 |
| GBM | $dS = \mu S dt + \sigma S dW$ | Black-Scholes 模型 |
| Heston 模型 | $dv = \kappa(\theta - v)dt + \sigma_v\sqrt{v} dW^v$ | 波动率微笑建模 |

> **下一步**：继续学习 **07 信息论**——熵、互信息及其在量化金融中的应用（如投资组合信息系数、因子分析）。
