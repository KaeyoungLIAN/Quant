# Quant Learning 产品需求文档（PRD）

> App: `quant-learning` | 版本: v2.0.0
> 最后更新: 2026-06-11
> 作者: Kaeyoung

---

## 一、需求背景

现有项目是一个量化知识 Wiki + 学习路线混合体，包含 29 章教程、77 页 Wiki 和一个 FastAPI 后端（含注册登录/JWT/多用户进度系统）。

**核心问题：**
1. 多用户系统是多余的——只有一个人使用
2. 用户需要的是「打开网站 → 跟着线性路线学 → 做题 → 下一章」的沉浸式体验，而不是翻 Wiki
3. 后端的进度系统和前端学习路线脱节——`PHASES` 模块名和 `part-0-python-math/` 目录不匹配
4. AiTeacher 的「AI 出课」功能和已有教程重叠，token 换体验不值得

**目标：** 把多用户 Wiki 站改造为单用户线性学习网站。保持内容和 Wiki 不动，只改造导航、进度、练习验证三个模块。

---

## 二、学习路线（7 章 26 小节）

### 2.1 总体设计原则

- **线性推进**：章节按固定顺序排列，学完一节才能解锁下一节
- **无周数/时间承诺**：只说顺序，不说速度，用户自己控制节奏
- **每章独立可读**：每章 150-250 行 markdown，40-60 分钟阅读+练习
- **成就感即时反馈**：第一章就能画出 K 线图
- **学习 > 参考**：每章末尾有「深度阅读」链接到对应 Wiki 页面，供需要深入时查阅

### 2.2 章节结构

```
第一章：出发
  1.1 安装 Python + Jupyter —— 第一步总是最难
  1.2 第一次运行 yfinance —— 拿到真实数据
  1.3 画第一张 K 线图 —— "我做到了"
  1.4 设定学习目标 —— 你要解决什么问题？

第二章：金融扫盲 —— 你不能用代码写你不懂的东西
  2.1 交易品种：股票、ETF、期货、期权、债券
  2.2 市场机制：订单类型、滑点、流动性、交易时间
  2.3 时间价值：折现、复利、收益率
  2.4 风险入门：波动率、回撤、最大回撤

第三章：数学工具箱
  3.0 概述（MIT 18.S096 路线图）
  3.1 L1+L2 线性代数与向量化
  3.2 L3 概率论与蒙特卡洛
  3.3 L4 矩阵分解与 SVD
  3.4 L5 随机过程与布朗运动
  3.5 L6 回归分析与假设检验
  3.6 L7+L13 VaR 与商品模型
  3.7 L8+L11+L12 时间序列分析
  3.8 L9 波动率建模（GARCH）
  3.9 L10 正则化与风险模型
  3.10 L14-16 组合理论与 CAPM

  每节对应 MIT 18.S096 1-2 节课。先看 MIT 视频，然后用 Python 代码验证理解。每节包含：公式定义 → 手算例子 → Python 代码 → 练习。

第四章：量化编程速成
  4.1 NumPy 基础（向量、矩阵运算）
  4.2 Pandas 数据处理（DataFrame、时间索引）
  4.3 yfinance 数据获取与清洗
  4.4 可视化与回测骨架

第五章：经典策略
  5.1 趋势跟踪：均线、动量、MACD
  5.2 均值回归：布林带、RSI、配对交易
  5.3 统计套利：协整、多因子模型
  5.4 组合 & 风险管理：夏普比率、最大回撤、凯利公式

第六章：机器学习策略
  6.1 特征工程
  6.2 XGBoost 因子
  6.3 LSTM 时间序列
  6.4 过拟合 & 交叉验证 & 策略诊断

第七章：实战
  7.1 数据源 & API（A股、加密、外汇）
  7.2 资金管理 & 滑点模拟
  7.3 毕业设计：选题→回测→优化→文档
```

### 2.3 内容重用策略

> 已有 29 章内容（原 Part 0-5）不会被废弃——而是**重新映射**到新章节。

| 原 Part | 原内容 | 新映射 |
|---------|--------|--------|
| Part 0 数学预备（10章） | 线代/概率/矩阵/随机过程/回归/VaR/时序/波动率/正则化/组合 | 第三章（数学）+ 第二章部分（风险） |
| Part 1 回测基础（3章） | K线/回测/指标 | 第四章（编程）+ 第一章（K线） |
| Part 2 策略（4章） | 趋势/均值/套利/多因子 | 第五章（策略） |
| Part 3 风险（3章） | 过拟合/风险/诊断 | 第六章（ML）+ 第五章（风险） |
| Part 4 ML（3章） | 特征/XGBoost/LSTM | 第六章（ML） |
| Part 5 实战（3章） | 数据/资金/毕设 | 第七章（实战） |
| 第一章 出发 | 无对应 | 全新编写 |

**不直接移动文件**——每章按新结构重新组织，确保：
- 前置知识在前、后置知识在后（原结构里回测基础在策略前面、风险在策略后面，新结构也保持）
- 每章自成体系，不要求用户读懂前几章才能理解
- 金融扫盲（第二章）是新内容，需要全新编写

---

## 三、首页 & 导航设计

### 3.1 首页布局

```
╔══════════════════════════════════════════════╗
║            Quant Learning                    ║
║  ─────────────────────────────────────────   ║
║                                              ║
║  欢迎回来，Kaeyoung！                        ║
║                                              ║
║  ┌────────────────────────────────────────┐  ║
║  │                                        │  ║
║  │  你上次学到：第五章 经典策略            │  ║
║  │  当前进度：■■■■■■□□□□ 65%              │  ║
║  │                                        │  ║
║  │  [ ▶ 继续学习 ]                        │  ║
║  │                                        │  ║
║  └────────────────────────────────────────┘  ║
║                                              ║
║  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       ║
║  │ 📚   │ │ 📈   │ │ 🤖   │ │ 🔗   │       ║
║  │ 全部  │ │ 量化  │ │ AI & │ │ 资源  │       ║
║  │ 章节  │ │ 金融  │ │ 工具  │ │ 收藏  │       ║
║  └──────┘ └──────┘ └──────┘ └──────┘       ║
╚══════════════════════════════════════════════╝
```

- **顶部**：网站标题 + 导航栏（首页 | 学习路线 | 量化金融 | 前置数学 | AI 工具 | 技术栈 | 资源）
- **中间主体**：大卡片显示当前学习进度 + 「继续学习」按钮（这是第一优先级）
- **下方**：四张 feature card（全部章节 / 量化金融 Wiki / AI 工具 / 资源收藏）——与原首页类似，但放到次要位置

### 3.2 学习路线侧边栏

左侧边栏在 `/learn/` 路径下显示：

```
📚 全部章节
✅ 第一章：出发
✅ 第二章：金融扫盲
✅ 第三章：数学工具箱
⬜ 第四章：Python 量化编程  ← 当前
🔒 第五章：经典策略
🔒 第六章：机器学习策略
🔒 第七章：实战
```

- **✅** = 已通过（练习全部通过）
- **⬜** = 学习中（当前章节）
- **🔒** = 未解锁（前置章节未完成）

展开后显示子节列表，子节也有完成状态：

```
✅ 第四章：Python 量化编程
    ✅ 4.1 NumPy/Pandas 数据处理
    ⬜ 4.2 数据获取与清洗
    🔒 4.3 可视化
    🔒 4.4 回测框架
```

### 3.3 章节内布局

每章节页面结构：

```
# 4.2 数据获取与清洗

> 你知道交易所有多脏吗？——数据清洗占了量化开发 80% 的时间。

## 学习目标
...

## 核心内容
...（代码 + 解释 + 公式）

## 深度阅读
- Wiki → [yfinance 使用技巧](/quant-finance/...)
- Wiki → [数据清洗最佳实践](/tech-stack/data-tools)

## 练习

### 选择题（点击选择，即时反馈）

1. yfinance 的 ticker 格式中，A股股票代码后缀是？
   [A] .SS [B] .SZ [C] .HK [D] 无需后缀

### 论述题（AI 判分）

请解释为什么数据清洗在量化中如此重要？举例说明一个常见的脏数据问题。

[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]
|                                        |
|  (你的回答...)                          |
|                                        |
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]

[ 📤 提交答案 ]

---

⬅ 上一章：4.1 NumPy/Pandas    ➡ 下一章：4.3 可视化（🔒 未解锁）
```

**交互规则：**
- 选择题点击后即时显示对/错 + 解析
- 所有选择题答对后，论述题按钮变为可提交
- 论述题提交后 → 调用 DeepSeek → 返回评语 + 建议 → 评语认可即通过
- 通过后侧边栏图标更新为 ✅，下一节解锁

---

## 四、进度系统

### 4.1 数据模型（后端 SQLite，去多用户）

| 表 | 字段 | 说明 |
|---|---|---|
| `progress` | `chapter_key TEXT PK` | 章节标识（如 `4.2`） |
|  | `sub_items_done TEXT` | JSON 数组，记录该节下哪些练习通过 |
|  | `status TEXT` | `locked \| unlocked \| in_progress \| completed` |
|  | `updated_at TEXT` | ISO 时间戳 |

只有一张表。没有用户表。记录的就是全局进度。

### 4.2 解锁规则

```
第一章 → 开放（起点）
第一章完成 → 解锁第二章
第二章完成 → 解锁第三章
...
```

**不依赖 AI 判分通过才能解锁**——选择题是硬门槛（有标准答案），论述题提交即标记为「待审核」，允许先跳到下一章，回头补。用户可以在侧边栏看到哪些论述题没通过。

### 4.3 数据流向

```
用户打开首页
  ↓
前端 GET /api/progress → 返回所有章节状态
  ↓
渲染侧边栏（✅/⬜/🔒）
  ↓
用户做选择题 → 即时前端判对错
  ↓
用户提交论述题 → POST /api/progress/judge → DeepSeek 判分 → 返回评语
  ↓
通过 → POST /api/progress/advance 更新进度
  ↓
下次打开首页 → 进度恢复
```

---

## 五、AI Teacher 设计

### 5.1 砍掉的功能

- ❌ `/api/teacher/lesson`（AI 出课）— 已有完整教程，不重复造
- ❌ 多用户系统（注册/登录/JWT/User 表/ModuleTracker）
- ❌ 三阶段进度系统（`PHASES` 字典）

### 5.2 保留的功能

- ✅ `/api/chat`（AI 对话答疑）— 用户学习中有问题就点右下角气泡问
- ✅ `/api/progress/judge`（新增）— 判论述题
- ✅ `/api/progress`（新增）— 获取/更新学习进度

### 5.3 AI 对话场景

- 学习时卡住了 → 右下角气泡提问
- 做论述题 → 提交后自动判分
- 深度阅读时想讨论 → 选中文字右键提问（未来功能，v2）

---

## 六、后端 API 设计

### 6.1 基础路径

```
/api/v1/
```

### 6.2 接口列表

#### `GET /api/v1/progress` — 获取全部进度

**响应：**
```json
{
  "chapters": [
    {"key": "1.1", "status": "completed", "sub_items_done": ["mcq_1", "mcq_2", "mcq_3", "essay_1"]},
    {"key": "1.2", "status": "completed", ...},
    {"key": "1.3", "status": "completed", ...},
    {"key": "1.4", "status": "completed", ...},
    {"key": "2.1", "status": "in_progress", ...},
    {"key": "2.2", "status": "locked", ...}
  ],
  "last_visited": "2.1"
}
```

**解锁状态计算规则（服务端不存 `locked` 状态，只算）：**

```
chapters 按 key 排序
从第一条开始，所有 key 的初始 status = "locked"
找到第一条 status != "completed" 的记录 → status = "in_progress"
该条之后的所有条 → 仍为 "locked"

特殊情况：
- 如果所有条都 "completed" → 全部完成
- 如果某条不存在 → 视为 locked
```

#### `POST /api/v1/progress/advance` — 标记某节完成

**请求：**
```json
{
  "chapter_key": "1.1",
  "sub_item": "mcq_1"
}
```

#### `POST /api/v1/progress/judge` — AI 判论述题

**请求：**
```json
{
  "chapter_key": "4.2",
  "question": "请解释为什么数据清洗在量化中如此重要...",
  "answer": "因为市场数据经常有缺失值..."
}
```

**响应：**
```json
{
  "passed": true,
  "feedback": "回答得很好，特别是提到了前复权的问题。补充一点：...",
  "suggestions": ["建议阅读 yfinance 的 dividend 处理"]
}
```

#### `POST /api/v1/chat` — AI 对话（保留现有，路径调整）

**请求：**
```json
{
  "message": "macd的金叉死叉怎么判断假信号？",
  "context": {"chapter_key": "5.1", "progress": "in_progress"}
}
```

### 6.3 数据库

SQLite 单文件 `data/progress.db`，仅一张表：

```sql
CREATE TABLE progress (
    chapter_key TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'locked',  -- in_progress | completed
    sub_items_done TEXT NOT NULL DEFAULT '[]',  -- JSON array
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## 七、文件结构与迁移计划

### 7.1 前端文件结构

```
docs/
├── index.md                    ← 首页（大改，进度卡片 + 功能卡片）
├── learn/
│   ├── index.md                ← 学习路线总览
│   ├── 01-getting-started/      ← 全新
│   │   ├── index.md
│   │   ├── 01-setup.md
│   │   ├── 02-first-data.md
│   │   ├── 03-first-chart.md
│   │   └── 04-set-goal.md
│   ├── 02-finance-basics/       ← 全新/重写
│   │   ├── index.md
│   │   ├── 01-instruments.md
│   │   ├── 02-market-mechanism.md
│   │   ├── 03-time-value.md
│   │   └── 04-risk-intro.md
│   ├── 03-math-toolbox/         ← 从原 Part 0 映射
│   │   ├── index.md
│   │   ├── 01-linear-algebra.md
│   │   ├── 02-probability.md
│   │   ├── 03-statistics.md
│   │   └── 04-calculus.md
│   ├── 04-python-quant/         ← 从原 Part 0 + Part 1 映射
│   │   ├── index.md
│   │   ├── 01-numpy-pandas.md
│   │   ├── 02-data-wrangling.md
│   │   ├── 03-visualization.md
│   │   └── 04-backtest-framework.md
│   ├── 05-classic-strategies/   ← 从原 Part 2 + Part 3 映射
│   │   ├── index.md
│   │   ├── 01-trend-following.md
│   │   ├── 02-mean-reversion.md
│   │   ├── 03-stat-arb.md
│   │   └── 04-risk-management.md
│   ├── 06-ml-strategies/        ← 从原 Part 4 + Part 3 映射
│   │   ├── index.md
│   │   ├── 01-feature-engineering.md
│   │   ├── 02-xgboost.md
│   │   ├── 03-lstm.md
│   │   └── 04-overfitting.md
│   └── 07-live/                ← 从原 Part 5 映射
│       ├── index.md
│       ├── 01-data-sources.md
│       ├── 02-capital-mgmt.md
│       └── 03-graduation.md
├── quant-finance/...            ← 保留不变
├── prerequisite-math/...        ← 保留不变
├── tech-stack/...               ← 保留不变
├── resources/...                ← 保留不变
├── .vitepress/
│   ├── config.ts                ← 侧边栏大改，适配新结构
│   └── theme/
│       ├── index.ts             ← 修改：移除非必需组件
│       └── components/
│           ├── AiTeacher.vue    ← 保留并适配新 API 路径
│           └── ProgressSidebar.vue  ← 新增：带状态的侧边栏
├── public/
│   └── ...（保留不变）
```

### 7.2 后端文件结构

```
teacher/
├── main.py              ← 精简：去掉 auth、多用户、/teacher/lesson
├── llm.py               ← 保留不变
├── database.py          ← 精简：只保留 progress 表
├── models.py            ← 精简：只保留 Progress 模型
├── schemas.py           ← 精简
├── requirements.txt     ← 同前
└── .env                 ← 保留
```

### 7.3 删除的文件

| 文件 | 原因 |
|------|------|
| `docs/learn/part-0-python-math/` 全部 | 重组为第三章 |
| `docs/learn/part-1-backtest/` 全部 | 重组为第四章 |
| `docs/learn/part-2-strategies/` 全部 | 重组为第五章 |
| `docs/learn/part-3-risk/` 全部 | 重组为第五章+第六章 |
| `docs/learn/part-4-ml/` 全部 | 重组为第六章 |
| `docs/learn/part-5-live/` 全部 | 重组为第七章 |
| `teacher/init_db.py` | 初始化脚本，一次性功能 |
| `teacher/.env` | 不应进 git（已移出） |
| `start-teacher.sh` | 改为新的启动方式 |

### 7.4 侧边栏配置（config.ts）变化

**删除：**
- `/quant-finance/` 的完整侧边栏（改成所有 `collapsed: true` 收起，不删链接）
- `/learn/` 的旧 6 Part 结构

**新增：**
- `/learn/` 的 7 章带状态侧边栏
- 首页 `sidebar: false`

---

## 八、部署方案

维持现有模式不变：

```
VitePress build → 静态文件
FastAPI 后端 serve 静态文件 + API 代理
Cloudflare Tunnel → 外网访问
```

改动：
- FastAPI 后端在 `teacher/main.py` 中，端口统一为 `8000`
- `start.sh` 新脚本：build → 启动后端，同时打印 tunnel 命令
- `.gitignore` 已修复（保留 teacher 源代码）

---

## 九、开发阶段

### Phase 1 — 后端精简（1天）

1. 删除所有多用户代码（auth、User、ModuleTracker、Lesson、ChatHistory 等旧表）
2. 创建 `progress` 单表
3. 重写 API：`GET /progress`、`POST /progress/advance`、`POST /progress/judge`
4. `POST /chat` 保留，改为 `/api/v1/chat`
5. 测试：curl 验证所有 API 返回正确

### Phase 2 — 内容迁移 + 新章节编写（3天）

1. 创建 7 章目录结构和 index.md
2. 第一章（出发）全新编写——4 个小节
3. 第二章（金融扫盲）全新编写——4 个小节
4. 第三~七章：从旧文件映射+重写——每章平均 3-4 个小节，重用旧代码块
5. 更新 `config.ts` 侧边栏

### Phase 3 — 前端交互（2天）

1. 首页改版：进度卡片 + 功能卡片
2. 带状态的侧边栏组件（Vue）
3. 选择题交互（点击即反馈）
4. 论述题提交 → 调用 API
5. 进度自动同步
6. AiTeacher 对话框适配新 API 路径

### Phase 4 — 打磨（1天）

1. 修复 Build 警告（localStorage SSR）
2. 全量走一遍学习流程
3. 更新首页文案
4. push

---

## 十、不做的功能（Out of Scope）

| 功能 | 原因 |
|------|------|
| 多用户/注册/登录 | 单人使用 |
| AI 自动出课 (`/api/teacher/lesson`) | 已有完整教程，质量可控 |
| 第三方登录 | 单人使用 |
| 数据分析面板 | 单人不需要看统计 |
| 策略代码在线运行 | 需要沙箱，复杂度高 |
| 手机端适配 | VitePress 默认支持响应式，暂不专门适配 |
| Dark mode 开关 | VitePress 自带，不需要额外开发 |
| 选中文字提问 | v2 功能，现在不做 |

---

## 十一、开发记录

| 日期 | 变更 |
|------|------|
| 2026-06-11 | 初始 PRD 编写 |

---

## 附录 A：与旧系统的对应关系

| 新章节 | 旧文件来源 | 操作 |
|--------|-----------|------|
| 1.1 安装配置 | 无 | 全新 |
| 1.2 第一次 yfinance | `part-0-python-math/01-linear-algebra.md` 金融术语部分 | 剥离+改写 |
| 1.3 画 K 线图 | `part-1-backtest/01-from-data-to-candles.md` | 精简 |
| 1.4 设定目标 | 无 | 全新 |
| 2.1-2.4 金融扫盲 | `quant-finance/1.*`, `quant-finance/3.0*` | 从 Wiki 提取+改写为教程格式 |
| 3.0-3.10 数学工具箱 | `part-0-python-math/` 全部 10 章 | 保留，直接搬过去 |
| 4.1 NumPy 基础 | `part-0-python-math/01-linear-algebra.md` 的 NumPy 部分 | 剥离+精简 |
| 4.2 Pandas 处理 | `part-0-python-math/01-linear-algebra.md` 的 DataFrame 部分 | 剥离+精简 |
| 4.3 yfinance 数据 | `part-1-backtest/01-from-data-to-candles.md` | 精简，去掉 K 线图（移到第一章） |
| 4.4 可视化+回测骨架 | `part-1-backtest/02-first-backtest.md`（回测部分）+ 代码片段 | 精简 |
| 5.1 趋势跟踪 | `part-2-strategies/01-trend-following.md` | 保留 |
| 5.2 均值回归 | `part-2-strategies/02-mean-reversion.md` | 保留 |
| 5.3 统计套利 | `part-2-strategies/03-statistical-arbitrage.md` | 保留 |
| 5.4 风险管理 | `part-0-python-math/06-var-commodity.md`, `part-0-python-math/10-portfolio-theory.md`, `part-3-risk/02-risk-analysis.md` | 合并 |
| 6.1 特征工程 | `part-4-ml/01-feature-engineering.md` | 保留 |
| 6.2 XGBoost | `part-4-ml/02-xgboost-factor.md` | 保留 |
| 6.3 LSTM | `part-4-ml/03-lstm.md` | 保留 |
| 6.4 过拟合 | `part-3-risk/01-overfitting-cv.md`, `part-3-risk/03-strategy-diagnosis.md` | 合并 |
| 7.1 数据源 | `part-5-live/01-data-sources.md` | 保留 |
| 7.2 资金管理 | `part-5-live/02-execution-capital.md` | 保留 |
| 7.3 毕业设计 | `part-5-live/03-graduation-project.md` | 保留+增强 |
