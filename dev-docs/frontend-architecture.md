# 前端架构真源

## 一、设计基础（最小 token 集）

- 主色：#FF6B35（橙，点单场景常见食欲色）；辅色：#333 文字、#999 次要文字；成功/危险色使用 Element Plus 默认。
- 金额一律以「元」展示（后端传分，前端除 100 后保留两位）。
- 样式漂移防线：小程序端样式集中在 `miniprogram/styles/`，后台使用 Element Plus 默认主题 + 少量 CSS 变量，禁止页面内散落硬编码色值。
- 组件复用：商品卡片、数量步进器、状态徽标、价格文本必须抽公共组件，禁止复制粘贴实现。

## 二、微信小程序（miniprogram/）

原生开发，JS；微信开发者工具 + 测试号。

页面：

| 页面 | 路径 | 说明 |
| --- | --- | --- |
| 门店列表 | pages/store-list | 请求营业中门店；支持 onLoad 携带 store_id 直达菜单（扫码） |
| 门店菜单 | pages/menu | 分类切换 + 商品 + 购物车栏；展示限购/库存提示 |
| 确认下单 | pages/checkout | 明细、联系人/电话/备注、提交 |
| 下单成功 | pages/order-success | 订单号 + 状态提示 |
| 我的订单 | pages/my-orders | 输入手机号+订单号查询订单详情 |

公共组件：`components/product-card`、`components/cart-bar`、`components/price`、`components/status-badge`。

数据流：

- `utils/api.js`：统一 request 封装（baseURL 由 `config.js` 提供，局域网地址按 runtime.md 配置）。
- `store/cart.js`：本地购物车（按门店隔离：切换门店清空购物车并提示）。
- 提交订单：生成 `idempotency_key`（时间戳+随机），失败重试不产生重复订单。
- 下单参数带 entry_type：扫码进入默认 dinein，列表进入默认 preorder。

## 三、商家后台（admin/）

Vue 3 + TypeScript + Vite + Element Plus + vue-router + Pinia。

页面：

| 路由 | 说明 |
| --- | --- |
| /login | 登录 |
| /stores | 门店列表/新建/编辑/开关 |
| /stores/:id/menu | 菜单管理（分类 + 商品） |
| /orders | 订单列表（按门店/状态筛选，接单/完成/取消/标记付款） |

数据流：

- `src/api/`：axios 封装（JWT 注入、401 跳登录、统一错误提示）。
- `src/stores/auth.ts`：登录态与用户信息。
- 登录后选择“当前门店”并记住上次选择；订单列表 8 秒轮询，手机号脱敏展示。
- 表单金额输入以元为单位，提交转分为后端字段。

## 四、前后端契约

API 契约唯一 owner：dev-docs/backend-boundary.md。前端不得自行定义业务规则（如金额计算、状态流转），只展示后端结果。
