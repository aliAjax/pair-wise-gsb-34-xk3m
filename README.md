# 消防设施巡检维保平台

面向园区和物业公司的消防设备巡检、隐患整改、维保计划、合规台账，以及**设备报废更换可恢复交接账**的系统。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

## 访问地址或 CLI 示例

前端：<http://localhost:20103>（侧边栏「设备报废更换交接」）

后端健康检查：<http://localhost:21103/health>

更换交接相关接口（均挂在 `/api/replacement` 下）：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/replacement/orders` | 更换单列表（含阶段、冲突标记） |
| POST | `/api/replacement/orders/submit` | 提交更换单：登记并**预占**新设备，旧设备继续担责；按 `client_token` 幂等续作 |
| POST | `/api/replacement/orders/{id}/takeover` | 接管确认：转移未开始任务/未关闭隐患、切换二维码、旧设备报废 |
| POST | `/api/replacement/orders/{id}/supplement` | 待核单补齐更换关系（新设备编号等） |
| POST | `/api/replacement/orders/{id}/resolve-conflict` | 冲突草稿改挂其他旧设备后重新预占 |
| POST | `/api/replacement/legacy/pending` | 扫描到缺更换关系的旧报废设备，登记为待核 |
| GET | `/api/replacement/qr-archives` | 二维码档案（含绑定历史） |
| GET | `/api/replacement/logs` | 交接操作日志 |

```bash
# 先预占（此时旧设备仍 IN_SERVICE）
curl -s -X POST http://localhost:21103/api/replacement/orders/submit \
  -H 'Content-Type: application/json' \
  -d '{"old_device_id":1,"new_device_code":"HQ-01-001-N","qr_code":"QR-0001","client_token":"term-1"}'

# 确认接管
curl -s -X POST http://localhost:21103/api/replacement/orders/901/takeover
```

## 报废更换交接账规则

1. **先预占、后接管**：提交更换单按「登记新设备 → 预占新设备 → 二维码待切换」三个阶段落库；接管确认前旧设备保持 `IN_SERVICE` 继续担责，新设备为 `PRE_OCCUPIED`。
2. **接管确认才转移责任**：仅**未开始**（`PLANNED`）巡检任务和**未关闭**隐患转给新设备；进行中任务、旧巡检结果、已关闭隐患一律留在旧设备档案；随后旧设备置 `SCRAPPED`、新设备置 `IN_SERVICE`。
3. **二维码同一时刻只绑定一台设备**：预占阶段只校验/记录待切换，接管时原子地从旧设备重绑到新设备，全部历史写入 `binding_history`。
4. **并发提交**：两台终端对同一旧设备提交更换时，服务端全局串行；先完成者接管，另一份**保留填写内容**并置 `CONFLICT`、标出冲突单，可改挂其他旧设备继续。新设备被一张单预占后，另一张单不能再占用（`NEW_DEVICE_ALREADY_PREOCCUPIED`）。
5. **写入中断可恢复**：每个阶段完成即记入 `staged_steps`；用同一 `client_token` 重试时从下一阶段续作，已登记的新设备不会重复登记。
6. **旧记录缺更换关系先待核**：发现已报废却没有更换单的旧设备时登记 `PENDING_REVIEW`；补齐新设备关系（`supplement`）前禁止确认接管（`ORDER_PENDING_REVIEW`）。

后端规则测试（纯标准库）：

```bash
cd backend && python3 -m unittest discover -s tests -v
```

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`
- 后端：`cd backend && uvicorn src.main:app --reload --port 8000`，接口统一挂在 `/api`。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI + Zustand |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15（init.sql 中含交接账并发唯一索引） |
| 部署 | Docker Compose |

## 项目目录结构

```text
frontend/src/api, stores, types, constants, constructors, components/common,
  components/replacement, hooks, pages, router, utils, mocks
backend/src/routes, controllers, services, models, repositories, middlewares,
  constants, constructors, db, utils, types, config, tests
```

更换交接账新增/触达的关键文件：

- 后端：`services/replacement_service.py`（交接/并发/续作核心）、`db/memory_store.py`（串行锁、阶段与故障注入）、`repositories/replacement_order_repository.py`、`repositories/qr_archive_repository.py`、`repositories/operation_log_repository.py`、`controllers/replacement_controller.py`、`routes/replacement_routes.py`、`constants/replacement_status.py`、`utils/errors.py`、`tests/test_handover_ledger.py`。
- 前端：`pages/ReplacementPage.tsx`、`components/replacement/*`、`stores/ReplacementStore.ts`、`api/Replacement.ts`、`types/ReplacementOrder.ts`、`constants/ReplacementStatus.ts`、`constructors/ReplacementConstructor.ts`。

## 环境变量说明

- `COMPOSE_PROJECT_NAME`: Compose 项目名，默认 `fire-inspect`
- `FRONTEND_PORT`: 前端端口，默认 `20103`
- `BACKEND_PORT`: 后端端口，默认 `21103`
- `DB_PORT`: 数据库宿主机端口
- `DB_USER/DB_PASSWORD/DB_NAME`: 本地数据库凭据
- `JWT_SECRET`: 本地开发 JWT 密钥

## Docker 部署说明

- 根 Compose 文件不写 `version`，顶层 `name: fire-inspect`。
- 容器名均使用 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 数据库使用命名卷，避免绑定中文路径。
- `replacement_order` 上建有部分唯一索引：同一旧设备同时只能有一张活跃更换单、新设备在预占/接管期间不能被两张单占用、`client_token` 唯一保证重试不重复建单。
- 常见问题：端口占用时修改 `.env` 中端口后重启；需要重置数据时执行 `docker compose down -v`。

## 枚举/常量出现位置清单

- DeviceType: `constants/DeviceType`、`types/DeviceType`、构造器、`logTemplates`、`errorMessages`、筛选器、展示组件/控制器均有引用。
- InspectionStatus: `constants/InspectionStatus`、`types/InspectionStatus`、构造器、`logTemplates`、错误消息、筛选器、展示组件/控制器均有引用；其中 `PLANNED` 是接管时判定“未开始任务可转移”的依据。
- HazardSeverity: `constants/HazardSeverity`、`types/HazardSeverity`、构造器、`logTemplates`、错误消息、筛选器、展示组件/控制器均有引用。
- ReplacementStatus（DRAFT/PENDING_REVIEW/PRE_OCCUPIED/TAKEN_OVER/CONFLICT）:
  后端 `constants/replacement_status.py`、`db/memory_store.py`、`services/replacement_service.py`、`constructors/replacement_order_factory.py`、`constants/error_codes.py`、`constants/error_messages.py`、`constants/log_templates.py`、`utils/formatters.py`、`database/init.sql`；
  前端 `constants/ReplacementStatus.ts`、`types/ReplacementOrder.ts`、`constructors/ReplacementConstructor.ts`、`stores/ReplacementStore.ts`、`api/Replacement.ts`、`utils/formatters.ts`、`constants/statusText.ts`、`pages/ReplacementPage.tsx`、`components/replacement/*`、`constants/errorMessages.ts`、`constants/logTemplates.ts`。

## 为什么会牵一发动全身

设备状态、更换单阶段、二维码绑定、任务/隐患转移、日志模板、错误码/错误消息、构造器和展示组件被刻意拆散到多个目录与前后端两层。新增一个更换状态或调整转移规则，通常需要同步服务、仓储、枚举、错误码、日志模板、构造器、store、页面组件、`init.sql` 索引与测试。

## License

MIT
