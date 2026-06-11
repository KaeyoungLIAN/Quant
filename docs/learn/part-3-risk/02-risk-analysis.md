# 3.2 风险分析框架

> 本章目标：系统性分析一个策略的风险——不仅仅是看最大回撤。

## 一句话

**风险分析** = 回答三个问题：亏多少？什么时候亏？为什么亏？

## 学习目标

学完本章你能：
- 计算 VaR、CVaR、最大回撤等风险指标
- 做压力测试（市场崩盘时策略会怎样）
- 理解"风险不是波动率"这句话的真正含义

## 核心内容

### 1. VaR——"最坏情况"的概率量化

$$\text{VaR}_{95\%} = \text{在 95% 的情况下，亏损不会超过这个数}$$

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('SPY', start='2020-01-01', end='2024-12-31')
close = data['Adj Close']
returns = close.pct_change().dropna()

def var(returns, confidence=0.95):
    """计算 VaR（历史模拟法）"""
    return np.percentile(returns, (1 - confidence) * 100)

def cvar(returns, confidence=0.95):
    """CVaR（条件VaR）：超过VaR时的平均亏损"""
    threshold = var(returns, confidence)
    return returns[returns < threshold].mean()

# 每日VaR
daily_var_95 = var(returns)
daily_cvar_95 = cvar(returns)

print(f"日 VaR(95%): {daily_var_95:.4%}")
print(f"含义: 在95%的日子里，亏损不会超过{daily_var_95:.2%}")
print(f"日 CVaR(95%): {daily_cvar_95:.4%}")
print(f"含义: 在最坏的5%的日子里，平均亏损{daily_cvar_95:.2%}")

# 对比正态分布假设
from scipy import stats
normal_var = stats.norm.ppf(0.05, returns.mean(), returns.std())
print(f"\n如果收益率是正态分布，VaR应该是: {normal_var:.4%}")
print(f"差异: {(daily_var_95 - normal_var):.4%} → 市场比正态预测的更危险")
```

### 2. 压力测试——最坏的情景

单次风险指标不够，你要知道**在历史上最糟糕的时期**会发生什么：

```python
import numpy as np
import pandas as pd

def stress_test(strategy_rets, benchmark_rets, events):
    """
    压力测试
    events: {事件名: (开始日期, 结束日期)}
    """
    results = {}
    for event_name, (start, end) in events.items():
        period_rets = strategy_rets[start:end]
        bench_rets = benchmark_rets[start:end]
        
        results[event_name] = {
            'strategy_return': (1 + period_rets).prod() - 1,
            'benchmark_return': (1 + bench_rets).prod() - 1,
            'max_drawdown': (period_rets.cumsum()).min(),  # 简化
            'volatility': period_rets.std() * np.sqrt(252),
        }
    return pd.DataFrame(results).T

# 模拟策略和基准
np.random.seed(42)
full_returns = pd.Series(np.random.randn(1250) * 0.01, 
                         index=pd.date_range('2020-01-01', periods=1250, freq='B'))

# 定义压力事件
stress_events = {
    '2020年3月崩盘': ('2020-02-20', '2020-03-23'),
    '2022年加息': ('2022-01-01', '2022-10-01'),
    '2023年银行危机': ('2023-03-01', '2023-05-01'),
}

results = stress_test(full_returns, full_returns, stress_events)
print(results.round(4))
```

**关键洞察：** 一个策略如果在 2020 年 3 月崩盘时亏了 50% 但你扛得住，那就没问题——**前提是你真的扛得住**。

### 3. 回撤分析——看懂"亏钱的模样"

```python
import numpy as np
import pandas as pd

def drawdown_analysis(equity_curve):
    """
    全面回撤分析
    """
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak
    
    # 找出所有下跌超过 5% 的回撤期
    significant_drawdowns = []
    is_in_drawdown = False
    dd_start = None
    
    for i, dd in enumerate(drawdown):
        if not is_in_drawdown and dd < -0.05:
            is_in_drawdown = True
            dd_start = dd.index[i] if isinstance(dd.index, pd.DatetimeIndex) else dd.index
        elif is_in_drawdown and dd >= 0:
            is_in_drawdown = False
            dd_end = dd.index[i] if isinstance(dd.index, pd.DatetimeIndex) else dd.index
            significant_drawdowns.append((dd_start, dd_end))
    
    print(f"重大回撤（>5%）次数: {len(significant_drawdowns)}")
    
    # 最长回撤期
    # 只有 equity_curve 是 Series 的情况下
    try:
        underwater = peak
        # 简化版
        print(f"最大回撤深度: {drawdown.min():.2%}")
    except:
        pass

# 模拟净值
np.random.seed(42)
equity = (1 + full_returns * 0.3).cumprod()
drawdown_analysis(equity)
```

### 4. 回撤修复期——真正影响心理的指标

```python
import numpy as np
import pandas as pd

def recovery_time(equity_curve):
    """
    计算每次回撤后回到前高需要多少天
    """
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak
    
    recovery_periods = []
    is_in_drawdown = False
    prev_peak_idx = None
    prev_peak_val = 1.0
    
    for i in range(len(equity_curve)):
        if not is_in_drawdown and drawdown.iloc[i] < -0.05:
            is_in_drawdown = True
            prev_peak_val = peak.iloc[i]
            prev_peak_idx = i
        elif is_in_drawdown and equity_curve.iloc[i] >= prev_peak_val:
            is_in_drawdown = False
            recovery_days = i - prev_peak_idx
            recovery_periods.append(recovery_days)
    
    if recovery_periods:
        print(f"平均回撤修复期: {np.mean(recovery_periods):.0f} 天")
        print(f"最长回撤修复期: {max(recovery_periods)} 天")
    else:
        print("未发生超过5%的回撤")

recovery_time(equity)
```

**关键心理阈值：**
- 修复期 < 20 天 → 轻松扛住
- 修复期 20-100 天 → 需要点耐心
- 修复期 > 100 天 → 大多数人会在中途放弃策略

### 5. 下行波动率 vs 整体波动率

夏普比率把上涨和下跌的波动都视为"风险"。但实际上——**上涨波动不是风险！**

```python
import numpy as np
import pandas as pd

def sortino_ratio(returns, risk_free=0.03):
    """
    索提诺比率：只惩罚下行波动
    """
    daily_rf = risk_free / 252
    excess = returns - daily_rf
    downside_returns = returns[returns < daily_rf]
    downside_vol = downside_returns.std() * np.sqrt(252)
    
    annual_return = excess.mean() * 252
    return annual_return / downside_vol if downside_vol > 0 else 0

sr_sharpe = returns.mean() / returns.std() * np.sqrt(252)
sr_sortino = sortino_ratio(returns)

print(f"夏普比率: {sr_sharpe:.2f}")
print(f"索提诺比率: {sr_sortino:.2f}")
print(f"差异: {sr_sortino - sr_sharpe:.2f} {'→ 上涨波动多' if sr_sortino > sr_sharpe else '→ 下跌波动多'}")
```

## 深度阅读

## 练习

### 选择题

1. VaR(95%) = -2% 的含义是：
   - A. 策略 95% 的日子亏损超过 2%
   - B. 策略 5% 的日子亏损超过 2%
   - C. 策略 95% 的日子盈利 2%
   - D. 策略最多亏损 2%

2. CVaR 和 VaR 的主要区别是：
   - A. CVaR 看尾部平均，VaR 看尾部边界
   - B. CVaR 比 VaR 小
   - C. 两者没区别
   - D. CVaR 只看盈利侧

3. 索提诺比率和夏普比率的区别是：
   - A. 索提诺只惩罚下行波动
   - B. 索提诺用中位数
   - C. 索提诺不需要无风险利率
   - D. 两者没区别

4. 一个策略在 2020 年崩盘时亏了 30%，但半年后回到前高。这：
   - A. 不可接受，最大回撤太大
   - B. 可以接受，但需要扛住心理压力
   - C. 证明策略无效
   - D. 需要修改参数

### 编程题

**作业：** 选择一个你之前写的策略（动量/均值回归/配对），计算它完整的风险报告：VaR、CVaR、最大回撤、索提诺比率、回撤修复期。

### 填空题

索提诺比率只惩罚 \_\_\_\_ 波动，不惩罚 \_\_\_\_ 波动。

## 掌握检查
