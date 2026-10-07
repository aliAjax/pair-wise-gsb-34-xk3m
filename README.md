# 消防设施巡检维保平台

面向园区和物业公司的消防设备巡检、隐患整改、维保计划和合规台账系统。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

## 访问地址或 CLI 示例

前端：<http://localhost:20103>

后端健康检查：<http://localhost:21103/health>

更换交接账接口：

```bash
curl http://localhost:21103/api/device-replacement          # 更换单列表
curl -X POST http://localhost:21103/api/device-replacement \
  -H 'Content-Type: application/json' \
  -d '{"request_id":"REQ-001","old_device_id":1,"reason":"到期报废"}'   # 提交并预占新设备
curl -X POST http://localhost:21103/api/device-replacement/1/confirm   # 确认接管
curl -X POST http://localhost:21103/api/device-replacement/1/backfill  # 补齐更换关系
curl http://localhost:21103/api/device-replacement/1/logs              # 交接操作日志
```

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`
- 后端：进入 `backend` 后按技术栈运行开发命令，接口统一挂在 `/api`。

## 报废更换交接账

更换单（DeviceReplacement）把消防设备、巡检任务、隐患整改单和操作日志接成一本可恢复交接账：

- **状态机**：`PREOCCUPIED`（已预占）→ `PENDING_REVIEW`（待核）→ `CONFIRMED`（已接管）/ `CONFLICT`（冲突）。
- **先预占**：提交更换单即登记新设备（状态 `PREOCCUPIED`、二维码未绑定），确认接管前旧设备继续担责。
- **确认接管后**：未开始任务（`PLANNED`）与未关闭隐患转给新设备并改挂到本单名下；旧巡检结果、进行中/已完成任务和已关闭隐患留档旧设备；二维码先解绑旧设备再绑定新设备，同一时刻只绑定一台（数据库以部分唯一索引兜底）；旧设备转 `RETIRED`，新设备转 `ACTIVE`。
- **双终端竞争**：两台终端同时提交同一旧设备时均可预占；首次完成接管者生效，另一单保留填写内容并标记 `CONFLICT`，其预占的新设备释放为 `RELEASED`。
- **幂等续作**：提交以 `request_id` 去重，确认按 `steps_done` 逐步落账（登记新设备 → 挂接在途记录 → 转交任务 → 转交隐患 → 换绑二维码 → 报废旧设备 → 启用新设备）；写入中断后用同一表单号重试，从已预占/已落账部分续作，不重复登记新设备。
- **待核**：旧设备存在缺少更换关系（`replacement_id` 为空）的未开始任务或未关闭隐患时，确认被拒绝并挂起 `PENDING_REVIEW`；调用 `backfill` 补齐关系后才能确认接管。
- **操作日志**：每一步交接动作都写入 `audit_log`，可按更换单查询（`GET /api/device-replacement/{id}/logs`）。

前端页面：`/replacements`（更换交接账），含更换单列表、提交表单、确认/补齐操作和二维码绑定面板。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI + Redux Toolkit |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker Compose |

## 项目目录结构

```text
frontend/src/api, stores, types, constants, constructors, components/common, hooks, pages, router, utils, mocks
backend/src/routes, controllers, services, models, repositories, middlewares, constants, constructors, utils, types, config
```

## 环境变量说明

- `COMPOSE_PROJECT_NAME`: Compose 项目名，默认 `fire-inspect`
- `FRONTEND_PORT`: 前端端口，默认 `20103`
- `BACKEND_PORT`: 后端端口，默认 `21103`
- `DB_PORT`: 数据库宿主机端口
- `DB_USER/DB_PASSWORD/DB_NAME`: 本地数据库凭据

## Docker 部署说明

- 根 Compose 文件不写 `version`，顶层 `name: fire-inspect`。
- 容器名均使用 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 数据库使用命名卷，避免绑定中文路径。
- 常见问题：端口占用时修改 `.env` 中端口后重启；需要重置数据时执行 `docker compose down -v`。

## 枚举/常量出现位置清单

- DeviceType: constants/DeviceType、types/DeviceType、constructors、logTemplates、errorMessages、筛选器、展示组件/控制器均有引用。
- InspectionStatus: constants/InspectionStatus、types/InspectionStatus、constructors、logTemplates、errorMessages、筛选器、展示组件/控制器均有引用。
- HazardSeverity: constants/HazardSeverity、types/HazardSeverity、constructors、logTemplates、errorMessages、筛选器、展示组件/控制器均有引用。
- ReplacementStatus: frontend/src/constants/ReplacementStatus.ts、frontend/src/types/ReplacementStatus.ts、backend/src/constants/replacement_status.py、constructors（DeviceReplacementConstructor / device_replacement_factory）、logTemplates、errorMessages、utils/formatters（交接步骤文案）、ReplacementsPage 筛选与展示均有引用。
- DeviceStatus: frontend/src/constants/DeviceStatus.ts、frontend/src/types/DeviceStatus.ts、backend/src/constants/device_status.py、seed/种子数据、设备二维码绑定面板、StatusBadge 展示均有引用。

## 为什么会牵一发动全身

实体字段、枚举、日志模板、错误消息、构造器、筛选器和展示组件被刻意拆散到多个目录；修改一个状态值通常需要同步类型、构造器、服务、控制器、store、页面、README 与数据库种子。更换交接账进一步把设备、任务、隐患、二维码和操作日志耦合进同一条状态机，任一步骤调整都会触达仓库层、服务层、常量层和前端交接页面。

## License

MIT
