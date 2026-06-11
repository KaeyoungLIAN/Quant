# 2.2 市场机制：订单·滑点·流动性

> 你下单后发生了什么？为什么看到的成交价和下单时的价格不一样？为什么有些策略回测完美、实盘血亏？**答案藏在市场微观结构里。**

## 一句话

**市场不是免费的——每一笔交易都有摩擦成本。** 滑点、价差、流动性——忽略这些，你的回测就是在自欺欺人。

## 学习目标

学完本章你能：
- 理解市价单和限价单的区别
- 用代码模拟滑点对交易成本的影响
- 解释为什么流动性低的品种不适合大资金策略
- 明白为什么"回测王者"常常是"实盘青铜"

## 核心内容

### 1. 订单类型：你在和市场说什么？

| 订单类型 | 你说的话 | 保证什么 | 不保证什么 |
|---------|---------|---------|-----------|
| **市价单 (Market Order)** | "现在就成交，多少钱都行" | 执行 | 价格 |
| **限价单 (Limit Order)** | "低于X我不卖/高于X我不买" | 价格 | 执行 |

**市价单**是最直接的——以当前市场上最好的价格立即成交。代价是**你吃了买卖价差（Bid-Ask Spread）**。

**限价单**挂在那里等——如果价格不到，单子就不成交。好处是**不用付价差成本**，甚至可能赚到价差。

```python
import numpy as np
import pandas as pd

# 模拟一个简单的订单簿
order_book = {
    'ask_price': [100.05, 100.06, 100.08, 100.10],
    'ask_size':  [500, 1200, 3000, 800],
    'bid_price': [100.00, 99.99, 99.98, 99.97],
    'bid_size':  [1000, 2500, 800, 1500]
}

print("=== 模拟订单簿 ===")
print(f"卖一: {order_book['ask_price'][0]} ({order_book['ask_size'][0]}股)")
print(f"买一: {order_book['bid_price'][0]} ({order_book['bid_size'][0]}股)")
print(f"价差: {order_book['ask_price'][0] - order_book['bid_price'][0]:.2f}")
print()

# 模拟：买入 5000 股的市价单
order_size = 5000
filled = 0
total_cost = 0
print(f"=== 模拟市价买单: {order_size}股 ===")
for i in range(len(order_book['ask_price'])):
    available = order_book['ask_size'][i]
    buy_now = min(available, order_size - filled)
    cost = buy_now * order_book['ask_price'][i]
    total_cost += cost
    filled += buy_now
    print(f"  层级{i+1}: {buy_now}股 @ ${order_book['ask_price'][i]:.2f} → ${cost:.2f}")
    if filled >= order_size:
        break

avg_price = total_cost / filled
mid_price = (order_book['ask_price'][0] + order_book['bid_price'][0]) / 2
slippage = (avg_price - mid_price) / mid_price * 100

print(f"\n成交 {filled} 股，均价 ${avg_price:.3f}")
print(f"中间价: ${mid_price:.3f}")
print(f"滑点: {slippage:.3f}%")
```

### 2. 滑点（Slippage）：你看到的 ≠ 你得到的

滑点是**下单时的预期价格**和**实际成交价格**的差异。它是市场摩擦的最直接体现。

**滑点的三个来源：**
1. **价差成本** — 买入立即比中间价高一个价差
2. **市场冲击** — 大单推高/推低价格
3. **延迟** — 下单到成交之间的价格变动

```python
# 模拟滑点对交易成本的影响
np.random.seed(42)

def simulate_trades(n_trades=1000, slippage_bps=5):
    """
    模拟 n_trades 笔交易，每笔有固定滑点
    slippage_bps: 滑点，单位为基点 (1 bps = 0.01%)
    """
    # 假设每笔交易的理论价格随机在 $50-$150 之间
    theoretical_prices = np.random.uniform(50, 150, n_trades)
    # 方向随机：50% 买入，50% 卖出
    directions = np.random.choice([1, -1], n_trades)  # 1=买入, -1=卖出
    
    # 实际成交价 = 理论价 ± 滑点
    slippage_factor = slippage_bps / 10000  # 转成小数
    actual_prices = theoretical_prices * (1 + directions * slippage_factor)
    
    total_cost = np.sum(np.abs(theoretical_prices - actual_prices))
    avg_slippage_cost = total_cost / n_trades
    
    print(f"=== 滑点模拟 ({n_trades} 笔交易, {slippage_bps} bps) ===")
    print(f"交易总成本（因滑点）: ${total_cost:.2f}")
    print(f"每笔平均滑点成本: ${avg_slippage_cost:.4f}")
    
    # 对比不同滑点水平
    print("\n=== 不同滑点水平下的年化影响 ===")
    for bps in [1, 5, 10, 20, 50]:
        cost_per_trade = np.mean(theoretical_prices) * (bps / 10000)
        annual_cost = cost_per_trade * 250 * 2  # 假设每天2笔，每年250个交易日
        print(f"  {bps:3d} bps → 每笔${cost_per_trade:.3f} → 年化${annual_cost:.2f}")

simulate_trades(1000, 5)
```

**关键洞察：** 一个年化 30% 的策略，如果每天交易两次 + 10 bps 滑点，光是交易成本就能吃掉 5-10% 的年化收益。

### 3. 流动性（Liquidity）：你的对手盘是谁？

流动性 = **你能以合理价格快速买卖的能力**。

| 流动性 | 特征 | 例子 |
|--------|------|------|
| 高 | 价差小、大单不冲击价格 | AAPL, SPY |
| 中 | 价差适中、中等冲击 | 大部分ETF |
| 低 | 价差大、小单就砸盘 | 小盘股、垃圾债 |

```python
# 用 yfinance 数据观察流动性——用成交量 + 价差来近似
import yfinance as yf

tickers = ["SPY", "AAPL", "IWM", "TLT", "USO"]
data = yf.download(tickers, start="2024-01-01", end="2024-12-31")

# 用日成交量近似流动性
volume = data['Volume']
avg_volume = volume.mean()

print("=== 日均成交量（流动性近似指标）===")
for t in tickers:
    print(f"{t:6s}: 日均 {avg_volume[t]/1e6:.2f}M 股")

# 用日收益的极端值来近似"价差"冲击
close = data['Adj Close']
daily_returns = close.pct_change().dropna()
max_daily_move = daily_returns.abs().max() * 100

print("\n=== 单日最大波动（流动性风险信号）===")
for t in tickers:
    print(f"{t:6s}: 最大日波动 {max_daily_move[t]:+.2f}%")
```

**流动性陷阱：** 看起来便宜的品种（小盘股、低交易量ETF），实际交易成本可能远高于大盘股。**一个 100 万的策略放在日均交易 10 万的品种上，你就是市场本身。**

### 4. 交易时间：市场不是 24 小时营业的

| 时段 | 时间（美东） | 特点 |
|------|-------------|------|
| **盘前** | 4:00-9:30 | 流动性差，价差大 |
| **盘中** | 9:30-16:00 | 流动性最好 |
| **盘后** | 16:00-20:00 | 流动性急剧下降 |

```python
# 展示盘前盘后的影响——用挂单来模拟
# 实际上我们可以看开盘跳空（gap）
spy = yf.download("SPY", start="2024-01-01", end="2024-12-31")['Adj Close']
gaps = spy.pct_change().dropna()

# 大幅跳空（开盘和前一天收盘差距大）
large_gaps = gaps[abs(gaps) > 0.005]
print(f"=== SPY 2024年日间跳空分析 ===")
print(f"总交易日: {len(gaps)}")
print(f"大幅跳空(>0.5%)天数: {len(large_gaps)} ({len(large_gaps)/len(gaps)*100:.1f}%)")
print(f"最大单日跳空: {gaps.max()*100:.2f}%")
print(f"最差单日跳空: {gaps.min()*100:.2f}%")
print()
print("💡 隔夜跳空 = 盘前信息的冲击 = 你在收盘时无法交易")
print("💡 跳空是滑点的极端表现形式")
```

### 5. 完整模拟：市场订单 vs 限价订单

```python
import numpy as np

def simulate_market_vs_limit(n_days=252, mu=0.0005, sigma=0.01, slippage_bps=5):
    """
    模拟一年内，用市价单 vs 限价单交易同一标的
    mu: 日均收益（年化约12.6%）
    sigma: 日波动率
    slippage_bps: 市价单的滑点
    """
    np.random.seed(42)
    prices = [100.0]
    for _ in range(n_days):
        ret = np.random.normal(mu, sigma)
        prices.append(prices[-1] * (1 + ret))
    
    prices = np.array(prices)
    
    # 市价单策略：每天买入1股，承受滑点
    market_cost = 0
    market_shares = 0
    for p in prices:
        actual_cost = p * (1 + slippage_bps / 10000)
        market_cost += actual_cost
        market_shares += 1
    
    # 限价单策略：只在价格低于昨日收盘价-0.5%时买入
    limit_cost = 0
    limit_shares = 0
    for i in range(1, len(prices)):
        target_price = prices[i-1] * 0.995  # 低于昨日收盘价0.5%
        if prices[i] <= target_price:
            limit_cost += prices[i]  # 限价单无滑点
            limit_shares += 1
    
    final_value_open = market_shares * prices[-1]
    market_value = market_shares * prices[-1]
    limit_value = limit_shares * prices[-1]
    
    print(f"=== 市价单 vs 限价单 (一年模拟) ===")
    print(f"最终股价: ${prices[-1]:.2f}")
    print()
    print(f"【市价单策略】")
    print(f"  买入: {market_shares} 股")
    print(f"  总成本: ${market_cost:.2f}")
    print(f"  最终价值: ${market_value:.2f}")
    print(f"  利润: ${market_value - market_cost:.2f}")
    print()
    print(f"【限价单策略】")
    print(f"  买入: {limit_shares} 股（只成交了 {limit_shares/market_shares*100:.1f}%）")
    print(f"  总成本: ${limit_cost:.2f}")
    print(f"  最终价值: ${limit_value:.2f}")
    print(f"  利润: ${limit_value - limit_cost:.2f}")
    print()
    print(f"限价单成本更低，但可能买不到！→ 踏空风险")
    print(f"市价单保证执行但有滑点成本")

simulate_market_vs_limit(252)
```

## 关键洞察

**回测中忽略滑点 = 考试中忽略扣分项。** 一个看起来年化 25% 的策略，加上 10 bps 滑点和每天一次交易，实际可能只剩 10-15%。更糟的是，有些策略完全依赖低延迟或在流动性差的品种上交易——这类策略在回测中完美，在实盘中灾难。

**专业量化团队的黄金法则：** 在回测中至少尝试三个滑点假设（0 bps / 5 bps / 20 bps），如果策略在 20 bps 下滑点下变负，说明策略实质上不可交易。

## 深度阅读

| 主题 | 链接 |
|------|------|
| 订单簿结构与价差计算 | [1.2 订单类型与市场机制](/quant-finance/1.2-order-types) |
| 市场微观结构 | [5.0 市场微观结构](/quant-finance/5.0-market-microstructure) |
| 订单簿分析 | [5.1 订单簿分析](/quant-finance/5.1-order-book-analysis) |
| 执行算法 | [5.2 执行算法](/quant-finance/5.2-execution-algorithms) |

## 练习

### 选择题

1. 以下哪种订单可以**保证成交价格**但**不保证一定成交**？
   - A. 市价单
   - B. 限价单
   - C. 止损单
   - D. 冰山订单

2. 在流动性低的品种上交易，最可能遇到？
   - A. 更低的佣金
   - B. 更大的滑点和市场冲击
   - C. 更快的成交速度
   - D. 更高的夏普比率

### 编程题

**题目：** 写一个函数 `slippage_impact(n_trades, slippage_bps)`，模拟在 100 笔交易中，滑点从 1 bps 到 50 bps 对总交易成本的影响。输出一个表格（品种 × 滑点水平 × 年化成本），假设平均交易额为 $10,000，每年 250 个交易日，每天交易一次。

```python
# 你的代码
```

### 论述题

**题目：** 为什么滑点对**高频策略**的影响远大于**中低频策略**？用 200-300 字分析，至少包括：
- 高频策略的交易频率特征
- 高频策略对价格的敏感度
- 你的模拟结果如何支持你的论点

---

> 💡 **下一节：** [2.3 时间价值 — 为什么 $100 ≠ $100](./03-time-value)
