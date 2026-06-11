# 0.10 组合理论与 CAPM

> 对应 MIT 18.S096 L14 (Portfolio Theory) + L15 (CAPM) + L16 (Factor Models)
>
> 🎬 [先看 L14](https://youtu.be/HF_8Fx7Ef7k) → [L15](https://youtu.be/W0DkNBWlwnQ) → [L16](https://youtu.be/sHd1e0LJhFk) → 然后学本章代码

## 一句话

**不要把所有鸡蛋放在同一个篮子里**——但要科学地放，让相同风险下收益最大（或相同收益下风险最小）。

## 学习目标

学完本章你能：
- 用 Python 计算有效前沿并找到最优组合
- 理解 CAPM 的核心逻辑：只有系统性风险才该被定价
- 用因子模型分解收益来源（Alpha 从哪来？Beta 暴露了多少？）

## 核心内容

### 1. 组合风险与收益——马科维茨的基础

```python
import numpy as np
import pandas as pd
import yfinance as yf

# 取 4 只资产：SPY, TLT, GLD, IWM（股票、债券、黄金、小盘股）
tickers = ['SPY', 'TLT', 'GLD', 'IWM']
data = yf.download(tickers, start='2020-01-01', end='2024-12-31')['Adj Close']
returns = data.pct_change().dropna()

# 年化收益率和协方差
mu = returns.mean() * 252        # 年化预期收益
cov = returns.cov() * 252        # 年化协方差矩阵

print("年化预期收益率:")
print(mu.round(4))
print("\n年化协方差矩阵:")
print(cov.round(4))

# 等权组合
n = len(tickers)
w_eq = np.ones(n) / n
port_return = w_eq @ mu
port_vol = np.sqrt(w_eq @ cov @ w_eq)

print(f"\n等权组合:")
print(f"  预期收益率: {port_return:.2%}")
print(f"  风险(波动率): {port_vol:.2%}")
print(f"  夏普比率: {(port_return - 0.05) / port_vol:.2f}")  # 假设无风险利率 5%
```

**直觉：** 等权组合不一定是最好的。有些资产预期收益低但风险也低（TLT），有些正好相反。我们想要的是——**在给定风险水平下收益最高**的那个组合。

### 2. 有效前沿——每个风险水平上的最优组合

```python
def efficient_frontier(mu, cov, n_points=100):
    """计算有效前沿上的所有组合"""
    n = len(mu)
    target_returns = np.linspace(mu.min(), mu.max(), n_points)
    
    portfolios = []
    for target in target_returns:
        # 优化：min σ² s.t. w'μ = target, sum(w)=1
        # 封闭解（Lagrange multiplier）
        ones = np.ones(n)
        cov_inv = np.linalg.inv(cov)
        
        A = ones @ cov_inv @ ones
        B = mu @ cov_inv @ ones
        C = mu @ cov_inv @ mu
        D = A * C - B**2
        
        # 最小方差组合权重
        g = (cov_inv @ ones) / A
        h = (cov_inv @ mu) / B
        
        # 对目标收益率的最优权重
        w = g + (target - g @ mu) * (h - g)
        w = w / w.sum()  # 归一化
        
        port_vol = np.sqrt(w @ cov @ w)
        portfolios.append({'return': target, 'vol': port_vol, 'weights': w})
    
    return portfolios

# 计算有效前沿
frontier = efficient_frontier(mu, cov)

# 找到夏普比率最大的组合（切线组合）
risk_free = 0.05
best_sharpe = -np.inf
best_portfolio = None

for p in frontier:
    sharpe = (p['return'] - risk_free) / p['vol']
    if sharpe > best_sharpe:
        best_sharpe = sharpe
        best_portfolio = p

print("最优（最大夏普）组合:")
print(f"  收益率: {best_portfolio['return']:.2%}")
print(f"  波动率: {best_portfolio['vol']:.2%}")
print(f"  夏普比率: {best_sharpe:.2f}")
print("  权重分配:")
for t, w in zip(tickers, best_portfolio['weights']):
    print(f"    {t}: {w:.1%}")

# 找到最小方差组合
min_var = min(frontier, key=lambda p: p['vol'])
print(f"\n最小方差组合:")
print(f"  收益率: {min_var['return']:.2%}")
print(f"  波动率: {min_var['vol']:.2%}")
```

**关键洞察：** 有效前沿上的所有组合都是"有效"的——无法在不增加风险的前提下提高收益。投资者应该根据自己的风险偏好选择前沿上的某个点，然后与无风险资产混合（资本配置线）。

### 3. CAPM——Beta 决定一切

CAPM 说：市场上唯一被定价的风险是**系统性风险（Beta）**。个股的预期收益只取决于它对市场组合的贡献：

$$E[r_i] = r_f + \beta_i (E[r_m] - r_f)$$

```python
# CAPM 回归：AAPL vs 市场（SPY）
aapl = yf.download('AAPL', start='2020-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()
spy = yf.download('SPY', start='2020-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()

# 对齐日期
common_dates = aapl.index.intersection(spy.index)
aapl, spy = aapl[common_dates], spy[common_dates]

# 超额收益
risk_free_daily = 0.05 / 252
aapl_excess = aapl - risk_free_daily
spy_excess = spy - risk_free_daily

# OLS 回归
import statsmodels.api as sm
X = sm.add_constant(spy_excess)
model = sm.OLS(aapl_excess, X).fit()

print(model.summary().tables[1])
print(f"\nR² = {model.rsquared:.3f}")

# 解读：
beta = model.params.iloc[1]  # .iloc[1] for the market coefficient
alpha = model.params.iloc[0] * 252  # 年化 Alpha

print(f"\nAAPL 的 Beta: {beta:.2f}")
print(f"年化 Alpha: {alpha:.2%}")
print(f"Alpha 显著? {'是' if model.pvalues.iloc[0] < 0.05 else '否'}")
```

**CAPM 的核心结论：**
- Alpha > 0 且显著 → 股票跑赢了市场，有超额收益
- Beta = 1.2 → 市场涨 1%，股票平均涨 1.2%
- CAPM 说 Alpha 应该为零（市场有效）——实际中能找到 Alpha，但很难持续

### 4. 因子模型——超越 CAPM

CAPM 用一个因子（市场）解释收益。Fama-French 用三个（市场 + 市值 + 价值）：

$$r_i - r_f = \alpha + \beta_m (r_m - r_f) + \beta_s SMB + \beta_h HML + \varepsilon$$

```python
# 用代理构建 Fama-French 因子
# SMB (Small Minus Big) = IWM - SPY
# HML (High Minus Low) = VTV - SPYG（价值 - 成长）

iwm = yf.download('IWM', start='2020-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()
vtv = yf.download('VTV', start='2020-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()
spyg = yf.download('SPYG', start='2020-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()

# 对齐
dfs = [spy, iwm, vtv, spyg]
common = dfs[0].index
for df in dfs[1:]:
    common = common.intersection(df.index)

spy, iwm, vtv, spyg = [df[common] for df in dfs]

# 构建因子
mkt_excess = spy - risk_free_daily
smb = iwm - spy   # 小盘 - 大盘
hml = vtv - spyg  # 价值 - 成长

# 三因子回归：AAPL 的超额收益
aapl_excess = aapl[common] - risk_free_daily
X_ff = pd.DataFrame({
    'MKT': mkt_excess,
    'SMB': smb,
    'HML': hml
})
X_ff = sm.add_constant(X_ff)
model_ff = sm.OLS(aapl_excess, X_ff).fit()

print(model_ff.summary().tables[1])
print(f"\nR² = {model_ff.rsquared:.3f} (vs CAPM R² = {model.rsquared:.3f})")
```

**因子模型的价值：**
- R² 越高 → 你能更好地解释收益来源
- 如果一个策略的 Alpha 在加入因子后消失了 → 它其实是在赚因子暴露的钱，不是真 Alpha
- 这就是策略归因分析的核心逻辑

### 5. Black-Litterman 模型（直观理解）

实际中，马科维茨有个大问题：**对输入参数太敏感**。预期收益率稍微调一点，最优权重就剧烈变化。

Black-Litterman 的直觉：先假设市场是有效的（用市值权重反推隐含收益率），然后只在你有信心的地方调整预期。

```python
# 简化版：市值加权的隐含收益率（逆向优化）
# 假设市场组合权重 = 市值比例

market_caps = np.array([500, 100, 50, 100])  # 万亿（示例）
mkt_weights = market_caps / market_caps.sum()

# 由市场权重反推隐含收益率
# 逆向优化：Π = δ * Σ * w_mkt
# Π = 隐含超额收益率向量
delta = 2.5  # 风险厌恶系数（典型值 2-3）

# 协方差矩阵和权重
Sigma = cov.values  # 年化协方差
implied_excess = delta * Sigma @ mkt_weights

print("市场组合权重:")
for t, w in zip(tickers, mkt_weights):
    print(f"  {t}: {w:.1%}")

print("\n隐含预期超额收益率（逆向优化）:")
for t, r in zip(tickers, implied_excess):
    print(f"  {t}: {r:.2%}")

print("\n实际历史超额收益率:")
actual_excess = mu.values - risk_free
for t, r in zip(tickers, actual_excess):
    print(f"  {t}: {r:.2%}")
```

**直觉：** 如果市场的隐含收益率和历史收益率差距很大 → 要么市场定价错了，要么你的历史估计有问题。Black-Litterman 让你在这两者之间做加权平均。

## 深度阅读

- Wiki → [有效前沿与最优组合](/quant-finance/2.1-efficient-frontier)
- Wiki → [夏普比率与绩效度量](/quant-finance/2.2-sharpe-ratio)
- Wiki → [因子模型](/quant-finance/2.3-factor-models)
- Wiki → [组合收益与风险](/quant-finance/2.0-portfolio-risk-return)

## 练习

### 选择题

1. 有效前沿上的组合具有什么特性？
   - A. 夏普比率相同
   - B. 给定风险下收益最大
   - C. 所有资产权重相等
   - D. 波动率最低

2. CAPM 中，Alpha 代表：
   - A. 市场超额收益
   - B. 股票的系统性风险
   - C. 无法由市场因子解释的超额收益
   - D. 无风险利率

3. Fama-French 三因子模型比 CAPM 多加了哪两个因子？
   - A. 动量 + 流动性
   - B. 市值 + 价值
   - C. 波动率 + 偏度
   - D. 行业 + 国家

4. 马科维茨组合优化的主要实际问题是：
   - A. 计算太复杂
   - B. 对输入参数太敏感
   - C. 只能用正态分布
   - D. 只适用于股票

### 编程题

**题目：** 取 6 只行业 ETF（XLF金融, XLE能源, XLK科技, XLV医疗, XLI工业, XLP消费必需品）3 年数据。

1. 计算有效前沿
2. 找到最大夏普组合
3. 用 CAPM 回归看哪个行业 Beta 最高
4. 判断：哪个行业的 Alpha 最显著？

```python
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ['XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP']

# 你的代码
```

### 填空题

有效前沿上的所有组合都是 _____ 的，意味着无法在不增加 _____ 的前提下提高收益。

## 掌握检查
