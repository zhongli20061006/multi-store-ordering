# 贡献指南

感谢你对「多门店线上点单系统」的兴趣！本项目是小团队/个人维护的开源原型，遵循简洁、可验证的协作方式。

## 开发环境

- Python 3.11+（后端，**必须使用 `backend/.venv`，禁用系统 Python**）
- Node.js 20+（建议 24）
- 微信开发者工具（预览小程序，测试号即可）

## 起步

按根 [README.md](README.md)「快速开始」三步把项目跑起来，并确认测试全绿：

```powershell
cd backend && .\.venv\Scripts\python.exe -m pytest -q
cd admin && npm run test && npm run build
cd miniprogram && npm test
```

## 提交规范

- 分支：功能开发在 `feat/*` 分支进行，完成后合入 `master`。
- 提交信息用中文，遵循 `type(scope): 摘要` 格式（如 `feat(backend): ...`、`fix(miniprogram): ...`、`docs: ...`），并在正文写明**验证证据**（测试结果、接口冒烟输出等）。
- 禁止 `git add .`，用明确路径暂存。
- 每个逻辑改动独立提交；验收和回写文档后再提交 Git 检查点。

## 测试门禁

行为变更遵循「先写失败测试 → 实现 → 全量回归」：

- 后端业务规则（金额/状态机/库存/归属）必须有 pytest 覆盖。
- 后台纯逻辑（格式化/下载/告警/审计）有 vitest 覆盖；小程序纯逻辑有 node:test 覆盖。
- 合入前必须通过全部测试与后台构建，并由维护者复核。

## PR 流程

1. 在 issue 中说明要解决的问题（或认领已有 issue）。
2. 从 `master` 切 `feat/xxx` 分支实现。
3. 本地跑通全部测试与构建，按提交规范逐个提交。
4. 发起 PR，按 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md) 填写改动说明与验证证据。

## 行为准则

- 不提交真实密钥、`.env`、数据库文件、内部开发文档（`dev-docs/` 本地保留，不推送）。
- 不引入 mock 假成功；缺失证据如实标注「未验证」。
- 支付/微信登录/核销/上线等阶段四/五能力不在本仓库实现，相关改动会先讨论边界。
