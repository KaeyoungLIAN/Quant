# 0.5 回归分析与假设检验

> 对应 MIT 18.S096 L6: Regression Analysis
>
> 🎬 [看 L6 视频](https://youtu.be/8Fo_-BPfFkY) → 然后学本章代码

## 一句话

回归分析告诉你一个因子对收益是否有**统计显著的**影响——以及这个影响的**大小**和**方向**，附带 p-value 告诉你这个结论是否值得相信。

## 学习目标

学完本章你能：
- 用 OLS 估计单因子和多因子回归模型，理解 β、R²、p-value 的含义
- 用 t 检验和 F 检验判断因子是否显著
- 检测多重共线性（VIF）并正确解读回归结果
- 用 CAPM 和 Fama-French 风格因子模型计算 Alpha 和 Beta

## 核心内容

### 1. OLS 回归基础——y = Xβ + ε

最小二乘法（OLS）是量化金融里最常用的统计工具——它是 CAPM Beta、因子模型暴露、Alpha 计算的基础。

```python
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
from scipy import stats

# 1a. 手动计算 Beta
# 公式：β = Cov(rᵢ, rₘ) / Var(rₘ)

# 下载数据
spy = yf.download('SPY', start='2024-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()
aapl = yf.download('AAPL', start='2024-01-01', end='2024-12-31')['Adj Close'].pct_change().dropna()

# 对齐索引
returns = pd.concat({'SPY': spy, 'AAPL': aapl}, axis=1).dropna()

# 手动 Beta
cov = np.cov(returns['AAPL'], returns['SPY'])[0, 1]
var_market = np.var(returns['SPY'])
beta_manual = cov / var_market
print(f"手动计算 Beta = {beta_manual:.4f}")

# 1b. 用 statsmodels OLS —— 自动给出 p-value, R²
X = sm.add_constant(returns['SPY'])     # 加截距项
model = sm.OLS(returns['AAPL'], X).fit()
print(model.summary())
```

输出解读：
- `coef` 列：**β（SPY 的系数）** 和 **α（const 截距）**
- `P>|t|` 列：p-value，小于 0.05 说明系数在 5% 水平显著 ≠ 0
- `R-squared`：模型解释了多少收益方差

### 2. 假设检验——"这个因子真的有用吗？"

#### t 检验：单个系数是否显著

```python
# t 统计量的手动计算
beta = model.params['SPY']
beta_se = model.bse['SPY']    # 标准误
t_stat = beta / beta_se
p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=model.df_resid))

print(f"Beta t-stat = {t_stat:.3f}, p-value = {p_value:.4f}")
print(f"statsmodels 报告: t = {model.tvalues['SPY']:.3f}, p = {model.pvalues['SPY']:.4f}")
print(f"结论: Beta {'显著 ≠ 0' if p_value < 0.05 else '不显著于 0'} (5% 水平)")
```

**p-value 的量化含义：**
- p < 0.01 → **非常显著**（99% 置信度该因子有用）
- p < 0.05 → **显著**（标准阈值）
- p < 0.10 → **边缘显著**（可参考但谨慎）
- p ≥ 0.10 → **不显著**（无法排除该系数为 0）

#### F 检验：整个模型是否显著

```python
# F 检验：所有斜率系数是否同时为 0
f_stat = model.fvalue
f_pvalue = model.f_pvalue
print(f"F-stat = {f_stat:.3f}, p-value = {f_pvalue:.6f}")
print(f"结论: 模型整体{'显著' if f_pvalue < 0.05 else '不显著'}")
```

### 3. 多元回归与多重共线性

现实中一只股票受多个因子驱动。但多个自变量之间可能**高度相关**——这就是多重共线性。

```python
# 下载多个因子：MKT(SPY), SMB, HML (用相近 ETF 近似)
# SPY = 市场, IWM = 小盘股(SMB proxy), VTV = 价值股(HML proxy)

factors = yf.download(['SPY', 'IWM', 'VTV'], start='2024-01-01', end='2024-12-31')['Adj Close']
factor_returns = factors.pct_change().dropna()
factor_returns.columns = ['MKT', 'SMB', 'HML']

# 回归 AAPL 对三个因子
X_multi = sm.add_constant(factor_returns)
model_multi = sm.OLS(returns['AAPL'], X_multi).fit()
print(model_multi.summary())
```

#### VIF（方差膨胀因子）——共线性的探测器

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 计算 VIF
X_array = sm.add_constant(factor_returns).values
vif_data = pd.DataFrame()
vif_data['variable'] = ['const', 'MKT', 'SMB', 'HML']
vif_data['VIF'] = [variance_inflation_factor(X_array, i) for i in range(X_array.shape[1])]
print(vif_data)

# VIF 判断标准
# VIF = 1    → 完全无共线性
# VIF < 5    → 可接受
# VIF 5–10   → 中等共线性，值得注意
# VIF > 10   → 严重共线性，需处理
```

**处理多重共线性的方法：**
1. 剔除高度相关的因子之一
2. 用 PCA 将相关因子合成为独立主成分
3. 用正则化回归（Ridge/Lasso）

### 4. 回归在量化中的应用

#### CAPM 回归——Alpha 就是截距

CAPM 说：$R_i - R_f = \alpha + \beta(R_m - R_f) + \varepsilon$

其中 $\alpha$ 就是**超额收益**——如果显著 > 0，说明股票跑赢了市场风险调整后的预期。

```python
# CAPM 回归
rf = 0.05 / 252  # 假设无风险利率 5% 年化 → 日化

# 计算超额收益
aapl_excess = returns['AAPL'] - rf
spy_excess = returns['SPY'] - rf

X_capm = sm.add_constant(spy_excess)
capm_model = sm.OLS(aapl_excess, X_capm).fit()
print(capm_model.summary())

alpha = capm_model.params['const']
alpha_pval = capm_model.pvalues['const']
beta = capm_model.params['SPY']
annual_alpha = alpha * 252  # 年化 Alpha

print(f"\nCAPM 结果:")
print(f"  Alpha (日) = {alpha:.6f}")
print(f"  Alpha (年化) = {annual_alpha:.4%}")
print(f"  Alpha p-value = {alpha_pval:.4f}")
print(f"  Beta = {beta:.4f}")
print(f"  Alpha 显著{'!' if alpha_pval < 0.05 else '（不显著）'}")
```

#### 因子模型——Fama-French 风格

```python
# AAPL 的三因子回归
# Rᵢ - R_f = α + β₁(Rₘ - R_f) + β₂(Rₛₘₐₗₗ - R_big) + β₃(R_ᵥₐₗᵤₑ - R_₉ᵣₒᵤᵽ) + ε

# 用 factor_returns (SPY≈MKT, IWM≈SMB, VTV≈HML) 做三因子
X_ff = sm.add_constant(factor_returns)
ff_model = sm.OLS(returns['AAPL'] - rf, X_ff).fit()
print(ff_model.summary())

# 关键解读
alpha_ff = ff_model.params['const']
print(f"\n三因子模型 Alpha (年化) = {alpha_ff * 252:.4%}")
print(f"因子暴露: β_MKT = {ff_model.params['MKT']:.3f}, "
      f"β_SMB = {ff_model.params['SMB']:.3f}, "
      f"β_HML = {ff_model.params['HML']:.3f}")
```

**量化意义：**
- **Alpha（截距）**：不能被市场、规模、价值因子解释的超额收益——真正的"选股能力"
- **Beta（因子暴露）**：股票对每个因子的敏感度
- 如果 Alpha 显著 > 0，说明选股策略有效；如果不显著，收益完全来自因子暴露

#### 回归诊断速查表

| 指标 | 范围 | 含义 |
|------|------|------|
| R² | 0–1 | 因子解释的收益方差比例 |
| p-value（系数） | < 0.05 | 该因子有统计显著的边际影响 |
| F 检验 p-value | < 0.05 | 模型整体显著 |
| VIF | > 5–10 | 存在多重共线性 |
| Durbin-Watson | ≈ 2 | 残差无自相关（合理） |

## 深度阅读

- Wiki → [ANOVA 与方差分析](/prerequisite-math/04-statistics/4.3-anova)
- Wiki → [因子模型](/quant-finance/2.3-factor-models)

## 练习

### 选择题

1. OLS 回归中，t 统计量 = β̂ / SE(β̂) 用于检验：
   - A. 所有系数是否同时为 0
   - B. 单个系数是否等于 0
   - C. 模型是否拟合良好
   - D. 数据是否正态分布

2. R² = 0.65 意味着：
   - A. 65% 的预测值在真实值的 65% 范围内
   - B. 因子解释了 65% 的收益方差
   - C. 有 65% 的概率因子是有效的
   - D. 模型有 65% 的显著性

3. VIF > 10 表明：
   - A. 模型拟合很好
   - B. 存在严重的多重共线性
   - C. 残差异方差
   - D. 数据量不足

4. Fama-French 三因子模型中，Alpha 显著为正意味着：
   - A. 股票有正的 Beta
   - B. 股票有正的超额收益，不能用市场/规模/价值因子解释
   - C. 股票属于大市值公司
   - D. 股票波动率低

### 编程题

**题目：** 下载 TSLA 和 SPY 2024 年数据，做 CAPM 回归。TSLA 的 Alpha 是否统计显著？（α ≠ 0 在 5% 水平？）

```python
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm

# 你的代码
```

### 填空题

CAPM 回归方程是 $R_i - R_f = \\_\\_\\_\\_ + \\_\\_\\_\\_ (R_m - R_f) + \\varepsilon$，其中截距项称为 \\_\\_\\_\\_，代表不能被市场风险解释的超额收益。VIF 大于 \\_\\_\\_\\_ 通常认为是严重共线性的信号。

## 掌握检查
