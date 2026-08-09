export interface ThemeOption {
  value: 'warm' | 'white' | 'night' | 'berry'
  label: string
  primary: string
  bg: string
}

export const THEME_OPTIONS: ThemeOption[] = [
  { value: 'warm', label: '暖橙经典（熟食/热餐）', primary: '#F0643A', bg: '#F7F4EF' },
  { value: 'white', label: '纯白简约（奶茶/咖啡）', primary: '#8B5E3C', bg: '#FAFAF8' },
  { value: 'night', label: '深夜墨绿（夜宵/烧烤）', primary: '#F0793E', bg: '#1C2521' },
  { value: 'berry', label: '莓果甜心（甜品/烘焙）', primary: '#D98E94', bg: '#FBF4EF' },
]
