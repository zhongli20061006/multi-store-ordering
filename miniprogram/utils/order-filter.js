// 我的订单状态筛选（纯展示过滤）
const GROUPS = {
  all: () => true,
  pending: (o) => o.order_status === 'pending',
  active: (o) => o.order_status === 'accepted' || o.order_status === 'served',
  completed: (o) => o.order_status === 'completed',
  cancelled: (o) => o.order_status === 'cancelled',
}

function filterOrders(orders, group) {
  const fn = GROUPS[group] || GROUPS.all
  return orders.filter(fn)
}

module.exports = { filterOrders }
