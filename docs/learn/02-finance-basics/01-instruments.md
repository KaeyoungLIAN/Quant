# 2.1 交易品种：股票·ETF·期货·期权·债券

> 量化交易首先是个选择题：**你交易什么品种？** 不同品种的风险收益特征天差地别。这一节帮你建立品种全景图，并用 Python 看真实数据。

## 一句话

**股票代表公司所有权，ETF是一篮子资产，期货是杠杆赌约，期权是权利买卖，债券是借钱收息。** 每个品种的数学结构不同，策略代码自然不同。

## 学习目标

学完本章你能：
- 用 yfinance 下载股票、ETF、债券数据
- 理解股息、拆分对数据的影响
- 解释为什么不同品种的收益/风险曲线完全不同
- 对比股票和债券的风险特征

## 核心内容

### 1. 股票（Stocks）：最基础的品种

股票代表公司的所有权份额。你持有的每一股都在法律上代表公司的一部分。

**关键概念：**
- **股息（Dividend）** — 公司从利润中分给股东的钱
- **拆股（Stock Split）** — 一股拆成多股，总价值不变，但每股价格降低

```python
import yfinance as yf
import pandas as pd

# 下载苹果公司数据——带股息信息
aapl = yf.download("AAPL", start="2022-01-01", end="2024-12-31", auto_adjust=False)
print("=== AAPL 最近5行原始数据 ===")
print(aapl.tail(5))
print()

# 查看股息发放记录
aapl_div = aapl['Dividends'][aapl['Dividends'] > 0]
print(f"\n=== AAPL 股息发放记录 ({len(aapl_div)} 次) ===")
print(aapl_div.tail(10))
print(f"平均股息: ${aapl_div.mean():.4f}")
```

输出示例：
```
=== AAPL 最近5行原始数据 ===
                  Open        High  ...    Dividends  Stock Splits
Date                                ...
2024-12-24  255.070007  258.489990  ...   0.000000           0.0
2024-12-26  258.350006  260.459991  ...   0.000000           0.0
...

=== AAPL 股息发放记录 (8 次) ===
Date
2022-02-04    0.22
...
2024-05-10    0.25
Name: Dividends, dtype: float64
平均股息: $0.2425
```

**注意：** `auto_adjust=False` 才能看到原始的股息和拆分数据。如果用默认的 `auto_adjust=True`，价格已经被后向调整过，股息数据消失。如果你做股息策略，必须用原始数据。

### 2. ETF（交易所交易基金）：一篮子资产的盲盒

ETF 是一只**买了其他资产的基金**，像股票一样在交易所交易。

| ETF | 追踪标的 | 含义 |
|-----|---------|------|
| SPY | S&P 500 指数 | 美国最大的500家公司 |
| QQQ | Nasdaq 100 指数 | 科技巨头（Apple, Microsoft, Google...） |
| TLT | 20+年国债 | 长期美国政府债券 |
| GLD | 黄金价格 | 实物黄金 |

ETF 存在的意义：**你不用选股**，买 SPY = 拥有 500 家公司的一小部分。

```python
# 下载并比较四种 ETF 的表现
tickers = ["SPY", "QQQ", "TLT", "GLD"]
data = yf.download(tickers, start="2020-01-01", end="2024-12-31")['Adj Close']

# 归一化到 100 起点，方便比较
normalized = data / data.iloc[0] * 100

print("=== 归一化价格（2020年初 = 100）===")
print(normalized.tail(5))
print()

# 计算总收益率
total_return = (data.iloc[-1] / data.iloc[0] - 1) * 100
print("=== 2020-2024 总收益率 ===")
for t in tickers:
    print(f"{t:5s}: {total_return[t]:+6.1f}%")
```

关键观察：
- SPY（大盘股）和 QQQ（科技股）长期上涨，但 QQQ 波动更大
- TLT（国债）涨跌和经济周期反向——经济差时资金涌入国债
- GLD（黄金）在通胀和危机时表现好

**这就是分散化的基础：** 同时持有这四种，比只持有任何一种更平稳。

### 3. 期货（Futures）：杠杆游戏

期货是**约定在未来某天以约定价格买卖某物**的合约。

核心特征：
- **杠杆** — 只需交保证金就能控制大额资产（5-20倍）
- **到期日** — 合约有生命期，到期必须交割或展期
- **双向交易** — 可以做空（赌跌）和做多（赌涨）

```python
# 期货数据比较复杂，这里仅看概念
# yfinance 支持部分期货 ETF，如 USO（原油ETF）
uso = yf.download("USO", start="2023-01-01", end="2024-12-31")['Adj Close']
returns = uso.pct_change().dropna()

print("=== USO（原油ETF）2023-2024 日收益统计 ===")
print(f"日均收益: {returns.mean()*100:.4f}%")
print(f"日波动率: {returns.std()*100:.2f}%")
print(f"最高日收益: {returns.max()*100:.2f}%")
print(f"最低日收益: {returns.min()*100:.2f}%")
```

> ⚠️ **实盘警告：** 期货的杠杆是双刃剑。玉米期货 20 倍杠杆意味着价格波动 5%，你的本金归零。**永远不要用期货仓位模拟来替代真实资金管理。**

### 4. 期权（Options）：买一个"选择权"

期权给你**权利但不义务**在到期前以特定价格买卖某物。

| 类型 | 含义 | 什么时候赚钱 |
|------|------|-------------|
| **Call（看涨期权）** | 以 X 价买入的权利 | 股价 > X 时 |
| **Put（看跌期权）** | 以 X 价卖出的权利 | 股价 < X 时 |

```python
# 期权数据需用 yf.Ticker().option_chain()
# 这里仅展示如何查看某只股票的期权链
aapl = yf.Ticker("AAPL")
try:
    # 获取最近到期日的期权链
    expirations = aapl.options
    print(f"AAPL 可选到期日: {expirations[:5]}...")
    
    calls = aapl.option_chain(expirations[0]).calls
    print(f"\n=== 最近到期日Call（前5行）===")
    print(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume']].head())
except:
    print("期权数据可能需要网络或认证，跳过")
```

### 5. 债券（Bonds）：借钱收息

债券是**借条**：你借钱给政府/公司，他们按期付息并在到期还本。

**核心关系：债券价格 ↔ 利率（反向）**

利率上升 → 已有债券吸引力下降 → 价格下跌。

```python
# TLT = 长期国债 ETF，用来观察债券价格和利率的关系
import yfinance as yf

tlt = yf.download("TLT", start="2021-01-01", end="2024-12-31")['Adj Close']
tlt_returns = tlt.pct_change().dropna()

print("=== TLT（长期国债）年度表现 ===")
for year in ['2021', '2022', '2023', '2024']:
    yr_data = tlt_returns.loc[year]
    ret = (1 + yr_data).prod() - 1
    print(f"{year}: {ret*100:+5.1f}%")

# 美联储2022年暴力加息，TLT暴跌
# 2024年开始降息预期，TLT反弹
print("\n💡 2022年美联储加息 → TLT跌了约30%")
print("💡 2024年降息预期 → TLT反弹")
```

### 6. 品种对比：同时间段不同命运

```python
# 同一时间段（2022-2024）对比各个品种的表现
tickers = ["SPY", "QQQ", "TLT", "GLD", "USO"]
data = yf.download(tickers, start="2022-01-01", end="2024-12-31")['Adj Close']

ann_returns = {}
ann_vols = {}
for t in tickers:
    rets = data[t].pct_change().dropna()
    ann_returns[t] = (1 + rets.mean()) ** 252 - 1
    ann_vols[t] = rets.std() * (252 ** 0.5)

print(f"{'品种':6s} {'年化收益':>10s} {'年化波动':>10s}")
print("-" * 30)
for t in tickers:
    print(f"{t:6s} {ann_returns[t]*100:+8.2f}% {ann_vols[t]*100:8.2f}%")
```

你会发现：**同一时间段，不同品种的风险收益特征完全不一样。** 这就是为什么策略的第一步是选品种。

## 深度阅读

| 主题 | 链接 |
|------|------|
| 各品种合约规格与手工计算 | [1.1 交易品种](/quant-finance/1.1-market-instruments) |
| 期货保证金与杠杆计算 | [3.2 期货定价](/quant-finance/3.2-futures-pricing) |
| 期权基础与定价 | [3.3 期权基础](/quant-finance/3.3-options-intro) |
| 债券定价与久期 | [3.1 债券定价](/quant-finance/3.1-bond-pricing) |

## 练习

### 选择题

1. 以下哪个 ETF 追踪的是美国科技股？
   - A. SPY
   - B. TLT
   - C. QQQ
   - D. GLD

2. 当市场利率上升时，债券价格通常：
   - A. 上涨
   - B. 下跌
   - C. 不变
   - D. 取决于股票市场

### 编程题

**题目：** 用 yfinance 下载 SPY 和 TLT 在 2020-2024 的数据，计算两者的**日收益相关系数**和**年化波动率**。写一段代码输出这两个指标，并写一行注释解释结果的含义。

```python
# 你的代码在这里
```

### 论述题

**题目：** 用 200-300 字比较股票和债券的风险特征。至少提到：(1) 价格波动性差异 (2) 收益来源不同 (3) 什么情况下债券比股票更安全、什么情况下更危险。用你从 TLT 和 SPY 的数据中看到的真实表现支持你的论点。

---

> 💡 **下一节：** [2.2 市场机制 — 订单·滑点·流动性](./02-market-mechanism)
