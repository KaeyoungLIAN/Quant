# 6.3 时间序列模型（LSTM）

> 本章目标：理解 LSTM 如何处理时间序列数据，并用于金融序列预测。

## 一句话

**LSTM** = 带"记忆"的神经网络，能记住很久以前的模式，适合处理时间序列。

## 学习目标

学完本章你能：
- 理解 LSTM 的核心概念（门控、记忆单元）
- 用 PyTorch/Keras 构建一个简单的 LSTM 预测模型
- 对比 LSTM 与 XGBoost 在时序任务上的表现

## 核心内容

### 1. 为什么需要 LSTM？

```python
# 简单对比：普通 MLP vs LSTM
# MLP：把过去5天的数据当成5个独立的特征
# LSTM：知道这5天是有顺序的——第1天影响第2天，第2天影响第3天

"""
普通神经网络（MLP）:
  输入: [day1_feat, day2_feat, ..., day5_feat]
  处理: 全部平等对待 → 丢失了时间顺序信息

LSTM:
  输入: [day1_feat] → [day2_feat] → [day3_feat] → ...
  处理: 序列化处理，每个时间步保留"记忆" → 捕捉时序依赖
"""
```

### 2. 数据准备：序列化

```python
import numpy as np
import pandas as pd
import yfinance as yf

# 加载数据
data = yf.download('SPY', start='2015-01-01', end='2024-12-31')
close = data['Adj Close']

# 创建序列数据
def create_sequences(data, seq_length=20):
    """
    将时间序列转换为 (样本, 时间步, 特征) 格式
    seq_length: 用过去 N 天预测未来
    """
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

# 先用简单一维数据演示
# 归一化（重要！）
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
close_scaled = scaler.fit_transform(close.values.reshape(-1, 1)).flatten()

seq_length = 20
X, y = create_sequences(close_scaled, seq_length)

# 时间序列分割
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

print(f"训练集形状: {X_train.shape}")  # (样本数, 20, 1)
print(f"测试集形状: {X_test.shape}")
```

### 3. 构建 LSTM 模型（PyTorch）

```python
import torch
import torch.nn as nn
import torch.optim as optim

# 如果没装 torch，用 numpy 和 sklearn 实现简化版
# 这里用最小化的 LSTM 演示

class SimpleLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=32, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, (hidden, cell) = self.lstm(x)
        # 取最后一个时间步的输出
        out = self.fc(out[:, -1, :])
        return out

# 转为 PyTorch 张量
X_train_t = torch.FloatTensor(X_train).reshape(-1, seq_length, 1)
y_train_t = torch.FloatTensor(y_train).reshape(-1, 1)
X_test_t = torch.FloatTensor(X_test).reshape(-1, seq_length, 1)
y_test_t = torch.FloatTensor(y_test).reshape(-1, 1)

# 初始化模型
model = SimpleLSTM(input_size=1, hidden_size=32)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练
n_epochs = 50
batch_size = 32
n_batches = len(X_train_t) // batch_size

for epoch in range(n_epochs):
    model.train()
    epoch_loss = 0
    
    for i in range(0, len(X_train_t), batch_size):
        batch_X = X_train_t[i:i+batch_size]
        batch_y = y_train_t[i:i+batch_size]
        
        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{n_epochs}, Loss: {epoch_loss/n_batches:.6f}")
```

### 4. 预测与反向变换

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 预测
model.eval()
with torch.no_grad():
    y_pred_scaled = model(X_test_t).numpy()

# 反向归一化
y_pred = scaler.inverse_transform(y_pred_scaled)
y_actual = scaler.inverse_transform(y_test_t.numpy())

# 评估
mae = mean_absolute_error(y_actual, y_pred)
rmse = np.sqrt(mean_squared_error(y_actual, y_pred))

print(f"MAE: ${mae:.2f}")
print(f"RMSE: ${rmse:.2f}")

# 方向准确率（涨/跌预测）
actual_returns = np.diff(y_actual.flatten())
pred_returns = np.diff(y_pred.flatten())
direction_accuracy = np.mean((actual_returns > 0) == (pred_returns > 0))
print(f"方向准确率: {direction_accuracy:.2%}")
```

### 5. LSTM vs XGBoost——对比

```python
# LSTM 适合：
# - 数据量大（1000+ 样本）
# - 强时间依赖关系
# - 多步预测

# XGBoost 适合：
# - 数据量中等
# - 特征工程丰富
# - 需要可解释性

# 经验法则：
# 对于金融时间序列，XGBoost 通常比 LSTM 更好用
# LSTM 的优势在更长序列（60+ 天）和更复杂模式上才体现
```

### 6. LSTM 在量化中的实际用法

LSTM 在量化中通常不直接预测价格（太难），而是：

```python
# 1. 预测波动率方向
# 2. 预测因子的 IC 衰减
# 3. 作为多模型集成的一部分

# 一个更实用的方向：用 LSTM 预测波动率
returns = close.pct_change().dropna()
realized_vol = returns.rolling(20).std()

# 用过去 60 天的收益率预测未来 20 天的波动率
# 这比预测价格容易得多，也更有实用价值
```

## 深度阅读

## 练习

### 选择题

1. LSTM 相比普通 MLP 的核心优势是：
   - A. 训练速度更快
   - B. 能处理序列数据中的时间依赖关系
   - C. 不需要归一化
   - D. 代码更短

2. 为什么 LSTM 的输入是 3D 张量 (batch, seq_len, features)？
   - A. 只是为了兼容 PyTorch/Keras 的 API
   - B. 因为需要同时表示样本数量、时间步、特征维度
   - C. 不需要，只是习惯
   - D. 为了加速 GPU 计算

3. 金融序列预测中，LSTM 比 XGBoost 通常：
   - A. 总是更好
   - B. 不一定，XGBoost 经常表现更好
   - C. 差得多
   - D. 不适合

4. "方向准确率"衡量的是：
   - A. 价格预测的准确度
   - B. 涨跌方向预测的正确比例
   - C. 特征数量
   - D. 模型大小

### 编程题

**作业：** 在上面的 LSTM 代码基础上，将输入改为多特征（价格+成交量），用 30 天序列预测未来 5 天的平均收益率方向。与 XGBoost 的结果做对比。

### 填空题

LSTM 的输入形状是 (batch, \_\_\_\_, features)，其中第二个维度代表 \_\_\_\_ 步。

## 掌握检查
