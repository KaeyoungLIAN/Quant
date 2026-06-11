# 7.2 执行与资金管理

> 本章目标：理解从交易信号到实际下单之间的差距——资金管理、滑点、执行成本。

## 一句话

**一个好的策略 + 差的执行 = 亏损。** 赚钱的决定性因素往往不是策略本身，而是怎么管理资金、怎么下单。

## 学习目标

学完本章你能：
- 理解凯利公式和固定比例资金管理
- 估算滑点成本
- 设计一个稳健的资金管理方案

## 核心内容

### 1. 凯利公式——最优下注比例

$$f^* = \frac{bp - q}{b}$$

其中：
- $f^*$ = 最优下注比例
- $b$ = 盈亏比
- $p$ = 胜率
- $q = 1-p$ = 败率

```python
import numpy as np

def kelly_criterion(win_rate, profit_ratio, loss_ratio=1):
    """
    凯利公式
    win_rate: 胜率
    profit_ratio: 平均盈利 / 平均亏损
    """
    b = profit_ratio / loss_ratio  # 净盈亏比
    p = win_rate
    q = 1 - p
    
    f = (b * p - q) / b
    return f

# 示例
# 胜率 55%，盈亏比 1.5
f = kelly_criterion(0.55, 1.5)
print(f"凯利比例: {f:.2%}")
print(f"建议: 每笔交易投入 {f:.1%} 的资金")

# 凯利的建议通常太大（全仓的风险太高）
# 实际使用半凯利：f/2
print(f"半凯利: {f/2:.2%}")
```

### 2. 固定比例 vs 凯利

```python
import numpy as np
import pandas as pd

def simulate_money_management(strategy_rets, initial_capital=100000):
    """比较不同资金管理方式"""
    
    methods = {}
    
    # 1. 固定数量（每笔固定 1000 股）
    capital = initial_capital
    for ret in strategy_rets:
        capital *= (1 + ret)
    methods['full_reinvest'] = capital
    
    # 2. 固定比例（每笔投入 20% 资金）
    capital = initial_capital
    position_pct = 0.2
    for ret in strategy_rets:
        capital *= (1 + ret * position_pct)
    methods['fixed_20pct'] = capital
    
    # 3. 半凯利
    win_rate = (strategy_rets > 0).mean()
    avg_win = strategy_rets[strategy_rets > 0].mean()
    avg_loss = abs(strategy_rets[strategy_rets < 0].mean())
    f_half = kelly_criterion(win_rate, avg_win/avg_loss) / 2
    f_half = max(0.01, min(f_half, 0.5))  # 限制在 1%-50%
    
    capital = initial_capital
    for ret in strategy_rets:
        capital *= (1 + ret * f_half)
    methods[f'semi_kelly_{f_half:.0%}'] = capital
    
    return methods

# 模拟策略收益率
np.random.seed(42)
sample_rets = np.random.choice([0.02, -0.01, 0.01, -0.005], 
                                size=200, p=[0.3, 0.2, 0.3, 0.2])
sample_rets = pd.Series(sample_rets)

results = simulate_money_management(sample_rets)
for name, capital in results.items():
    print(f"{name}: ${capital:,.0f}")
```

### 3. 滑点——真实的敌人

```python
def simulate_slippage(signal, close, slippage_bps=5):
    """
    模拟滑点对策略的影响
    slippage_bps: 滑点，单位是基点（1bp = 0.01%）
    """
    # 买入时价格更贵，卖出时价格更便宜
    slippage = slippage_bps / 10000  # 转小数
    
    # 找出交易切换的日期
    trades = signal.diff().abs() > 0
    
    # 开仓时 + 滑点，平仓时 - 滑点
    trade_cost = trades * slippage * 2  # 双边
    
    returns = close.pct_change()
    strategy_rets = signal.shift(1) * returns - trade_cost.shift(1).fillna(0)
    
    return strategy_rets

# 对比不同滑点下的收益
for bps in [0, 5, 10, 20, 50]:
    rets = simulate_slippage(signal, close, bps)
    total = (1 + rets.dropna()).prod() - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(252)
    print(f"滑点{bps}bp: 总收益 {total:.2%}, 夏普 {sharpe:.2f}")
```

### 4. 完整的交易前检查清单

```python
def pre_trade_checklist(strategy, current_position):
    """
    下单前的检查清单
    """
    checks = []
    
    # 1. 风险检查
    if abs(current_position) > 0.25:
        checks.append("⚠️ 单一仓位超过 25%，建议减仓")
    
    # 2. 流动性检查
    # （需要实时数据：略）
    
    # 3. 市场状态
    # （涨跌停、停牌等）
    
    # 4. 心理检查
    print("你是不是因为"觉得这次不一样"而加仓？")
    print("你做好亏损 20% 的心理准备了吗？")
    
    return checks

pre_trade_checklist('momentum', 0.3)
```

## 深度阅读

## 练习

### 选择题

1. 凯利公式的作用是：
   - A. 选股
   - B. 计算最优下注比例
   - C. 回测策略
   - D. 数据清洗

2. 半凯利通常比全凯利更好的原因是：
   - A. 赚得更多
   - B. 更保守，降低了破产风险
   - C. 计算更简单
   - D. 没有区别

3. 滑点对以下哪种策略影响最大？
   - A. 年交易 5 次
   - B. 月交易 20 次
   - C. 日交易 50 次
   - D. 周交易 2 次

### 编程题

**作业：** 对一个回测结果计算不同资金管理策略下的最终资金曲线（全仓 vs 半凯利 vs 固定比例 20%），绘图对比。

### 填空题

凯利公式中 $f^* = (bp - q)/b$，其中 $p$ 代表 \_\_\_\_，$b$ 代表 \_\_\_\_。

## 掌握检查
