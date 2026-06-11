import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import AiTeacher from './components/AiTeacher.vue'
import ProgressCard from './components/ProgressCard.vue'
import ProgressStatus from './components/ProgressStatus.vue'
import ChapterNav from './components/ChapterNav.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ProgressCard', ProgressCard)
    app.component('ChapterNav', ChapterNav)
  },
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(AiTeacher),
      'sidebar-nav-before': () => h(ProgressStatus),
      'doc-after': () => h(ChapterNav),
    })
  },
} satisfies Theme
