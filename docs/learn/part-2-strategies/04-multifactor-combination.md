# 2.4 多因子组合

> 本章目标：把多个策略/因子组合成一个完整的投资组合——单因子有风险，多因子更稳健。

## 一句话

**多因子** = 不赌单一策略，而是让多个策略"投票"——东边不亮西边亮。

## 学习目标

学完本章你能：
- 理解多因子模型的基本架构（打分法 vs 回归法）
- 构建一个包含 3 个因子的简单多因子组合
- 用等权/风险平价两种方式分配因子权重

## 核心内容

### 1. 为什么需要多因子？

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('AAPL', start='2020-01-01', end='2024-12-31')
close = data['Adj Close']

# 两个单因子策略
def momentum_factor(close, window=60):
    """动量因子：过去收益"""
    return close.pct_change(window)

def value_factor(close, window=20):
    """价值因子：当前价格 vs 均线（便宜的回到均线以下）"""
    ma = close.rolling(window).mean()
    return (close - ma) / ma * -1  # 低于均线 = 高价值分

mom = momentum_factor(close)
val = value_factor(close)

# 因子之间的相关性
factor_corr = pd.concat([mom, val], axis=1).dropna()
factor_corr.columns = ['动量', '价值']
print("因子相关性:\n", factor_corr.corr())
```

**关键洞察：** 好的因子组合中，因子之间**相关性低**——一个因子亏钱的时候另一个赚。

### 2. 打分法——最简单的多因子

```python
import numpy as np
import pandas as pd

def score_stocks(close_df, factor_functions, weights=None):
    """
    多因子打分法
    
    对每只股票：
    1. 计算各因子得分
    2. 因子得分归一化（z-score）
    3. 加权求和得到总分
    4. 选总分最高的股票
    """
    if weights is None:
        weights = [1/len(factor_functions)] * len(factor_functions)
    
    total_score = pd.Series(0, index=close_df.columns)
    
    for func, weight in zip(factor_functions, weights):
        factor_scores = func(close_df)
        # 归一化
        zscore = (factor_scores - factor_scores.mean()) / factor_scores.std()
        total_score += weight * zscore
    
    return total_score.sort_values(ascending=False)

# 示例：对多只股票打分
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA']
multi_data = yf.download(tickers, start='2024-01-01', end='2024-12-31')['Adj Close']

# 两个因子
factors = [
    momentum_factor,  # 动量因子
    value_factor,     # 价值因子
]

scores = score_stocks(multi_data, factors, weights=[0.6, 0.4])
print("多因子打分排名:")
for rank, (ticker, score) in enumerate(scores.items(), 1):
    print(f"  {rank}. {ticker}: {score:.3f}")
```

### 3. 等权组合——多个策略的投票

```python
import numpy as np
import pandas as pd
import yfinance as yf

# 假设我们有3个策略，先分别回测
results = {}
for ticker in ['SPY']:
    d = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    c = d['Adj Close']
    r = c.pct_change()
    
    # 三个策略
    # 策略1: 动量
    s1 = momentum_strategy(c, 60, 20)  # 从2.1章
    
    # 策略2: 布林带
    from bollinger_strategy import bollinger_strategy as s2  # 假设已定义
    # 这里用简化版
    s2 = pd.Series(0, index=c.index)
    ma = c.rolling(20).mean()
    std = c.rolling(20).std()
    s2[c > ma + 2*std] = -1
    s2[c < ma - 2*std] = 1
    
    # 策略3: 海龟
    s3 = turtle_strategy(d['High'], d['Low'], c)  # 从2.1章
    
    # 等权组合
    combined_signal = (s1 + s2 + s3) / 3
    combo_rets = combined_signal.shift(1) * r
    
    results['strategy_1'] = (1 + s1.shift(1) * r).prod() - 1
    results['strategy_2'] = (1 + s2.shift(1) * r).prod() - 1
    results['strategy_3'] = (1 + s3.shift(1) * r).prod() - 1
    results['combined'] = (1 + combo_rets.dropna()).prod() - 1
    
    print("单策略 vs 组合收益:")
    for k, v in results.items():
        print(f"  {k}: {v:.2%}")
```

**关键点：** 组合的夏普比率通常高于任何一个单策略——这就是"分散化的免费午餐"。

### 4. 风险平价——更聪明的权重分配

等权分配风险，而不是分配资金：

```python
import numpy as np
import pandas as pd

def risk_parity_weights(returns_df):
    """
    风险平价：让每个策略贡献相等的风险
    
    简单实现：权重与历史波动率成反比
    """
    vols = returns_df.std()
    weights = (1 / vols) / (1 / vols).sum()
    return weights

# 模拟三个策略的收益率
np.random.seed(42)
strategy_rets = pd.DataFrame({
    '动量': np.random.normal(0.0005, 0.01, 500),
    '均值回归': np.random.normal(0.0003, 0.008, 500),
    '套利': np.random.normal(0.0004, 0.005, 500),
})

# 等权
equal_weight = np.array([1/3, 1/3, 1/3])
equal_portfolio = strategy_rets @ equal_weight

# 风险平价
rp_weights = risk_parity_weights(strategy_rets)
rp_portfolio = strategy_rets @ rp_weights

print(f"等权组合 夏普: {equal_portfolio.mean()/equal_portfolio.std() * np.sqrt(252):.2f}")
print(f"风险平价 夏普: {rp_portfolio.mean()/rp_portfolio.std() * np.sqrt(252):.2f}")
print(f"风险平价权重: {rp_weights.values.round(3)}")
```

### 5. 一个完整的多因子组合框架

```python
import numpy as np
import pandas as pd

class MultiFactorPortfolio:
    """多因子组合框架"""
    
    def __init__(self, factors: dict):
        """
        factors: {'因子名': (信号函数, 权重)}
        """
        self.factors = factors
    
    def generate_signals(self, data):
        """生成组合信号"""
        all_signals = []
        
        for name, (signal_func, weight) in self.factors.items():
            signal = signal_func(data)
            all_signals.append(signal * weight)
        
        combined = sum(all_signals)
        return combined / sum(w for _, w in self.factors.values())
    
    def backtest(self, data):
        """组合回测"""
        signal = self.generate_signals(data)
        close = data['Adj Close']
        returns = close.pct_change()
        strategy_rets = signal.shift(1) * returns
        cumulative = (1 + strategy_rets).cumprod()
        
        return {
            'signal': signal,
            'returns': strategy_rets,
            'equity': cumulative,
            'sharpe': strategy_rets.mean() / strategy_rets.std() * np.sqrt(252),
        }
```

## 深度阅读

## 练习

### 选择题

1. 多因子组合的核心优势是：
   - A. 每个因子都加倍赚钱
   - B. 因子间相关性低，分散风险
   - C. 减少交易次数
   - D. 降低手续费

2. 打分法中各因子的得分需要先：
   - A. 求平均值
   - B. 归一化（z-score或标准化）
   - C. 乘以交易量
   - D. 取绝对值

3. 风险平价的权重依据是：
   - A. 各策略的历史收益
   - B. 各策略的历史风险（波动率）
   - C. 投资者的主观判断
   - D. 各策略的夏普比率

4. 以下哪个是好的多因子组合？
   - A. 三个动量因子
   - B. 动量+均值回归+套利
   - C. 两个完全正相关的因子
   - D. 一个因子重复三次

5. 组合的夏普比率通常___每个单策略的夏普：
   - A. 低于
   - B. 高于
   - C. 等于
   - D. 不确定

### 编程题

**作业：** 构建一个由动量 + 布林带 + RSI 组成的三因子组合，在 SPY 上做回测。比较组合 vs 每个单因子的夏普比率和最大回撤。

### 填空题

多因子组合中，最好选择因子之间 \_\_\_\_ 越 \_\_\_\_（高/低）越好。

## 掌握检查
