const { getStores } = require('../../utils/api/stores')

Page({
  data: {
    loading: true,
    error: false,
    stores: [],
  },

  onLoad() {
    this.load()
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh())
  },

  load() {
    this.setData({ loading: true, error: false })
    return getStores()
      .then((stores) => this.setData({ stores }))
      .catch(() => this.setData({ error: true, stores: [] }))
      .finally(() => this.setData({ loading: false }))
  },

  goMenu(e) {
    const { id, name } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/menu/menu?store_id=${id}&store_name=${encodeURIComponent(name)}&entry_type=preorder`,
    })
  },

  retry() {
    this.load()
  },
})
