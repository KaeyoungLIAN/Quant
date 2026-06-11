# 6.4 过拟合检测与策略诊断

> 本章目标：识别并避免量化回测中最隐蔽的敌人——过拟合，并学会系统性地诊断策略问题。

## 一句话

**过拟合** = 你的策略记住了历史走势而不是学到规律——回测漂亮，实盘崩溃。

## 学习目标

学完本章你能：
- 识别过拟合的信号（参数敏感度、数据窥探）
- 用交叉验证方法评估策略的真实稳健性
- 理解"样本外测试"为什么是最重要的防线

## 核心内容

### 1. 过拟合是什么？

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('SPY', start='2015-01-01', end='2024-12-31')
close = data['Adj Close']

# 演示过拟合：随机数据上"找到"一个策略
np.random.seed(42)
random_returns = np.random.randn(1000) * 0.01  # 纯随机

# 找50个参数组合，选最好的
best_sharpe = -999
for i in range(50):
    threshold = np.random.uniform(0.5, 0.7)  # 随机阈值
    signal = np.where(np.abs(random_returns) > threshold, 
                      np.sign(random_returns), 0)
    strategy_rets = signal * random_returns
    sharpe = strategy_rets.mean() / strategy_rets.std() * np.sqrt(252)
    if sharpe > best_sharpe:
        best_sharpe = sharpe

print(f"50次随机参数中的最佳夏普: {best_sharpe:.2f}")
print(f"结论: 在纯随机数据上也能找到夏普>1的策略→过拟合!")
```

**这是每个量化新手的陷阱：** 参数调得越多，越容易"记住"数据中的噪声。

### 2. 样本内 vs 样本外

```python
import numpy as np
import pandas as pd

def train_test_backtest(close, train_ratio=0.7):
    """分割样本内/样本外测试策略"""
    n = len(close)
    split = int(n * train_ratio)
    
    train_close = close.iloc[:split]
    test_close = close.iloc[split:]
    
    # 在训练集上"调"参数（这里用固定参数）
    train_rets = train_close.pct_change()
    test_rets = test_close.pct_change()
    
    # 信号（在训练集上生成，在测试集上验证）
    ma_short = train_close.rolling(20).mean()
    ma_long = train_close.rolling(60).mean()
    train_signal = pd.Series(0, index=train_close.index)
    train_signal[ma_short > ma_long] = 1
    
    # 测试集上用训练集的最后一个信号？
    # ❌ 不对！测试集应该独立回测
    test_ma_short = test_close.rolling(20).mean()
    test_ma_long = test_close.rolling(60).mean()
    test_signal = pd.Series(0, index=test_close.index)
    test_signal[test_ma_short > test_ma_long] = 1
    
    train_strat = train_signal.shift(1) * train_rets
    test_strat = test_signal.shift(1) * test_rets
    
    train_sharpe = train_strat.mean() / train_strat.std() * np.sqrt(252)
    test_sharpe = test_strat.mean() / test_strat.std() * np.sqrt(252)
    
    print(f"样本内夏普: {train_sharpe:.2f}")
    print(f"样本外夏普: {test_sharpe:.2f}")
    print(f"差异: {train_sharpe - test_sharpe:.2f} {'⚠️ 可能过拟合' if test_sharpe < train_sharpe - 0.5 else '✅ 稳健'}")

train_test_backtest(close)
```

**黄金法则：** 样本外夏普是唯一的真相。如果样本内夏普 2.0，样本外 0.3——你的策略是垃圾。

### 3. 交叉验证（滚动窗口）

```python
import numpy as np
import pandas as pd

def walk_forward_cv(close, n_splits=5):
    """
    滚动交叉验证
    每次用前2年训练，后1年验证
    """
    total_len = len(close)
    split_size = total_len // n_splits
    
    test_sharpes = []
    
    for i in range(n_splits):
        train_end = split_size * (i + 1) - split_size // 2
        test_start = train_end
        test_end = min(train_end + split_size // 2, total_len)
        
        if test_end <= test_start:
            continue
        
        train = close.iloc[:train_end]
        test = close.iloc[test_start:test_end]
        
        # 训练集上回测
        train_rets = train.pct_change()
        ma_s = train.rolling(20).mean()
        ma_l = train.rolling(60).mean()
        train_sig = pd.Series(0, index=train.index)
        train_sig[ma_s > ma_l] = 1
        train_strat = train_sig.shift(1) * train_rets
        
        # 测试集上验证
        test_rets = test.pct_change()
        test_ma_s = test.rolling(20).mean()
        test_ma_l = test.rolling(60).mean()
        test_sig = pd.Series(0, index=test.index)
        test_sig[test_ma_s > test_ma_l] = 1
        test_strat = test_sig.shift(1) * test_rets
        
        test_sharpes.append(
            test_strat.mean() / test_strat.std() * np.sqrt(252)
        )
    
    test_sharpes = pd.Series([s for s in test_sharpes if not np.isnan(s)])
    print(f"各期样本外夏普: {test_sharpes.values.round(2)}")
    print(f"平均样本外夏普: {test_sharpes.mean():.2f}")
    print(f"夏普标准差: {test_sharpes.std():.2f}")
    print(f"结论: {'✅ 稳健' if test_sharpes.mean() > 0.5 else '⚠️ 不稳定'}")

walk_forward_cv(close)
```

### 4. 过拟合的四个预警信号

```python
import numpy as np
import pandas as pd

def overfitting_warning(close):
    """过拟合预警检查"""
    warnings = []
    
    # 1. 参数敏感度
    results = []
    for s in [10, 20, 30, 50, 100]:
        for l in [30, 60, 90, 120, 200]:
            ma_s = close.rolling(s).mean()
            ma_l = close.rolling(l).mean()
            sig = pd.Series(0, index=close.index)
            sig[ma_s > ma_l] = 1
            rets = close.pct_change()
            strat = sig.shift(1) * rets
            sr = strat.mean() / strat.std() * np.sqrt(252)
            results.append((s, l, sr))
    
    sharpes = [r[2] for r in results]
    sharpe_range = max(sharpes) - min(sharpes)
    if sharpe_range > 2:
        warnings.append(f"参数高度敏感（夏普范围: {sharpe_range:.2f}）")
    
    # 2. 样本外显著下降
    # （见上面的 walk_forward）
    
    # 3. 交易频率过低
    sig = pd.Series(0, index=close.index)
    ma_s = close.rolling(20).mean()
    ma_l = close.rolling(60).mean()
    sig[ma_s > ma_l] = 1
    n_trades = (sig.diff().abs() > 0).sum() // 2
    if n_trades < 10:
        warnings.append(f"交易次数太少（{n_trades}笔），统计不可靠")
    
    # 4. 单一时间段表现
    total_ret = (1 + (sig.shift(1) * close.pct_change())).prod() - 1
    half = len(close) // 2
    first_half = (1 + (sig.shift(1) * close.pct_change())).iloc[:half].prod() - 1
    second_half = (1 + (sig.shift(1) * close.pct_change())).iloc[half:].prod() - 1
    
    if (first_half > 0) != (second_half > 0):
        warnings.append("前后半段收益方向不同，可能是过拟合")
    
    if warnings:
        print("⚠️ 过拟合预警:")
        for w in warnings:
            print(f"  • {w}")
    else:
        print("✅ 未检测到明显过拟合")
    
    return warnings

overfitting_warning(close)
```

### 5. 策略诊断：当一个策略表现不好时

```python
import numpy as np
import pandas as pd

def strategy_checklist(strategy_rets, signal, returns):
    """
    策略诊断清单
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
    
    if not issues:
        issues.append("✅ 策略通过基本诊断")
    
    for issue in issues:
        print(issue)
    return issues
```

### 6. 什么时候该放弃？

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

- Wiki → [过拟合检测](/quant-finance/3.0-overfitting)
- Wiki → [策略诊断](/quant-finance/3.2-strategy-diagnosis)

## 练习

### 选择题

1. 过拟合的直接表现是：
   - A. 样本内夏普 2.0，样本外夏普 0.3
   - B. 样本内夏普 0.8，样本外夏普 0.7
   - C. 两个都高
   - D. 两个都低

2. 减少过拟合最有效的做法是：
   - A. 用更多数据
   - B. 用更少参数
   - C. 做样本外测试
   - D. 以上都是

3. 滚动交叉验证的好处是：
   - A. 只需要一个数据集
   - B. 测试策略在不同市场环境下的稳定性
   - C. 总能得到高夏普
   - D. 不需要清洗数据

4. "数据窥探偏差"指的是：
   - A. 数据质量有问题
   - B. 反复在同一个数据集上调参数，直到找到"好"的
   - C. 数据泄露
   - D. 使用了未来数据

### 编程题

**作业：** 选择一个策略（如 2.1 的海龟策略），做 5 折滚动交叉验证，报告每折的样本外夏普。

### 填空题

样本外夏普是指数在模型训练时 \_\_\_\_ 使用过的数据上计算得到的夏普比率。

## 掌握检查
