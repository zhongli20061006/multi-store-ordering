// 统一 request：Promise、超时 10s、{code,message,data} 解析、统一 toast。
// loading 由调用方按需传入（整页加载用）；局部操作由页面控制按钮态。
const { BASE_URL } = require('../config')

function request({ url, method = 'GET', data, loading = false, loadingText = '加载中' }) {
  if (loading) wx.showLoading({ title: loadingText, mask: true })
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      timeout: 10000,
      header: { 'Content-Type': 'application/json' },
      success(res) {
        const { statusCode, data: body } = res
        if (statusCode >= 200 && statusCode < 300 && body && body.code === 0) {
          resolve(body.data)
          return
        }
        const msg = (body && body.message) || '请求失败'
        if (loading) wx.hideLoading()
        wx.showToast({ title: msg, icon: 'none' })
        reject(new Error(msg))
      },
      fail() {
        if (loading) wx.hideLoading()
        wx.showToast({ title: '网络异常，请稍后重试', icon: 'none' })
        reject(new Error('网络异常'))
      },
      complete() {
        if (loading) wx.hideLoading()
      },
    })
  })
}

module.exports = { request }
