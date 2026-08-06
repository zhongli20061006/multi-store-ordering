// 下单联系人预填（纯函数）：姓名/手机号分别「个人资料优先、最近一单兜底」。
// recent_orders 新单在前，取第一条；个人资料昵称为默认「微信用户」时视为未填。
function resolveContact(profile, recentOrders) {
  const p = profile || {}
  const first = Array.isArray(recentOrders) && recentOrders.length ? recentOrders[0] : {}
  const name = p.nickname && p.nickname !== '微信用户' ? p.nickname : first.customer_name || ''
  const phone = p.phone || first.customer_phone || ''
  return { name, phone }
}

module.exports = { resolveContact }
