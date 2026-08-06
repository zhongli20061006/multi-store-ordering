// 门店信息卡按钮可用性（纯函数）：导航需完整坐标；电话需号码非空。
function canNavigate(store) {
  if (!store || store.latitude == null || store.longitude == null) return false
  const latitude = Number(store.latitude)
  const longitude = Number(store.longitude)
  return Number.isFinite(latitude) && Number.isFinite(longitude)
}

function canCall(store) {
  return !!(store && store.phone && String(store.phone).trim())
}

module.exports = { canNavigate, canCall }
