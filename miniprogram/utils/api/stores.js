const { request } = require('../request')

function getStores() {
  return request({ url: '/stores', loading: true, loadingText: '加载中' })
}

function getStoreMenu(storeId) {
  return request({ url: `/stores/${storeId}/menu`, loading: true, loadingText: '加载中' })
}

module.exports = { getStores, getStoreMenu }
