# 第 3 章：数学工具箱

> 本章跟 **MIT 18.S096 Topics in Mathematics with Applications in Finance** 路线走。先看 MIT 视频课，然后用本章的 Python 代码和练习验证理解。

## 使用方法

1. **看 MIT 视频课** → [YouTube 播放列表](https://www.youtube.com/playlist?list=PLUl4u3cNGP63ctJIEC1UnZ0btsphnnoHR)
2. **学本章内容** → 对应 MIT 课的 Python 实现 + 练习
3. **做练习** → 选择题/编程题验证掌握
4. **点「掌握检查」** → 解锁下一章

## 章节对应

| 本章 | MIT 课 | 主题 | Python 重点 |
|------|--------|------|-------------|
| 3.1 | L1+L2: Introduction + Linear Algebra | 金融概念、向量、矩阵、线性变换 | NumPy 基础、向量化操作 |
| 3.2 | L3: Probability Theory | 概率空间、随机变量、分布、期望 | SciPy 分布、蒙特卡洛模拟 |
| 3.3 | L4: Matrix Primer | 矩阵分解、PCA、特征值 | `np.linalg`、SVD |
| 3.4 | L5: Stochastic Processes I | 随机游走、布朗运动、Ito 引理直觉 | 模拟路径、可视化 |
| 3.5 | L6: Regression Analysis | OLS、假设检验、多重共线性 | statsmodels、sklearn |
| 3.6 | L7+L13: VaR + Commodity | 风险价值、压力测试、商品模型 | 风险指标计算 |
| 3.7 | L8+L11+L12: Time Series | ARIMA、单位根、协整 | statsmodels 时序 |
| 3.8 | L9: Volatility Modeling | GARCH、波动率聚集 | ARCH 模型拟合 |
| 3.9 | L10: Regularized Models | 岭回归、Lasso、风险模型 | sklearn 正则化 |
| 3.10 | L14-16: Portfolio Theory | 有效前沿、CAPM、组合优化 | 组合优化实现 |

## 数据来源

所有章节使用 `yfinance` 获取真实市场数据进行练习——你的代码跑在真实数据上。

## 进度

每章预计 1-2 小时（看视频 + 学代码 + 做练习）。全部 10 章约 2-3 周。
