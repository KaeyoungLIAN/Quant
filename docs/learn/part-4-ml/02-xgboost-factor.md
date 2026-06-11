# 4.2 XGBoost 因子

> 本章目标：用 XGBoost 从特征中学习"什么样的情况下涨的概率高"——将 ML 预测转化为交易信号。

## 一句话

**XGBoost 因子** = 让树模型学习历史模式，然后用它的预测值作为选股/择时信号。

## 学习目标

学完本章你能：
- 理解 XGBoost 的基本原理（梯度提升 + 决策树）
- 用 XGBoost 训练一个分类模型预测涨跌
- 将模型输出转化为可交易因子

## 核心内容

### 1. XGBoost 直观理解

```python
"""
XGBoost 的本质：

1. 第一棵树：学一个"大致正确"的模型
2. 第二棵树：专注学第一棵树"错"的地方
3. 第三棵树：专注学前两棵树"错"的地方
...
N. 最终的预测 = 所有树的预测之和

你不需要理解数学细节（虽然很简单），只需要知道：
- XGBoost = 很多棵小树合作投票
- 每棵新树专注于修补之前的错误
- 结果是训练集上效果很好，但需要防过拟合
"""
```

### 2. 数据准备

```python
import numpy as np
import pandas as pd
import yfinance as yf
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# 加载数据
data = yf.download('SPY', start='2015-01-01', end='2024-12-31')
close = data['Adj Close']

# 构建特征（复用 4.1 的函数）
def build_features(data):
    close = data['Adj Close']
    volume = data['Volume']
    high = data['High']
    low = data['Low']
    open_ = data['Open']
    
    df = pd.DataFrame(index=close.index)
    ret_1d = close.pct_change()
    
    for d in [1, 2, 5, 10, 21]:
        df[f'mom_{d}d'] = close.pct_change(d)
    for d in [5, 10, 21, 63]:
        df[f'vol_{d}d'] = ret_1d.rolling(d).std()
    df['volume_ratio'] = volume / volume.rolling(20).mean()
    df['high_low'] = (high - low) / close
    df['close_open'] = (close - open_) / open_
    for d in [5, 10, 20, 60]:
        ma = close.rolling(d).mean()
        df[f'dist_ma_{d}'] = (close - ma) / ma
    
    return df

features = build_features(data)

# 创建标签：未来5天涨=1，跌=0
future_ret = close.shift(-5) / close - 1
labels = (future_ret > 0).astype(int)

# 对齐并删除 NaN
combined = pd.concat([features, labels.rename('label')], axis=1).dropna()
X = combined.drop('label', axis=1)
y = combined['label']

print(f"样本数: {len(X)}, 特征数: {X.shape[1]}")
print(f"涨跌比例:\n{y.value_counts(normalize=True)}")
```

### 3. 训练 XGBoost 模型

```python
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# 时间序列分割（不能用随机分割！）
split_idx = int(len(X) * 0.8)
X_train = X.iloc[:split_idx]
X_test = X.iloc[split_idx:]
y_train = y.iloc[:split_idx]
y_test = y.iloc[split_idx:]

print(f"训练集: {len(X_train)} ({X_train.index[0].date()} ~ {X_train.index[-1].date()})")
print(f"测试集: {len(X_test)} ({X_test.index[0].date()} ~ {X_test.index[-1].date()})")

# 训练 XGBoost
model = XGBClassifier(
    n_estimators=100,        # 100棵树
    max_depth=3,             # 每棵树最多3层（防止过拟合）
    learning_rate=0.1,       # 学习率
    subsample=0.8,           # 每棵树只用80%的样本
    colsample_bytree=0.8,    # 每棵树只用80%的特征
    random_state=42,
    eval_metric='logloss',
)

model.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False
)

# 预测
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # 上涨概率

accuracy = accuracy_score(y_test, y_pred)
print(f"测试集准确率: {accuracy:.2%}")

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
print(f"混淆矩阵:\n{cm}")
print(f"真正例（正确预测涨）: {cm[1,1]}")
print(f"假正例（误报涨）: {cm[0,1]}")
```

**关键理解：** 准确率略高于 50% 就很好了——如果模型能做到 55%，意味着它找到了微弱但真实的预测信号。

### 4. 特征重要性——模型在"看"什么

```python
import numpy as np
import pandas as pd

# 特征重要性
importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_,
}).sort_values('importance', ascending=False)

print("Top 10 最重要的特征:")
print(importance.head(10).to_string(index=False))
```

### 5. 将模型预测转化为因子/信号

```python
import numpy as np
import pandas as pd

# 在测试集上生成交易信号
test_signal = pd.Series(0, index=X_test.index)
test_signal[y_prob > 0.55] = 1     # 上涨概率 > 55% → 做多
test_signal[y_prob < 0.45] = -1    # 上涨概率 < 45% → 做空

# 回测
test_returns = close.pct_change().loc[y_prob.index]
strategy_rets = test_signal.shift(1) * test_returns

cumulative = (1 + strategy_rets.dropna()).cumprod()
print(f"XGBoost 因子收益: {cumulative.iloc[-1] - 1:.2%}")

# 对比买入持有
bh_ret = close.pct_change().loc[y_prob.index]
bh_cum = (1 + bh_ret).cumprod()
print(f"买入持有: {bh_cum.iloc[-1] - 1:.2%}")
```

### 6. 超参数调优

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterGrid
from xgboost import XGBClassifier
from scipy.stats import spearmanr

# 用时间序列交叉验证调参
def ts_cv_score(X, y, params, n_splits=3):
    """时间序列交叉验证"""
    n = len(X)
    fold_size = n // n_splits
    scores = []
    
    for i in range(n_splits - 1, n_splits):
        train_end = fold_size * (i + 1)
        if train_end >= n:
            break
        
        X_tr = X.iloc[:train_end]
        y_tr = y.iloc[:train_end]
        X_te = X.iloc[train_end:min(train_end + fold_size, n)]
        y_te = y.iloc[train_end:min(train_end + fold_size, n)]
        
        if len(X_te) < 10:
            continue
        
        model = XGBClassifier(**params, random_state=42, eval_metric='logloss')
        model.fit(X_tr, y_tr, verbose=False)
        y_prob = model.predict_proba(X_te)[:, 1]
        
        # 用 Information Coefficient 衡量
        ic, _ = spearmanr(y_prob, y_te)
        scores.append(ic)
    
    return np.mean(scores) if scores else 0

# 简单调参示例
param_grid = {
    'max_depth': [2, 3, 4],
    'learning_rate': [0.05, 0.1],
    'n_estimators': [50, 100],
}

best_score = -999
best_params = None

for params in ParameterGrid(param_grid):
    score = ts_cv_score(X_train, y_train, params)
    if score > best_score:
        best_score = score
        best_params = params

print(f"最佳参数: {best_params}")
print(f"最佳 IC: {best_score:.4f}")
```

## 深度阅读

## 练习

### 选择题

1. XGBoost 的核心思想是：
   - A. 随机森林的改进版
   - B. 多棵树串行训练，每棵修正前一棵的错误
   - C. 单棵决策树
   - D. 支持向量机

2. 为什么时间序列数据不能用随机分割？
   - A. 防止信息从未来泄露到过去（前视偏差）
   - B. 计算更方便
   - C. 代码更简单
   - D. 不需要分割

3. XGBoost 中 `max_depth=3` 的作用是：
   - A. 提高训练速度
   - B. 防止过拟合（树不要太复杂）
   - C. 降低内存使用
   - D. 以上都是

4. Information Coefficient (IC) 衡量的是：
   - A. 预测准确率
   - B. 预测值排序与实际值排序的相关性
   - C. 特征数量
   - D. 训练时间

### 编程题

**作业：** 用 AAPL 数据训练 XGBoost 分类器（预测 5 天后的涨跌），做时间序列 80/20 分割。报告测试集准确率、IC、并将模型预测转化为交易信号做回测。

### 填空题

XGBoost 的核心公式思想：预测 = 所有 \_\_\_\_ 的预测值之和。

## 掌握检查
