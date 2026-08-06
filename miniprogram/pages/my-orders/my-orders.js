const { queryOrder, cancelOrder, pickupOrder } = require('../../utils/api/orders')
const { getStores } = require('../../utils/api/stores')
const recentOrders = require('../../store/recent-orders')
const { filterOrders } = require('../../utils/order-filter')

Page({
  data: {
    orders: [],
    phone: '',
    orderNo: '',
    querying: false,
    showFinder: false,
    storeNames: {},
    filterGroup: 'all',
    filterTabs: [
      { group: 'all', label: '全部' },
      { group: 'pending', label: '待接单' },
      { group: 'active', label: '进行中' },
      { group: 'completed', label: '已完成' },
      { group: 'cancelled', label: '已取消' },
    ],
  },

  onLoad() {
    this.loadStoreNames()
  },

  onShow() {
    const entry = wx.getStorageSync('profile_entry')
    if (entry) {
      wx.removeStorageSync('profile_entry')
      if (entry === 'history') this.setData({ showFinder: true })
    }
    this.renderOrders()
    this.refreshActive()
    if (!this._refreshTimer) {
      this._refreshTimer = setInterval(() => this.refreshActive(), 8000)
    }
  },

  onHide() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer)
      this._refreshTimer = null
    }
  },

  onUnload() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer)
      this._refreshTimer = null
    }
  },

  refreshActive() {
    recentOrders.list().forEach((o) => {
      if (o.order_status === 'pending' || o.order_status === 'accepted' || o.order_status === 'served') {
        this.silentRefresh(o)
      }
    })
  },

  loadStoreNames() {
    getStores()
      .then((stores) => {
        const map = {}
        stores.forEach((s) => {
          map[s.id] = s.name
        })
        this.setData({ storeNames: map })
      })
      .catch(() => {})
  },

  storeNameOf(storeId) {
    return this.data.storeNames[storeId] || `门店 #${storeId}`
  },

  renderOrders() {
    const orders = filterOrders(recentOrders.list(), this.data.filterGroup).map((o) =>
      Object.assign({}, o, { storeName: this.storeNameOf(o.store_id) })
    )
    this.setData({ orders })
  },

  onFilter(e) {
    this.setData({ filterGroup: e.currentTarget.dataset.group })
    this.renderOrders()
  },

  applyOrder(order) {
    recentOrders.upsert(order)
    this.renderOrders()
  },

  silentRefresh(order) {
    queryOrder(order.customer_phone, order.order_no)
      .then((fresh) => this.applyOrder(fresh))
      .catch(() => {})
  },

  toggleFinder() {
    this.setData({ showFinder: !this.data.showFinder })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onSearch() {
    const { phone, orderNo, querying } = this.data
    if (querying) return
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!orderNo.trim()) {
      wx.showToast({ title: '请输入订单号', icon: 'none' })
      return
    }
    this.setData({ querying: true })
    queryOrder(phone, orderNo.trim())
      .then((order) => this.applyOrder(order))
      .catch(() => {})
      .finally(() => this.setData({ querying: false }))
  },

  onDetail(e) {
    const { order_no: orderNo, customer_phone: phone } = e.detail.order
    wx.navigateTo({
      url: `/pages/order-detail/order-detail?order_no=${orderNo}&phone=${phone}`,
    })
  },

  onCancel(e) {
    const { order_no: orderNo, customer_phone: phone } = e.detail.order
    wx.showModal({
      title: '取消订单',
      content: '确定取消该订单？未制作的取消将回补限库存商品。',
      success: (res) => {
        if (!res.confirm) return
        cancelOrder(orderNo, phone)
          .then((fresh) => {
            wx.showToast({ title: '已取消', icon: 'success' })
            this.applyOrder(fresh)
          })
          .catch(() => {})
      },
    })
  },

  onPickup(e) {
    const { order_no: orderNo, customer_phone: phone } = e.detail.order
    wx.showModal({
      title: '确认取单',
      content: '确认已取到该订单的餐品？',
      success: (res) => {
        if (!res.confirm) return
        pickupOrder(orderNo, phone)
          .then((fresh) => {
            wx.showToast({ title: '已取单', icon: 'success' })
            this.applyOrder(fresh)
          })
          .catch(() => {})
      },
    })
  },
})
