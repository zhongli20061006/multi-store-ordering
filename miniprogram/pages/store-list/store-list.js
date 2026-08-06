const { getStores } = require('../../utils/api/stores')
const { filterStores } = require('../../utils/store-filter')
const { buildLocationPayload } = require('../../utils/store-location')
const notifyStore = require('../../utils/notify-store')

Page({
  data: {
    loading: true,
    error: false,
    stores: [],
    allStores: [],
    keyword: '',
    unreadCount: 0,
  },

  onLoad() {
    this.load()
  },

  onShow() {
    this.setData({ unreadCount: notifyStore.unreadCount() })
  },

  goNotify() {
    wx.navigateTo({ url: '/pages/notify/notify' })
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh())
  },

  load() {
    this.setData({ loading: true, error: false })
    return getStores()
      .then((stores) => {
        this.setData({ allStores: stores })
        this.applyFilter()
      })
      .catch(() => this.setData({ error: true, allStores: [], stores: [] }))
      .finally(() => this.setData({ loading: false }))
  },

  applyFilter() {
    this.setData({ stores: filterStores(this.data.allStores, this.data.keyword) })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
    this.applyFilter()
  },

  goMenu(e) {
    const { id, name } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/menu/menu?store_id=${id}&store_name=${encodeURIComponent(name)}&entry_type=preorder`,
    })
  },

  onNavigate(e) {
    const store = e.currentTarget.dataset.item
    const payload = buildLocationPayload(store)
    if (!payload) {
      wx.showToast({ title: '该门店暂未配置导航位置', icon: 'none' })
      return
    }
    wx.openLocation({
      ...payload,
      fail: () => wx.showToast({ title: '打开地图失败', icon: 'none' }),
    })
  },

  retry() {
    this.load()
  },
})
