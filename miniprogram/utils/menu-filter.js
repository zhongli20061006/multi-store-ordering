// 菜单本地过滤（原型：菜单已整单加载；商品量大后再上服务端搜索/分页）
function filterMenu(groups, keyword) {
  const kw = (keyword || '').trim().toLowerCase()
  if (!kw) return groups
  return groups
    .map((g) => Object.assign({}, g, { items: g.items.filter((i) => (i.name || '').toLowerCase().includes(kw)) }))
    .filter((g) => g.items.length > 0)
}

module.exports = { filterMenu }
