<template>
  <div class="quiz-section">
    <h2 class="quiz-title">📝 练习</h2>

    <!-- 选择题 -->
    <div v-for="(q, qi) in questions" :key="'q' + qi" class="question-block">
      <p class="question-text">{{ qi + 1 }}. {{ q.text }}</p>
      <div class="options">
        <label
          v-for="(opt, oi) in q.options"
          :key="oi"
          class="option"
          :class="{ selected: q.selected === oi, correct: q.showResult && oi === q.correct, wrong: q.showResult && q.selected === oi && oi !== q.correct }"
          @click="selectOption(qi, oi)"
        >
          <span class="option-key">{{ 'ABCD'[oi] }}</span>
          <span class="option-text">{{ opt }}</span>
          <span v-if="q.showResult && oi === q.correct" class="mark correct-mark">✓</span>
          <span v-if="q.showResult && q.selected === oi && oi !== q.correct" class="mark wrong-mark">✗</span>
        </label>
      </div>
      <div v-if="q.showResult && q.selected === q.correct" class="feedback correct">
        ✅ 正确！{{ q.feedback || '' }}
      </div>
      <div v-else-if="q.showResult" class="feedback wrong">
        ❌ {{ q.feedback || `正确答案是 ${'ABCD'[q.correct]}` }}
      </div>
    </div>

    <!-- 论述题 -->
    <div class="essay-section">
      <p class="question-text">💬 论述题</p>
      <p class="essay-hint">{{ essayPrompt }}</p>
      <textarea
        v-model="essayAnswer"
        placeholder="输入你的回答..."
        rows="4"
        :disabled="essaySubmitted"
      ></textarea>
      <div class="essay-actions">
        <button
          v-if="!essaySubmitted"
          class="submit-btn"
          :disabled="!essayAnswer.trim() || judging"
          @click="submitEssay"
        >
          {{ judging ? '判题中...' : '📮 提交判题' }}
        </button>
        <button v-if="essaySubmitted" class="retry-btn" @click="resetEssay">
          🔄 重新回答
        </button>
        <button v-if="!essaySubmitted && essayAnswer.trim()" class="mark-done-btn" @click="markChapterDone">
          ✅ 标记本章完成
        </button>
      </div>
      <div v-if="judgeResult" class="judge-result">
        <div class="judge-verdict" :class="judgeResult.passed ? 'passed' : 'failed'">
          {{ judgeResult.passed ? '✅ 通过' : '❌ 需要改进' }}
        </div>
        <div class="judge-feedback">{{ judgeResult.feedback }}</div>
        <ul v-if="judgeResult.suggestions.length" class="judge-suggestions">
          <li v-for="(s, si) in judgeResult.suggestions" :key="si">{{ s }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData } from 'vitepress'

const { page } = useData()

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'

// ─── Chapter-specific questions ────────────────────────────

const EXERCISES = {
  '01-getting-started/01-setup': {
    questions: [
      { text: "安装完 Python 和 jupyter 后，在终端输入什么命令可以启动 Jupyter Notebook？", options: ["`start jupyter`", "`jupyter notebook`", "`run jupyter`", "`python jupyter`"], correct: 1, feedback: "`jupyter notebook` 启动本地 Notebook 服务器。" },
      { text: "在 Jupyter 单元格中运行代码的快捷键是？", options: ["`Ctrl + Enter`", "`Enter`", "`Shift + Enter`", "`Alt + Enter`"], correct: 2, feedback: "`Shift+Enter` 运行并跳转到下一格。" },
      { text: "以下哪个不是本章安装的量化库？", options: ["`numpy`", "`scikit-learn`", "`pandas`", "`yfinance`"], correct: 1, feedback: "scikit-learn 是 ML 库，非本章必需。" },
    ],
    essay: "请用一段话描述你现在的开发环境，包括：你的电脑是什么系统？Python 版本是多少？你对接下来学量化有什么期待？",
  },
  '01-getting-started/02-first-data': {
    questions: [
      { text: "`yfinance` 是干什么用的？", options: ["画 K 线图", "下载股票数据", "做机器学习", "算数学公式"], correct: 1, feedback: "yfinance 从 Yahoo Finance 下载股票历史数据。" },
      { text: "OHLCV 中的 **C** 代表什么？", options: ["开盘价", "最高价", "收盘价", "成交量"], correct: 2, feedback: "C = Close（收盘价）。" },
      { text: "`data.head()` 显示数据的哪一部分？", options: ["最后几行", "随机几行", "前几行", "中间几行"], correct: 2, feedback: "head() 默认显示前 5 行。" },
    ],
    essay: "假设有人问你在量化投资中「每天的价格数据包含什么」，你会怎么用一句话解释？",
  },
  '01-getting-started/03-first-chart': {
    questions: [
      { text: "K 线图中，**实体**代表什么？", options: ["开盘价到收盘价的区间", "最高价到最低价的区间", "成交量的大小", "当天的涨跌幅比例"], correct: 0, feedback: "实体表示开盘价与收盘价之间的区间。" },
      { text: "红色（阴线）的 K 线意味着：", options: ["收盘价 > 开盘价", "收盘价 < 开盘价", "成交量增加", "价格创出新高"], correct: 1, feedback: "阴线表示收盘价低于开盘价。" },
      { text: "`mplfinance` 中 `volume=True` 的作用是：", options: ["显示交易量", "放大图表", "调整颜色", "显示数据标签"], correct: 0, feedback: "在 K 线下方显示成交量柱。" },
    ],
    essay: "观察你画的 K 线图。最近十天是涨得多还是跌得多？哪天的波动最大？",
  },
  '01-getting-started/04-set-goal': {
    questions: [
      { text: "这套课程一共包含几个章节？", options: ["5 个", "6 个", "7 个", "8 个"], correct: 2, feedback: "7 章：出发→金融扫盲→数学→Python→策略→ML→实战。" },
      { text: "以下哪个不是量化学习的三个基础领域？", options: ["数学", "英语", "编程", "金融"], correct: 1, feedback: "三基础：数学 + 编程 + 金融。" },
    ],
    essay: "你学量化的最终目的是什么？如果一年后的今天你已经学会了你想学的一切——那时的你在做什么？",
  },
  '02-finance-basics/01-instruments': {
    questions: [
      { text: "以下哪个 ETF 追踪的是美国科技股？", options: ["SPY", "TLT", "QQQ", "GLD"], correct: 2, feedback: "QQQ 追踪纳斯达克 100（科技股）。" },
      { text: "当市场利率上升时，债券价格通常：", options: ["上涨", "下跌", "不变", "取决于股票市场"], correct: 1, feedback: "利率上升→折现率上升→债券价格下跌。" },
    ],
    essay: "用 200-300 字比较股票和债券的风险特征。",
  },
  '02-finance-basics/02-market-mechanism': {
    questions: [
      { text: "以下哪种订单可以保证成交价格但不保证一定成交？", options: ["市价单", "限价单", "止损单", "冰山订单"], correct: 1, feedback: "限价单保证价格但可能不成交。" },
      { text: "在流动性低的品种上交易，最可能遇到：", options: ["更低的佣金", "更大的滑点和市场冲击", "更快的成交速度", "更高的夏普比率"], correct: 1, feedback: "流动性低→买卖价差大→滑点大。" },
    ],
    essay: "为什么滑点对高频策略的影响远大于中低频策略？",
  },
  '02-finance-basics/03-time-value': {
    questions: [
      { text: "如果 APR = 12% 按月复利，APY 大约是多少？", options: ["12.00%", "12.68%", "13.00%", "12.50%"], correct: 1, feedback: "APY = (1+0.12/12)^12 - 1 ≈ 12.68%" },
      { text: "NPV 计算中折现率从 8% 提到 12%，NPV 会？", options: ["不变", "增加", "减少", "变为负数"], correct: 2, feedback: "折现率提高→现金流现值降低→NPV 减少。" },
    ],
    essay: "货币时间价值在量化策略的回测中有哪些应用？",
  },
  '02-finance-basics/04-risk-intro': {
    questions: [
      { text: "年化波动率 20% 意味着什么？", options: ["每年最多亏 20%", "收益在 ±20% 之间的概率约 68%", "每年必定亏 20%", "每天波动不超过 20%"], correct: 1, feedback: "正态假设下年收益 ±1σ 的概率约 68%。" },
      { text: "夏普比率 0.8，年化波动率 15%，无风险利率 3%，年化收益约？", options: ["12%", "15%", "18%", "21%"], correct: 1, feedback: "夏普=(R-3%)/15%=0.8 → R=15%" },
    ],
    essay: "有人说比特币过去十年涨了几百倍是最好的投资。请用波动率、最大回撤、夏普比率分析。",
  },
  '03-math-toolbox/01-linear-algebra': {
    questions: [
      { text: "向量 a=[1,2], b=[3,4]，a·b = ?", options: ["10", "11", "3", "7"], correct: 1, feedback: "1×3+2×4=11" },
      { text: "矩阵 A(5,3) 向量 v(3,)，A@v 结果形状：", options: ["(5,3)", "(5,)", "(3,)", "(5,3)"], correct: 1, feedback: "(5,3)×(3,) → (5,)" },
      { text: "PCA 第一主成分解释方差比例最高意味着：", options: ["数据主要由一个方向的变化驱动", "数据是随机的", "特征值都等于 1", "需要更多主成分"], correct: 0, feedback: "第一主成分方向方差最大。" },
      { text: "Beta > 1 意味着：", options: ["股票比市场波动大", "股票比市场波动小", "与市场无关", "收益率高于市场"], correct: 0, feedback: "Beta>1→波动放大倍数>1。" },
      { text: "特征值分解中较大特征值对应特征向量：", options: ["方差贡献最小的方向", "方差贡献最大的方向", "随机方向", "零向量"], correct: 1, feedback: "较大特征值=较大方差方向。" },
    ],
    essay: "",
  },
  '03-math-toolbox/02-probability': {
    questions: [
      { text: "蒙特卡洛模拟的适用场景是：", options: ["有解析解的问题", "没有解析解或太复杂的概率问题", "只需要点估计", "确定性问题"], correct: 1, feedback: "蒙特卡洛用于解析解不可行的概率问题。" },
      { text: "中心极限定理说：", options: ["原始数据是正态分布", "大样本均值趋近正态分布", "方差趋近零", "样本量越大越好"], correct: 1, feedback: "CLT：样本均值的分布渐近正态。" },
      { text: "条件概率 P(盈利|信号) 的含义：", options: ["信号出现时盈利的概率", "盈利时信号出现的概率", "二者同时发生的概率", "信号出现的概率"], correct: 0, feedback: "给定信号条件下盈利的条件概率。" },
      { text: "95% VaR=-2% 表示：", options: ["95%概率亏损超2%", "5%概率亏损超2%", "最多亏2%", "平均亏2%"], correct: 1, feedback: "VaR(95%)=5%分位数的绝对值。" },
    ],
    essay: "",
  },
  '03-math-toolbox/03-matrix-decomposition': {
    questions: [
      { text: "SVD 分解 UΣV^T 中 V 的列代表：", options: ["时间模式", "资产权重/主成分方向", "奇异值", "残差"], correct: 1, feedback: "V 的列是右奇异向量对应主成分方向。" },
      { text: "Cholesky 分解要求输入矩阵：", options: ["对称正定", "可逆", "对角矩阵", "正交矩阵"], correct: 0, feedback: "Cholesky 要求矩阵对称正定。" },
      { text: "条件数大的矩阵在求逆时会：", options: ["更快", "数值不稳定", "总是失败", "精度更高"], correct: 1, feedback: "条件数大→病态→求逆数值不稳定。" },
    ],
    essay: "",
  },
  '03-math-toolbox/04-stochastic-processes': {
    questions: [
      { text: "布朗运动 W(t) 的增量分布是：", options: ["W(t)-W(s)~N(0,t-s)", "W(t)-W(s)~N(0,t+s)", "~Uniform(-1,1)", "与时间无关"], correct: 0, feedback: "布朗运动增量~N(0,t-s)。" },
      { text: "几何布朗运动 S_T 服从：", options: ["正态分布", "对数正态分布", "泊松分布", "均匀分布"], correct: 1, feedback: "GBM 假设收益率正态→价格对数正态。" },
      { text: "Ito 引理中 d(log S) 比链式法则多出一项因为：", options: ["布朗运动的二次变分不为零", "数学家在搞复杂", "对数函数不连续", "随机过程不可微"], correct: 0, feedback: "布朗运动二次变分 dW²=dt，影响 Ito 公式。" },
      { text: "波动率拖累 (volatility drag) 的数值是：", options: ["σ", "σ²/2", "μ-σ", "σ√dt"], correct: 1, feedback: "μ_g = μ - σ²/2。" },
    ],
    essay: "",
  },
  '03-math-toolbox/05-regression': {
    questions: [
      { text: "t 统计量=β̂/SE(β̂) 用于检验：", options: ["所有系数是否同时为0", "单个系数是否等于0", "模型是否拟合良好", "数据是否正态"], correct: 1, feedback: "t 检验单个系数的显著性。" },
      { text: "R²=0.65 意味着：", options: ["65%预测在真实值65%范围", "因子解释65%收益方差", "有65%概率因子有效", "模型65%显著"], correct: 1, feedback: "R² 解释响应变量的方差比例。" },
      { text: "VIF>10 表明：", options: ["模型拟合很好", "严重多重共线性", "残差异方差", "数据量不足"], correct: 1, feedback: "VIF>10 表示严重多重共线性。" },
    ],
    essay: "",
  },
  '03-math-toolbox/06-var-commodity': {
    questions: [
      { text: "关于 VaR 的说法错误的是：", options: ["VaR(95%)=5%分位数绝对值", "VaR 满足次可加性", "参数法假设正态", "历史模拟法无需分布假设"], correct: 1, feedback: "VaR 不满足次可加性。" },
      { text: "Contango 意味着：", options: ["远期>现货", "远月<近月", "现货供应紧张", "展期收益为正"], correct: 0, feedback: "Contango：期货溢价远月>近月。" },
    ],
    essay: "",
  },
  '03-math-toolbox/07-time-series': {
    questions: [
      { text: "AR(1) y_t=0.8y_{t-1}+ε_t 的 PACF：", options: ["所有滞后显著", "lag 1 显著后截尾", "lag 2 显著后截尾", "lag 1 后线性衰减"], correct: 1, feedback: "AR(p) 的 PACF 在 lag p 后截尾。" },
      { text: "ADF 检验 p=0.32 意味着：", options: ["序列平稳", "有单位根需差分", "有强季节性", "模型拟合好"], correct: 1, feedback: "p>0.05 不拒绝原假设序列非平稳。" },
      { text: "两只 I(1) 序列协整意味着：", options: ["高度相关", "价差平稳可用配对交易", "协方差很大", "同行业"], correct: 1, feedback: "协整=线性组合 I(0)，价差合理。" },
    ],
    essay: "",
  },
  '03-math-toolbox/08-volatility': {
    questions: [
      { text: "收益率平方的 ACF 多滞后期显著说明：", options: ["收益率有自相关", "收益率平稳", "方差有自相关/波动率聚集", "有季节性"], correct: 2, feedback: "平方收益ACF显著=波动率聚集。" },
      { text: "GARCH(1,1) 中 α+β=0.99 表示：", options: ["波动率无记忆", "冲击消失快", "波动率持久性强", "参数不显著"], correct: 2, feedback: "α+β接近1=高持久性。" },
    ],
    essay: "",
  },
  '03-math-toolbox/10-portfolio-theory': {
    questions: [
      { text: "有效前沿上的组合特性：", options: ["夏普相同", "给定风险下收益最大", "权重相等", "波动率最低"], correct: 1, feedback: "有效前沿=Pareto 最优。" },
      { text: "CAPM 中 Alpha 代表：", options: ["市场超额", "系统风险", "无法由市场解释的超额收益", "无风险利率"], correct: 2, feedback: "Alpha=实际收益-CAPM 预期收益。" },
      { text: "Fama-French 三因子多加哪两个因子？", options: ["动量+流动性", "市值+价值", "波动+偏度", "行业+国家"], correct: 1, feedback: "SMB(市值)+HML(账面市值比)。" },
      { text: "马科维茨组合优化的主要实际问题是：", options: ["计算太复杂", "对输入参数太敏感", "只能用正态分布", "只适用于股票"], correct: 1, feedback: "参数敏感是最主要的实际问题。" },
    ],
    essay: "",
  },
  '04-python-quant/01-numpy-pandas': {
    questions: [
      { text: "np.array([1,2,3]) @ np.array([4,5,6]) = ?", options: ["32", "[4,10,18]", "形状不匹配", "6"], correct: 0, feedback: "点积=1×4+2×5+3×6=32" },
      { text: "Pandas shift(1) 的作用：", options: ["数据前移1行", "数据后移1行", "删除第一行", "计算差分"], correct: 0, feedback: "shift(1) 向下移动1行。" },
      { text: "年化波动率公式：", options: ["日标准差×√252", "日均值×252", "日标准差×252", "日最大值×√252"], correct: 0, feedback: "σ_annual=σ_daily×√252" },
      { text: "rolling(20).mean() 计算：", options: ["20个点的累加平均", "过去20个点的移动平均", "未来20个点的预测", "20个点的中位数"], correct: 1, feedback: "rolling(20) 用过去20个点计算。" },
    ],
    essay: "",
  },
  '04-python-quant/02-data-wrangling': {
    questions: [
      { text: "OHLCV 中 O 代表：", options: ["收盘价", "开盘价", "最高价", "成交量"], correct: 1, feedback: "O=Open（开盘价）。" },
      { text: "阳线表示：", options: ["Close<Open", "Close>Open", "High>Low", "Volume增加"], correct: 1, feedback: "阳线=收盘价>开盘价。" },
      { text: "复权收盘价考虑了什么？", options: ["通货膨胀", "分红和拆股", "手续费", "市场情绪"], correct: 1, feedback: "Adj Close 调整了分红和拆股。" },
    ],
    essay: "",
  },
  '04-python-quant/03-visualization': {
    questions: [
      { text: "十字星 K 线表示：", options: ["强力上涨", "强力下跌", "多空平衡/变盘信号", "成交量异常"], correct: 2, feedback: "十字星=开盘≈收盘多空平衡。" },
      { text: "mav=(5,10,20) 的作用：", options: ["画3条均线", "设置大小", "调整颜色", "设置时间范围"], correct: 0, feedback: "mav 参数画移动平均线。" },
      { text: "长上影线表示：", options: ["买方完全主导", "卖方在高位反击上涨遇阻", "趋势确立", "成交量放大"], correct: 1, feedback: "长上影线=价格上涨后被打回。" },
    ],
    essay: "",
  },
  '04-python-quant/04-backtest-framework': {
    questions: [
      { text: "signal.shift(1) 的目的是：", options: ["提高准确率", "避免前视偏差", "减少交易次数", "美化曲线"], correct: 1, feedback: "shift(1) 确保用前一天收盘信号交易。" },
      { text: "以下哪个是前视偏差？", options: ["用今天收盘价做今天信号", "用昨天成交量", "去除停牌日", "使用复权价"], correct: 0, feedback: "用今天收盘价做今天信号=未来数据。" },
      { text: "short=20,long=60 均线交叉策略：", options: ["20上穿60买入", "60上穿20买入", "价格突破20买入", "放量买入"], correct: 0, feedback: "短均线上穿长均线=金叉。" },
    ],
    essay: "",
  },
  '05-classic-strategies/01-trend-following': {
    questions: [
      { text: "趋势跟踪核心假设：", options: ["市场随机", "过去趋势会延续", "价格均值回复", "技术面>基本面"], correct: 1, feedback: "趋势跟踪=动量延续假设。" },
      { text: "MACD 金叉：", options: ["MACD上穿Signal", "MACD下穿Signal", "价格上穿MACD", "Signal上穿MACD"], correct: 0, feedback: "MACD线上穿信号线=金叉。" },
      { text: "海龟交易入场条件：", options: ["突破N日高点", "均线金叉", "MACD金叉", "放量"], correct: 0, feedback: "唐奇安通道突破入场。" },
    ],
    essay: "",
  },
  '05-classic-strategies/02-mean-reversion': {
    questions: [
      { text: "均值回归在什么市场最赚钱？", options: ["单边上涨", "震荡市场", "单边下跌", "高波动"], correct: 1, feedback: "震荡市均值回归有效。" },
      { text: "布林带突破上轨：", options: ["买入", "卖出/做空", "平仓", "加仓"], correct: 1, feedback: "突破上轨=超买→做空。" },
      { text: "RSI<30 通常解释为：", options: ["超买", "超卖", "正常", "趋势形成"], correct: 1, feedback: "RSI<30=超卖→反弹信号。" },
    ],
    essay: "",
  },
  '05-classic-strategies/03-stat-arb': {
    questions: [
      { text: "配对交易 Z-score > 2 应：", options: ["做多A做空B", "做空A做多B", "同时做多", "同时做空"], correct: 0, feedback: "Z>2 价差过高→做空价差。" },
      { text: "配对交易的最大风险：", options: ["协整断裂", "交易成本", "A和B", "没有风险"], correct: 2, feedback: "协整断裂+成本的组合风险。" },
    ],
    essay: "",
  },
  '05-classic-strategies/04-risk-management': {
    questions: [
      { text: "多因子组合的核心优势：", options: ["每个因子加倍赚钱", "因子间低相关分散风险", "减少交易次数", "降低手续费"], correct: 1, feedback: "低相关因子组合降低整体波动。" },
      { text: "风险平价的权重依据是：", options: ["历史收益", "历史风险/波动率", "主观判断", "夏普比率"], correct: 1, feedback: "风险平价=等风险贡献。" },
    ],
    essay: "",
  },
  '06-ml-strategies/01-feature-engineering': {
    questions: [
      { text: "以下哪个不是良好ML特征？", options: ["过去5天收益率", "股票名称", "滚动波动率", "成交量比"], correct: 1, feedback: "股票名称是无意义标识符。" },
      { text: "为什么原始价格不适合做特征？", options: ["价格不平稳", "价格变化无常", "非负", "原因A"], correct: 0, feedback: "非平稳序列导致伪回归。" },
      { text: "标签 shift(-5) 的含义：", options: ["用过去5天预测未来", "预测未来5天后的收益", "回溯5天的收益", "滚动5天窗口"], correct: 1, feedback: "shift(-5)=将未来5天后的收益对齐到今天。" },
    ],
    essay: "",
  },
  '06-ml-strategies/02-xgboost': {
    questions: [
      { text: "XGBoost 核心思想：", options: ["随机森林改进", "多棵树串行修正错误", "单棵决策树", "SVM"], correct: 1, feedback: "Boosting=串行修正残差。" },
      { text: "时间序列为什么不用随机分割？", options: ["防止前视偏差", "更方便", "代码更简单", "不需要"], correct: 0, feedback: "随机分割让未来信息泄露到训练集。" },
      { text: "max_depth=3 的作用：", options: ["加快训练", "防过拟合", "降低内存", "以上都是"], correct: 3, feedback: "限制树深度防止过拟合。" },
    ],
    essay: "",
  },
  '06-ml-strategies/03-lstm': {
    questions: [
      { text: "LSTM 相比 MLP 核心优势：", options: ["训练更快", "处理序列时间依赖", "不需归一化", "代码更短"], correct: 1, feedback: "LSTM 设计核心=长程依赖。" },
      { text: "LSTM 输入是3D张量因为：", options: ["为了兼容API", "表示样本/时间步/特征", "只是习惯", "加速GPU"], correct: 1, feedback: "3D=(batch,seq_len,features)" },
    ],
    essay: "",
  },
  '06-ml-strategies/04-overfitting': {
    questions: [
      { text: "过拟合的直接表现：", options: ["样本内夏普2.0样本外0.3", "样本内0.8样本外0.7", "两个都高", "两个都低"], correct: 0, feedback: "样本内→样本外大幅衰减=过拟合。" },
      { text: "减少过拟合最有效：", options: ["更多数据", "更少参数", "样本外测试", "以上都是"], correct: 2, feedback: "样本外测试是验证泛化的核心手段。" },
      { text: "滚动交叉验证的好处：", options: ["只需一个数据集", "测试策略在不同市场的稳定性", "总能高夏普", "不需清洗数据"], correct: 1, feedback: "滚动CV避免前视偏差并测试稳定性。" },
      { text: "数据窥探偏差指：", options: ["数据质量有问题", "反复调参直到找到好的", "数据泄露", "使用未来数据"], correct: 1, feedback: "反复在同一个数据集上试参数=数据窥探。" },
    ],
    essay: "",
  },
  '07-live/01-data-sources': {
    questions: [
      { text: "回测最需要的数据精度：", options: ["实时tick", "精确历史OHLCV", "任意数据", "只需收盘价"], correct: 1, feedback: "精确历史OHLCV是回测基础。" },
      { text: "数据清洗需检查OHLC关系因为：", options: ["格式要求", "数据供应商可能出错", "为了美观", "不需检查"], correct: 1, feedback: "保证OHLC的逻辑一致性。" },
      { text: "持仓3个月的策略应该用：", options: ["分钟数据", "日线数据", "周线数据", "B或C"], correct: 3, feedback: "低频策略可用日线或周线。" },
    ],
    essay: "",
  },
  '07-live/02-capital-mgmt': {
    questions: [
      { text: "凯利公式的作用：", options: ["选股", "计算最优下注比例", "回测策略", "数据清洗"], correct: 1, feedback: "凯利公式最大化长期复利增长率。" },
      { text: "半凯利比全凯利好的原因：", options: ["赚更多", "更保守降低破产风险", "计算更简单", "没区别"], correct: 1, feedback: "半凯利降低波动和破产概率。" },
      { text: "滑点对以下哪种策略影响最大？", options: ["年交易5次", "月交易20次", "日交易50次", "周交易2次"], correct: 2, feedback: "交易越频繁滑点影响越大。" },
    ],
    essay: "",
  },
}

// ─── State ─────────────────────────────────────────────────

const questionData = ref([])
const essayPrompt = ref('')
const essayAnswer = ref('')
const essaySubmitted = ref(false)
const judging = ref(false)
const judgeResult = ref(null)

const currentSlug = computed(() => {
  const relPath = page.value.relativePath.replace(/\.md$/, '')
  // Remove leading learn/ if present
  return relPath.replace(/^learn\//, '')
})

onMounted(() => {
  const ex = EXERCISES[currentSlug.value]
  if (!ex) return
  questionData.value = ex.questions.map(q => ({
    ...q,
    selected: null,
    showResult: false,
  }))
  essayPrompt.value = ex.essay || ''
})

function selectOption(qi, oi) {
  const q = questionData.value[qi]
  if (q.showResult) return
  q.selected = oi
  q.showResult = true
}

async function submitEssay() {
  if (!essayAnswer.value.trim() || judging.value) return
  judging.value = true
  judgeResult.value = null
  try {
    const res = await fetch(`${API_BASE}/api/v1/progress/judge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chapter_key: currentSlug.value,
        question: essayPrompt.value,
        answer: essayAnswer.value,
      }),
    })
    const data = await res.json()
    judgeResult.value = data
    essaySubmitted.value = true
  } catch (e) {
    judgeResult.value = {
      passed: false,
      feedback: '网络错误，请稍后重试。',
      suggestions: [],
    }
  } finally {
    judging.value = false
  }
}

function resetEssay() {
  essaySubmitted.value = false
  judgeResult.value = null
  essayAnswer.value = ''
}

async function markChapterDone() {
  try {
    await fetch(`${API_BASE}/api/v1/progress/advance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_key: currentSlug.value }),
    })
    alert('✅ 本章已标记完成！')
  } catch {
    alert('保存失败，请重试')
  }
}
</script>

<style scoped>
.quiz-section {
  margin-top: 40px;
  padding: 24px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
}
.quiz-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  margin-top: 0 !important;
}
.question-block {
  margin-bottom: 20px;
}
.question-text {
  font-weight: 500;
  margin-bottom: 8px !important;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  background: var(--vp-c-bg);
}
.option:hover {
  border-color: var(--vp-c-brand-2);
}
.option.selected {
  border-color: var(--vp-c-brand-1);
}
.option.correct {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
}
.option.wrong {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
}
.option-key {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--vp-c-bg-mute);
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
.option.correct .option-key {
  background: #22c55e;
  color: #fff;
}
.option.wrong .option-key {
  background: #ef4444;
  color: #fff;
}
.option-text {
  flex: 1;
  font-size: 14px;
}
.mark {
  font-size: 16px;
  font-weight: 700;
}
.correct-mark { color: #22c55e; }
.wrong-mark { color: #ef4444; }
.feedback {
  margin-top: 6px;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 6px;
}
.feedback.correct {
  color: #166534;
  background: rgba(34, 197, 94, 0.1);
}
.feedback.wrong {
  color: #991b1b;
  background: rgba(239, 68, 68, 0.1);
}

.essay-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--vp-c-divider);
}
.essay-hint {
  font-size: 14px;
  color: var(--vp-c-text-2);
  margin-bottom: 10px !important;
  line-height: 1.6;
}
textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}
textarea:focus {
  border-color: var(--vp-c-brand-1);
}
textarea:disabled {
  opacity: 0.6;
}
.essay-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.submit-btn, .retry-btn, .mark-done-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn {
  background: var(--vp-c-brand-1);
  color: #fff;
}
.submit-btn:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.retry-btn {
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-divider);
}
.mark-done-btn {
  background: #22c55e;
  color: #fff;
}
.mark-done-btn:hover {
  background: #16a34a;
}
.judge-result {
  margin-top: 14px;
  padding: 14px;
  border-radius: 8px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
}
.judge-verdict {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
}
.judge-verdict.passed { color: #22c55e; }
.judge-verdict.failed { color: #ef4444; }
.judge-feedback {
  font-size: 14px;
  line-height: 1.6;
  color: var(--vp-c-text-1);
}
.judge-suggestions {
  margin-top: 8px;
  padding-left: 18px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}
.judge-suggestions li {
  margin-bottom: 4px;
}
</style>
