const recentOrders = require('../../store/recent-orders')
const { filterHistory, categoriesOf } = require('../../utils/history-filter')
const { centsToYuan, formatTime } = require('../../utils/format')
const { statusText } = require('../../utils/status-map')
const { getStores } = require('../../utils/api/stores')

Page({
  data: {
    orders: [],
    keyword: '',
    categories: [],
    category: 'all',
    storeNames: {},
  },

  onShow() {
    this.loadStoreNames()
    this.refresh()
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

  decorate(o) {
    return Object.assign({}, o, {
      storeName: this.storeNameOf(o.store_id),
      displayTime: formatTime(o.created_at),
      statusLabel: statusText(o.order_status),
      totalYuan: centsToYuan(o.total_cents),
    })
  },

  refresh() {
    const all = recentOrders.list()
    this.setData({ categories: categoriesOf(all) })
    this.applyFilter()
  },

  applyFilter() {
    const orders = filterHistory(recentOrders.list(), { keyword: this.data.keyword, category: this.data.category }).map((o) =>
      this.decorate(o)
    )
    this.setData({ orders })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
    this.applyFilter()
  },

  onCategory(e) {
    this.setData({ category: e.currentTarget.dataset.category })
    this.applyFilter()
  },

  goDetail(e) {
    const { order_no: orderNo, phone } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/order-detail/order-detail?order_no=${orderNo}&phone=${phone}` })
  },
})
