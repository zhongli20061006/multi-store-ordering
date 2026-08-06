const { getStores } = require('../../utils/api/stores')
const { filterStores } = require('../../utils/store-filter')

Page({
  data: {
    loading: true,
    error: false,
    stores: [],
    allStores: [],
    keyword: '',
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

  retry() {
    this.load()
  },
})
