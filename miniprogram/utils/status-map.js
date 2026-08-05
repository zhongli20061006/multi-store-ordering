// 纯展示映射；枚举值与含义以后端 backend-boundary.md 为 owner。
const ORDER_STATUS_TEXT = {
  pending: '待接单',
  accepted: '已接单',
  completed: '已完成',
  cancelled: '已取消',
}

const ENTRY_TYPE_TEXT = {
  dinein: '到店点单',
  preorder: '提前点单',
}

const PAYMENT_STATUS_TEXT = {
  unpaid: '未付款',
  paid: '已付款',
}

function statusText(status) {
  return ORDER_STATUS_TEXT[status] || status
}

function entryTypeText(type) {
  return ENTRY_TYPE_TEXT[type] || type
}

function paymentStatusText(status) {
  return PAYMENT_STATUS_TEXT[status] || status
}

module.exports = { statusText, entryTypeText, paymentStatusText }
