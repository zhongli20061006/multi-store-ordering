# 项目内部真源索引

本目录是项目的内部开发真源（truth），不是对外文档。AI 和开发人员在做任何判断、改代码、验收前，先读本索引指向的当前真源；文档与代码冲突时，以真源为准并先修正真源。

## 真源清单

| 文档 | 职责 | 状态 |
| --- | --- | --- |
| [design-draft.md](design-draft.md) | 1-6 步架构讨论汇总的设计初稿（评审依据） | 待用户评审 |
| [project-brief.md](project-brief.md) | 产品定位、目标用户、MVP、非目标、演进边界 | 已确认（待技术路线确认后定稿） |
| [function-list.md](function-list.md) | 功能清单、复杂功能索引、大阶段规划 | 已建立 |
| [stage-plan.md](stage-plan.md) | 大阶段划分与各阶段验收标准 | 已建立 |
| [technical-selection.md](technical-selection.md) | 技术选型唯一 owner：驱动因素、证据、候选组合、最终组合、迁移悬崖 | recommendation_ready（待用户确认产品后果） |
| [architecture.md](architecture.md) | 当前宏观架构：进程、模块、owner map、数据/信任/事务边界 | 草案（随选型确认而定稿） |
| [database-design.md](database-design.md) | 数据对象、表结构、字段规则、订单生命周期 | 草案 |
| [frontend-architecture.md](frontend-architecture.md) | 小程序与商家后台的页面、组件、数据流、设计基础 | 草案 |
| [backend-boundary.md](backend-boundary.md) | 后端责任边界、API 合同、模块 owner | 草案 |
| [security-boundary.md](security-boundary.md) | 身份、权限、数据归属、敏感信息、安全红线 | 草案 |
| [acceptance.md](acceptance.md) | 原型验收规则与证据要求 | 草案 |
| [runtime.md](runtime.md) | 运行环境、启动命令、依赖与版本 | 已核验（2026-08-04） |
| stages/stage-1.md | 第一阶段（本地原型）实施真源 | 执行中（1.1/1.2 已完成，下一步 1.3） |

## 规则

- 一个概念只有一个 owner，任何文档不得复制另一份真源的字段规则。
- 新结论只有写回对应真源后才算生效；聊天里的决定不算真源。
- 缺失证据一律标记 `未验证`，不得包装成已完成。
- 技术选型确认前，不得写功能代码。
