const { request } = require('../request')

function createOrder(payload) {
  return request({ url: '/orders', method: 'POST', data: payload })
}

function cancelOrder(orderNo, phone) {
  return request({ url: `/orders/${orderNo}/cancel`, method: 'POST', data: { phone } })
}

function queryOrder(phone, orderNo) {
  return request({ url: '/orders', data: { phone, order_no: orderNo } })
}

module.exports = { createOrder, cancelOrder, queryOrder }
