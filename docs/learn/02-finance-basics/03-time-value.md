# 2.3 时间价值：为什么 $100 ≠ $100

> **今天的 $100 比明天的 $100 更值钱**——因为今天你可以拿它投资赚利息。这个简单的道理是量化金融所有定价模型的根基。

## 一句话

**今天的钱可以生钱，所以同样的金额，越早拿到越值钱。** 时间价值的计算就是量化你在什么时候拿到多少钱更划算。

## 学习目标

学完本章你能：
- 用 Python 计算终值（FV）、现值（PV）
- 区分复利和单利、APR 和 APY
- 理解连续复利及其在衍生品定价中的角色
- 用净现值（NPV）判断一个投资项目是否值得

## 核心内容

### 1. 终值（Future Value）：今天存的钱明天变多少？

核心公式：
```
FV = PV × (1 + r)^n
```

其中：
- PV = 现值（今天有多少钱）
- r = 每期利率
- n = 期数

```python
# 终值计算：$1,000 投资 5 年，年化收益 8%
pv = 1000          # 现值
r = 0.08           # 年利率
n = 5              # 年数

fv = pv * (1 + r) ** n
print(f"💰 ${pv} 投资 {n} 年，年化 {r*100}%")
print(f"   终值 = ${pv} × (1 + {r})^{n} = ${fv:.2f}")
print(f"   收益 = ${fv - pv:.2f}")
print()

# 不同年限对比
print("=== 不同年限的终值 ($1000 @ 8%) ===")
for years in [1, 3, 5, 10, 20, 30]:
    fv_y = pv * (1 + r) ** years
    print(f"  {years:2d} 年 → ${fv_y:>8.2f} (翻了 {fv_y/pv:.1f}x)")
```

### 2. 现值（Present Value）：未来的钱今天值多少？

核心公式（终值的逆运算）：
```
PV = FV / (1 + r)^n
```

```python
# 现值计算：5 年后收到的 $10,000，折现率 6%
fv = 10000
r = 0.06
n = 5

pv = fv / (1 + r) ** n
print(f"💰 若 {n} 年后收到 ${fv}，按 {r*100}% 折现")
print(f"   现值 = ${fv} / (1 + {r})^{n} = ${pv:.2f}")
print(f"   也就是说，今天存 ${pv:.2f} 到年化 {r*100}% 的账户里，")
print(f"   {n} 年后刚好变成 ${fv}")
print()

# 不同折现率的影响
print("=== 不同折现率下，5年后$10,000的现值 ===")
for rate in [0.02, 0.05, 0.08, 0.10, 0.15]:
    pv_r = fv / (1 + rate) ** n
    print(f"  折现率 {rate*100:4.0f}% → 现值 ${pv_r:>8.2f}")
```

**关键洞察：** 折现率越高，未来的钱在今天越不值钱。这就是为什么高通胀环境下，人们更愿意"活在当下"。

### 3. APR vs APY：名义利率 vs 实际利率

**APR（年化百分比利率）** = 名义年利率，不考虑复利
**APY（年化百分比收益率）** = 实际年收益率，考虑复利

```python
# APR 和 APY 的差异
def calc_apy(apr, compounding_per_year):
    """将 APR 转换为 APY"""
    return (1 + apr / compounding_per_year) ** compounding_per_year - 1

apr = 0.10  # 10% 名义利率

print(f"=== APR = {apr*100}% 在不同复利频率下的 APY ===")
print(f"{'复利频率':15s} {'APR':>8s} {'APY':>12s}")
print("-" * 35)

# 不同复利频率
frequencies = [
    ("年复利", 1),
    ("半年复利", 2),
    ("季度复利", 4),
    ("月复利", 12),
    ("日复利", 365),
]

for name, freq in frequencies:
    apy = calc_apy(apr, freq)
    print(f"{name:15s} {apr*100:7.1f}% {apy*100:10.4f}%")

print()
print("💡 APR 和 APY 差异 = 复利的威力")
print("💡 银行喜欢报 APR（数字小），存款产品喜欢报 APY（数字大）")
```

### 4. 连续复利：衍生品定价的核心

当复利频率趋近无限大时，终值公式变成：
```
FV = PV × e^(r × t)
```

```python
import numpy as np

# 连续复利 vs 离散复利
pv = 1000
r = 0.08
t = 5

# 离散复利（年复利）
fv_annual = pv * (1 + r) ** t

# 连续复利
fv_continuous = pv * np.exp(r * t)

print(f"=== 连续复利 vs 离散复利 ($1000 @ 8% × 5年) ===")
print(f"年复利:     ${fv_annual:.2f}")
print(f"连续复利:   ${fv_continuous:.2f}")
print(f"差异:       ${fv_continuous - fv_annual:.2f}")
print()

# 为什么量化金融使用连续复利？
# 1. 数学上更好处理（可微）
# 2. 收益可以加总（对数收益可加性）
daily_returns = np.random.normal(0.08/252, 0.15/np.sqrt(252), 252)
total_log_return = np.sum(daily_returns)
total_simple_return = np.prod(1 + daily_returns) - 1

print(f"=== 对数收益的可加性 ===")
print(f"日收益之和（对数）: {total_log_return*100:.4f}%")
print(f"   等价于: PV × e^(总和) = ${pv * np.exp(total_log_return):.2f}")
print(f"简单收益累乘:      {total_simple_return*100:.4f}%")
print(f"   等价于: PV × ∏(1+R_i) = ${pv * (1+total_simple_return):.2f}")
```

### 5. 净现值（NPV）：投资决策的核心工具

NPV 将项目所有未来现金流折现到今天，减去初始投资：
```
NPV = Σ CF_t / (1+r)^t - C_0
```

NPV > 0 → 项目值得投资
NPV < 0 → 项目不值得

```python
def npv(cashflows, discount_rate, initial_investment):
    """
    计算净现值
    cashflows: 未来每期的现金流列表
    discount_rate: 折现率
    initial_investment: 初始投资（正数）
    """
    total_pv = 0
    for t, cf in enumerate(cashflows, 1):
        pv = cf / (1 + discount_rate) ** t
        total_pv += pv
        print(f"  第{t}年: CF=${cf:>6.2f} → PV=${pv:>6.2f}")
    
    npv_value = total_pv - initial_investment
    print(f"\n  未来现金流现值总计: ${total_pv:.2f}")
    print(f"  初始投资:           ${initial_investment:.2f}")
    print(f"  {'='*35}")
    print(f"  NPV =               ${npv_value:.2f}")
    
    if npv_value > 0:
        print(f"  ✅ NPV > 0 → 值得投资！")
    else:
        print(f"  ❌ NPV < 0 → 不值得")
    
    return npv_value

print("=== 投资决策案例 ===")
print("项目: 开一家奶茶店")
print("初始投资: $50,000")
print("预计年收益: $15,000（连续5年）")
print("折现率: 8%（你的资金成本）")

cf = npv(
    cashflows=[15000, 15000, 15000, 15000, 15000],
    discount_rate=0.08,
    initial_investment=50000
)

print()
# 如果折现率提高到15%呢？
print("=== 同样的项目，改变折现率 ===")
cf2 = npv(
    cashflows=[15000, 15000, 15000, 15000, 15000],
    discount_rate=0.15,
    initial_investment=50000
)
```

### 6. 在策略回测中的应用

时间价值在量化策略中至少出现在三个地方：

```python
import yfinance as yf

# 应用1: 策略收益需要年化，不能只看总收益
spy = yf.download("SPY", start="2020-01-01", end="2024-12-31")['Adj Close']
total_return = spy.iloc[-1] / spy.iloc[0] - 1
trading_days = len(spy)
years = trading_days / 252

# 年化收益率（考虑复利！）
annual_return = (1 + total_return) ** (1 / years) - 1

print(f"=== SPY 2020-2024 ===")
print(f"投资天数: {trading_days} ({years:.1f}年)")
print(f"总收益率: {total_return*100:.2f}%")
print(f"年化收益率（复利）: {annual_return*100:.2f}%")
print()

# 应用2: 回测中每天的现金应该计息
cash_interest_rate = 0.05  # 5% 无风险利率
daily_cash_rate = (1 + cash_interest_rate) ** (1/252) - 1

# 假设回测中某段时间持有 $10,000 现金 30 天
cash_balance = 10000
days_held = 30
cash_earned = cash_balance * ((1 + daily_cash_rate) ** days_held - 1)
print(f"持有 ${cash_balance} 现金 {days_held} 天，无风险收益: ${cash_earned:.2f}")

# 应用3: 现金流折现——5年后到期的策略收益需要折现
future_profit = 50000  # 5年后实现的策略收益
risk_free_rate = 0.04   # 4% 无风险利率
present_profit = future_profit / (1 + risk_free_rate) ** 5
print(f"5年后的 $50,000 收益 = 今天的 ${present_profit:.2f}")
```

**关键洞察：** 很多业余量化回测框架不计算现金的利息收益，回测结果偏差 0.5-1% 年化。看起来小，但长期复利后差异巨大。

## 深度阅读

| 主题 | 链接 |
|------|------|
| TVM 详细推导与手工计算 | [3.0 货币时间价值](/quant-finance/3.0-time-value-of-money) |
| 债券定价中的贴现应用 | [3.1 债券定价](/quant-finance/3.1-bond-pricing) |
| 期权定价中的连续复利 | [3.4 Black-Scholes 模型](/quant-finance/3.4-black-scholes) |

## 练习

### 选择题

1. 如果 APR = 12%，按月复利，APY 大约是多少？
   - A. 12.00%
   - B. 12.68%
   - C. 13.00%
   - D. 12.50%

2. 计算 NPV 时，如果折现率从 8% 提高到 12%，NPV 会怎样？
   - A. 不变
   - B. 增加
   - C. 减少
   - D. 变为负数

### 编程题

**题目：** 一家公司考虑投资一个新项目，初始投入 $100,000。预计未来 5 年每年的现金流分别为：$20,000, $25,000, $30,000, $35,000, $40,000。折现率为 10%。

写一段代码计算这个项目的 NPV，并判断是否值得投资。然后计算：**折现率为多少时 NPV = 0**（即 IRR - 内部收益率）。

```python
# 你的代码
```

### 论述题

**题目：** 货币时间价值在量化策略的回测中有哪些应用？举两个具体的例子说明如果不考虑时间价值，回测结果会产生怎样的偏差。（200-300字）

---

> 💡 **下一节：** [2.4 风险入门 — 波动率·回撤·夏普比率](./04-risk-intro)
