// 新订单检测：对比上一轮订单 id 集合，找出新增的 pending 订单
export function detectNewPending(
  previousIds: number[],
  orders: { id: number; order_status: string }[],
): number[] {
  const seen = new Set(previousIds)
  return orders.filter((o) => o.order_status === 'pending' && !seen.has(o.id)).map((o) => o.id)
}
