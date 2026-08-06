const { createOrder } = require('../../utils/api/orders')
const { generateKey } = require('../../utils/idempotency')
const cart = require('../../store/cart')
const recentOrders = require('../../store/recent-orders')
const profileStore = require('../../utils/profile-store')

Page({
  data: {
    storeId: 0,
    storeName: '',
    entryType: 'preorder',
    items: [],
    totalCount: 0,
    totalCents: 0,
    customerName: '',
    customerPhone: '',
    remark: '',
    submitting: false,
    submitKey: '',
  },

  onLoad(options) {
    const storeId = Number(options.store_id || 0)
    const storeName = decodeURIComponent(options.store_name || '')
    const entryType = options.entry_type === 'preorder' ? 'preorder' : 'dinein'
    const current = cart.getCart()
    if (!current || current.storeId !== storeId || current.items.length === 0) {
      wx.showToast({ title: '购物车为空', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 600)
      return
    }
    const profile = profileStore.read()
    this.setData({
      storeId,
      storeName,
      entryType,
      items: current.items,
      totalCount: cart.getTotalCount(),
      totalCents: cart.getTotalCents(),
      customerPhone: profile.phone,
      customerName: profile.nickname === '微信用户' ? '' : profile.nickname,
    })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onSubmit() {
    const {
      customerName,
      customerPhone,
      remark,
      submitting,
      storeId,
      entryType,
      items,
      submitKey,
    } = this.data
    if (submitting) return
    if (!customerName.trim()) {
      wx.showToast({ title: '请填写联系人姓名', icon: 'none' })
      return
    }
    if (!/^1[3-9]\d{9}$/.test(customerPhone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    // 幂等键：首次点击生成；失败重试复用同一个键（重试不会变成新订单）
    const key = submitKey || generateKey()
    this.setData({ submitting: true, submitKey: key })
    createOrder({
      store_id: storeId,
      entry_type: entryType,
      customer_name: customerName.trim(),
      customer_phone: customerPhone,
      remark: remark.trim() || null,
      idempotency_key: key,
      items: items.map((i) => ({ menu_item_id: i.menu_item_id, quantity: i.quantity })),
    })
      .then((order) => {
        cart.clearCart()
        recentOrders.upsert(order)
        wx.redirectTo({
          url: `/pages/order-success/order-success?order_no=${order.order_no}&total_cents=${order.total_cents}&store_name=${encodeURIComponent(this.data.storeName)}`,
        })
      })
      .catch(() => {
        // 失败：按钮恢复，submitKey 保留，可重试
        this.setData({ submitting: false })
      })
  },
})
