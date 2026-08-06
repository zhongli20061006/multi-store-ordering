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
    selectMode: false,
    selected: {},
    selectedCount: 0,
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

  onRowTap(e) {
    const { order_no: orderNo, phone } = e.currentTarget.dataset
    if (this.data.selectMode) {
      this.toggleSelect(orderNo)
    } else {
      wx.navigateTo({ url: `/pages/order-detail/order-detail?order_no=${orderNo}&phone=${phone}` })
    }
  },

  onManage() {
    this.setData({ selectMode: true, selected: {}, selectedCount: 0 })
  },

  onCancelSelect() {
    this.setData({ selectMode: false, selected: {}, selectedCount: 0 })
  },

  toggleSelect(orderNo) {
    const selected = Object.assign({}, this.data.selected)
    if (selected[orderNo]) {
      delete selected[orderNo]
    } else {
      selected[orderNo] = true
    }
    this.setData({ selected, selectedCount: Object.keys(selected).length })
  },

  onConfirmDelete() {
    const count = this.data.selectedCount
    if (count === 0) {
      wx.showToast({ title: '请先选择记录', icon: 'none' })
      return
    }
    wx.showModal({
      title: '批量删除',
      content: `确定删除选中的 ${count} 条本地记录？`,
      success: (res) => {
        if (!res.confirm) return
        Object.keys(this.data.selected).forEach((orderNo) => recentOrders.remove(orderNo))
        this.refresh()
        this.onCancelSelect()
        wx.showToast({ title: '已删除', icon: 'success' })
      },
    })
  },

  onClearAll() {
    wx.showModal({
      title: '清空记录',
      content: '确定清空全部本地历史记录？',
      success: (res) => {
        if (!res.confirm) return
        recentOrders.clear()
        this.refresh()
        this.onCancelSelect()
        wx.showToast({ title: '已清空', icon: 'success' })
      },
    })
  },
})
