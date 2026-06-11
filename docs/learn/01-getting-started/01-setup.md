# 1.1 安装 Python + Jupyter

> 本章唯一的目标：**让代码在你电脑上跑起来**。不用理解每行代码什么意思——先跑通，再理解。

## 一句话

量化开发只需要装三样东西：Python 解释器、Jupyter Notebook、五个库。装完你就能跑代码了。

## 学习目标

学完本章你能：
- 在你的电脑上安装 Python
- 用 pip 安装 Python 库
- 启动 Jupyter Notebook 并创建第一个 notebook
- 运行人生第一行 Python 代码

## 核心内容

### 1. 安装 Python

去 [python.org](https://www.python.org/downloads/) 下载 Python。

**关键提示：**
- Windows：安装时**务必勾选「Add Python to PATH」**
- macOS：下载 .pkg 文件直接安装
- Linux：`sudo apt install python3 python3-pip`

装完后验证：

```bash
python --version
```

你应该看到类似 `Python 3.12.x` 的输出。如果看到这个，恭喜——Python 装好了。

> 💡 **如果卡住了：** 90% 的问题都是没有勾选「Add Python to PATH」。重装一次，勾上就好。

### 2. 安装 Jupyter Notebook

Jupyter Notebook 是量化开发者最常用的工具——它让你在浏览器里写代码，代码和结果显示在一起。

打开终端（Windows 用 CMD 或 PowerShell，macOS/Linux 用 Terminal），输入：

```bash
pip install jupyter
```

等它跑完。网速决定时间，一般 1-3 分钟。

### 3. 安装量化工具库

一行命令装完所有需要的东西：

```bash
pip install numpy pandas yfinance mplfinance
```

这四个库分别是：
- **numpy** — 数值计算的基础（数组、矩阵运算）
- **pandas** — 数据分析神器（表格操作、时间序列）
- **yfinance** — 获取股票数据的接口（雅虎财经）
- **mplfinance** — 画 K 线图的专用工具

> ⏳ pip 会自动安装依赖，耐心等待就行。看到 `Successfully installed...` 就完成了。

### 4. 启动 Jupyter

在终端输入：

```bash
jupyter notebook
```

浏览器会自动打开一个页面（地址通常是 `http://localhost:8888`）。这就是 Jupyter 的主界面。

点击右上角 **New → Python 3 (ipykernel)**，创建一个新的 notebook。

### 5. 跑第一行代码

在 notebook 的单元格里输入：

```python
print("Hello Quant!")
```

然后按 **Shift + Enter** 运行。

如果你看到输出：

```
Hello Quant!
```

**你做到了！** 🎉 Python 量化开发环境已经搭建完成。

### 6. Jupyter 速成（够用就行）

| 操作 | 快捷键 / 方法 |
|------|-------------|
| 运行当前单元格 | `Shift + Enter` |
| 新建单元格 | 工具栏「+」按钮 |
| 删除单元格 | 选中后按 `DD`（按两次 D） |
| 改代码后重新运行 | `Shift + Enter` 重新执行 |
| 保存 notebook | `Cmd + S` (macOS) / `Ctrl + S` (Windows) |
| 关闭 | 终端按 `Ctrl + C` 停止 Jupyter 服务 |

你现在只需要知道这些。其他功能边用边学。

## 练习

### 选择题

1. 安装完 Python 和 jupyter 后，在终端输入什么命令可以启动 Jupyter Notebook？
   - A. `start jupyter`
   - B. `jupyter notebook`
   - C. `run jupyter`
   - D. `python jupyter`

2. 在 Jupyter 单元格中运行代码的快捷键是？
   - A. `Ctrl + Enter`
   - B. `Enter`
   - C. `Shift + Enter`
   - D. `Alt + Enter`

3. 以下哪个不是本章安装的量化库？
   - A. `numpy`
   - B. `scikit-learn`
   - C. `pandas`
   - D. `yfinance`

### 论述题

请用一段话描述你现在的开发环境，包括：
- 你的电脑是什么系统（Windows / macOS / Linux）？
- Python 版本是多少？
- 你在终端还是 Jupyter 里写代码？
- 你对接下来学量化有什么期待？好奇？兴奋？还是有点紧张？

> 不需要写得多好——写下来就是给自己看的。这是你量化之路的第一篇日记。
