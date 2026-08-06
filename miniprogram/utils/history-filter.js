// 历史记录筛选：按订单号 + 商品类别（本地过滤）
function filterHistory(orders, options = {}) {
  const kw = (options.keyword || '').trim().toLowerCase()
  const category = options.category || 'all'
  return orders.filter((o) => {
    if (kw && !o.order_no.toLowerCase().includes(kw)) return false
    if (category !== 'all') {
      const has = (o.items || []).some((i) => i.category_name === category)
      if (!has) return false
    }
    return true
  })
}

function categoriesOf(orders) {
  const set = new Set()
  orders.forEach((o) => (o.items || []).forEach((i) => {
    if (i.category_name) set.add(i.category_name)
  }))
  return Array.from(set)
}

module.exports = { filterHistory, categoriesOf }
