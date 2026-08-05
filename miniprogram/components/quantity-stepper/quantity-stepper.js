Component({
  properties: {
    item: { type: Object, value: null },
  },
  methods: {
    onMinus() {
      const item = this.data.item
      if (!item) return
      this.triggerEvent('change', { id: item.menu_item_id, quantity: item.quantity - 1 })
    },
    onPlus() {
      const item = this.data.item
      if (!item) return
      if (item.stock != null && item.quantity >= item.stock) {
        wx.showToast({ title: '库存不足', icon: 'none' })
        return
      }
      this.triggerEvent('change', { id: item.menu_item_id, quantity: item.quantity + 1 })
    },
  },
})
