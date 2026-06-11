# 3.2 概率论与蒙特卡洛模拟

> 对应 MIT 18.S096 L3: Probability Theory
>
> 🎬 [先看 L3 视频](https://youtu.be/mVjD8sMMh20) → 然后学本章代码

## 一句话

量化交易本质上是一个**概率游戏**——你不知道某笔交易会赚会亏，但知道长期期望值是正的。

## 学习目标

学完本章你能：
- 用 Python 生成任意分布并验证概率定理
- 用蒙特卡洛模拟计算复杂衍生品的期望收益
- 理解中心极限定理为什么是"量化的数学基础"

## 核心内容

### 1. 随机变量与分布

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 正态分布——金融模型最常用的假设
mu, sigma = 0, 0.02  # 日收益均值 0%，波动率 2%
normal = stats.norm(mu, sigma)

# 生成 1000 个日收益率
samples = normal.rvs(1000)

# 概率密度函数（PDF）在 x=0 处的值
print(f"P(X=0) ≈ {normal.pdf(0):.2f}")

# 累计分布函数（CDF）：P(X < -3%)
print(f"亏损超过3%的概率: {normal.cdf(-0.03):.2%}")

# 分位点：95% VaR
print(f"95% VaR: {normal.ppf(0.05):.2%}")
```

### 2. 蒙特卡洛模拟——L3 最实用的工具

不知道解析解？跑 10 万次模拟即可：

```python
# 问题：一个策略胜率 55%，每笔赚 2% 或亏 1.5%。
# 交易 100 次后，最可能的结果是什么？

np.random.seed(42)
n_simulations = 100000
n_trades = 100

# 每次模拟的收益
all_outcomes = []
for _ in range(n_simulations):
    trade_results = np.random.choice(
        [0.02, -0.015], 
        size=n_trades,
        p=[0.55, 0.45]
    )
    total_return = (1 + trade_results).prod() - 1
    all_outcomes.append(total_return)

all_outcomes = np.array(all_outcomes)
print(f"平均总收益: {all_outcomes.mean():.2%}")
print(f"95%区间: [{np.percentile(all_outcomes, 2.5):.2%}, {np.percentile(all_outcomes, 97.5):.2%}]")
print(f"亏钱的概率: {(all_outcomes < 0).mean():.2%}")
```

### 3. 条件概率——策略信号的核心

```python
# P(涨 | 信号出现) vs P(涨 | 无信号)
# 模拟一个信号系统

n_days = 10000
# 基础上涨概率 52%
base_up_prob = 0.52

# 信号——出现概率 30%，出现时涨的概率提高到 65%
signal_appears = np.random.random(n_days) < 0.3
signal_up_prob = np.where(signal_appears, 0.65, base_up_prob)

# 生成收益率
daily_ret = np.where(
    np.random.random(n_days) < signal_up_prob,
    np.random.normal(0.001, 0.015, n_days),   # 涨的日子
    np.random.normal(-0.001, 0.015, n_days)    # 跌的日子
)

# 验证条件概率
signal_days = daily_ret[signal_appears]
no_signal_days = daily_ret[~signal_appears]

print(f"信号日胜率: {(signal_days > 0).mean():.2%}")
print(f"无信号日胜率: {(no_signal_days > 0).mean():.2%}")
print(f"信号日平均收益: {signal_days.mean():.4%}")
```

### 4. 中心极限定理——L3 最重要的定理

```python
# 抛一枚硬币（期望值 0.5），抛 N 次取平均
# N → ∞ 时，均值分布趋近正态分布

means = []
for _ in range(10000):
    coin = np.random.choice([0, 1], size=100)  # 抛 100 次
    means.append(coin.mean())

means = np.array(means)
print(f"均值: {means.mean():.4f} (理论: 0.5)")
print(f"标准差: {means.std():.4f} (理论: sqrt(0.5*0.5/100) = {np.sqrt(0.25/100):.4f})")

# 无论原始分布是什么（伯努利），均值分布趋近正态
# 这就是为什么你可以用正态分布近似策略收益
```

**量化意义：** 一个策略交易了 100 笔，胜率 55%。这是真本事还是运气？
由 CLT，胜率的 95% 置信区间是：$0.55 \pm 1.96 \times \sqrt{0.55 \times 0.45 / 100} = [45.2\%, 64.8\%]$

区间包含 50% → 不能排除运气的可能。需要更多交易。

## 练习

### 选择题

1. 蒙特卡洛模拟的适用场景是：
   - A. 有解析解的问题
   - B. 没有解析解或解析解太复杂的概率问题
   - C. 只需要一个点估计
   - D. 确定性问题

2. 中心极限定理说：
   - A. 原始数据是正态分布
   - B. 大样本均值趋近正态分布
   - C. 方差趋近零
   - D. 样本量越大越好

3. 条件概率 $P(\text{盈利} | \text{信号})$ 在量化中的含义是：
   - A. 信号出现时盈利的概率
   - B. 盈利时信号出现的概率
   - C. 信号和盈利同时发生的概率
   - D. 信号出现的概率

4. 95% VaR = -2% 表示：
   - A. 95% 的概率亏损超过 2%
   - B. 5% 的概率亏损超过 2%
   - C. 最多亏损 2%
   - D. 平均亏损 2%

### 编程题

**题目：** 用蒙特卡洛模拟计算一个一元期权（欧式看涨）的价格。
假设：S0=100, K=105, T=1年, r=5%, σ=20%。
公式：$C = e^{-rT}E[\max(S_T - K, 0)]$

```python
import numpy as np

S0, K, T, r, sigma = 100, 105, 1, 0.05, 0.2
n_simulations = 100000

# 你的代码：模拟 S_T，计算 payoff，折现
# ST = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
```

### 填空题

蒙特卡洛模拟的核心步骤是：\_\_\_\_ → 计算 payoff → \_\_\_\_ 。

## 掌握检查
