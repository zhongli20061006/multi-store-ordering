const { getStoreMenu, getStores } = require('../../utils/api/stores')
const { filterMenu } = require('../../utils/menu-filter')
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
    keyword: '',
    allGroups: [],
    hours: '',
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
    // 营业时间从门店列表补全；扫码直达（URL 只有 store_id）时同时补门店名（真源约定）
    this.fetchStoreInfo(storeId)
  },

  fetchStoreInfo(storeId) {
    getStores()
      .then((stores) => {
        const found = stores.find((s) => s.id === storeId)
        if (!found) return
        const patch = { hours: found.open_time ? `${found.open_time} - ${found.close_time}` : '' }
        if (!this.data.storeName) {
          patch.storeName = found.name
          cart.ensureStore(storeId, found.name)
        }
        this.setData(patch)
      })
      .catch(() => {})
  },

  loadMenu() {
    this.setData({ loading: true, error: false })
    return getStoreMenu(this.data.storeId)
      .then((groups) => {
        this.setData({ allGroups: groups })
        this.applyFilter()
      })
      .catch(() => this.setData({ error: true, categories: [], items: [] }))
      .finally(() => {
        this.setData({ loading: false })
        this.refreshCart()
      })
  },

  applyFilter() {
    const groups = filterMenu(this.data.allGroups, this.data.keyword)
    const active = groups.length ? groups[0].id : 0
    this.setData({
      categories: groups,
      activeCategoryId: active,
      items: groups.length ? groups[0].items : [],
    })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
    this.applyFilter()
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
