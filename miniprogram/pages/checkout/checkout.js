const { createOrder } = require('../../utils/api/orders')
const { getStoreMenu } = require('../../utils/api/stores')
const { generateKey } = require('../../utils/idempotency')
const cart = require('../../store/cart')
const recentOrders = require('../../store/recent-orders')
const profileStore = require('../../utils/profile-store')
const { resolveContact } = require('../../utils/contact-prefill')
const { applyStockCorrection } = require('../../utils/stock-correction')

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
    const contact = resolveContact(profileStore.read(), recentOrders.list())
    this.setData({
      storeId,
      storeName,
      entryType,
      items: current.items,
      totalCount: cart.getTotalCount(),
      totalCents: cart.getTotalCents(),
      customerPhone: contact.phone,
      customerName: contact.name,
    })
    this.refreshStockSnapshot()
  },

  applyCart() {
    const current = cart.getCart()
    if (!current || current.items.length === 0) {
      wx.showToast({ title: '购物车为空', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 600)
      return
    }
    this.setData({
      items: current.items,
      totalCount: cart.getTotalCount(),
      totalCents: cart.getTotalCents(),
    })
  },

  // 静默刷新库存快照：限库存商品按最新可售量钳制，防止结算页长期停留后超卖
  refreshStockSnapshot() {
    getStoreMenu(this.data.storeId)
      .then((groups) => {
        const stockById = {}
        groups.forEach((group) =>
          (group.items || []).forEach((item) => {
            stockById[item.id] = item.stock == null ? null : item.stock
          }),
        )
        const current = cart.getCart()
        if (!current) return
        current.items.forEach((item) => {
          const latest = stockById[item.menu_item_id]
          if (latest != null) {
            cart.updateQuantity(this.data.storeId, item.menu_item_id, Math.min(item.quantity, latest))
          }
        })
        this.applyCart()
      })
      .catch(() => {})
  },

  onChangeQuantity(e) {
    const { id, quantity } = e.detail
    cart.updateQuantity(this.data.storeId, id, quantity)
    this.applyCart()
  },

  onRemoveItem(e) {
    const { id, name } = e.currentTarget.dataset
    wx.showModal({
      title: '删除商品',
      content: `确定删除「${name}」？`,
      success: (res) => {
        if (!res.confirm) return
        cart.removeItem(this.data.storeId, id)
        this.applyCart()
      },
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
          url: `/pages/order-success/order-success?order_no=${order.order_no}&total_cents=${order.total_cents}&store_id=${this.data.storeId}&store_name=${encodeURIComponent(this.data.storeName)}`,
        })
      })
      .catch((err) => {
        // 失败：按后端 detail 自动修正库存不足商品，按钮恢复，submitKey 保留可重试
        const insufficient = err && err.detail && err.detail.insufficient_items
        if (Array.isArray(insufficient) && insufficient.length) {
          const corrected = applyStockCorrection(this.data.items, insufficient)
          corrected.forEach((item) => cart.updateQuantity(this.data.storeId, item.menu_item_id, item.quantity))
          this.applyCart()
          wx.showToast({ title: '部分商品库存不足，已调整数量', icon: 'none' })
        }
        this.setData({ submitting: false })
      })
  },
})
