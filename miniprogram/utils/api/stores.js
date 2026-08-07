const { request } = require('../request')

function getStores() {
  return request({ url: '/stores', loading: true, loadingText: '加载中' })
}

function getStoreMenu(storeId) {
  return request({ url: `/stores/${storeId}/menu`, loading: true, loadingText: '加载中' })
}

function getStore(storeId) {
  return request({ url: `/stores/${storeId}` })
}

function getStoreItem(storeId, itemId) {
  return request({ url: `/stores/${storeId}/items/${itemId}` })
}

function getStoreBanners(storeId) {
  return request({ url: `/stores/${storeId}/banners` })
}

module.exports = { getStores, getStoreMenu, getStore, getStoreItem, getStoreBanners }
