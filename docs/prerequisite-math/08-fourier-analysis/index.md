---
title: "08 傅里叶分析"
description: "傅里叶级数、傅里叶变换的定义与手算实例，频域直觉，以及量化金融中的频谱分析与周期识别"
---

# 08 傅里叶分析

> 傅里叶分析是信号处理的数学语言——它将时间序列从"时域"变换到"频域"，让隐藏的周期性模式无所遁形。在量化金融中，从识别商业周期到去除市场微观结构噪音，处处可见傅里叶的身影。

---

## 一、傅里叶级数（Fourier Series）

### 1.1 定义

任何一个周期为 $T$ 的**周期函数** $f(t)$ 都可以分解为三角函数的无穷级数：

$$
f(t) = \frac{a_0}{2} + \sum_{n=1}^{\infty} \left[ a_n \cos\left(\frac{2\pi n t}{T}\right) + b_n \sin\left(\frac{2\pi n t}{T}\right) \right]
$$

其中系数由以下公式给出：

$$
a_n = \frac{2}{T} \int_0^T f(t) \cos\left(\frac{2\pi n t}{T}\right) dt,\quad
b_n = \frac{2}{T} \int_0^T f(t) \sin\left(\frac{2\pi n t}{T}\right) dt
$$

- $n=1$ 称为**基波**（fundamental），频率 $f_0 = 1/T$
- $n=2,3,\dots$ 称为**谐波**（harmonics），频率为 $n \cdot f_0$

### 1.2 手算实例：方波的傅里叶系数

考虑一个周期为 $T=2\pi$ 的**方波** $f(t)$：

$$
f(t) = \begin{cases}
+1, & 0 < t < \pi \\
-1, & \pi < t < 2\pi
\end{cases}
$$

方波是奇函数，因此所有 $a_n = 0$。只需计算 $b_n$：

$$
b_n = \frac{2}{T} \int_0^T f(t) \sin(nt) dt
= \frac{1}{\pi} \left[ \int_0^\pi (+1) \sin(nt) dt + \int_\pi^{2\pi} (-1) \sin(nt) dt \right]
$$

**分步手算**（以 $n=1$ 为例）：

| 步骤 | 计算 | 结果 |
|------|------|------|
| 积分 1 | $\int_0^\pi \sin(t) dt = [-\cos(t)]_0^\pi = [-(-1)] - [-1] = 1 + 1 = 2$ | $2$ |
| 积分 2 | $\int_\pi^{2\pi} (-\sin(t)) dt = -[-\cos(t)]_\pi^{2\pi} = [\cos(t)]_\pi^{2\pi} = 1 - (-1) = 2$ | $2$ |
| 求和 | $2 + 2 = 4$ | $4$ |
| 系数 | $b_1 = \frac{1}{\pi} \times 4 = \frac{4}{\pi}$ | $\frac{4}{\pi} \approx 1.2732$ |

**通用公式**：对于方波，$b_n = \frac{4}{n\pi}$ 对奇数 $n$，$b_n = 0$ 对偶数 $n$。

| 谐波阶数 $n$ | $b_n = \frac{4}{n\pi}$ | 近似值 |
|-------------|------------------------|--------|
| 基波 $n=1$ | $4/\pi$ | $1.2732$ |
| 3 次谐波 $n=3$ | $4/(3\pi)$ | $0.4244$ |
| 5 次谐波 $n=5$ | $4/(5\pi)$ | $0.2546$ |
| 7 次谐波 $n=7$ | $4/(7\pi)$ | $0.1819$ |

方波的 $N=1$ 近似（仅基波）：

$$
f(t) \approx \frac{4}{\pi} \sin(t)
$$

$N=3$ 近似（基波 + 3 次 + 5 次谐波）：

$$
f(t) \approx \frac{4}{\pi} \sin(t) + \frac{4}{3\pi} \sin(3t) + \frac{4}{5\pi} \sin(5t)
$$

> **Quant Link**：金融时间序列中的周期性信号（如季节性波动率模式）可以类似地分解为**频率分量**。方波近似中，**Gibbs 现象**（在跳变处有过冲）对应了市场中异常事件（如财报发布）附近的过度反应。

---

## 二、傅里叶变换（Fourier Transform）

### 2.1 定义

傅里叶变换将**非周期**函数 $f(t)$ 从时域变换到频域：

$$
F(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt
$$

逆变换：

$$
f(t) = \frac{1}{2\pi} \int_{-\infty}^{\infty} F(\omega) e^{i\omega t} d\omega
$$

- $F(\omega)$ 是复数，表示频率 $\omega$ 处的**幅度**和**相位**
- $|F(\omega)|$ 称为**幅度谱**（amplitude spectrum）

### 2.2 手算实例：高斯函数的傅里叶变换

令 $f(t) = e^{-t^2}$（标准高斯函数）：

$$
F(\omega) = \int_{-\infty}^{\infty} e^{-t^2} e^{-i\omega t} dt
= \int_{-\infty}^{\infty} e^{-(t^2 + i\omega t)} dt
$$

**配方法**：$t^2 + i\omega t = (t + \frac{i\omega}{2})^2 + \frac{\omega^2}{4}$

$$
F(\omega) = e^{-\omega^2/4} \int_{-\infty}^{\infty} e^{-(t + \frac{i\omega}{2})^2} dt
$$

利用高斯积分 $\int_{-\infty}^{\infty} e^{-u^2} du = \sqrt{\pi}$：

$$
F(\omega) = \sqrt{\pi} \cdot e^{-\omega^2/4}
$$

| $\omega$ | $F(\omega) = \sqrt{\pi} \cdot e^{-\omega^2/4}$ |
|----------|-----------------------------------------------|
| $0$ | $\sqrt{\pi} \approx 1.7725$ |
| $1$ | $\sqrt{\pi} \cdot e^{-0.25} \approx 1.3807$ |
| $2$ | $\sqrt{\pi} \cdot e^{-1} \approx 0.6520$ |
| $3$ | $\sqrt{\pi} \cdot e^{-2.25} \approx 0.1880$ |

高斯函数的傅里叶变换仍是高斯函数——这说明高斯函数在时域和频域中都是"最集中"的，恰好对应了**海森堡不确定性原理**的下界。

> **Quant Link**：在**波动率建模**中，不同时间尺度的波动率（如日频 vs 月频）的关系可以通过傅里叶分析描述。**均方根波动率** $\sigma_{\text{RMS}}$ 是所有频率分量的积分。

---

## 三、频域直觉：时间序列的"另一面"

### 3.1 时域 vs 频域

| 视角 | 横轴 | 观察什么 | 典型问题 |
|------|------|----------|----------|
| 时域 | 时间 $t$ | 价格 $P(t)$ 如何随时间变化 | 价格是否趋势上涨？ |
| 频域 | 频率 $\omega$ | 不同频率成分的幅度 $|F(\omega)|$ | 价格是否存在 3 个月周期？ |

**核心直觉**：任何看似不规则的时间序列都可以看作**多个正弦波**的叠加，每个正弦波有其特定的频率、幅度和相位。

### 3.2 从时域到频域意味着什么？

- **低频**（大周期）：长期趋势、商业周期（~3-5 年）、宏观因子
- **中频**（中等周期）：季节性（~1 年）、财报周期（~3 个月）
- **高频**（短周期）：市场微观结构噪音、做市商报价跳跃

> **Quant Link**：在**HFT 策略**中，高频交易者通过傅里叶分析分解订单簿的更新速率，识别微观结构中的周期性模式，如每隔一定毫秒出现的**大宗交易（block trade）信号**。

---

## 四、Quant Link：金融时间序列的频谱分析

### 4.1 识别商业周期

对 GDP 增长率或股票指数收益率序列做傅里叶变换，通常会在以下频率处看到**尖峰**（显著周期）：

| 周期 | 对应频率（月$^{-1}$） | 可能来源 |
|------|----------------------|----------|
| 3-5 年 | $0.017$-$0.028$ | 经济周期（扩张/收缩） |
| 1 年 | $0.083$ | 季节性（销售旺季、税收效应） |
| 3 个月 | $0.333$ | 财报季节效应 |
| 1 个月 | $1.0$ | 月末效应、结算周期 |

### 4.2 频谱插值与缺口填充

在固定收益中，**频谱分析法**（Spectral Analysis）用于识别债券收益率曲线中的周期模式，帮助**填补流动性不足的期限缺口**。

> **Quant Link**：**Malliavin 和 Mancino (2002)** 提出了用傅里叶变换估计**已实现协方差**的方法——通过对价格增量做傅里叶变换并乘积，可以得到**同步且稳健的波动率和协方差估计**，避免了 Epps 效应（不同频率采样导致的相关系数低估）。

---

## 五、Python 示例：FFT 合成信号分解

```python
import numpy as np
import matplotlib.pyplot as plt

# --- 合成信号：两个正弦波 + 噪音 ---
np.random.seed(42)
fs = 1000          # 采样率 (Hz)
T = 2              # 信号时长 (秒)
t = np.linspace(0, T, int(fs * T), endpoint=False)

# 两个频率成分
f1, f2 = 5, 50     # Hz
signal = (1.0 * np.sin(2 * np.pi * f1 * t) +
          0.5 * np.sin(2 * np.pi * f2 * t))

# 添加噪音
noise = 0.3 * np.random.randn(len(t))
signal_noisy = signal + noise

# --- FFT ---
N = len(signal_noisy)
fft_vals = np.fft.fft(signal_noisy)
fft_freqs = np.fft.fftfreq(N, 1/fs)

# 取正频率部分并计算幅度谱
pos_mask = fft_freqs > 0
freqs = fft_freqs[pos_mask]
amplitude = 2.0 / N * np.abs(fft_vals[pos_mask])

# 找出主导频率
top_idx = np.argsort(amplitude)[-5:]  # 前 5 大幅度
print("主导频率分量:")
for idx in top_idx[::-1]:
    print(f"  频率 = {freqs[idx]:.2f} Hz, "
          f"幅度 = {amplitude[idx]:.4f}")

# --- 输出示例 ---
# 主导频率分量:
#   频率 = 5.00 Hz, 幅度 = 1.0012
#   频率 = 50.00 Hz, 幅度 = 0.5015
#   (其余为噪音引起的小幅度杂散频率)
```

**关键结论**：FFT 准确地恢复了合成信号的两个主导频率（5 Hz 和 50 Hz），幅度也与真实值（1.0 和 0.5）非常接近。在量化金融中，对收益率序列做 FFT 可以自动识别出**显著的周期性模式**。

---

### 5.1 用 FFT 分析实际收益率

```python
import yfinance as yf
# 下载标普 500 日收益率（示例，需联网）
# spx = yf.download('^GSPC', start='2010-01-01')['Adj Close']
# returns = np.diff(np.log(spx.values))  # 对数收益率
# 
# N = len(returns)
# fft_ret = np.fft.fft(returns)
# freqs = np.fft.fftfreq(N, d=1)  # d=1 表示日频
# 
# 正频率幅度
# pos = freqs > 0
# 周期 = 1/freqs[pos]  # 以交易日为单位
# 通过观察哪些周期对应的幅度显著异常，可以识别出季度效应、年度效应等
```

> **Quant Link**：实际应用中，金融收益率序列通常**不是**平稳的——FFT 仅适用于弱平稳序列。因此常配合**差分**或**Hodrick-Prescott 滤波**预处理后再做频谱分析。

---

## 小结

| 概念 | 公式 | 量化金融应用 |
|------|------|-------------|
| 傅里叶级数 | $f(t) = \frac{a_0}{2} + \sum a_n \cos(nt) + b_n \sin(nt)$ | 识别交易量、波动率的季节性模式 |
| 傅里叶变换 | $F(\omega) = \int f(t) e^{-i\omega t} dt$ | 收益率谱分析、因子周期检测 |
| FFT | $\mathcal{O}(N \log N)$ 快速算法 | 大规模时间序列的实时频谱估计 |
| 频谱分析 | $|F(\omega)|^2$ 作为功率谱 | 经济周期识别、日历效应验证 |

> **下一步**：掌握傅里叶分析后，学习 **09 数值计算**——处理计算机中实数的表示问题，以及数值求解无法解析计算的金融模型。
