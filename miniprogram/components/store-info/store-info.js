const { buildLocationPayload } = require('../../utils/store-location')
const { canNavigate, canCall } = require('../../utils/store-actions')

Component({
  properties: {
    store: { type: Object, value: null },
  },
  data: {
    navVisible: false,
    callVisible: false,
  },
  observers: {
    store(store) {
      this.setData({ navVisible: canNavigate(store), callVisible: canCall(store) })
    },
  },
  methods: {
    onNavigate() {
      const store = this.data.store
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
    onCall() {
      const store = this.data.store
      if (!store || !store.phone) return
      wx.makePhoneCall({
        phoneNumber: store.phone,
        fail: () => wx.showToast({ title: '拨号失败', icon: 'none' }),
      })
    },
  },
})
