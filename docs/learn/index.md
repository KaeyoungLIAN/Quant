# 📚 量化学习体系

> 从零到独立策略开发的完整路线，**33 节课**，7 个章节。线性推进，学完一节自动解锁下一节。

---

## 🚀 快速开始

如果你是第一天接触量化，从第一章开始：

[👉 开始第一章：出发 →](/learn/01-getting-started/01-setup)

---

## 📖 学习路线总览

---

### 第一章：出发

> 30分钟从零到画出第一张K线图。不用懂任何金融知识。

- [1.1 安装配置](/learn/01-getting-started/01-setup)
- [1.2 第一次获取数据](/learn/01-getting-started/02-first-data)
- [1.3 画第一张K线图](/learn/01-getting-started/03-first-chart)
- [1.4 设定学习目标](/learn/01-getting-started/04-set-goal)

**学完能干什么：** 装好 Python，拿到真实股票数据，画出人生第一张 K 线图。🎉

---

### 第二章：金融扫盲

> 在写量化代码之前，先理解金融市场在交易什么、怎么交易。

- [2.1 交易品种](/learn/02-finance-basics/01-instruments)
- [2.2 市场机制](/learn/02-finance-basics/02-market-mechanism)
- [2.3 时间价值](/learn/02-finance-basics/03-time-value)
- [2.4 风险入门](/learn/02-finance-basics/04-risk-intro)

**学完能干什么：** 看懂股票、期货、期权的区别，理解钱的时间价值和风险的含义。

---

### 第三章：数学工具箱

> 跟 MIT 18.S096 课程路线走，每个理论都有量化案例。**共 10 节 + 1 节路线图。**

- [3.0 MIT路线图](/learn/03-math-toolbox/00-overview) — 怎么配合 MIT 视频课使用
- [3.1 线性代数](/learn/03-math-toolbox/01-linear-algebra) — 向量、矩阵与 Python 向量化
- [3.2 概率与蒙特卡洛](/learn/03-math-toolbox/02-probability) — 随机变量、蒙特卡洛模拟
- [3.3 矩阵分解](/learn/03-math-toolbox/03-matrix-decomposition) — SVD、PCA 在因子模型中的应用
- [3.4 随机过程](/learn/03-math-toolbox/04-stochastic-processes) — 随机游走、布朗运动、伊藤引理
- [3.5 回归分析](/learn/03-math-toolbox/05-regression) — 最小二乘法、多重共线性
- [3.6 VaR与商品](/learn/03-math-toolbox/06-var-commodity) — 风险价值、商品期货定价
- [3.7 时间序列](/learn/03-math-toolbox/07-time-series) — ARIMA、协整、波动率聚集
- [3.8 波动率建模](/learn/03-math-toolbox/08-volatility) — ARCH、GARCH 模型
- [3.9 正则化模型](/learn/03-math-toolbox/09-regularization) — Ridge、Lasso、弹性网
- [3.10 组合理论](/learn/03-math-toolbox/10-portfolio-theory) — 有效前沿、Black-Litterman

---

### 第四章：量化编程速成

> 从 Python 数据处理到完整的回测框架。**4 节速成，只讲量化必需的。**

- [4.1 NumPy/Pandas](/learn/04-python-quant/01-numpy-pandas) — 向量化、DataFrame、金融数据
- [4.2 数据获取与清洗](/learn/04-python-quant/02-data-wrangling) — yfinance、数据清洗、对齐
- [4.3 可视化](/learn/04-python-quant/03-visualization) — K线图、技术指标、净值曲线
- [4.4 回测骨架](/learn/04-python-quant/04-backtest-framework) — 事件驱动回测引擎原型

---

### 第五章：经典策略

> 四个最经典的量化策略类型，**每个都有完整的回测作业**。

- [5.1 趋势跟踪](/learn/05-classic-strategies/01-trend-following) — 动量、MACD、海龟交易
- [5.2 均值回归](/learn/05-classic-strategies/02-mean-reversion) — 布林带、RSI、配对交易
- [5.3 统计套利](/learn/05-classic-strategies/03-stat-arb) — 协整、价差回归
- [5.4 风险管理](/learn/05-classic-strategies/04-risk-management) — 仓位控制、止损、组合优化

---

### 第六章：机器学习因子

> 可解释的 ML 因子，从特征工程到模型诊断。**不是黑箱预测，是更聪明的因子挖掘。**

- [6.1 特征工程](/learn/06-ml-strategies/01-feature-engineering) — 技术指标、交叉特征、滚动统计
- [6.2 XGBoost](/learn/06-ml-strategies/02-xgboost) — 树模型在因子排序中的应用
- [6.3 LSTM](/learn/06-ml-strategies/03-lstm) — 时序深度学习与注意力
- [6.4 过拟合与诊断](/learn/06-ml-strategies/04-overfitting) — 回测过拟合、交叉验证、稳健性

---

### 第七章：实战冲刺

> 从回测到实盘，把前 6 章的知识整合成可运行的量化系统。

- [7.1 数据源与API](/learn/07-live/01-data-sources) — 实时数据、历史数据、券商API
- [7.2 资金管理](/learn/07-live/02-capital-mgmt) — Kelly公式、风险预算、交易成本
- [7.3 毕业设计](/learn/07-live/03-graduation) — 从零构建一个完整的量化策略系统

---

## 🎯 学习建议

| 如果你 | 建议路线 |
| --- | --- |
| 完全零基础 | 第 1 → 2 → 3 → 4 → 5 → 6 → 7 章，按顺序来 |
| 有编程基础但金融零基础 | 第 2 → 3 → 5 章是重点 |
| 有金融背景但不会编程 | 第 1 → 4 章速成后进第 5 章 |
| 只想看策略 | 直接从第 5 章开始，用到什么补什么 |

---

<ProgressCard />

<style>
h2 { margin-top: 40px; padding-bottom: 8px; border-bottom: 1px solid var(--vp-c-divider); }
h3 { margin-top: 28px; }
</style>
