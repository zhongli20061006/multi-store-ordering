const { API_ORIGIN } = require('../../config')
const { getStoreItem } = require('../../utils/api/stores')
const { createOrder } = require('../../utils/api/orders')
const { generateKey } = require('../../utils/idempotency')
const { defaultSelections, buildSpecsPayload } = require('../../utils/specs')
const recentOrders = require('../../store/recent-orders')
const notifyStore = require('../../utils/notify-store')
const profileStore = require('../../utils/profile-store')
const { resolveContact } = require('../../utils/contact-prefill')

Page({
  data: {
    storeId: 0,
    itemId: 0,
    entryType: 'dinein',
    storeName: '',
    item: null,
    groups: [],
    selections: [],
    quantity: 1,
    remark: '',
    customerName: '',
    customerPhone: '',
    imgBase: API_ORIGIN,
    submitting: false,
    submitKey: '',
  },

  onLoad(options) {
    const storeId = Number(options.store_id || 0)
    const itemId = Number(options.item_id || 0)
    const entryType = options.entry_type === 'preorder' ? 'preorder' : 'dinein'
    const storeName = decodeURIComponent(options.store_name || '')
    const contact = resolveContact(profileStore.read(), recentOrders.list())
    this.setData({ storeId, itemId, entryType, storeName, customerName: contact.name, customerPhone: contact.phone })
    this.load()
  },

  load() {
    getStoreItem(this.data.storeId, this.data.itemId)
      .then((item) => {
        const groups = item.spec_groups || []
        this.setData({ item, groups, selections: defaultSelections(groups) })
      })
      .catch(() => {})
  },

  onSelectSpec(e) {
    const { name, option } = e.currentTarget.dataset
    const selections = this.data.selections.map((s) => (s.name === name ? { name, option } : s))
    this.setData({ selections })
  },

  onMinus() {
    if (this.data.quantity > 1) {
      this.setData({ quantity: this.data.quantity - 1 })
    }
  },

  onPlus() {
    const { quantity, item } = this.data
    if (item.stock != null && quantity >= item.stock) {
      wx.showToast({ title: '库存不足', icon: 'none' })
      return
    }
    this.setData({ quantity: quantity + 1 })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onSubmit() {
    const {
      item,
      storeId,
      entryType,
      quantity,
      remark,
      selections,
      customerName,
      customerPhone,
      submitting,
      submitKey,
    } = this.data
    if (submitting || !item) return
    if (!customerName.trim()) {
      wx.showToast({ title: '请填写联系人姓名', icon: 'none' })
      return
    }
    if (!/^1[3-9]\d{9}$/.test(customerPhone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    const key = submitKey || generateKey()
    this.setData({ submitting: true, submitKey: key })
    createOrder({
      store_id: storeId,
      entry_type: entryType,
      customer_name: customerName.trim(),
      customer_phone: customerPhone,
      remark: remark.trim() || null,
      idempotency_key: key,
      items: [
        {
          menu_item_id: item.id,
          quantity,
          specs: buildSpecsPayload(selections),
        },
      ],
    })
      .then((order) => {
        recentOrders.upsert(order)
        notifyStore.add(`订单 ${order.order_no} 已下单，等待商家接单`)
        wx.showToast({ title: '下单成功', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 800)
      })
      .catch(() => this.setData({ submitting: false }))
  },
})
