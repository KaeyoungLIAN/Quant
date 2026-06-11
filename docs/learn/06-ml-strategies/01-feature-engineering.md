# 6.1 特征工程

> 本章目标：从原始量价数据中提取可用于 ML 模型的特征——好特征比好模型更重要。

## 一句话

**特征工程** = 把价格和成交量变成模型能"读懂"的信号——趋势、波动、形态、关系。

## 学习目标

学完本章你能：
- 从 OHLCV 数据中提取技术指标作为特征
- 理解特征选择的基本原则（相关性、稳定性、可解释性）
- 构建一个用于预测未来收益的特征矩阵

## 核心内容

### 1. 特征 vs 原始数据

```python
import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download('SPY', start='2015-01-01', end='2024-12-31')
close = data['Adj Close']
high = data['High']
low = data['Low']
volume = data['Volume']

# 原始数据本身不适合做 ML 特征——价格不平稳
# 我们需要"变换"它们

# 好的特征类别：
features = pd.DataFrame(index=close.index)

# 1. 收益率
features['ret_1d'] = close.pct_change(1)
features['ret_5d'] = close.pct_change(5)
features['ret_20d'] = close.pct_change(20)

# 2. 波动率
features['vol_10d'] = features['ret_1d'].rolling(10).std()
features['vol_60d'] = features['ret_1d'].rolling(60).std()

# 3. 成交量特征
features['volume_ratio'] = volume / volume.rolling(20).mean()  # 量比
features['dollar_volume'] = close * volume  # 成交额

# 4. 价格位置
ma_20 = close.rolling(20).mean()
features['price_to_ma20'] = close / ma_20 - 1  # 偏离均线的比例
features['high_low_range'] = (high - low) / close  # 日内振幅

print("特征矩阵:", features.shape)
print(features.dropna().head())
```

### 2. 特征构建实战

```python
import numpy as np
import pandas as pd

def build_features(data):
    """从 OHLCV 构建完整特征集"""
    close = data['Adj Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']
    open_ = data['Open']
    
    df = pd.DataFrame(index=close.index)
    
    # 动量类
    for d in [1, 2, 5, 10, 21, 63]:
        df[f'mom_{d}d'] = close.pct_change(d)
    
    # 波动类
    ret_1d = close.pct_change()
    for d in [5, 10, 21, 63]:
        df[f'vol_{d}d'] = ret_1d.rolling(d).std()
        df[f'skew_{d}d'] = ret_1d.rolling(d).skew()  # 偏度
        df[f'kurt_{d}d'] = ret_1d.rolling(d).kurt()   # 峰度
    
    # 成交量类
    df['volume_ma_ratio_5'] = volume / volume.rolling(5).mean()
    df['volume_ma_ratio_20'] = volume / volume.rolling(20).mean()
    df['dollar_volume'] = close * volume
    
    # 价格形态类
    df['high_low_pct'] = (high - low) / close
    df['close_open_pct'] = (close - open_) / open_
    df['upper_shadow'] = (high - close.max(1)) / close  # 上影线
    
    # 均线偏离
    for d in [5, 10, 20, 60, 120]:
        ma = close.rolling(d).mean()
        df[f'dist_ma_{d}'] = (close - ma) / ma
    
    # 滚动相关系数
    df['vol_corr'] = ret_1d.rolling(20).corr(volume.pct_change())
    
    return df

features = build_features(data)
print(f"特征数: {features.shape[1]}")
print(features.columns.tolist())
```

### 3. 标签定义——预测什么？

```python
import numpy as np
import pandas as pd

# 我们想预测未来 N 天的收益率
def create_labels(close, forward_days=5):
    """创建预测标签"""
    forward_ret = close.shift(-forward_days) / close - 1
    return forward_ret

# 三种常见标签
labels_1d = close.shift(-1) / close - 1      # 预测明天
labels_5d = close.shift(-5) / close - 1       # 预测未来一周
labels_21d = close.shift(-21) / close - 1     # 预测未来一个月

# 分类标签（涨/跌）
labels_class = (labels_5d > 0).astype(int)     # 5天后涨=1，跌=0

print(f"涨跌比例: {labels_class.value_counts(normalize=True)}")
```

### 4. 特征选择——用哪些不用哪些？

```python
import numpy as np
import pandas as pd

def select_features(features, labels, threshold=0.01):
    """
    简单特征选择：去掉与目标相关性太低的特征
    """
    combined = pd.concat([features, labels], axis=1).dropna()
    X = combined.iloc[:, :-1]
    y = combined.iloc[:, -1]
    
    correlations = X.corrwith(y).abs().sort_values(ascending=False)
    selected = correlations[correlations > threshold]
    
    print(f"原始特征数: {X.shape[1]}")
    print(f"选择后特征数: {len(selected)}")
    print("\nTop 10 最相关的特征:")
    print(selected.head(10).to_string())
    
    return selected.index.tolist()

# 示例
features_clean = features.dropna()
labels_5d = close.shift(-5).loc[features_clean.index] / features_clean.index.to_series().apply(
    lambda x: close.loc[x] if x in close.index else np.nan
) - 1
```

### 5. 特征稳定性——过去有效将来还有效吗？

```python
import numpy as np
import pandas as pd

def feature_stability(features, labels):
    """
    检查特征有效性的时间稳定性
    """
    n = len(features)
    half = n // 2
    
    # 前半段相关性
    corr_first = features.iloc[:half].corrwith(labels.iloc[:half])
    # 后半段相关性
    corr_second = features.iloc[half:].corrwith(labels.iloc[half:])
    
    stability = pd.DataFrame({
        'first_half': corr_first,
        'second_half': corr_second,
        'change': corr_second - corr_first,
    }).dropna()
    
    print("最不稳定的 5 个特征（相关性变化最大）:")
    print(stability.sort_values('change', key=abs, ascending=False).head(5))
    
    print("\n最稳定的 5 个特征:")
    print(stability.sort_values('change', key=abs).head(5))

# 注意：这里用 SPY 的特征和未来收益做示例很粗糙
# 真实场景中应该用截面数据（多只股票的同一时间点）
```

## 深度阅读

## 练习

### 选择题

1. 以下哪个不是良好的 ML 特征？
   - A. 过去 5 天的收益率
   - B. 股票名称
   - C. 滚动波动率
   - D. 成交量比

2. 为什么原始价格不适合直接做特征？
   - A. 价格不平稳
   - B. 价格变化无常
   - C. 价格非负
   - D. 原因 A

3. 标签 `shift(-5)` 的含义是：
   - A. 用过去 5 天预测未来
   - B. 预测未来 5 天后的收益
   - C. 回溯 5 天的收益
   - D. 滚动 5 天窗口

4. 特征选择的主要目的是：
   - A. 减少计算量
   - B. 去掉无关/噪声特征，提高模型泛化能力
   - C. 增加特征数量
   - D. 让模型更复杂

### 编程题

**作业：** 对 TSLA 构建特征集（动量类+波动类+成交量类），创建 5 日未来收益率标签，计算特征与标签的相关性排名。

### 填空题

好的特征应该具有 \_\_\_\_ 性（在不同时间段表现相似），而不好的特征只在某段历史中有效。

## 掌握检查
