export const AUDIT_ACTION_TEXT: Record<string, string> = {
  accepted: '接单',
  served: '出单',
  cancelled: '取消',
  paid: '标记付款',
  customer_cancelled: '顾客取消',
  customer_pickup: '顾客取单',
}

export function auditActionText(action: string): string {
  return AUDIT_ACTION_TEXT[action] || action
}
