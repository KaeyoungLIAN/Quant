# 1.3 绩效指标：夏普·回撤·胜率

> 本章目标：掌握一个策略好不好的衡量标准——不再凭感觉判断策略。

## 一句话

只看收益率是赌博思维，量化思维看的是：**收益 / 风险**。

## 学习目标

学完本章你能：
- 计算并解释夏普比率、最大回撤、卡玛比率
- 判断一个策略的收益是否"配得上它的风险"
- 从回测报告中识别策略的优缺点

## 核心内容

### 1. 夏普比率——收益/风险比

夏普比率是量化里最常用的指标：**每承受一单位风险，获得多少超额收益**。

$$\text{Sharpe} = \frac{E(R_p - R_f)}{\sigma_p}$$

量化里通常简化为：$$\text{Sharpe} \approx \frac{\text{年化收益率}}{\text{年化波动率}}$$

```python
import numpy as np
import pandas as pd
import yfinance as yf

def sharpe_ratio(returns, risk_free=0.03):
    """
    计算年化夏普比率
    returns: 日收益率序列
    risk_free: 无风险利率（默认 3%，年化）
    """
    daily_rf = risk_free / 252
    excess_returns = returns - daily_rf
    annualized_return = excess_returns.mean() * 252
    annualized_vol = returns.std() * np.sqrt(252)
    return annualized_return / annualized_vol if annualized_vol > 0 else 0

# 从上一章的回测结果计算
data = yf.download('AAPL', start='2023-01-01', end='2024-12-31')
close = data['Adj Close']

# 回测
ma_short = close.rolling(20).mean()
ma_long = close.rolling(60).mean()
signal = pd.Series(0, index=close.index)
signal[ma_short > ma_long] = 1

returns = close.pct_change()
strategy_rets = signal.shift(1) * returns

sr = sharpe_ratio(strategy_rets.dropna())
print(f"策略夏普比率: {sr:.2f}")
print(f"解释: 每承受1%的波动，获得{sr:.2f}%的超额收益")

# 夏普比率参考
# < 0.5   一般
# 0.5 - 1.0   可接受
# 1.0 - 2.0   优秀
# > 2.0    极为出色（但要注意可能过拟合）
```

### 2. 最大回撤——最坏情况

夏普只告诉平均表现，最大回撤告诉你**在最倒霉的时候亏多少**——这对心理承受力至关重要。

```python
def max_drawdown(equity_curve):
    """
    计算最大回撤（从峰值跌倒谷底的最大跌幅）
    equity_curve: 净值曲线（从1开始）
    """
    peak = equity_curve.expanding().max()  # 到每个时刻的历史最高
    drawdown = (equity_curve - peak) / peak  # 回撤幅度
    max_dd = drawdown.min()  # 最大回撤（负数）
    
    # 找出回撤区间
    dd_end = drawdown.idxmin()  # 回撤最低点日期
    dd_start = drawdown[:dd_end].idxmax()  # 回撤起点日期
    
    return max_dd, dd_start, dd_end

# 计算净值曲线
equity = (1 + strategy_rets).cumprod()
mdd, dd_start, dd_end = max_drawdown(equity)

print(f"最大回撤: {mdd:.2%}")
print(f"开始日期: {dd_start.date()}")
print(f"结束日期: {dd_end.date()}")

# 回撤修复期（从最低点回到前高的天数）
recovery = equity[dd_end:].expanding().max()
recovery_days = len(recovery[recovery < peak.loc[dd_start]])
print(f"回撤修复期: {recovery_days} 天")
```

**关键直觉：** 一个最大回撤 30% 但最终收益 50% 的策略，和一个最大回撤 5% 收益 15% 的策略——后者对大多数人来说更"好"。

### 3. 卡玛比率——夏普的"保守版"

$$\text{Calmar} = \frac{\text{年化收益率}}{|\text{最大回撤}|}$$

```python
def calmar_ratio(returns, equity_curve):
    annual_return = returns.mean() * 252
    mdd, _, _ = max_drawdown(equity_curve)
    return annual_return / abs(mdd) if mdd != 0 else 0

cr = calmar_ratio(strategy_rets.dropna(), equity)
print(f"卡玛比率: {cr:.2f}")
# 一般 > 1 就算不错，> 2 很优秀
```

### 4. 胜率·盈亏比·期望值

这三个指标一起告诉你每笔交易的质量。

```python
def trade_stats(signal, returns):
    """分析每笔交易"""
    # 找到开仓和平仓日
    position_changes = signal.diff().fillna(0)
    entries = position_changes[position_changes == 1].index
    exits = position_changes[position_changes == -1].index
    
    # 计算每笔交易收益
    trade_returns = []
    for entry, exit_ in zip(entries, exits):
        trade_rets = returns[entry:exit_].sum()  # 简单累加
        trade_returns.append(trade_rets)
    
    trade_returns = pd.Series(trade_returns)
    wins = trade_returns[trade_returns > 0]
    losses = trade_returns[trade_returns < 0]
    
    print(f"总交易次数: {len(trade_returns)}")
    print(f"胜率: {len(wins) / len(trade_returns):.1%}")
    print(f"平均盈利: {wins.mean():.2%}" if len(wins) > 0 else "平均盈利: N/A")
    print(f"平均亏损: {losses.mean():.2%}" if len(losses) > 0 else "平均亏损: N/A")
    
    # 盈亏比
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 1
    profit_ratio = avg_win / avg_loss
    print(f"盈亏比: {profit_ratio:.2f}")
    
    # 期望值 E = 胜率×平均盈利 - 败率×平均亏损
    win_rate = len(wins) / len(trade_returns) if len(trade_returns) > 0 else 0
    expected_return = win_rate * avg_win - (1 - win_rate) * abs(losses.mean())
    print(f"每笔交易期望值: {expected_return:.4%}")
    
    return {
        'n_trades': len(trade_returns),
        'win_rate': win_rate,
        'profit_ratio': profit_ratio,
        'expected_return': expected_return,
    }

trade_stats(signal, returns)
```

### 5. 完整的绩效报告

```python
def performance_report(strategy_rets, equity_curve):
    """打印完整的策略绩效报告"""
    ret = strategy_rets.dropna()
    ann_ret = ret.mean() * 252
    ann_vol = ret.std() * np.sqrt(252)
    sr = sharpe_ratio(ret)
    mdd, dd_s, dd_e = max_drawdown(equity_curve)
    cr = calmar_ratio(ret, equity_curve)
    
    print("=" * 40)
    print("       策略绩效报告")
    print("=" * 40)
    print(f"年化收益率:     {ann_ret:.2%}")
    print(f"年化波动率:     {ann_vol:.2%}")
    print(f"夏普比率:       {sr:.2f}")
    print(f"最大回撤:       {mdd:.2%}")
    print(f"卡玛比率:       {cr:.2f}")
    print(f"正收益天数:     {(ret > 0).sum()} / {len(ret)} ({(ret > 0).mean():.1%})")
    print(f"最大单日涨幅:   {ret.max():.2%}")
    print(f"最大单日跌幅:   {ret.min():.2%}")
    print("=" * 40)

performance_report(strategy_rets, equity)
```

### 指标对比速查

| 指标 | 衡量什么 | 理想值 | 局限性 |
|------|---------|--------|--------|
| 夏普比率 | 收益/波动率 | > 1.0 | 不区分上涨/下跌波动 |
| 最大回撤 | 最坏亏损 | 越小越好 | 依赖数据区间 |
| 卡玛比率 | 收益/最大回撤 | > 1.0 | 对回撤期间的收益不敏感 |
| 胜率 | 赚钱交易比例 | > 50% | 可能赢小输大 |
| 盈亏比 | 平均盈利/亏损 | > 2.0 | 样本少时不稳定 |

## 深度阅读

- Wiki → [夏普比率详解](/quant-finance/2.2-sharpe-ratio)

## 练习

### 选择题

1. 夏普比率为 1.5 意味着：
   - A. 策略绝对收益 150%
   - B. 每单位风险获得 1.5 单位超额收益
   - C. 有 150% 的概率赚钱
   - D. 最大回撤 1.5%

2. 最大回撤的计算基础是：
   - A. 年初到年底的跌幅
   - B. 历史最高点到最低点的跌幅
   - C. 平均亏损
   - D. 年化波动率

3. 以下哪个策略更"稳健"？
   - A. 夏普 1.2，最大回撤 25%
   - B. 夏普 0.8，最大回撤 8%
   - C. 夏普 2.0，最大回撤 40%
   - D. 夏普 0.5，最大回撤 3%

4. 盈亏比 3.0，胜率 40%——期望值是正还是负？
   - A. 正（因为赢的时候赚得多）
   - B. 负（因为输的次数多）
   - C. 不确定
   - D. 等于零

5. 卡玛比率的公式是：
   - A. 夏普比率 × 交易次数
   - B. 年化收益 / |最大回撤|
   - C. 总收益 / 最大回撤
   - D. 波动率 / 最大回撤

### 编程题

**题目：** 写一个函数 `walk_forward_sharpe(rets, train_window=504, test_window=63)`——用滚动窗口计算样本外夏普比率。每次用前 2 年（504 天）数据估算策略参数，在后 63 天（1 季度）上计算夏普，然后滑动。

```python
def walk_forward_sharpe(rets, train_window=504, test_window=63):
    # 你的代码
    pass

# 测试
rets = strategy_rets.dropna()
wf_sharpes = walk_forward_sharpe(rets)
print(f"平均样本外夏普: {np.mean(wf_sharpes):.2f}")
print(f"夏普标准差: {np.std(wf_sharpes):.2f}")
```

### 填空题

如果胜率 60%，平均盈利 2%，平均亏损 3%，每笔交易的期望收益是 \_\_\_\_%。

（计算公式：0.6 × 2% - 0.4 × 3%）

## 掌握检查
