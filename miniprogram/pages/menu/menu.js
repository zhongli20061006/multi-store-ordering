const { getStoreMenu } = require('../../utils/api/stores')
const cart = require('../../store/cart')

Page({
  data: {
    storeId: 0,
    storeName: '',
    entryType: 'dinein',
    loading: true,
    error: false,
    categories: [],
    activeCategoryId: 0,
    items: [],
    cartVisible: false,
    cartOpen: false,
    cartItems: [],
    cartCount: 0,
    cartTotalCents: 0,
  },

  onLoad(options) {
    const storeId = Number(options.store_id || 0)
    const storeName = decodeURIComponent(options.store_name || '')
    // 列表进入显式带 entry_type=preorder；扫码直达 URL 只有 store_id，缺省 dinein
    const entryType = options.entry_type === 'preorder' ? 'preorder' : 'dinein'
    this.setData({ storeId, storeName, entryType })
    cart.ensureStore(storeId, storeName)
    this.loadMenu()
  },

  loadMenu() {
    this.setData({ loading: true, error: false })
    return getStoreMenu(this.data.storeId)
      .then((groups) => {
        const active = groups.length ? groups[0].id : 0
        this.setData({
          categories: groups,
          activeCategoryId: active,
          items: groups.length ? groups[0].items : [],
        })
      })
      .catch(() => this.setData({ error: true, categories: [], items: [] }))
      .finally(() => {
        this.setData({ loading: false })
        this.refreshCart()
      })
  },

  switchCategory(e) {
    const id = e.currentTarget.dataset.id
    const group = this.data.categories.find((g) => g.id === id)
    this.setData({ activeCategoryId: id, items: group ? group.items : [] })
  },

  refreshCart() {
    this.setData({
      cartCount: cart.getTotalCount(),
      cartTotalCents: cart.getTotalCents(),
      cartItems: (cart.getCart() || { items: [] }).items,
      cartVisible: cart.getCart() !== null,
    })
  },

  onAddItem(e) {
    const item = e.detail
    cart.addItem(this.data.storeId, this.data.storeName, {
      menu_item_id: item.id,
      name: item.name,
      unit_price_cents: item.price_cents,
      stock: item.stock,
      quantity: 1,
    })
    this.refreshCart()
  },

  onChangeQuantity(e) {
    const { id, quantity } = e.detail
    cart.updateQuantity(this.data.storeId, id, quantity)
    this.refreshCart()
  },

  toggleCartPanel() {
    this.setData({ cartOpen: !this.data.cartOpen })
  },

  closeCartPanel() {
    this.setData({ cartOpen: false })
  },

  noop() {},

  goCheckout() {
    if (this.data.cartCount === 0) return
    wx.navigateTo({
      url: `/pages/checkout/checkout?store_id=${this.data.storeId}&store_name=${encodeURIComponent(this.data.storeName)}&entry_type=${this.data.entryType}`,
    })
  },

  retry() {
    this.loadMenu()
  },
})
