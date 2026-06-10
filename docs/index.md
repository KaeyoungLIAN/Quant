---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "Quant Wiki"
  text: "量化金融 & AI 技术知识库"
  tagline: 系统化整理量化交易、人工智能、技术栈的笔记与资源
  image:
    src: /hero.svg
    alt: Quant Wiki
  actions:
    - theme: brand
      text: 开始阅读
      link: /quant-finance/
    - theme: alt
      text: 前置数学知识
      link: /prerequisite-math/
    - theme: alt
      text: AI 工具
      link: /ai/
    - theme: alt
      text: GitHub
      link: https://github.com/KaeyoungLIAN/Quant

features:
  - title: 🗺️ 学习路线
    details: 从零到独立策略开发的个性化方案，数学搭桥→核心能力→实战，配合视频与 Wiki 内容。
    link: /learn/
  - title: 📈 量化金融
    details: 策略模型、回测框架、风险管理、市场微观结构。从基础概念到实战经验，系统化整理。
    link: /quant-finance/
  - title: 🔢 前置数学知识
    details: 教材级量化 & AI 必备数学，配 Python 示例。极限、导数、线代、概率、统计、时间序列...
    link: /prerequisite-math/
  - title: 🤖 AI 技术与工具
    details: LLM、AI Agent、RAG、数据爬取分析。关注与量化交易结合的前沿 AI 工具。
    link: /ai/
  - title: 🛠️ 技术栈
    details: Python 生态、Django、React、数据库、部署运维。量化系统的工程实践笔记。
    link: /tech-stack/
  - title: 📚 资源收藏
    details: 优质书籍、论文、博客、数据集、开源项目。持续更新的学习资料索引。
    link: /resources/
---

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
