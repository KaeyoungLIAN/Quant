---
title: "CloakBrowser — C++ 级别的反检测浏览器"
description: "在 C++ 源码层修补 Chromium 指纹的隐身浏览器，通过 Cloudflare Turnstile 等 30+ 检测，可作 Playwright/Puppeteer 的即插即用替代"
---

# CloakBrowser — C++ 级别的反检测浏览器

> 不是 JS 注入、不是配置补丁——是在 Chromium 的 C++ 源码层修改浏览器指纹的隐身方案。反爬系统判定它为正常浏览器，**因为它就是**。

---

## 背景

网页反爬虫技术已经从简单的 User-Agent 检查进化到了**浏览器指纹检测**。主流检测包括：

- Canvas/WebGL 指纹
- 字体列表与渲染
- GPU 与 WebRTC 特征
- 自动化信号（`navigator.webdriver`、CDP 行为）
- 网络时间精度
- 屏幕与窗口属性

传统规避方案（`playwright-stealth`、`undetected-chromedriver`）通过在 JS 层覆盖属性来伪装，但**检测方也在 JS 层验证**——猫鼠游戏，检测方永远占优。

**CloakBrowser 的思路**：去掉"伪装"这一步，直接在 Chromium 编译阶段改源码。

---

## 核心原理

### 源码级补丁

CloakBrowser 维护了 **58 个 C++ 源码补丁**，覆盖：

| 补丁类别 | 覆盖范围 | 效果 |
|----------|---------|------|
| Canvas | 指纹噪声注入、TextMetrics 精度修改 | 与正常浏览器无异 |
| WebGL | 渲染器字符串、GPU 型号、最大纹理尺寸 | 不暴露 headless 特征 |
| Audio | AudioContext 指纹时序 | 人类浏览器级别 |
| 字体 | 系统字体列表 | 与安装环境一致 |
| WebRTC | IP 泄露防护、设备枚举 | 不暴露真实 IP |
| 自动化 | CDP 输入行为、`navigator.webdriver` | 完全移除自动化痕迹 |

### 不自带代理

CloakBrowser 本身**不包含代理功能**。它只解决**浏览器指纹**问题。如果需要绕过 IP 限制，需要搭配 residential proxy：

```python
from cloakbrowser import launch

browser = launch(
    proxy="http://user:pass@residential-proxy:port",
    geoip=True,       # 自动匹配时区/locale 到代理 IP
    headless=False,    # 某些站点检测 headless
    humanize=True,     # 类人鼠标曲线、键盘时序、滚动模式
)
```

> **Quant Link**：爬取交易所数据、新闻情绪分析、另类数据收集时，经常需要突破 Cloudflare 保护。CloakBrowser 能让你用标准 Playwright API 完成这些任务，无需额外反爬策略。

---

## 对比

| 特性 | Playwright | playwright-stealth | undetected-chromedriver | Camoufox | **CloakBrowser** |
|------|-----------|-------------------|------------------------|----------|-----------------|
| reCAPTCHA v3 评分 | 0.1 | 0.3-0.5 | 0.3-0.7 | 0.7-0.9 | **0.9** |
| Cloudflare Turnstile | ❌ | 偶发 | 偶发 | ✅ | **✅** |
| 补丁层面 | 无 | JS 注入 | 配置补丁 | C++ (Firefox) | **C++ (Chromium)** |
| 浏览器引擎 | Chromium | Chromium | Chrome | Firefox | **Chromium** |
| Playwright API | 原生 | 原生 | 无(Selenium) | 无 | **原生** |
| 维护状态 | ✅ | 停滞 | 停滞 | 不稳定 | **活跃** |

---

## 快速上手

### 安装

```bash
pip install cloakbrowser
```

首次运行自动下载 stealth Chromium 二进制文件（~200MB，本地缓存）。

### 基础使用（3 行代码）

```python
from cloakbrowser import launch

browser = launch()
page = browser.new_page()
page.goto("https://example.com")
browser.close()
```

完全兼容 Playwright API——直接把 `from playwright import ...` 换成 `from cloakbrowser import ...` 即可。

### 测试反爬效果

```docker
docker run --rm cloakhq/cloakbrowser cloaktest
```

会依次测试 30+ 检测站点，输出通过/失败结果。

### JavaScript 版本

```javascript
import { launch } from 'cloakbrowser';

const browser = await launch();
const page = await browser.newPage();
await page.goto('https://example.com');
await browser.close();
```

也支持 Puppeteer：`import { launch } from 'cloakbrowser/puppeteer'`

---

## 实战：爬取 Cloudflare 保护的行情数据

```python
from cloakbrowser import launch
import json

browser = launch(
    proxy="http://user:pass@your-proxy:port",
    geoip=True,
    humanize=True,
)
page = browser.new_page()

# 访问受 Cloudflare 保护的行情页面
page.goto("https://some-exchange.com/api/ticker")

# 正常读取响应
content = page.text_content("pre")
data = json.loads(content)
print(data)
```

---

## 注意事项

| 问题 | 说明 |
|------|------|
| 代理 | 需要 residential proxy（数据中心 IP 仍会被封） |
| headless 检测 | 部分站点检测 headless 模式，设置 `headless=False` |
| 维护成本 | 58 个 C++ 补丁需要随 Chromium 版本更新而维护，不是零成本 |
| 商业可行性 | 开源免费，但有 `ko-fi` 支持渠道，长期可持续性待观察 |

---

## 参考

- GitHub: [github.com/CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser)
- 安装: `pip install cloakbrowser` / `npm install cloakbrowser`
