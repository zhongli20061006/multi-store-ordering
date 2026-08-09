// 门店主题（纯逻辑）：四套主题 token + 按门店缓存。
// 页面根节点用 themeStyle(theme) 注入 CSS 变量；app.wxss 保留 warm 兜底。
const STORE_THEME_KEY = 'store_theme:v1'

const THEMES = {
  warm: {
    '--brand-primary': '#F0643A',
    '--brand-strong': '#D9532B',
    '--brand-soft': '#FDE8E0',
    '--text-main': '#26221E',
    '--text-secondary': '#7A736B',
    '--text-disabled': '#B8B0A7',
    '--bg-page': '#F7F4EF',
    '--surface': '#FFFFFF',
    '--surface-muted': '#F1EDE6',
    '--border-color': '#E8E1D8',
    '--shadow-card': '0 6rpx 24rpx rgba(38,34,30,0.06)',
    '--success': '#3E9B63',
    '--warning': '#D98E32',
    '--danger': '#D9564A',
    '--info': '#8A8278',
    '--accent-1': '#E9B44C',
    '--accent-2': '#8FAF6B',
  },
  white: {
    '--brand-primary': '#8B5E3C',
    '--brand-strong': '#6F4529',
    '--brand-soft': '#EFE6DC',
    '--text-main': '#2A2724',
    '--text-secondary': '#8A857F',
    '--text-disabled': '#BDB8B2',
    '--bg-page': '#FAFAF8',
    '--surface': '#FFFFFF',
    '--surface-muted': '#F2F1ED',
    '--border-color': '#EAE6E0',
    '--shadow-card': '0 6rpx 24rpx rgba(42,39,36,0.06)',
    '--success': '#4E9A6D',
    '--warning': '#D2A03E',
    '--danger': '#CC6A5E',
    '--info': '#8F8A83',
    '--accent-1': '#E6C98F',
    '--accent-2': '#A8BFA0',
  },
  night: {
    '--brand-primary': '#F0793E',
    '--brand-strong': '#DF6B30',
    '--brand-soft': 'rgba(240,121,62,0.18)',
    '--text-main': '#F5F1EA',
    '--text-secondary': '#A9B3AC',
    '--text-disabled': '#7C8780',
    '--bg-page': '#1C2521',
    '--surface': '#29332E',
    '--surface-muted': '#323D37',
    '--border-color': '#3A4740',
    '--shadow-card': '0 6rpx 24rpx rgba(0,0,0,0.28)',
    '--success': '#74BE92',
    '--warning': '#D9A441',
    '--danger': '#E07B6A',
    '--info': '#929E97',
    '--accent-1': '#F0B65A',
    '--accent-2': '#7FA98E',
  },
  berry: {
    '--brand-primary': '#D98E94',
    '--brand-strong': '#C26A72',
    '--brand-soft': '#FBECEC',
    '--text-main': '#3A3230',
    '--text-secondary': '#94867F',
    '--text-disabled': '#C4B8B2',
    '--bg-page': '#FBF4EF',
    '--surface': '#FFFFFF',
    '--surface-muted': '#F5EBE4',
    '--border-color': '#EFE3DD',
    '--shadow-card': '0 6rpx 24rpx rgba(58,50,48,0.06)',
    '--success': '#7FA98E',
    '--warning': '#D9A441',
    '--danger': '#D97B84',
    '--info': '#A89A93',
    '--accent-1': '#EAC586',
    '--accent-2': '#E7B7C0',
  },
}

function themeStyle(theme) {
  const tokens = THEMES[theme] || THEMES.warm
  return Object.keys(tokens)
    .map((key) => `${key}:${tokens[key]}`)
    .join(';')
}

function _readMap() {
  const map = wx.getStorageSync(STORE_THEME_KEY)
  return map && typeof map === 'object' ? map : {}
}

function rememberTheme(storeId, theme) {
  if (!storeId || !THEMES[theme]) return
  const map = _readMap()
  map[storeId] = theme
  wx.setStorageSync(STORE_THEME_KEY, map)
}

function themeOf(storeId) {
  const map = _readMap()
  return map[storeId] || 'warm'
}

module.exports = { THEMES, themeStyle, rememberTheme, themeOf }
