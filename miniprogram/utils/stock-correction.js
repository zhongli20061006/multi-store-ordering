// 提交失败后按后端返回的库存不足明细调整购物车条目（纯函数）。
function applyStockCorrection(items, insufficientItems) {
  const availableById = {}
  ;(insufficientItems || []).forEach((entry) => {
    availableById[entry.menu_item_id] = entry.available_stock
  })
  return items.map((item) => {
    const available = availableById[item.menu_item_id]
    if (available == null || item.quantity <= available) return item
    return Object.assign({}, item, { quantity: available, stock: available })
  })
}

module.exports = { applyStockCorrection }
