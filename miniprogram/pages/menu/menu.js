const { getStoreMenu, getStores, getStoreBanners } = require('../../utils/api/stores')
const { API_ORIGIN } = require('../../config')
const { filterMenu } = require('../../utils/menu-filter')
const { buildLocationPayload } = require('../../utils/store-location')
const cart = require('../../store/cart')
const { themeStyle, themeOf, rememberTheme } = require('../../utils/theme')

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
    phone: '',
    address: '',
    latitude: null,
    longitude: null,
    banners: [],
    imgBase: API_ORIGIN,
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
    this.setData({ storeId, storeName, entryType, themeStyle: themeStyle(themeOf(storeId)) })
    cart.ensureStore(storeId, storeName)
    this.loadMenu()
    this.loadBanners(storeId)
    // 营业时间从门店列表补全；扫码直达（URL 只有 store_id）时同时补门店名（真源约定）
    this.fetchStoreInfo(storeId)
  },

  loadBanners(storeId) {
    getStoreBanners(storeId)
      .then((banners) => this.setData({ banners }))
      .catch(() => {})
  },

  fetchStoreInfo(storeId) {
    getStores()
      .then((stores) => {
        const found = stores.find((s) => s.id === storeId)
        if (!found) return
        const patch = {
          hours: found.open_time ? `${found.open_time} - ${found.close_time}` : '',
          phone: found.phone || '',
          address: found.address || '',
          latitude: found.latitude ?? null,
          longitude: found.longitude ?? null,
        }
        if (!this.data.storeName) {
          patch.storeName = found.name
          cart.ensureStore(storeId, found.name)
        }
        rememberTheme(storeId, found.theme)
        patch.themeStyle = themeStyle(found.theme)
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

  onItemDetail(e) {
    const { item } = e.detail
    if (!item) return
    wx.navigateTo({
      url: `/pages/item-detail/item-detail?store_id=${this.data.storeId}&item_id=${item.id}&entry_type=${this.data.entryType}&store_name=${encodeURIComponent(this.data.storeName)}`,
    })
  },

  onNavigate() {
    const payload = buildLocationPayload({
      latitude: this.data.latitude,
      longitude: this.data.longitude,
      name: this.data.storeName,
      address: this.data.address,
    })
    if (!payload) {
      wx.showToast({ title: '该门店暂未配置导航位置', icon: 'none' })
      return
    }
    wx.openLocation({
      ...payload,
      fail: () => wx.showToast({ title: '打开地图失败', icon: 'none' }),
    })
  },

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
