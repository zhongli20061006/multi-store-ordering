// 商品规格（纯函数）：默认选中每组第一项；构造下单 specs；格式化展示。
function defaultSelections(groups) {
  return (groups || []).map((group) => ({ name: group.name, option: group.options[0] }))
}

function buildSpecsPayload(selections) {
  return (selections || []).map((s) => ({ name: s.name, option: s.option }))
}

function formatSpecs(specs) {
  if (!specs) return ''
  return Object.keys(specs)
    .map((key) => specs[key])
    .join(' · ')
}

module.exports = { defaultSelections, buildSpecsPayload, formatSpecs }
