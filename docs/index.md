---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "Quant Learning"
  text: "系统化学习量化交易"
  tagline: 从零到独立策略开发，数学→编程→金融→实战，一步一个脚印
  image:
    src: /hero.svg
    alt: Quant Learning
  actions:
    - theme: brand
      text: 🚀 开始学习
      link: /learn/01-getting-started/01-setup
    - theme: alt
      text: 📋 查看完整路线
      link: /learn/

features:
  - title: 📚 7 章线性学习路线
    details: 从装 Python 到写策略，33 节课循序渐进。学完一节自动解锁下一节，学习进度一目了然。
    link: /learn/
  - title: 🤖 AI 助教随时答疑
    details: 学习中遇到不懂的概念？点击右下角机器人，直接问。支持数学公式和代码示例。
  - title: 🧮 数学从零到实战
    details: 跟 MIT 18.S096 课程路线走，线性代数→概率论→随机过程，每个理论都有量化金融案例。
    link: /learn/03-math-toolbox/00-overview
  - title: 📊 代码驱动学习
    details: 每章都有可运行的 Python 代码和回测练习。先跑通，再理解，最后独立构建策略。
    link: /learn/04-python-quant/
---

<ProgressCard />

<style>
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: -webkit-linear-gradient(120deg, #0ea5e9 30%, #38bdf8);

  --vp-home-hero-image-background-image: linear-gradient(-45deg, #0ea5e9 30%, #7dd3fc 80%);
  --vp-home-hero-image-filter: blur(88px);

  --vp-c-brand-1: #0ea5e9;
  --vp-c-brand-2: #38bdf8;
  --vp-c-brand-3: #7dd3fc;
}

@media (min-width: 640px) {
  :root {
    --vp-home-hero-image-filter: blur(120px);
  }
}

@media (min-width: 960px) {
  :root {
    --vp-home-hero-image-filter: blur(150px);
  }
}

.VPHome {
  padding-bottom: 48px;
}

.VPHomeHero .container {
  padding: 64px 24px 32px;
}

.VPHomeFeatures .container {
  padding: 0 24px;
}

.VPFeature {
  border-radius: 12px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.VPFeature:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(14, 165, 233, 0.10);
}

.dark .VPFeature:hover {
  box-shadow: 0 12px 32px rgba(14, 165, 233, 0.15);
}
</style>
