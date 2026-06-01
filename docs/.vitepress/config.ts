import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Quant Wiki',
  description: '量化 & AI 技术知识库',
  lang: 'zh-CN',

  head: [
    ['link', { rel: 'icon', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#0ea5e9' }],
  ],

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: '首页', link: '/' },
      { text: '量化金融', link: '/quant-finance/' },
      { text: 'AI 技术与工具', link: '/ai/' },
      { text: '技术栈', link: '/tech-stack/' },
      { text: '资源收藏', link: '/resources/' },
    ],

    sidebar: {
      '/quant-finance/': [
        {
          text: '量化金融',
          items: [
            { text: '概述', link: '/quant-finance/' },
          ],
        },
      ],
      '/ai/': [
        {
          text: 'AI 技术与工具',
          items: [
            { text: '概述', link: '/ai/' },
          ],
        },
      ],
      '/tech-stack/': [
        {
          text: '技术栈',
          items: [
            { text: '概述', link: '/tech-stack/' },
          ],
        },
      ],
      '/resources/': [
        {
          text: '资源收藏',
          items: [
            { text: '资料索引', link: '/resources/' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/KaeyoungLIAN/Quant' },
    ],

    footer: {
      message: 'Built with VitePress',
      copyright: 'Copyright © 2026 Kaeyoung',
    },

    search: {
      provider: 'local',
    },

    editLink: {
      pattern: 'https://github.com/KaeyoungLIAN/Quant/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页',
    },

    lastUpdated: {
      text: '最后更新',
    },
  },

  cleanUrls: true,
  lastUpdated: true,
})
