## 改动说明

<!-- 用一两段话说明本次改动解决了什么问题、怎么解决的。 -->

## 改动范围

- [ ] 后端（backend/）
- [ ] 商家后台（admin/）
- [ ] 顾客小程序（miniprogram/）
- [ ] 文档/CI/其他

## 验证证据

<!-- 必须贴出实际验证输出，例如：
cd backend && .\.venv\Scripts\python.exe -m pytest -q   → 123 passed
cd admin && npm run test && npm run build               → 16 passed + 构建通过
cd miniprogram && npm test                              → 76 passed
或接口冒烟请求/响应摘要 -->

## 关联 issue

Fixes #（如有）

## 检查清单

- [ ] 未使用 `git add .`，提交路径明确
- [ ] 提交信息为中文并含验证证据
- [ ] 无真实密钥、`.env`、数据库文件入库
- [ ] 无支付/微信登录/核销/上线的假实现
