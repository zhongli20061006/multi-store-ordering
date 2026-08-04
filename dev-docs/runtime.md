# 运行环境与启动（runtime truth）

> 本文件记录当前可复现的运行基线；依赖安装后以实际解析版本回写。

## 本机环境

- Windows，Python 3.11.4，Node.js 24.15.0，npm 11.12.1，Git 2.54.0

## 后端

- 依赖清单：backend/requirements.txt
- 环境变量：复制 backend/.env.example → backend/.env（密钥与种子管理员密码）
- 安装：`cd backend && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt`
- 初始化数据：`.venv\Scripts\python -m app.seed`（在 backend 目录执行；重复执行会跳过）
- 启动：`.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000`
- 健康检查：`http://127.0.0.1:8000/api/v1/health`
- 测试：`.venv\Scripts\python -m pytest`

## 已核验版本（2026-08-04）

- Python 3.11.4；fastapi 0.141.1；sqlalchemy 2.0.51；pydantic 2.13.4；PyJWT/bcrypt 已装
- 测试：32 passed（鉴权、门店归属、菜单、订单金额、状态机、幂等、限库存、越权）
- 实机验证：/api/v1/health 返回 ok；下单 total=2400、status=pending；admin1 查单 1 单；跨店访问返回 403
- 演示账号：admin1 → 中山路店，admin2 → 万达店，密码 admin123456（仅本地开发用，正式使用前必须改）

## 商家后台

- 待实施（1.3）：`cd admin && npm install && npm run dev`（端口 5173）

## 微信小程序

- 待实施（1.4）：微信开发者工具导入 miniprogram/，测试号预览；后端 baseURL 指向本机局域网地址

## 未验证

- 真实 AppID、微信登录、支付、部署、HTTPS、域名备案等均为未验证（本阶段不涉及）。
