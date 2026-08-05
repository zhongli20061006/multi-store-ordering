# 商家后台（admin）

多门店点单系统的商家网页后台：管理门店、菜单、订单，对接后端 `backend/` 的 `/api/v1` 管理接口（纯前端，无独立后端）。

## 技术栈

Vue 3 / TypeScript / Vite / Element Plus / vue-router / Pinia / axios / vitest

## 快速开始

先启动后端（见 `../backend/README.md`），再在 `admin/` 目录执行：

```powershell
npm install
npm run dev
```

访问 http://localhost:5173/login （注意用 localhost），演示账号：`admin1` / `admin123456`（或 `admin2`）。

## 常用命令

```powershell
npm run dev      # 开发服务（端口 5173）
npm run test     # 单元测试（vitest）
npm run build    # 类型检查 + 生产构建（输出 dist/）
npm run preview  # 预览生产构建
```

## 功能

- 登录 / 退出；未登录自动跳转登录页
- 主布局：侧边栏导航 + 顶栏“当前门店”选择（记住上次选择）
- 门店管理：列表、新建、编辑、开关营业、删除（有订单的门店后端拒绝删除）
- 菜单管理：分类 CRUD（删除连带下架分类内商品）、商品 CRUD（价格以元输入、可设限库存或留空不限量、上下架）
- 订单管理：按门店/状态筛选、8 秒自动刷新、接单、完成、取消（选择“未制作/已制作”）、标记到店付款、详情（完整电话与明细）；列表手机号由后端脱敏

## 目录结构

```text
admin/src/
├── api/          # 接口调用（http.ts 统一封装 JWT 与错误提示）
├── components/   # 公共组件（金额/状态徽章/电话）
├── composables/  # useAsync（统一 loading/错误）
├── router/       # 路由与登录守卫
├── stores/       # auth（登录态）、store（当前门店）
├── styles/       # tokens.css（样式变量唯一 owner）
├── utils/        # 金额转换等纯工具
└── views/        # Login / Layout / Stores / MenuManage / Orders
```

## 说明

- 移动端适配（抽屉菜单）为原型期可选项，暂未实现。
- 打包体积提示（Element Plus 全量引入）为已知优化项，上线前按需处理。
