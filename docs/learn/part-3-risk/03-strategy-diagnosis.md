# 3.3 策略诊断与改进

> 本章目标：当一个策略表现不好时——知道怎么诊断、怎么修。

## 一句话

**策略诊断** = 拆解收益来源，找到薄弱环节，针对性改进。

## 学习目标

学完本章你能：
- 用收益归因分析找到策略赚钱/亏钱的真正原因
- 诊断回测中的"假信号"（交易成本、滑点、流动性）
- 知道什么时候应该放弃一个策略，什么时候应该改进

## 核心内容

### 1. 收益归因——钱从哪来？

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('SPY', start='2020-01-01', end='2024-12-31')
close = data['Adj Close']
returns = close.pct_change().dropna()

# 双均线策略
ma_s = close.rolling(20).mean()
ma_l = close.rolling(60).mean()
signal = pd.Series(0, index=close.index)
signal[ma_s > ma_l] = 1
strategy_rets = signal.shift(1) * returns

def attribution_analysis(signal, returns, strategy_rets):
    """分解策略收益来源"""
    
    position_changes = signal.diff().fillna(0)
    entries = position_changes[position_changes > 0].index
    exits = position_changes[position_changes < 0].index
    
    # 每笔交易收益
    trade_rets = []
    for i in range(min(len(entries), len(exits))):
        entry = entries[i]
        exit_ = exits[i]
        if entry < exit_:
            trade_rets.append(returns[entry:exit_].sum())
    
    trade_rets = pd.Series(trade_rets)
    
    print("=== 交易分析 ===")
    print(f"总交易: {len(trade_rets)}")
    print(f"赚钱: {(trade_rets > 0).sum()} ({(trade_rets > 0).mean():.1%})")
    print(f"亏钱: {(trade_rets < 0).sum()} ({(trade_rets < 0).mean():.1%})")
    print(f"平均盈利: {trade_rets[trade_rets > 0].mean():.4%}")
    print(f"平均亏损: {trade_rets[trade_rets < 0].mean():.4%}")
    print(f"盈亏比: {abs(trade_rets[trade_rets > 0].mean() / trade_rets[trade_rets < 0].mean()):.2f}")
    
    # 收益按月份分析
    monthly = strategy_rets.resample('ME').sum()
    monthly_pos = monthly[monthly > 0]
    monthly_neg = monthly[monthly < 0]
    print(f"\n=== 月度分析 ===")
    print(f"盈利月份: {len(monthly_pos)} ({len(monthly_pos)/len(monthly):.0%})")
    print(f"亏损月份: {len(monthly_neg)} ({len(monthly_neg)/len(monthly):.0%})")
    print(f"最佳月份: {monthly.max():.2%}")
    print(f"最差月份: {monthly.min():.2%}")
    
    return trade_rets, monthly

trade_rets, monthly = attribution_analysis(signal, returns, strategy_rets)
```

### 2. 交易成本的影响

```python
import numpy as np
import pandas as pd

def simulate_trading_costs(signal, returns, cost_per_trade=0.001):
    """
    模拟交易成本对策略的影响
    cost_per_trade: 每笔交易成本（0.001 = 10bp，约等于买卖各5bp）
    """
    # 计算交易次数
    trades = signal.diff().abs() > 0
    n_trades = trades.sum()
    
    # 无成本收益
    no_cost_rets = signal.shift(1) * returns
    
    # 有成本收益
    cost = trades * cost_per_trade
    with_cost_rets = signal.shift(1) * returns - cost.shift(1).fillna(0)
    
    no_cost_sharpe = no_cost_rets.mean() / no_cost_rets.std() * np.sqrt(252)
    with_cost_sharpe = with_cost_rets.mean() / with_cost_rets.std() * np.sqrt(252)
    
    print(f"交易次数: {n_trades}")
    print(f"无成本夏普: {no_cost_sharpe:.2f}")
    print(f"有成本夏普: {with_cost_sharpe:.2f}")
    print(f"夏普损失: {no_cost_sharpe - with_cost_sharpe:.2f}")
    print(f"总成本消耗: {(1 - (1 + with_cost_rets).prod() / (1 + no_cost_rets).prod()):.2%}")
    
    # 找出盈亏平衡的交易成本
    for cost in [0.0005, 0.001, 0.002, 0.003, 0.005]:
        c = trades * cost
        final_rets = signal.shift(1) * returns - c.shift(1).fillna(0)
        final_ret = (1 + final_rets.dropna()).prod() - 1
        if final_ret <= 0:
            print(f"→ 交易成本{c:.1%}时策略归零")
            break

simulate_trading_costs(signal, returns)
```

**关键数据：**
- 美国股票：买卖 1-2bp
- A 股：5-10bp + 印花税 10bp
- 高频交易（日交易 10+ 次）：成本会吃掉大部分收益

### 3. 时间选择性——策略什么时候赚钱？

```python
import numpy as np
import pandas as pd

def temporal_patterns(strategy_rets):
    """分析策略的时间模式"""
    
    # 星期几效果
    day_of_week = strategy_rets.groupby(strategy_rets.index.dayofweek).mean()
    print("每周收益分布:")
    for i, ret in enumerate(['周一','周二','周三','周四','周五']):
        print(f"  {ret}: {day_of_week.iloc[i]:.4%}")
    
    # 月份效果
    monthly = strategy_rets.resample('ME').sum()
    month_of_year = monthly.groupby(monthly.index.month).mean()
    print("\n每月收益分布:")
    for m in range(1, 13):
        print(f"  {m}月: {month_of_year.get(m, pd.NA):.4%}")
    
    # 市场波动环境
    vol = strategy_rets.rolling(20).std()
    high_vol = strategy_rets[vol > vol.median()]
    low_vol = strategy_rets[vol <= vol.median()]
    print(f"\n高波动期表现: {high_vol.mean():.4%}")
    print(f"低波动期表现: {low_vol.mean():.4%}")

temporal_patterns(strategy_rets)
```

### 4. 策略改进清单

当策略表现不好时，按顺序检查：

```python
import numpy as np
import pandas as pd

def strategy_checklist(strategy_rets, signal, returns):
    """
    策略诊断清单
    
    返回：问题列表和建议
    """
    issues = []
    
    # 1. 是否有正期望值？
    if strategy_rets.mean() <= 0:
        issues.append("❌ 策略期望值为负——不要再继续了")
    elif strategy_rets.mean() < 0.0001:
        issues.append("⚠️ 期望值接近零——可能只是噪声")
    
    # 2. 交易次数够不够？
    trades = (signal.diff().abs() > 0).sum()
    if trades < 20:
        issues.append("❌ 交易次数太少（<20）——统计不可靠")
    elif trades < 50:
        issues.append("⚠️ 交易次数较少（<50）——谨慎评估")
    
    # 3. 正收益是否集中在一段时间？
    half = len(strategy_rets) // 2
    first_half = strategy_rets.iloc[:half].sum()
    second_half = strategy_rets.iloc[half:].sum()
    if (first_half > 0) != (second_half > 0):
        issues.append("⚠️ 收益集中在某一段时间——过拟合风险")
    
    # 4. 最大回撤是否过大？
    equity = (1 + strategy_rets).cumprod()
    peak = equity.expanding().max()
    dd = (equity - peak) / peak
    if dd.min() < -0.3:
        issues.append("⚠️ 最大回撤超过 30%——检查是否扛得住")
    
    # 5. 有没有多笔连续亏损？
    losing_streak = 0
    max_losing_streak = 0
    for r in strategy_rets:
        if r < 0:
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0
    if max_losing_streak > 10:
        issues.append(f"⚠️ 最长连续亏损 {max_losing_streak} 次——心理压力大")
    
    if not issues:
        issues.append("✅ 策略通过基本诊断")
    
    for issue in issues:
        print(issue)
    
    return issues

strategy_checklist(strategy_rets, signal, returns)
```

### 5. 什么时候该放弃？

```
该放弃的信号：
├── 样本外夏普 < 0.3
├── 参数微调就崩盘（参数敏感）
├── 高交易成本下归零
├── 逻辑不成立（"因为月亮圆所以买入"）
└── 你自己都不信

该改进的信号：
├── 胜率低但盈亏比高 → 降低止损
├── 胜率高但盈亏比低 → 让利润奔跑
├── 只在某些月份赚钱 → 增加择时过滤
└── 样本外夏普 > 0.5 → 值得打磨
```

## 深度阅读

## 练习

### 选择题

1. 策略诊断中最先检查的是：
   - A. 夏普比率是否够高
   - B. 策略期望值是否为正
   - C. 回撤是否在承受范围内
   - D. 交易次数

2. 一个策略盈亏比 3:1，胜率 30%：
   - A. 期望值为负
   - B. 期望值为正（0.3×3 - 0.7×1 = 0.2）
   - C. 无法判断
   - D. 胜率太低应该放弃

3. 交易成本对以下哪种策略影响最大？
   - A. 长期持有策略（年交易<5次）
   - B. 日级别回测策略
   - C. 高频策略（日交易>10次）
   - D. 配对交易策略

4. 策略在 2020-2021 年表现极好，2022-2023 年表现很差，这：
   - A. 说明策略完全无效
   - B. 可能是在特定市场环境（低利率）下过度拟合
   - C. 需要修改参数
   - D. 是正常现象

### 编程题

**作业：** 拿你之前写的一个策略，做完整的诊断检查（交易成本、时间模式、归因分析），写一份改进建议。

### 填空题

盈亏比 2:1、胜率 40% 的策略，其期望值是 \_\_\_\_ 。

## 掌握检查
