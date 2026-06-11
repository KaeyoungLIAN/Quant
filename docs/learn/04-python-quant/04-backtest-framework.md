# 4.4 回测框架搭建

> 本章目标：写你的第一个完整回测——双均线交叉策略，理解回测的核心逻辑。

## 一句话

**回测** = 用历史数据模拟交易，看一个策略在过去能不能赚钱。

## 学习目标

学完本章你能：
- 理解回测的完整流程（数据 → 信号 → 交易 → 绩效）
- 写一个完整的双均线交叉策略回测
- 看懂回测曲线的含义
- 理解前视偏差的危害

## 核心内容

### 1. 回测的基本框架

```
数据 → 生成信号 → 模拟交易 → 计算绩效 → 分析
```

所有回测都遵循这个流程。你只需要定义"信号生成"那一步——剩下的框架是通用的。

```python
import pandas as pd
import numpy as np
import yfinance as yf

# ─── 1. 数据 ───
data = yf.download('AAPL', start='2023-01-01', end='2024-12-31')
close = data['Adj Close']

# ─── 2. 信号 ───
ma_short = close.rolling(20).mean()   # 短期均线
ma_long = close.rolling(60).mean()    # 长期均线

signal = pd.Series(0, index=close.index)
signal[ma_short > ma_long] = 1        # 多头持仓
signal[ma_short <= ma_long] = 0       # 空仓

# ─── 3. 模拟交易 ───
returns = close.pct_change()          # 每日收益率
strategy_returns = signal.shift(1) * returns  # 信号T+1执行

# ─── 4. 绩效 ───
cumulative = (1 + strategy_returns).cumprod()
buy_hold = (1 + returns).cumprod()

print(f"策略总收益: {cumulative.iloc[-1] - 1:.2%}")
print(f"买入持有总收益: {buy_hold.iloc[-1] - 1:.2%}")
```

**关键细节：** `signal.shift(1)` — 信号当天收盘生成，第二天才执行，避免前视偏差。

### 2. 理解前视偏差

前视偏差是回测中最常见也最致命的错误。

```python
# ❌ 错误！用了当天的信息
wrong_rets = signal * returns  # 信号和收益率同一天→作弊

# ✅ 正确！只能用前一天的信息
correct_rets = signal.shift(1) * returns
```

**规则：** 回测时你只能使用**今天之前**的信息来做交易决策。任何用"今天数据预测今天"的行为都是作弊。

### 3. 完整的回测函数

```python
def backtest_ma_crossover(data, short_win=20, long_win=60):
    """
    双均线交叉回测
    返回: DataFrame 含每日持仓和收益
    """
    close = data['Adj Close'].copy()
    
    # 信号
    ma_short = close.rolling(short_win).mean()
    ma_long = close.rolling(long_win).mean()
    
    positions = pd.Series(0, index=close.index)
    positions[ma_short > ma_long] = 1
    
    # 交易
    returns = close.pct_change()
    strategy_rets = positions.shift(1) * returns
    
    # 统计
    total_return = (1 + strategy_rets).prod() - 1
    buy_hold_return = (1 + returns).prod() - 1
    n_trades = (positions.diff().abs() > 0).sum() // 2  # 开平各算一次
    
    return {
        'total_return': total_return,
        'buy_hold_return': buy_hold_return,
        'n_trades': n_trades,
        'strategy_returns': strategy_rets,
        'positions': positions,
    }

# 测试 AAPL
result = backtest_ma_crossover(data)
print(f"均线(20,60) 在 AAPL 上的表现:")
print(f"  策略收益: {result['total_return']:.2%}")
print(f"  买入持有: {result['buy_hold_return']:.2%}")
print(f"  交易次数: {result['n_trades']}")
```

### 4. 可视化回测曲线

```python
import matplotlib.pyplot as plt

strategy_curve = (1 + result['strategy_returns']).cumprod()
buy_hold_curve = (1 + data['Adj Close'].pct_change()).cumprod()

plt.figure(figsize=(12, 6))
plt.plot(strategy_curve.index, strategy_curve, label='策略', linewidth=2)
plt.plot(buy_hold_curve.index, buy_hold_curve, label='买入持有', linewidth=1, alpha=0.7)
plt.plot(result['positions'] * strategy_curve.iloc[-1], 
         label='持仓信号', alpha=0.3, color='gray')
plt.title('AAPL 双均线策略回测')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### 5. 参数敏感性测试

不同的参数组合效果天差地别：

```python
results = []
for short_win in [5, 10, 20, 30, 50]:
    for long_win in [30, 60, 90, 120]:
        r = backtest_ma_crossover(data, short_win, long_win)
        results.append({
            'short': short_win,
            'long': long_win,
            'return': r['total_return'],
            'trades': r['n_trades'],
        })

results_df = pd.DataFrame(results)
print("最快几组参数:")
print(results_df.sort_values('return', ascending=False).head(5))
```

**关键洞察：** 参数调优第一次就出好结果？90% 是因为过拟合。牢记：**参数只是故事的配角，逻辑才是主角**。

## 深度阅读

## 练习

### 选择题

1. 回测中 `signal.shift(1)` 的目的是：
   - A. 提高信号准确率
   - B. 避免前视偏差
   - C. 减少交易次数
   - D. 美化收益曲线

2. 以下哪个是前视偏差的表现？
   - A. 用今天的收盘价作为今天的交易信号
   - B. 用昨天的成交量过滤今天的信号
   - C. 去除停牌日的数据
   - D. 使用复权价格

3. 双均线交叉策略中，`short_win=20, long_win=60` 意味着：
   - A. 20日均线上穿60日均线时买入
   - B. 60日均线上穿20日均线时买入
   - C. 价格突破20日均线时买入
   - D. 成交量放大时买入

4. 策略收益 > 买入持有收益说明：
   - A. 策略一定有效
   - B. 在这个时间段内策略跑赢了基准
   - C. 策略没有交易成本
   - D. 策略适用于所有股票

5. 回测中交易次数越少，通常：
   - A. 策略越好
   - B. 策略越简单
   - C. 滑点成本越低
   - D. B 和 C

### 编程题

**题目：** 在双均线策略基础上加一个**成交量过滤**——只有当 20 日均量高于过去 60 日均量时（放量），才执行信号。

```python
def backtest_ma_with_volume(data, short_win=20, long_win=60):
    """
    含成交量过滤的双均线策略
    额外条件：成交量 > 60日均量 才开仓
    """
    close = data['Adj Close']
    volume = data['Volume']
    
    # 你的代码：均线信号 + 成交量过滤
    
    pass
```

### 填空题

在回测中，`signal` 要在第 \\_\\_\\_\\_ 天执行，所以代码需要 `signal.shift(1)` 来对齐。

## 掌握检查
