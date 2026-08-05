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

function pickupOrder(orderNo, phone) {
  return request({ url: `/orders/${orderNo}/pickup`, method: 'POST', data: { phone } })
}

module.exports = { createOrder, cancelOrder, queryOrder, pickupOrder }
