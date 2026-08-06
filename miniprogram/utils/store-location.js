// 门店导航参数构造（纯函数）：返回 wx.openLocation 所需参数；坐标缺失/非法返回 null。
function buildLocationPayload(store) {
  if (!store || store.latitude == null || store.longitude == null) return null
  const latitude = Number(store.latitude)
  const longitude = Number(store.longitude)
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null
  return { latitude, longitude, name: store.name || '', address: store.address || '' }
}

module.exports = { buildLocationPayload }
