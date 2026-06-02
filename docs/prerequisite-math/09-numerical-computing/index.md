---
title: "09 数值计算"
description: "浮点数精度问题、根求解（牛顿法）、数值积分（梯形法）的手算实例，以及量化金融中的数值 Greeks 和 Monte Carlo 模拟"
---

# 09 数值计算

> **Most quant models have no closed-form solution — numerical methods bridge theory and practice.**

> 大多数量化模型没有解析解——Black-Scholes 的隐含波动率需要数值求解，奇异期权的 Greeks 需要用有限差分法近似，Monte Carlo 定价需要大量随机模拟。数值计算是连接数学理论与可执行代码的桥梁。

---

## This Chapter in Context

前八章我们构建了"纸上数学"的完整工具箱：微积分、线性代数、概率论、随机过程、信息论、傅里叶分析——这些理论提供了优雅的公式和解析解。但真实世界不太配合：隐含波动率的方程 $C_{\text{market}} = BS(\sigma)$ 没有解析反函数；奇异期权的定价函数没有闭合形式；风险度量的 Monte Carlo 模拟需要 $10^6$ 次路径。**数值计算解决的就是"理论能写出来但算不出来"的问题。**

本章直接依赖 **01 高等数学**（数值积分是定积分的近似，数值 Greeks 是导数的有限差分近似）和 **05 最优化**（牛顿法在 5.3 首次引入，本章将其作为根求解工具深化——实际上，风险预算中的牛顿法优化与 IRR 计算中的牛顿法求根是同一个数学内核的不同侧面）。

量化金融中几乎所有"上线运行"的代码都涉及数值计算：期权交易系统每日计算 Greeks 使用有限差分法，风控系统用 Monte Carlo 估计 VaR 和 CVaR，做市商模型用数值方法求解最优报价。**忽略数值计算的细节会直接导致交易损失**——$10^{16}+1-10^{16}=0$ 的灾难性抵消在 Greeks 计算中会抹去关键的价差信号。

## Internal Logic

本章的递进逻辑是：**计算机的数学局限 → 方程求解 → 积分数值化 → 风险度量**。

1. **9.1 浮点精度**：不可跳过的基础。了解机器 epsilon、灾难性抵消、Kahan 求和——否则后续的所有数值结果都可能是"精确的错误"。Greeks 计算中 $\epsilon$ 的选择直接受浮点精度约束：$\epsilon$ 太小导致灾难性抵消，太大导致截断误差。
2. **9.2 根求解**：从"解方程"入手。牛顿法用切线逼近求根，二分法保证收敛但慢。隐含波动率求解是根求解最经典的量化应用——市场报价 $C_{\text{market}}$ 已知，求解 $\sigma$ 使得 $BS(\sigma) = C_{\text{market}}$。
3. **9.3 数值积分**：从方程到积分。梯形法则和 Simpson 法则将定积分近似为加权求和。期权定价中的期望值 $V = e^{-rT}\mathbb{E}^Q[\text{payoff}]$ 本质上就是一个积分——当解析解不存在时，数值积分是替代方案。
4. **9.4 数值 Greeks**：综合应用。有限差分法数值计算 Delta/Gamma/Vega，$\epsilon$ 的选择需要结合 9.1 的浮点精度分析。Monte Carlo 方法的 $\mathcal{O}(1/\sqrt{N})$ 收敛速度意味着要提高精度需大幅增加模拟次数。

## Knowledge Chain

| 节 | 核心概念 | 量化金融应用 |
|-----|---------|-------------|
| 9.1 | 浮点精度、机器 epsilon $\varepsilon_m$、灾难性抵消 | Greeks 计算中 $\epsilon$ 的选择、大规模组合归因 |
| 9.2 | 牛顿法 $x_{n+1} = x_n - f(x_n)/f'(x_n)$ | 隐含波动率求解、IRR 计算、YTM 求解 |
| 9.3 | 数值积分（梯形法则 $\mathcal{O}(h^2)$、Simpson 法则 $\mathcal{O}(h^4)$） | 奇异期权定价、利率曲线拟合、合约平均价格 |
| 9.4 | 有限差分 $\Delta \approx (V(S+\epsilon)-V(S-\epsilon))/(2\epsilon)$ | 数值 Delta/Gamma/Vega 对冲、Monte Carlo 定价 |

## Learning Path

**前置知识**：01 高等数学（导数、定积分）、05 最优化（5.3 牛顿法）。建议先复习 01.2 导数与微分和 01.3 定积分。

**推荐顺序**：9.1 → 9.2 → 9.3 → 9.4。9.1 浮点精度是所有后续内容的基础——如果不理解灾难性抵消，在 9.4 中选择 $\epsilon$ 时就会犯致命错误。9.4 综合了根求解（隐含波动率）和数值积分（Monte Carlo Greeks），是本章的顶点。

## Section Links

- [9.1 浮点精度](./9.1-floating-point) — 机器 epsilon、灾难性抵消、Kahan 求和
- [9.2 根求解](./9.2-root-finding) — 二分法与牛顿法，隐含波动率与 IRR 计算
- [9.3 数值积分](./9.3-numerical-integration) — 梯形法则与 Simpson 法则，期权定价数值积分
- [9.4 数值 Greeks](./9.4-numerical-greeks) — 有限差分法、Delta/Gamma/Vega、Monte Carlo 定价

> **下一步**：掌握数值计算后，学习 **[10 图论基础](../10-graph-theory/index)**——建模金融网络中的支付系统、交易对手风险和区块链。
