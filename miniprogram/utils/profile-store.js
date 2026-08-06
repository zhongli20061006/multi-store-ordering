// 个人资料（本地）：昵称 + 常用手机号；原型无登录，本地存储，下单页预填。
const PROFILE_KEY = 'profile:v1'

function read() {
  const p = wx.getStorageSync(PROFILE_KEY) || {}
  return { nickname: p.nickname || '微信用户', phone: p.phone || '' }
}

function save(profile) {
  const next = {
    nickname: (profile.nickname || '').trim() || '微信用户',
    phone: (profile.phone || '').trim(),
  }
  wx.setStorageSync(PROFILE_KEY, next)
  return next
}

module.exports = { read, save }
