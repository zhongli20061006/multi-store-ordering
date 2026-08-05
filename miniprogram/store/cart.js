// 购物车：单 key 'cart:v1'，按门店隔离（切换门店清空+提示）。
// 合计是实时派生值，不存 total 字段；金额真源在后端，本模块仅用于展示。
const CART_KEY = 'cart:v1'

function read() {
  return wx.getStorageSync(CART_KEY) || null
}

function write(cart) {
  wx.setStorageSync(CART_KEY, cart)
}

function getCart() {
  const cart = read()
  if (!cart) return null
  return {
    storeId: cart.storeId,
    storeName: cart.storeName,
    items: cart.items.slice(),
  }
}

function ensureStore(storeId, storeName) {
  const cart = read()
  if (!cart) {
    write({ storeId, storeName, items: [] })
    return
  }
  if (cart.storeId !== storeId) {
    write({ storeId, storeName, items: [] })
    wx.showToast({ title: '已切换门店，购物车已清空', icon: 'none' })
  }
}

function addItem(storeId, storeName, item) {
  ensureStore(storeId, storeName)
  const cart = read()
  const existing = cart.items.find((i) => i.menu_item_id === item.menu_item_id)
  if (existing) {
    existing.quantity += item.quantity
  } else {
    cart.items.push({
      menu_item_id: item.menu_item_id,
      name: item.name,
      unit_price_cents: item.unit_price_cents,
      stock: item.stock == null ? null : item.stock,
      quantity: item.quantity,
    })
  }
  write(cart)
}

function updateQuantity(storeId, itemId, quantity) {
  const cart = read()
  if (!cart || cart.storeId !== storeId) return
  const index = cart.items.findIndex((i) => i.menu_item_id === itemId)
  if (index === -1) return
  if (quantity <= 0) {
    cart.items.splice(index, 1)
  } else {
    cart.items[index].quantity = quantity
  }
  write(cart)
}

function removeItem(storeId, itemId) {
  updateQuantity(storeId, itemId, 0)
}

function clearCart() {
  wx.removeStorageSync(CART_KEY)
}

function getTotalCount() {
  const cart = read()
  if (!cart) return 0
  return cart.items.reduce((sum, i) => sum + i.quantity, 0)
}

function getTotalCents() {
  const cart = read()
  if (!cart) return 0
  return cart.items.reduce((sum, i) => sum + i.unit_price_cents * i.quantity, 0)
}

module.exports = {
  getCart,
  ensureStore,
  addItem,
  updateQuantity,
  removeItem,
  clearCart,
  getTotalCount,
  getTotalCents,
}
