# 日麻俱乐部（HuatingRiichiClub）重构项目

本仓库用于把原有的老日麻雀庄运营系统重构为现代化架构：后端使用 FastAPI、管理后台使用 Vue 3、移动小程序使用 UniApp。目标是可维护、模块化、便于本地开发与自动部署。

## 主要目标
- 保持现有业务流程与数据的兼容性（逐步迁移）
- 使用 FastAPI 提供稳定、可测试的 REST/GraphQL 接口
- 管理后台：Vue 3 + Vite，易于扩展的权限与运营页面
- 移动端：UniApp 小程序，复用组件/接口

## 技术栈
- 后端：Python 3.10+、FastAPI、Uvicorn / Gunicorn
- 数据库：PostgreSQL / MySQL（按项目配置）
- 管理后台：Vue 3、Vite、Pinia、Vue Router
- 小程序：UniApp
- 工具与流程：Docker、Git、CI/CD（可接 GitHub Actions / Azure DevOps / GitLab CI）

## 仓库结构（概要）
- `service/`：后端 FastAPI 源代码与文档
  - `service/docs/`：后端相关说明（见快速开始）
- `frontend/`：管理后台代码（Vue 3）
- `uniapp/`：小程序源码与产品分析文档（见 `uniapp/项目分析`）

详细的页面与接口说明见：
- 后端快速开始：[service/docs/05-fastapi-quickstart.md](service/docs/05-fastapi-quickstart.md#L1)
- 小程序与页面文档：[uniapp/项目分析/00-项目与接口总览.md](uniapp/项目分析/00-项目与接口总览.md#L1)

## 快速开始（开发环境）
下面给出常见的本地开发示例，实际命令请参照各模块下的 README 或文档。

1) 后端（FastAPI）

```powershell
# 进入后端目录
cd service

# 创建虚拟环境（Windows 示例）
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖（如有 requirements.txt）
pip install -r requirements.txt

# 启动开发服务器（若入口为 app.main:app，替换为实际路径）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

有关后端初始化、数据库迁移等详细步骤，请参阅：[service/docs/05-fastapi-quickstart.md](service/docs/05-fastapi-quickstart.md#L1)

2) 管理后台（Vue 3）

```bash
# 进入管理后台目录（若位于 frontend/ 或 service/frontend/）
cd frontend

# 安装依赖（npm / yarn / pnpm）
npm install

# 启动开发
npm run dev
```

3) UniApp 小程序

- 推荐使用 HBuilderX 或使用 uni-app 官方脚手架与 `npm`/`cli`。
- 参考项目内 `uniapp/项目分析` 中的页面与接口定义。

## 环境与配置
- 使用 `.env` 或 `config` 文件管理敏感配置（不要将 `.env` 提交到仓库）。
- 推荐为不同环境（dev/staging/prod）准备不同的配置文件或使用环境变量。

## 数据库迁移与备份
- 若使用 Alembic/Flyway 等工具，请在 `service/` 下维护迁移脚本并把迁移命令加入 `Makefile` 或 npm scripts。

## 部署建议
- 后端：使用 Gunicorn + Uvicorn workers 或直接使用 Uvicorn 在容器中运行；使用 Dockerfile 构建镜像并推送镜像仓库。
- 前端：构建静态文件后部署到 CDN 或静态主机（如 Nginx）。
- 小程序：使用 uniapp 构建并通过平台上传小程序包。

示例 Docker 流程（概述）：

1. 后端：构建镜像 -> CI 运行测试 -> 推送镜像 -> 部署到 Kubernetes / VM
2. 前端：`npm run build` -> 将构建产物上传到静态托管或容器

## 贡献与开发流程
- 使用 GitFlow / trunk-based flow：提交前运行 lint、单元测试与基本静态检查。
- 提交 PR 时请附上变更说明、影响范围与回归风险评估。

## 常见问题与参考文档
- 后端快速启动与 API 设计指南见： [service/docs/05-fastapi-quickstart.md](service/docs/05-fastapi-quickstart.md#L1)
- 现有页面与接口总览见： [uniapp/项目分析/00-项目与接口总览.md](uniapp/项目分析/00-项目与接口总览.md#L1)
- 旧系统的 API 列表与管理员页面说明见： [service/docs/02-legacy-api-list.md](service/docs/02-legacy-api-list.md#L1) 和 [service/docs/03-legacy-admin-pages.md](service/docs/03-legacy-admin-pages.md#L1)

## 联系方式
- 若需项目相关历史信息或运营规则，请联系项目负责人或查看旧系统文档目录。

---
如需我把 README 同步翻译为英文版，或为后端/前端添加具体的 `Dockerfile`、`docker-compose.yml` 与 CI 配置模板，我可以继续生成。请告诉我你希望优先完善的模块（后端/管理后台/小程序/部署）。
