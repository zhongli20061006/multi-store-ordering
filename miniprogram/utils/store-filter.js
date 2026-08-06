// 门店本地过滤（按店名，不区分大小写）
function filterStores(stores, keyword) {
  const kw = (keyword || '').trim().toLowerCase()
  if (!kw) return stores
  return stores.filter((s) => (s.name || '').toLowerCase().includes(kw))
}

module.exports = { filterStores }
