# 前置数学知识

> 量化金融 & AI 必备数学知识。教材级深度，配 Python 示例。

---

本系列包含 **10 大板块**，从基础到应用进阶。左侧目录可展开具体小节。

## 知识全景

```
数学基础
├── 01 高等数学 — 极限、导数、积分、多元微积分
├── 02 线性代数 — 向量矩阵、线性方程组、特征分解、PCA、矩阵微积分
├── 03 概率论 — 概率空间、分布、期望、大数定律、中心极限定理
├── 04 数理统计 — 参数估计、假设检验、ANOVA、回归分析、时间序列

应用进阶
├── 05 最优化理论 — 梯度下降、约束优化、凸优化、KKT 条件
├── 06 随机过程 — 马尔可夫链、布朗运动、伊藤引理、蒙特卡洛
├── 07 信息论 — 熵、交叉熵、KL 散度、互信息
├── 08 傅里叶分析 — 傅里叶变换、滤波器（高频交易）

AI/ML 专项
├── 09 数值计算 — 浮点数精度、反向传播、自动微分
└── 10 图论基础 — 图的基本概念、遍历、最短路径
```

---

## 推荐学习路径

### 路径 A：量化金融方向

```
第 1 阶段（2-4 周）：基础
  概率论 → 数理统计基础 → 线性代数 → 微积分

第 2 阶段（4-6 周）：核心
  回归分析 → 时间序列 → 约束优化 → 随机过程基础

第 3 阶段（4-6 周）：金融专项
  伊藤引理 → 蒙特卡洛模拟 → 傅里叶分析

第 4 阶段：持续进阶
  学到新策略就回查相关概念
```

### 路径 B：AI/ML 方向

```
第 1 阶段（2-3 周）：基础
  线性代数 → 微积分（梯度部分）→ 概率论

第 2 阶段（3-4 周）：统计+优化
  回归分析 → 最优化 → 信息论

第 3 阶段（3-4 周）：深度学习
  数值计算（反向传播）→ 多元微积分 + 矩阵微积分

第 4 阶段：持续进阶
  图论 → 随机过程（强化学习/时序模型）
```

## 推荐资源

### 书籍

| 书名 | 作者 | 适合 |
|------|------|------|
| 《Convex Optimization》 | Boyd & Vandenberghe | 凸优化入门 |
| 《Options, Futures, and Other Derivatives》 | John Hull | 期权定价数学 |
| 《The Concepts and Practice of Mathematical Finance》 | Mark Joshi | 量化实践 |
| 《Linear Algebra Done Right》 | Axler | 线性代数（理论向） |
| 《The Elements of Statistical Learning》 | Hastie 等 | ML 数学基础 |
| 《深度学习》（花书） | Goodfellow 等 | DL 数学基础 |
| 《Inside the Black Box》 | Rishi K. Narang | 量化策略实践 |

### 在线课程

- [MIT 18.06 线性代数 (Strang)](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/)
- [Statistical Learning (Hastie)](https://www.youtube.com/playlist?list=PLoROMvodv4rOzrYsAxzQyHb8n_RWNuS1e)
- [Machine Learning (Andrew Ng)](https://www.coursera.org/learn/machine-learning)
- [3Blue1Brown 系列](https://www.youtube.com/c/3blue1brown) — 直观理解数学

### 实用工具

- [Statsmodels](https://www.statsmodels.org/) — Python 统计建模
- [NumPy](https://numpy.org/) — 线性代数/数值计算
- [SciPy](https://scipy.org/) — 优化/统计/信号处理
