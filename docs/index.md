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
/* Homepage — Ethereal Glass Hero */
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(135deg, #e5e7eb 0%, #9ca3af 100%);

  --vp-home-hero-image-background-image: radial-gradient(ellipse 60% 60% at 50% 40%, rgba(34, 211, 238, 0.12) 0%, transparent 70%);
  --vp-home-hero-image-filter: blur(64px);

  --vp-c-brand-1: #22d3ee;
  --vp-c-brand-2: #06b6d4;
  --vp-c-brand-3: #0891b2;
}

@media (min-width: 640px) {
  :root {
    --vp-home-hero-image-filter: blur(80px);
  }
}

@media (min-width: 960px) {
  :root {
    --vp-home-hero-image-filter: blur(96px);
  }
}

/* Hero section — reduce padding for wiki feel */
.VPHomeHero {
  padding-top: 32px !important;
  padding-bottom: 0 !important;
}

.VPHomeHero .container {
  padding: 48px 24px 24px !important;
}

.VPHomeHero .main {
  gap: 20px !important;
}

/* Tagline */
.VPHomeHero .tagline {
  color: #9ca3af !important;
  font-weight: 400 !important;
  max-width: 480px !important;
}

/* Feature cards — Double-Bezel Glass */
.VPHomeFeatures {
  padding-top: 8px !important;
}

.VPHomeFeatures .container {
  padding: 0 24px 24px !important;
}

.VPFeature {
  border-radius: 16px !important;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1) !important;
  border: 1px solid rgba(255, 255, 255, 0.06) !important;
  background: rgba(255, 255, 255, 0.02) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  position: relative;
  overflow: hidden;
}

/* Gradient hairline glow on hover */
.VPFeature::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.3), transparent 50%, transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  pointer-events: none;
}

.VPFeature:hover::before {
  opacity: 1;
}

.VPFeature:hover {
  transform: translateY(-2px) !important;
  border-color: rgba(34, 211, 238, 0.2) !important;
  background: rgba(255, 255, 255, 0.04) !important;
  box-shadow: 0 8px 32px rgba(34, 211, 238, 0.06) !important;
}

/* Feature title */
.VPFeature .title {
  font-size: 18px !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  color: #e5e7eb !important;
}

/* Feature details */
.VPFeature .details {
  color: #9ca3af !important;
  font-size: 13px !important;
  line-height: 1.6 !important;
}

/* Feature box text (emoji icon) */
.VPFeature .box {
  background: transparent !important;
}

.VPFeature .icon {
  background: rgba(34, 211, 238, 0.08) !important;
  border: 1px solid rgba(34, 211, 238, 0.12) !important;
  border-radius: 12px !important;
  font-size: 22px !important;
}

/* Action buttons */
.VPHomeHero .actions {
  gap: 10px !important;
}

.VPHomeHero .actions .brand {
  border-radius: 9999px !important;
  padding: 10px 24px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  background: rgba(34, 211, 238, 0.1) !important;
  border: 1px solid rgba(34, 211, 238, 0.2) !important;
  color: #22d3ee !important;
  transition: all 0.25s cubic-bezier(0.32, 0.72, 0, 1) !important;
}

.VPHomeHero .actions .brand:hover {
  background: rgba(34, 211, 238, 0.18) !important;
  border-color: rgba(34, 211, 238, 0.35) !important;
  transform: scale(1.02);
}

.VPHomeHero .actions .alt {
  border-radius: 9999px !important;
  padding: 10px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: #9ca3af !important;
  transition: all 0.25s cubic-bezier(0.32, 0.72, 0, 1) !important;
}

.VPHomeHero .actions .alt:hover {
  border-color: rgba(255, 255, 255, 0.15) !important;
  color: #e5e7eb !important;
  background: rgba(255, 255, 255, 0.03) !important;
}

/* Image container */
.VPHomeHero .image-container {
  width: 192px !important;
  height: 192px !important;
}
</style>
