export interface ThemeOption {
  value: 'warm' | 'white' | 'green' | 'berry'
  label: string
  primary: string
  bg: string
}

export const THEME_OPTIONS: ThemeOption[] = [
  { value: 'warm', label: '暖橙经典（熟食/热餐）', primary: '#F0643A', bg: '#F7F4EF' },
  { value: 'white', label: '纯白简约（奶茶/咖啡）', primary: '#8B5E3C', bg: '#FAFAF8' },
  { value: 'green', label: '清新绿白（夜宵/轻食）', primary: '#5E9E68', bg: '#F3F8F1' },
  { value: 'berry', label: '莓果甜心（甜品/烘焙）', primary: '#D98E94', bg: '#FBF4EF' },
]
