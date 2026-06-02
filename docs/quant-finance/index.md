---
title: 量化金融
description: 量化交易知识体系 — 从基础概念到策略回测，系统化整理
---

# 量化金融

> 系统化整理量化交易领域的知识体系：策略模型、回测框架、风险管理、市场微观结构。

---

## 01 量化交易基础

- [概述](./01.0-overview) — 本章学习路线与前置知识
- [1.0 量化交易的本质](./1.0-overview) — 量化交易的核心思想、系统性 vs 主观交易
- [1.1 交易品种](./1.1-market-instruments) — 股票、期货、期权、债券的报价与基础计算
- [1.2 订单类型与市场机制](./1.2-order-types) — 市价单、限价单、止损、冰山订单、价差计算

## 02 组合管理与风险

- [概述](./02.0-overview) — 本章学习路线与前置知识
- [2.0 组合收益与风险](./2.0-portfolio-risk-return) — 简单/对数收益、组合方差、相关系数
- [2.1 有效前沿与最优组合](./2.1-efficient-frontier) — Markowitz 均值-方差优化
- [2.2 夏普比率与绩效度量](./2.2-sharpe-ratio) — Sharpe、Sortino、Calmar 等指标
- [2.3 因子模型](./2.3-factor-models) — CAPM、Beta 计算、Fama-French 三因子

## 03 衍生品与定价

- [概述](./03.0-overview) — 本章学习路线与前置知识
- [3.0 货币时间价值](./3.0-time-value-of-money) — PV、FV、贴现与复利
- [3.1 债券定价与久期](./3.1-bond-pricing) — 零息/息票债券定价、YTM、久期
- [3.2 期货定价](./3.2-futures-pricing) — 持有成本模型、基差
- [3.3 期权基础](./3.3-options-intro) — Call/Put、价内/价外、收益图
- [3.4 Black-Scholes 定价模型](./3.4-black-scholes) — BS 公式、手算实例、Python 实现
- [3.5 Greeks 与风险管理](./3.5-options-greeks) — Delta、Gamma、Theta、Vega、Rho
- [3.6 期权策略](./3.6-options-strategies) — Covered Call、Straddle、Spread 等

## 04 策略与回测

- [概述](./04.0-overview) — 本章学习路线与前置知识
- [4.0 趋势跟踪策略](./4.0-strategy-trend) — 均线交叉、动量策略
- [4.1 均值回归策略](./4.1-strategy-mean-reversion) — Bollinger Bands、Z-Score
- [4.2 回测框架与方法论](./4.2-backtesting) — Walk-forward、过拟合、偏差分析
- [4.3 绩效评估指标](./4.3-performance-metrics) — CAGR、MDD、Sharpe 手算

## 05 市场微观结构

- [概述](./05.0-overview) — 本章学习路线与前置知识
- [5.0 市场微观结构](./5.0-market-microstructure) — 订单簿基础、流动性、价差
- [5.1 订单簿分析](./5.1-order-book-analysis) — LOB 深度、订单不平衡
- [5.2 执行算法](./5.2-execution-algorithms) — TWAP、VWAP、Implementation Shortfall

---

> **下一步**：从 [量化交易基础概述](./01.0-overview) 开始，了解本章全貌。
