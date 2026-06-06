# 资源收藏

> 优质学习资源索引，持续更新。

---

## 📖 书籍

- *待补充*

## 📄 论文

- *待补充*

## 🔗 博客

- *待补充*

## 🎬 视频课程

### MIT 18.S096 Topics in Mathematics with Applications in Finance

> MIT 经典公开课，面向本科生和研究生，讲解金融行业中使用的数学概念与技术。数学部分由 MIT 教授讲授，应用部分由行业从业者授课。
> YouTube 播放列表：https://www.youtube.com/playlist?list=PLUl4u3cNGP63ctJIEC1UnZ0btsphnnoHR
> OCW 主页：http://ocw.mit.edu/courses/mathematics/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/
> 新版课程（Fall 2024）：https://ocw.mit.edu/courses/18-642-topics-in-mathematics-with-applications-in-finance-fall-2024/

**课程大纲（前 10 讲）：**

| # | 主题 | 时长 |
|---|------|------|
| 1 | Introduction, Financial Terms and Concepts | 1:00 |
| 2 | Linear Algebra | 1:12 |
| 3 | Probability Theory | 1:18 |
| 4 | Stochastic Processes I | 1:17 |
| 5 | Regression Analysis | 1:22 |
| 6 | Value At Risk (VAR) Models | 1:21 |
| 7 | Time Series Analysis I | 1:16 |
| 8 | Volatility Modeling | 1:21 |
| 9 | Regularized Pricing and Risk Models | 1:29 |
| 10 | Time Series Analysis II | 1:23 |
| 11–24 | 继续覆盖优化、期权定价、固定收益、随机微积分等主题 | — |

**在 Quant Wiki 中的应用：** 本课程与 Wiki 的前置数学知识章节（线性代数 → 概率论 → 随机过程 → 时间序列 → 优化）高度对应，可作为配套视频讲解材料。第 5–10 讲直接对应量化金融中的回归分析、VaR 模型、波动率建模、正则化定价等核心实务内容。

### QuantPy — 用 Python 学量化金融

> 专注于量化金融和 Python 编程的 YouTube 频道，内容覆盖期权做市、因子投资、风险模型、投资组合优化等实务话题。同时运营有 GitHub 仓库和课程网站。
> YouTube 频道：https://www.youtube.com/c/quantpy
> GitHub：https://github.com/thequantpy
> 课程网站：https://www.quantpykit.com/

**代表内容（92 个视频）：**
- **QuantPy Insights Podcast** — 邀请行业资深人士对话，如 "A 20-Year Veteran Reveals the World of Options Market Making"（52min）
- 期权做市、风险管理、投资组合优化的实战讲解
- 用 Python 实现因子投资、回测框架、波动率模型等量化技术
- 数据驱动的量化金融求职准备指导

**在 Quant Wiki 中的应用：** 适合作为量化进阶和实战场景的补充视频资源，特别是期权做市、因子投资和 Python 工程实现等 Wiki 内无法通过图文充分覆盖的实操话题。

## 💻 开源项目

### Qlib — AI 量化投资平台

> 微软开源的 AI 量化投资平台，覆盖从研究到生产的全流程。
> GitHub：[microsoft/qlib](https://github.com/microsoft/qlib) ｜ ⭐ 43.9k

**核心能力：**

- 支持多种 ML 范式：监督学习、市场动态建模、强化学习
- 内置 RD-Agent，实现量化策略研发自动化
- 数据获取 → 特征工程 → 模型训练 → 回测 → 实盘，全流程覆盖
- 生态完善，社区活跃（2k+ commits，6.9k forks）

**在 Quant Wiki 中的应用：** Qlib 可作为本地回测和策略开发的技术参考，其数据加载管道、因子计算和模型评估框架与本书策略章节（第 4 章）紧密相关。

## 📊 数据集

### Tushare

> 中国最大的免费金融数据社区平台，提供股票、基金、期货、期权、债券等全品类行情与基本面数据。
> 官网：[tushare.pro](https://tushare.pro) ｜ GitHub：[waditu/tushare](https://github.com/waditu/tushare)

**数据覆盖：**

| 类别 | 内容 |
|------|------|
| 沪深股票 | 日线/分钟/Tick行情、复权因子、上市公司信息、IPO、停复牌 |
| 财务数据 | 利润表、资产负债表、现金流量表、业绩预告/快报、财务指标 |
| 基金/ETF | 净值、持仓、分红、基金经理信息 |
| 期货/期权 | 日线行情、合约信息、主力合约、期权T型报价 |
| 指数 | 成分股、权重、行业分布 |
| 宏观经济 | GDP、CPI、PMI、利率、外汇储备、LPR、MLF |
| 港股/美股 | 行情、公司信息、财务数据 |
| 债券 | 到期收益率、久期、信用评级 |
| 特色数据 | 大模型语料、另类数据（新闻情绪、股东增减持等） |

**接入方式：**

- Python SDK: `pip install tushare`，通过 `pro = ts.pro_api(token)` 获取数据
- HTTP Restful: `https://api.tushare.pro`，支持任意语言调用
- 注册获取 token 后即可使用，基础数据免费

**在 Quant Wiki 中的应用：** 本书中所有涉及 A 股行情数据、财务数据的示例和回测，均依赖 Tushare 作为数据源。

---

> 📝 内容构建中，欢迎推荐资源。
