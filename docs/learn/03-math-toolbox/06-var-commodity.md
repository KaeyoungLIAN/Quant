# 3.6 风险价值(VaR)与商品模型

> 对应 MIT 18.S096 L7: Value at Risk + L13: Commodity Models
>
> 🎬 [看 L7 视频](https://youtu.be/k4JcMh6HM1I) → 🎬 [看 L13 视频](https://youtu.be/yctQK6y2nm8) → 然后学本章代码

## 一句话

风险价值（VaR）告诉你"最坏情况下我最多亏多少"——而 CVaR 告诉你"真到了那个最坏情况，我平均会亏多少"；商品模型则解释了为什么持有期货不等同于持有现货（展期收益是关键）。

## 学习目标

学完本章你能：
- 用三种方法（参数法、历史模拟法、蒙特卡洛法）计算投资组合的 VaR 和 CVaR
- 理解 VaR 的局限性为什么催生了 CVaR（Expected Shortfall）
- 做压力测试和情景分析——"如果再来一次 2008 会怎样？"
- 理解 Contango 和 Backwardation 对期货持仓的影响
- 计算并量化展期收益（Roll Yield）

## 核心内容

### 1. 什么是 VaR？

$$
\text{VaR}_{95\%} = \text{阈值 T} \quad\text{使得}\quad P(\text{损失} > T) = 5\%
$$

通俗说：有 95% 的把握，明天一天你的最大损失不超过某个数。

```python
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

# 下载组合数据：SPY (大盘), AGG (债券), GLD (黄金)
tickers = ['SPY', 'AGG', 'GLD']
data = yf.download(tickers, start='2022-01-01', end='2024-12-31')['Adj Close']
returns = data.pct_change().dropna()

# 等权重组合
weights = np.array([1/3, 1/3, 1/3])
portfolio_returns = returns.dot(weights)

print(f"组合日收益率均值: {portfolio_returns.mean():.4f}")
print(f"组合日收益率标准差: {portfolio_returns.std():.4f}")
```

**关键区别**：VaR 是一个**阈值**（threshold），不是"平均损失"。它说"95% 的情况下损失不超过 X"，但它不说"剩下 5% 平均亏多少"——这就是 CVaR 要回答的问题。

### 2. 三种 VaR 计算方法

#### 方法一：参数法（Variance-Covariance）

假设收益率服从正态分布，VaR 就是分布的分位数：

$$
\text{VaR}_{95\%} = -\mu - 1.645\sigma \quad\text{(日收益率)}
$$

负号是因为我们要的是"损失"的正数。标准差越大 → VaR 越大 → 风险越高。

```python
confidence = 0.95
z_score = stats.norm.ppf(1 - confidence)  # 5% 左尾分位数 ≈ -1.645

mu = portfolio_returns.mean()
sigma = portfolio_returns.std()

# 日 VaR（数值为正 = 最大损失）
var_param = -(mu + z_score * sigma)
print(f"参数法 VaR(95%, 1天) = {var_param:.4f} = {var_param:.2%}")
```

**解读：** 正态假设下，有 95% 的把握组合一天亏损不超过 `var_param`。**但金融收益不是正态的**——尾部更肥（fat tail），所以参数法会低估风险。

#### 方法二：历史模拟法

不需要任何分布假设——直接用历史收益率的分位数：

```python
# 历史模拟：直接取历史收益率的 5% 分位数
var_hist = -np.percentile(portfolio_returns, 5)
print(f"历史模拟 VaR(95%, 1天) = {var_hist:.4f} = {var_hist:.2%}")

# 可视化：检查 VaR 阈值在分布中的位置
sorted_returns = np.sort(portfolio_returns)
# 5% 处的收益率
threshold_idx = int(len(sorted_returns) * 0.05)
print(f"    5% 分位收益率 = {sorted_returns[threshold_idx]:.4f}")
```

**优点**：不依赖分布假设，能捕捉真实尾部行为。
**缺点**：假设历史会重演——如果样本中没有暴跌，VaR 会低估。

#### 方法三：蒙特卡洛法

用 GBM 模拟 10,000+ 条未来路径，取模拟结果的分位数：

```python
# 蒙特卡洛模拟
np.random.seed(42)
n_sim = 10000
T = 1  # 1天
dt = T / 1  # 1步到终点

# 用组合的历史参数生成未来收益率
sim_returns = np.random.normal(mu, sigma, n_sim)
var_mc = -np.percentile(sim_returns, 5)
print(f"蒙特卡洛 VaR(95%, 1天) = {var_mc:.4f} = {var_mc:.2%}")

# 增加模拟次数检查稳定性
for n in [1000, 5000, 10000, 50000]:
    sim = np.random.normal(mu, sigma, n)
    print(f"  N={n:5d} → VaR = {-np.percentile(sim, 5):.4f}")
```

#### 三者对比

```python
print(f"\n=== VaR(95%, 1天) 对比 ===")
print(f"参数法(正态)         = {var_param:.4%}")
print(f"历史模拟             = {var_hist:.4%}")
print(f"蒙特卡洛(N=10000)    = {var_mc:.4%}")

# 为什么不同？
# - 参数法假设正态 → 通常给出最小 VaR（低估尾部风险）
# - 历史模拟使用真实数据 → 通常给出最大 VaR（包含真实尾部）
# - 蒙特卡洛介于两者之间 → 取决于随机数生成
```

**量化学到的规律**：

| 方法 | 假设 | 优点 | 缺点 |
|------|------|------|------|
| 参数法 | 正态分布 | 计算快、可解析 | 低估尾部风险 |
| 历史模拟 | 历史会重演 | 无分布假设 | 样本外风险未知 |
| 蒙特卡洛 | GBM 假设 | 灵活、可加情景 | 计算成本高 |

### 3. 条件 VaR（CVaR / Expected Shortfall）

VaR 只说"95% 的情况下亏损不超过 X"，但它不说"如果真亏损了，平均亏多少"。

$$
\text{CVaR}_{95\%} = E[\text{损失} \mid \text{损失} > \text{VaR}_{95\%}]
$$

```python
# CVaR 计算
def compute_cvar(returns, confidence=0.95):
    """计算经验 CVaR（Expected Shortfall）"""
    var = np.percentile(returns, (1 - confidence) * 100)
    # 取所有超过 VaR 的损失
    tail_losses = returns[returns < -var]
    cvar = -tail_losses.mean() if len(tail_losses) > 0 else var
    return var, cvar

var_hist, cvar_hist = compute_cvar(portfolio_returns)
print(f"历史模拟 VaR(95%)  = {var_hist:.4%}")
print(f"历史模拟 CVaR(95%) = {cvar_hist:.4%}")
print(f"CVaR/VaR 比值 = {cvar_hist / var_hist:.2f}x")
print(f"→ 尾部事件中的平均损失是 VaR 阈值的 {cvar_hist/var_hist:.1f} 倍")
```

**为什么 CVaR 更保守？**
- VaR：5% 尾部事件中最小的那个损失
- CVaR：5% 尾部事件中的**平均**损失
- 因为尾部损失分布是左偏的，CVaR 一定 ≥ VaR

```python
# 多资产组合的 CVaR vs VaR
print("\n多资产组合 VaR vs CVaR:")
for ticker in tickers:
    r = returns[ticker]
    v, cv = compute_cvar(r)
    print(f"  {ticker}: VaR={v:.4%}, CVaR={cv:.4%}, 比值={cv/v:.2f}")
```

**监管意义**：Basel III 转向要求 CVaR（Expected Shortfall）替代 VaR，正是因为 VaR 低估了极端损失。

### 4. 压力测试与情景分析

VaR 回答"一般情况下会怎样"，压力测试回答"如果世界末日呢？"

```python
# 压力测试：历史极端情景
scenarios = {
    '2008 金融危机': ('2008-09-15', '2008-12-31'),  # 雷曼倒闭后
    '2020 新冠熔断': ('2020-02-19', '2020-03-23'),
    '2022 加息周期': ('2022-01-03', '2022-06-30'),
}

print("=== 压力测试情景 ===")
for name, (start, end) in scenarios.items():
    scenario_data = yf.download(tickers, start=start, end=end)['Adj Close']
    scenario_ret = scenario_data.pct_change().dropna()
    scenario_portfolio = scenario_ret.dot(weights)
    
    total_return = (1 + scenario_portfolio).prod() - 1
    max_drawdown = (scenario_portfolio.cumsum() - scenario_portfolio.cumsum().cummax()).min()
    
    print(f"\n{name}:")
    print(f"  总收益: {total_return:.2%}")
    print(f"  最大回撤: {max_drawdown:.2%}")
    print(f"  日 VaR(95%): {-np.percentile(scenario_portfolio, 5):.2%}")

# "最坏 N 次"历史回撤
rolling_max = portfolio_returns.cumsum().cummax()
drawdowns = portfolio_returns.cumsum() - rolling_max
worst_drawdowns = sorted(drawdowns)[:5]
print(f"\n历史上 5 个最差回撤日:")
for i, dd in enumerate(worst_drawdowns, 1):
    print(f"  #{i}: {dd:.2%}")
```

#### 情景分析的"如果"问题

- **如果波动率翻倍？** 参数法 VaR 也会翻倍
- **如果相关性全部变成 1？** 分散化失效，VaR 达到单个资产最大 VaR
- **如果收益率均值下降 2σ？** 尾部损失分布整体左移

```python
# 敏感性分析：改变参数看 VaR 变化
print("\n=== VaR 敏感性分析 ===")
base_var = var_param

for factor in [0.5, 0.75, 1.0, 1.25, 1.5]:
    stress_sigma = sigma * factor
    stress_var = -(mu + z_score * stress_sigma)
    print(f"  σ × {factor:.2f} → VaR = {stress_var:.4%} (变化 {stress_var/base_var - 1:+.1%})")
```

### 5. 商品模型（L13）——期货曲线与展期收益

#### Contango 与 Backwardation

商品与股票最大的区别：**持有期货不等于持有现货**。

```
期货价格 F(T) 与现货 S 的关系：

   Contango（正向市场）:  F(T) > S    → 期货溢价，远端更贵
   Backwardation（反向市场）: F(T) < S  → 现货溢价，远端更便宜
```

```python
# 模拟两条期货曲线
import matplotlib.pyplot as plt

months = np.arange(1, 13)
S = 100  # 现货价格

# Contango: F(T) > S，远期溢价
contango_prices = S * np.exp(0.005 * months)  # 每月 +0.5%
# Backwardation: F(T) < S，远期折价
backwardation_prices = S * np.exp(-0.005 * months)  # 每月 -0.5%

print("=== 期货曲线 ===")
print(f"{'月份':<6} {'现货':<8} {'Contango':<12} {'Backwardation':<14}")
print("-" * 40)
for m, c, b in zip(months[:6], contango_prices[:6], backwardation_prices[:6]):
    print(f"{m:<6} {S:<8.2f} {c:<12.2f} {b:<14.2f}")

print(f"\nContango 第6月溢价: {(contango_prices[5]/S - 1):.2%}")
print(f"Backwardation 第6月折价: {(backwardation_prices[5]/S - 1):.2%}")
```

#### 展期收益（Roll Yield）

**核心概念**：如果市场处于 Contango，你每月需要"高价买入新的近月合约"——这会产生负的展期收益。反之，Backwardation 产生正的展期收益。

```python
# 模拟展期（Roll）过程
# 假设每个月到期前展期到下个月

def simulate_roll_yield(S0, curve_type='contango', n_months=12):
    """模拟持有期货的展期收益"""
    if curve_type == 'contango':
        roll_cost = -0.005  # 每月 -0.5%
    else:
        roll_cost = 0.005   # 每月 +0.5%
    
    cumulative_return = 1.0
    log_returns = []
    
    for m in range(n_months):
        # 每个月持有到期：价格收敛到现货
        # 展期损益 = 买入下月合约 - 卖出到期合约
        month_return = roll_cost
        cumulative_return *= (1 + month_return)
        log_returns.append(np.log1p(month_return))
    
    return cumulative_return - 1, np.exp(np.sum(log_returns)) - 1

# 对比两种市场结构
for curve_type in ['contango', 'backwardation']:
    total_ret, log_ret = simulate_roll_yield(100, curve_type, 12)
    print(f"\n{curve_type.capitalize()} 下持有12个月:")
    print(f"  总展期收益: {total_ret:.2%}")
    
    if total_ret < 0:
        print(f"  → 展期损耗 (negative roll yield)，商品多头亏损")
    else:
        print(f"  → 展期收益 (positive roll yield)，商品多头获利")

# 实际数据：用原油 ETF (USO) 展示 contango 的影响
print("\n=== 实际展期影响 ===")
uso = yf.download('USO', start='2023-01-01', end='2024-12-31')['Adj Close']
uso_ret = uso.pct_change().dropna()
uso_cumulative = (1 + uso_ret).prod() - 1

# 同期 SPY 做对比
spy = yf.download('SPY', start='2023-01-01', end='2024-12-31')['Adj Close']
spy_ret = spy.pct_change().dropna()
spy_cumulative = (1 + spy_ret).prod() - 1

print(f"USO (原油期货) 累计收益: {uso_cumulative:.2%}")
print(f"SPY (标普500) 累计收益: {spy_cumulative:.2%}")
print(f"差异: {(uso_cumulative - spy_cumulative):.2%}")
print("注意: USO 受展期损耗影响，长期表现通常弱于现货")
```

**量化含义**：
- Contango → 做多商品期货有负的展期收益 → 适合做空
- Backwardation → 做多商品期货有正的展期收益 → 适合做多
- 展期收益是商品**独立于价格涨跌**的收益来源——即使现货价格不变，展期也能产生损益

#### 完整例子：商品组合的 VaR 分析

```python
# 结合 VaR 和商品模型：商品组合的风险分析
commodity_tickers = ['USO', 'GLD', 'DBA']  # 原油、黄金、农产品
comm_data = yf.download(commodity_tickers, start='2022-01-01', end='2024-12-31')['Adj Close']
comm_returns = comm_data.pct_change().dropna()

# 等权重
comm_weights = np.array([1/3, 1/3, 1/3])
comm_portfolio = comm_returns.dot(comm_weights)

# 计算 VaR 和 CVaR
var_comm, cvar_comm = compute_cvar(comm_portfolio)
print(f"\n=== 商品组合风险 (VaR/CVaR) ===")
print(f"VaR(95%)  = {var_comm:.4%}")
print(f"CVaR(95%) = {cvar_comm:.4%}")
print(f"商品组合 CVaR/VaR = {cvar_comm/var_comm:.2f}x")

# 对比股票组合
stock_portfolio = returns[['SPY']].dot(np.array([1.0]))
var_stock, cvar_stock = compute_cvar(stock_portfolio)
print(f"\n股票组合 VaR(95%)  = {var_stock:.4%}")
print(f"股票组合 CVaR(95%) = {cvar_stock:.4%}")
print(f"商品波动率显著高于股票: {comm_portfolio.std()/stock_portfolio.std():.2f}x")
```

## 深度阅读

- Wiki → [组合收益与风险](/quant-finance/2.0-portfolio-risk-return) — 组合风险计算基础
- MIT 18.S096 L7: Value at Risk (VaR) — 完整数学推导与 VaR 的次可加性讨论
- MIT 18.S096 L13: Commodity Models — 期货定价、便利收益、仓储理论
- Basel III: Fundamental Review of the Trading Book — CVaR 取代 VaR 的监管背景

## 练习

### 选择题

1. 以下关于 VaR 的说法错误的是：
   - A. VaR(95%) = 5% 分位数的绝对值
   - B. VaR 满足次可加性（subadditivity）
   - C. 参数法 VaR 假设收益率服从正态分布
   - D. 历史模拟法不需要分布假设

2. CVaR（Expected Shortfall）与 VaR 的关系是：
   - A. CVaR 总是小于 VaR
   - B. CVaR 总是大于等于 VaR
   - C. CVaR 等于 VaR 的平方
   - D. CVaR 与 VaR 无关

3. 商品市场处于 Contango 意味着：
   - A. 远期价格高于现货价格
   - B. 远月合约比近月合约便宜
   - C. 现货供应紧张
   - D. 展期收益为正

4. 以下哪种方法最可能低估 VaR（假设实际收益有肥尾）：
   - A. 历史模拟法
   - B. 参数法（正态假设）
   - C. 蒙特卡洛法
   - D. 三种方法都一样

### 编程题

**题目：** 计算一个三资产组合（SPY + QQQ + TLT，等权重，2022–2024 数据）的 VaR(95%) 和 CVaR(95%)，分别用参数法和历史模拟法，并回答：哪个方法给出的 VaR 更大？为什么？

```python
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

tickers = ['SPY', 'QQQ', 'TLT']
weights = np.array([1/3, 1/3, 1/3])

# 你的代码
# 1. 下载数据，计算等权重组合日收益率
# 2. 参数法 VaR（假设正态分布）
# 3. 历史模拟法 VaR
# 4. 计算 CVaR（历史法）
# 5. 对比并解释差异
```

### 填空题

VaR(95%) 意味着有 \\_\\_\\_\\_% 的把握，在给定持有期内损失不超过某个阈值。CVaR 计算的是超过 VaR 阈值的损失的 \\_\\_\\_\\_（最大值/平均值/中位数）。商品市场的 \\_\\_\\_\\_ 指远期价格高于现货，此时做多期货面临负的 \\_\\_\\_\\_ 收益。监管标准 Basel III 要求使用 \\_\\_\\_\\_（VaR/CVaR/夏普比率）作为风险度量指标。

## 掌握检查

- [ ] 我能用三种方法计算单一资产和多资产组合的 VaR
- [ ] 我理解 VaR 和 CVaR 的区别，知道为什么 CVaR 更保守
- [ ] 我能做压力测试和"如果……"情景分析
- [ ] 我理解 Contango 和 Backwardation 对期货收益的影响
- [ ] 我能计算并解释商品期货的展期收益
