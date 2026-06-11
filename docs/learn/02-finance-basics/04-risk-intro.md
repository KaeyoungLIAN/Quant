# 2.4 风险入门：波动率·回撤·夏普比率

> **风险不是"亏钱"，而是不确定性。** 一个每年要么赚 50% 要么亏 40% 的资产，和一个每年稳定赚 8% 的资产——哪个更"危险"？答案取决于你怎么定义风险。

## 一句话

**量化金融只用两个维度评价一切：收益和风险。** 波动率告诉你价格跳动有多剧烈，回撤告诉你最多亏过多少，夏普比率告诉你每一分风险换来了多少回报。

## 学习目标

学完本章你能：
- 计算资产的日收益率、年化波动率
- 计算最大回撤（Maximum Drawdown）
- 计算和理解夏普比率（Sharpe Ratio）
- 用这三个指标评价任何一只股票或策略的表现

## 核心内容

### 1. 什么是风险？—— 不是"亏钱"，是"不确定"

先说一件反直觉的事：

| 资产 | 第一年 | 第二年 | 第三年 | 平均收益 | 最终结果 |
|------|--------|--------|--------|---------|---------|
| A | +50% | -40% | +50% | +20% | 1.5×0.6×1.5=1.35（+35%） |
| B | +10% | +10% | +10% | +10% | 1.1×1.1×1.1=1.331（+33.1%） |

A 的平均收益率（算术平均）更高（20% vs 10%），但最终结果和 B 差不多。**为什么？因为波动吞噬了复利。这就是风险的真实成本。**

```python
import numpy as np
import pandas as pd
import yfinance as yf

# 演示波动吞噬复利
scenarios = [
    ("稳定增长", [0.10, 0.10, 0.10, 0.10, 0.10]),
    ("波动大起", [0.50, -0.40, 0.50, -0.40, 0.50]),
    ("温和波动", [0.20, -0.10, 0.20, -0.10, 0.20]),
]

print("=== 不同波动下的复利结果 ===")
print(f"{'场景':12s} {'算术平均':>10s} {'5年总收益':>10s}")
print("-" * 35)
for name, returns in scenarios:
    arithmetic_mean = np.mean(returns)
    total = np.prod([1 + r for r in returns]) - 1
    print(f"{name:12s} {arithmetic_mean*100:9.2f}% {total*100:10.2f}%")

print()
print("💡 波动 = 复利杀手。波动越大，实际收益越低于算术平均收益")
```

### 2. 波动率（Volatility）：最基本的风险度量

波动率 = 收益率的标准差。它衡量价格上下跳动的剧烈程度。

公式：
```
日波动率 σ_daily = std(日收益率)
年化波动率 σ_annual = σ_daily × √252
```

为什么要乘以 √252？因为方差随时间线性累加，标准差随时间按 √t 累加。一年有约 252 个交易日。

```python
# 计算 SPY 的波动率
spy = yf.download("SPY", start="2020-01-01", end="2024-12-31")['Adj Close']

# 计算日收益率（对数收益率更常用）
daily_returns = np.log(spy / spy.shift(1)).dropna()

# 年化波动率
daily_vol = daily_returns.std()
annual_vol = daily_vol * np.sqrt(252)

print(f"=== SPY 波动率分析 (2020-2024) ===")
print(f"日均收益率: {daily_returns.mean()*100:.4f}%")
print(f"日波动率:   {daily_vol*100:.3f}%")
print(f"年化波动率: {annual_vol*100:.2f}%")
print()

# 对比不同资产的波动率
tickers = ["SPY", "QQQ", "TLT", "GLD", "BTC-USD"]
data = yf.download(tickers, start="2020-01-01", end="2024-12-31")['Adj Close']

print(f"{'品种':10s} {'年化波动率':>12s}")
print("-" * 25)
for t in tickers:
    rets = np.log(data[t] / data[t].shift(1)).dropna()
    vol = rets.std() * np.sqrt(252)
    print(f"{t:10s} {vol*100:11.2f}%")

print()
print("💡 TLT（国债）波动率 ≈ SPY 的 60-70%")
print("💡 BTC（比特币）波动率 ≈ SPY 的 3-4 倍")
print("💡 波动率 = 你需要承担的\"心跳程度\"")
```

### 3. 回撤（Drawdown）：你最多亏了多少

回撤 = 当前价格距离历史最高点的跌幅。
最大回撤（Max Drawdown）= 历史上最深的一次回撤。

```python
def compute_drawdown(price_series):
    """
    计算回撤序列和最大回撤
    返回: (drawdown_series, max_drawdown, max_drawdown_duration)
    """
    # 累计最高点（到每一天为止的历史最高）
    peak = price_series.cummax()
    
    # 回撤 = (当前值 - 历史最高) / 历史最高
    drawdown = (price_series - peak) / peak
    
    # 最大回撤 = 回撤序列的最小值
    max_dd = drawdown.min()
    
    # 最大回撤持续时间（从最高点到恢复）
    # 找到最大回撤的结束点（恢复到上一个高点）
    dd_below = drawdown < 0
    # 简单估算：连续处于回撤状态的最长天数
    max_duration = 0
    current_duration = 0
    for i in range(len(drawdown)):
        if drawdown.iloc[i] < 0:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0
    
    return drawdown, max_dd, max_duration

# 计算 SPY 的回撤
spy_dd, spy_max_dd, spy_dd_duration = compute_drawdown(spy)

print(f"=== SPY 回撤分析 (2020-2024) ===")
print(f"最大回撤: {spy_max_dd*100:.2f}%")
print(f"最长回撤持续: {spy_dd_duration} 个交易日 ≈ {spy_dd_duration/252:.1f} 年")
print()

# 找出来最大回撤发生在什么时候
min_dd_idx = spy_dd.idxmin()
print(f"最大回撤发生日期: {min_dd_idx}")
print(f"当时 SPY 价格:    ${spy.loc[min_dd_idx]:.2f}")
print(f"当时历史最高点:   ${spy[:min_dd_idx].max():.2f}")
print()

# 对比不同资产的最大回撤
print(f"{'品种':10s} {'最大回撤':>12s} {'最长回撤期(天)':>16s}")
print("-" * 42)
for t in tickers:
    dd, max_dd, duration = compute_drawdown(data[t])
    print(f"{t:10s} {max_dd*100:10.2f}% {duration:15d}")
```

### 4. 夏普比率（Sharpe Ratio）：风险调整后的收益

夏普比率是**量化金融中最重要的单一指标**。它回答一个问题：

> 我每承担一单位风险，赚了多少超额收益？

```
夏普比率 = (策略年化收益率 - 无风险利率) / 年化波动率
```

```python
def sharpe_ratio(price_series, risk_free_rate=0.05):
    """
    计算夏普比率
    """
    # 日收益率
    daily_returns = np.log(price_series / price_series.shift(1)).dropna()
    
    # 年化收益率（用几何平均，更准确）
    total_return = price_series.iloc[-1] / price_series.iloc[0]
    years = len(daily_returns) / 252
    annual_return = total_return ** (1 / years) - 1
    
    # 年化波动率
    annual_vol = daily_returns.std() * np.sqrt(252)
    
    # 夏普比率
    sharpe = (annual_return - risk_free_rate) / annual_vol
    
    return sharpe, annual_return, annual_vol

print(f"=== 各资产夏普比率对比 (2020-2024, 无风险利率=5%) ===")
print(f"{'品种':10s} {'年化收益':>10s} {'年化波动':>10s} {'夏普比率':>10s}")
print("-" * 45)
for t in tickers:
    sr, ann_ret, ann_vol = sharpe_ratio(data[t], risk_free_rate=0.05)
    print(f"{t:10s} {ann_ret*100:9.2f}% {ann_vol*100:9.2f}% {sr:9.3f}")

print()
print("💡 夏普 > 1 → 好策略")
print("💡 夏普 > 2 → 优秀策略（很少见）")
print("💡 夏普 < 0 → 你不如存银行")
print("💡 注意：夏普比率假设收益正态分布，在极端行情下会失真")
```

### 5. 完整案例：计算你想买的任何股票的这三个指标

```python
def evaluate_asset(ticker, start="2020-01-01", end="2024-12-31", risk_free=0.05):
    """计算任意资产的核心风险指标"""
    try:
        data = yf.download(ticker, start=start, end=end)['Adj Close']
    except:
        print(f"无法获取 {ticker} 的数据")
        return
    
    # 1. 基础统计
    daily_returns = np.log(data / data.shift(1)).dropna()
    
    # 2. 年化收益和波动
    total_ret = data.iloc[-1] / data.iloc[0] - 1
    years = len(daily_returns) / 252
    ann_ret = (1 + total_ret) ** (1 / years) - 1
    ann_vol = daily_returns.std() * np.sqrt(252)
    
    # 3. 最大回撤
    peak = data.cummax()
    drawdown = (data - peak) / peak
    max_dd = drawdown.min()
    
    # 4. 夏普比率
    sharpe = (ann_ret - risk_free) / ann_vol
    
    # 5. 收益分布特征
    positive_days = (daily_returns > 0).sum() / len(daily_returns)
    
    print(f"╔{'═'*40}╗")
    print(f"║ 📊 {ticker:10s} 风险评估报告        ║")
    print(f"╠{'═'*40}╣")
    print(f"║ 总收益率:        {total_ret*100:>8.2f}%       ║")
    print(f"║ 年化收益率:       {ann_ret*100:>8.2f}%       ║")
    print(f"║ 年化波动率:       {ann_vol*100:>8.2f}%       ║")
    print(f"║ 夏普比率:         {sharpe:>8.3f}         ║")
    print(f"║ 最大回撤:         {max_dd*100:>8.2f}%       ║")
    print(f"║ 上涨天数占比:     {positive_days*100:>8.2f}%       ║")
    print(f"╚{'═'*40}╝")

# 评估几个品种
for t in ["SPY", "QQQ", "AAPL", "TSLA"]:
    evaluate_asset(t)
    print()
```

### 6. 这些指标的投资智慧

```python
# 回测策略的常见陷阱：只看收益不看风险
import warnings
warnings.filterwarnings('ignore')

# 构造两个"策略"的模拟收益
np.random.seed(42)
days = 252 * 3  # 3年

# 策略A: 高收益高波动
strategy_a = np.random.normal(0.001, 0.02, days)  # 日均0.1%, 波动2%
# 策略B: 中收益低波动
strategy_b = np.random.normal(0.0006, 0.008, days)  # 日均0.06%, 波动0.8%

# 累计收益
cum_a = np.cumprod(1 + strategy_a)
cum_b = np.cumprod(1 + strategy_b)

print(f"=== 两个策略的对比（只看收益 vs 看风险调整后）===")
print(f"{'指标':25s} {'策略A(高波动)':>15s} {'策略B(低波动)':>15s}")
print("-" * 55)

# 总收益
total_a = cum_a[-1] - 1
total_b = cum_b[-1] - 1
print(f"{'总收益率':25s} {total_a*100:14.2f}% {total_b*100:14.2f}%")

# 年化收益
ann_a = (1 + total_a) ** (252 / days) - 1
ann_b = (1 + total_b) ** (252 / days) - 1
print(f"{'年化收益率':25s} {ann_a*100:14.2f}% {ann_b*100:14.2f}%")

# 年化波动
vol_a = strategy_a.std() * np.sqrt(252)
vol_b = strategy_b.std() * np.sqrt(252)
print(f"{'年化波动率':25s} {vol_a*100:14.2f}% {vol_b*100:14.2f}%")

# 最大回撤（简化）
peak_a = np.maximum.accumulate(cum_a)
peak_b = np.maximum.accumulate(cum_b)
mdd_a = ((cum_a - peak_a) / peak_a).min()
mdd_b = ((cum_b - peak_b) / peak_b).min()
print(f"{'最大回撤':25s} {mdd_a*100:14.2f}% {mdd_b*100:14.2f}%")

# 夏普比率
sharpe_a = (ann_a - 0.05) / vol_a
sharpe_b = (ann_b - 0.05) / vol_b
print(f"{'夏普比率':25s} {sharpe_a:14.3f} {sharpe_b:14.3f}")

print()
print("💡 策略A收益更高，但波动太大，夏普比率反而更低")
print("💡 策略B收益低但稳定，风险调整后回报更好")
print("💡 优秀的量化策略追求的是夏普 > 1，不是年化 > 100%")
```

## 深度阅读

| 主题 | 链接 |
|------|------|
| 组合风险-收益完整框架 | [2.0 组合收益与风险](/quant-finance/2.0-portfolio-risk-return) |
| 夏普比率详解 | [2.2 夏普比率](/quant-finance/2.2-sharpe-ratio) |
| 有效前沿与最优组合 | [2.1 有效前沿](/quant-finance/2.1-efficient-frontier) |
| 因子模型（系统风险分解） | [2.3 因子模型](/quant-finance/2.3-factor-models) |
| 策略诊断（风险归因） | [4.3 业绩指标](/quant-finance/4.3-performance-metrics) |

## 练习

### 选择题

1. 年化波动率 20% 意味着什么？
   - A. 每年最多亏 20%
   - B. 每年收益在 ±20% 之间的概率约为 68%
   - C. 每年必定亏 20%
   - D. 每天波动不超过 20%

2. 一个策略的夏普比率为 0.8，年化波动率 15%，无风险利率 3%。这个策略的年化收益率大约是多少？
   - A. 12%
   - B. 15%
   - C. 18%
   - D. 21%

### 编程题

**题目：** 任选一只你感兴趣的股票（非 SPY），用 yfinance 下载 2020-2024 的数据，计算：
1. 年化收益率
2. 年化波动率
3. 最大回撤
4. 夏普比率（无风险利率设为 5%）

然后和本章中 SPY 的结果做对比。用一句中文写：这只股票比 SPY 更值得投资吗？为什么？

```python
# 你的代码
```

### 论述题

**题目：** 有人说"比特币过去十年涨了几百倍，是最好的投资"。请用本章学到的三个风险指标（波动率、最大回撤、夏普比率）来分析这个观点。至少指出：
- 只看收益不看风险的误区
- 为什么高收益可能伴随着你无法承受的回撤
- 如果你是一个养老基金经理，你会建议配置 50% 比特币吗？为什么？

> **提示：** 先用 `evaluate_asset("BTC-USD")` 看看比特币的实际数据。

---

> 💡 **学完本章，你已经掌握了量化金融最基础但也最重要的四个概念。** 下一章开始，我们真正写策略代码。
