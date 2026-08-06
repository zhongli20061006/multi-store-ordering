// 再来一单：把订单明细快照映射为购物车条目（仅用于展示；下单仍由后端按现价重算/校验库存上架）
function itemsFromOrder(order) {
  return (order.items || []).map((i) => ({
    menu_item_id: i.menu_item_id,
    name: i.item_name,
    unit_price_cents: i.unit_price_cents,
    quantity: i.quantity,
  }))
}

module.exports = { itemsFromOrder }
