// 运行配置唯一 owner。
// 真机预览用电脑局域网 IP；模拟器也可用（后端需 --host 0.0.0.0 启动且防火墙放行 8000）。
const BASE_URL = 'http://10.81.163.177:8000/api/v1'
// 图片等静态资源在 /uploads 下，不带 /api/v1 前缀
const API_ORIGIN = BASE_URL.replace(/\/api\/v1$/, '')

module.exports = { BASE_URL, API_ORIGIN }
