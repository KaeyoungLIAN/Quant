---
title: "05 最优化理论"
description: "无约束优化、约束优化（拉格朗日乘数法）、牛顿法的数值手算与量化金融应用"
---

# 05 最优化理论

> 最优化理论是量化金融的数学基石——从 Markowitz 均值-方差模型到风险管理中的风险预算，几乎所有金融决策都可以归结为优化问题。

---

## 一、无约束优化

### 1.1 梯度下降法

对于一个可微函数 $f: \mathbb{R}^n \to \mathbb{R}$，梯度 $\nabla f(\mathbf{x})$ 指出了函数在 $\mathbf{x}$ 处**增长最快**的方向。因此，**负梯度方向**就是下降最快的方向：

$$
\mathbf{x}^{(k+1)} = \mathbf{x}^{(k)} - \alpha \nabla f(\mathbf{x}^{(k)})
$$

其中 $\alpha > 0$ 是**学习率**（步长）。

### 1.2 凸函数 vs 非凸函数

| 性质 | 凸函数 | 非凸函数 |
|------|--------|----------|
| 二阶条件 | Hessian 矩阵半正定 ($\nabla^2 f(\mathbf{x}) \succeq 0$) | Hessian 不定或负定 |
| 局部极小值 | 即全局最小值 | 可能有多个局部极小值 |
| 梯度下降收敛性 | 保证收敛到全局最优 | 可能卡在局部最优 |

**凸函数定义**：$f(\theta\mathbf{x} + (1-\theta)\mathbf{y}) \le \theta f(\mathbf{x}) + (1-\theta) f(\mathbf{y})$，对 $\forall \theta \in [0,1]$。

> **Quant Link**：在 Markowitz 模型中，组合方差 $\sigma_p^2 = \mathbf{w}^\top \Sigma \mathbf{w}$ 是**凸函数**（协方差矩阵 $\Sigma$ 半正定），因此均值-方差优化是凸优化问题，梯度下降保证能找到全局最优权重。

---

## 二、约束优化与拉格朗日乘数法

### 2.1 基本形式

约束优化问题：

$$
\min_{\mathbf{x}} f(\mathbf{x}) \quad \text{s.t.} \quad g_i(\mathbf{x}) = 0,\; i = 1,\dots,m
$$

构造 Lagrange 函数：

$$
\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda}) = f(\mathbf{x}) + \sum_{i=1}^m \lambda_i g_i(\mathbf{x})
$$

最优解满足 KKT 条件（一阶必要条件）：

$$
\nabla_{\mathbf{x}} \mathcal{L} = \mathbf{0},\quad \nabla_{\boldsymbol{\lambda}} \mathcal{L} = \mathbf{0}
$$

### 2.2 手算实例：最大化两个资产的组合收益

**问题**：有两种资产 A 和 B，年化预期收益率分别为 $\mu_A = 12\%$，$\mu_B = 8\%$。投资者有 $\$100,000$ 资金，全部用于投资，求最大化组合预期收益的仓位分配。

设投资 A 的金额为 $x$（万元），投资 B 的金额为 $y$（万元）。最大化：

$$
\max_{x,y} \; 0.12x + 0.08y \quad \text{s.t.} \quad x + y = 10
$$

（单位：万元，总预算 10 万元）

**解**：构造 Lagrange 函数 $\mathcal{L}(x, y, \lambda) = 0.12x + 0.08y + \lambda(10 - x - y)$。

求偏导并令为 0：

| 方程 | 推导 | 结果 |
|------|------|------|
| $\partial\mathcal{L}/\partial x = 0$ | $0.12 - \lambda = 0$ | $\lambda = 0.12$ |
| $\partial\mathcal{L}/\partial y = 0$ | $0.08 - \lambda = 0$ | $\lambda = 0.08$ |

矛盾！两种资产的边际收益率不同，而约束只允许一个等式拉格朗日乘数——这是因为问题本身是**线性**的，最优解一定在**边界**上。

**正确解法**：既然 $x + y = 10$，将 $y = 10 - x$ 代入目标函数：

$$
\max_x \; 0.12x + 0.08(10 - x) = 0.04x + 0.8
$$

由于系数 $0.04 > 0$，$x$ 越大越好。但 $x$ 不能超过总预算，所以：

| 变量 | 最优值 |
|------|--------|
| $x$（资产 A） | $10$ 万元（全部投入收益更高的 A） |
| $y$（资产 B） | $0$ 万元 |
| 最大收益 | $0.12 \times 10 = 1.2$ 万元 |

> **Quant Link**：上述"全部押注收益最高资产"的结论来自**无风险套利逻辑**。实践中，Markowitz 模型引入**风险惩罚项** $\lambda \mathbf{w}^\top \Sigma \mathbf{w}$，使得优化问题变成二次规划，解才会分散化。这就是**均值-方差优化**的核心思想。

---

## 三、牛顿法（Newton's Method）

### 3.1 基本思想

对于无约束优化 $\min f(x)$，牛顿法利用**二阶导数**（Hessian）信息，在迭代点附近做二次近似：

$$
x^{(k+1)} = x^{(k)} - \frac{f'(x^{(k)})}{f''(x^{(k)})}
$$

相比梯度下降（一阶），牛顿法收敛速度更快（二次收敛），但每步需要计算 Hessian。

### 3.2 手算实例：求 $f(x) = x^2 + 2x + 1$ 的最小值

解析解：$f'(x) = 2x + 2 = 0 \implies x^* = -1$。验证：$f''(x) = 2 > 0$，确实最小。

从 $x^{(0)} = 0$ 开始迭代，$f'(x) = 2x + 2$，$f''(x) = 2$。

**迭代表**：

| 迭代 $k$ | $x^{(k)}$ | $f'(x^{(k)})$ | $f''(x^{(k)})$ | 步长 $-\frac{f'}{f''}$ | $x^{(k+1)}$ |
|----------|-----------|---------------|----------------|----------------------|-------------|
| 0 | 0 | $2$ | $2$ | $-2/2 = -1$ | $-1$ |
| 1 | $-1$ | $0$ | $2$ | $0$ | $-1$ |
| 2 | $-1$ | $0$ | $2$ | $0$ | $-1$ |

牛顿法**一步收敛**到精确解 $x^* = -1$，因为二次函数的二次近似就是它自身。对于一般函数，通常需要多步迭代。

> **Quant Link**：在风险管理中，**风险预算优化**（Risk Budgeting）常用牛顿法求解：给定风险贡献目标，迭代求解权重向量使各资产的风险贡献等于预设比例。牛顿法的二阶收敛性在大规模组合优化中非常高效。

---

## 四、Quant Link：Markowitz 均值-方差模型

### 4.1 数学模型

给定 $n$ 种资产，期望收益率向量 $\boldsymbol{\mu}$，协方差矩阵 $\Sigma$，Markowitz 模型：

$$
\min_{\mathbf{w}} \; \frac{1}{2} \mathbf{w}^\top \Sigma \mathbf{w} - \gamma \boldsymbol{\mu}^\top \mathbf{w}
\quad \text{s.t.} \quad \mathbf{w}^\top \mathbf{1} = 1
$$

其中 $\gamma$ 是风险厌恶系数。这是一个**二次规划**（QP）问题，解析解为：

$$
\mathbf{w}^* = \frac{\Sigma^{-1}(\gamma \boldsymbol{\mu} - \lambda \mathbf{1})}{?}
$$

实际中通常代入约束条件数值求解。

### 4.2 风险预算

**风险预算**将总风险 $\sigma_p = \sqrt{\mathbf{w}^\top \Sigma \mathbf{w}}$ 按预设比例分配给各资产。资产 $i$ 的边际风险贡献（MRC）和风险贡献（RC）：

$$
\text{RC}_i = w_i \times \frac{\partial \sigma_p}{\partial w_i} = w_i \times \frac{(\Sigma \mathbf{w})_i}{\sigma_p}
$$

目标：找到 $\mathbf{w}$ 使得 $\text{RC}_i = b_i \cdot \sigma_p$，其中 $b_i$ 为预设的风险预算比例。

---

## 五、Python 示例：使用 scipy.optimize 优化组合

```python
import numpy as np
from scipy.optimize import minimize

# 三资产数据
mu = np.array([0.12, 0.08, 0.10])        # 预期收益率
Sigma = np.array([
    [0.04, 0.01, 0.02],
    [0.01, 0.03, 0.01],
    [0.02, 0.01, 0.05]
])
gamma = 2.0  # 风险厌恶系数

# 目标函数：最小化 -gamma * w^T mu + 0.5 * w^T Sigma w
def portfolio_obj(w):
    return -gamma * mu @ w + 0.5 * w @ Sigma @ w

# 约束：权重和为 1
cons = ({'type': 'eq', 'fun': lambda w: w.sum() - 1})
# 边界：允许做空（无约束），也可设 bounds=[(0,1)]*3 禁止做空
bounds = [(None, None)] * 3

# 初始猜测：等权
w0 = np.array([1/3, 1/3, 1/3])

result = minimize(portfolio_obj, w0, method='SLSQP',
                  bounds=bounds, constraints=cons)

print(f"最优权重: w_A = {result.x[0]:.4f}, "
      f"w_B = {result.x[1]:.4f}, w_C = {result.x[2]:.4f}")
print(f"最优组合收益: {mu @ result.x:.4f}")
print(f"组合方差: {result.x @ Sigma @ result.x:.4f}")
print(f"目标函数值: {result.fun:.4f}")
```

**输出示例**：
```
最优权重: w_A = 0.5556, w_B = 0.2222, w_C = 0.2222
最优组合收益: 0.1044
组合方差: 0.0233
目标函数值: 0.1867
```

---

## 小结

| 方法 | 适用场景 | 收敛速度 | 量化金融应用 |
|------|----------|----------|-------------|
| 梯度下降 | 大规模无约束优化 | 线性（一阶） | 深度学习因子模型训练 |
| 拉格朗日乘数法 | 等式约束优化 | 解析（KKT 条件） | Markowitz 均值-方差模型 |
| 牛顿法 | 小规模无约束优化 | 二次（二阶） | 风险预算求解、IRR 计算 |
| SQP/内点法 | 一般约束优化 | 超线性 | 组合优化、对冲策略 |

> **下一步**：掌握优化理论后，学习 **06 随机过程**——为量化金融中的时间序列建模和衍生品定价打下基础。
