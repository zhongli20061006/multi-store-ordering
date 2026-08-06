const { queryOrder, cancelOrder, pickupOrder } = require('../../utils/api/orders')
const { getStore } = require('../../utils/api/stores')
const { itemsFromOrder } = require('../../utils/reorder')
const { formatTime } = require('../../utils/format')
const recentOrders = require('../../store/recent-orders')
const cart = require('../../store/cart')

Page({
  data: {
    orderNo: '',
    phone: '',
    order: null,
    store: null,
  },

  onLoad(options) {
    const orderNo = options.order_no || ''
    const phone = options.phone || ''
    this.setData({ orderNo, phone })
    const found = recentOrders.list().find((o) => o.order_no === orderNo)
    if (found) {
      this.setData({ order: this.decorate(found) })
      this.loadStoreInfo(found.store_id)
    }
    this.refresh()
  },

  loadStoreInfo(storeId) {
    if (!storeId) return
    getStore(storeId)
      .then((store) => this.setData({ store }))
      .catch(() => {})
  },

  storeNameOf(storeId) {
    return (this.data.store && this.data.store.name) || `门店 #${storeId}`
  },

  decorate(order) {
    return Object.assign({}, order, {
      storeName: this.storeNameOf(order.store_id),
      displayTime: formatTime(order.created_at),
    })
  },

  refresh() {
    queryOrder(this.data.phone, this.data.orderNo)
      .then((order) => {
        this.setData({ order: this.decorate(order) })
        this.loadStoreInfo(order.store_id)
      })
      .catch(() => {})
  },

  onCancel() {
    const { order } = this.data
    wx.showModal({
      title: '取消订单',
      content: '确定取消该订单？未制作的取消将回补限库存商品。',
      success: (res) => {
        if (!res.confirm) return
        cancelOrder(order.order_no, order.customer_phone)
          .then((fresh) => {
            wx.showToast({ title: '已取消', icon: 'success' })
            this.setData({ order: this.decorate(fresh) })
          })
          .catch(() => {})
      },
    })
  },

  onPickup() {
    const { order } = this.data
    wx.showModal({
      title: '确认取单',
      content: '确认已取到该订单的餐品？',
      success: (res) => {
        if (!res.confirm) return
        pickupOrder(order.order_no, order.customer_phone)
          .then((fresh) => {
            wx.showToast({ title: '已取单', icon: 'success' })
            this.setData({ order: this.decorate(fresh) })
          })
          .catch(() => {})
      },
    })
  },

  onReorder() {
    const { order } = this.data
    if (!order || !order.items || order.items.length === 0) return
    cart.ensureStore(order.store_id, order.storeName)
    itemsFromOrder(order).forEach((item) => cart.addItem(order.store_id, order.storeName, item))
    wx.navigateTo({
      url: `/pages/checkout/checkout?store_id=${order.store_id}&store_name=${encodeURIComponent(order.storeName)}&entry_type=preorder`,
    })
  },
})
