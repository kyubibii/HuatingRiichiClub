# 项目初始化命令指南

> 目标架构：FastAPI 后端 + Vue3 OP（后台管理） + UniApp 小程序
> 运行环境：WSL2 Debian / Linux（生产）+ Windows 本地（开发）
> 容器化：Docker + docker-compose
> 版本策略：截至 2026 年稳定最新版

---

## 一、前置环境检查

### 1.1 所需工具版本

| 工具      | 最低版本 | 推荐安装方式                        | 用途                          |
| --------- | -------- | ----------------------------------- | ----------------------------- |
| Python    | 3.12+    | pyenv / 系统包管理器                | FastAPI 后端                  |
| uv        | 0.5+     | `pip install uv` 或官方脚本       | Python 包管理                 |
| Node.js   | 20 LTS   | nvm / fnm                           | Vue3 + UniApp                 |
| pnpm      | 9+       | `npm install -g pnpm`             | 前端包管理                    |
| Docker    | 27+      | Docker Desktop (Win) / apt (Debian) | 容器化                        |
| HBuilderX | 4.x      | 官网下载                            | UniApp 开发（可选，CLI 替代） |
| Git       | 2.40+    | 系统包管理器                        | 版本控制                      |

### 1.2 Windows 本地环境检查命令（PowerShell）

```powershell
python --version          # 期望: Python 3.12.x
uv --version              # 期望: uv 0.5.x
node --version            # 期望: v20.x.x
pnpm --version            # 期望: 9.x.x
docker --version          # 期望: Docker version 27.x.x
docker compose version    # 期望: Docker Compose version v2.x.x
git --version             # 期望: git version 2.x.x
```

### 1.3 WSL2 Debian 环境安装（在 WSL 终端执行）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3
sudo apt install -y python3 python3-venv python3-dev

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 安装 Node 22 LTS（通过 nvm）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22

# 安装 pnpm
npm install -g pnpm

# 安装 Docker（Debian）
sudo apt install ca-certificates curl gnupg -y
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
sudo usermod -aG docker $USER  # 免 sudo 运行 docker（需重新登录生效）
```

---

## 二、项目目录结构规划

```
HuatingRiichiClub/
├── service/
│   ├── backend/           # FastAPI 后端
│   │   ├── app/
│   │   │   ├── domain/        # 领域层（实体、值对象、仓储接口）
│   │   │   ├── application/   # 应用层（服务、用例、DTO）
│   │   │   ├── infrastructure/# 基础设施层（ORM、Redis、外部服务）
│   │   │   ├── api/           # 表现层（FastAPI 路由器）
│   │   │   └── shared/        # 共享工具（配置、异常、中间件）
│   │   ├── alembic/           # 数据库迁移
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── .env.example
│   ├── frontend/          # Vue3 OP（后台管理）
│   │   ├── src/
│   │   │   ├── views/
│   │   │   ├── components/
│   │   │   ├── stores/        # Pinia
│   │   │   ├── api/           # axios 封装
│   │   │   └── router/
│   │   ├── public/
│   │   ├── dist/              # pnpm build 输出（被 FastAPI 挂载）
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── Dockerfile         # 仅用于生产构建
│   └── docker-compose.yml
├── uniapp/                # UniApp 小程序（重构）
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── docs/                  # 本目录
```

---

## 三、FastAPI 后端初始化

### 3.1 创建项目（uv）

```bash
# 进入 service 目录
cd HuatingRiichiClub/service

# 创建 backend 目录并初始化 uv 项目
mkdir backend && cd backend
uv init --python 3.13

# 添加核心依赖
uv add fastapi[standard]     # FastAPI + uvicorn + pydantic
uv add sqlalchemy[asyncio]   # 异步 ORM
uv add alembic               # 数据库迁移
uv add asyncpg               # PostgreSQL 异步驱动（推荐）
# 或 MySQL 驱动：
# uv add aiomysql

uv add redis[hiredis]        # Redis 客户端
uv add python-jose[cryptography]  # JWT
uv add passlib[bcrypt]       # 密码哈希
uv add python-multipart      # 文件上传
uv add httpx                 # 异步 HTTP 客户端（调微信 API）
uv add pydantic-settings     # 环境变量配置管理

# 添加开发依赖
uv add --dev pytest pytest-asyncio httpx
uv add --dev ruff             # 代码检查与格式化
```

### 3.2 创建目录结构

```bash
# 在 backend/ 目录下执行
mkdir -p app/{domain,application,infrastructure,api,shared}
mkdir -p app/domain/{user,game,bill,member,rank}
mkdir -p app/application/{user,game,bill,member,rank}
mkdir -p app/infrastructure/{database,cache,wechat,storage}
mkdir -p app/api/v1/{user,game,bill,member,rank,admin}
mkdir -p app/shared/{config,exceptions,middleware,security}
mkdir -p alembic/versions tests
touch app/__init__.py
touch app/main.py
touch alembic/env.py
touch .env.example
```

### 3.3 启动开发服务器

```bash
# 开发模式（热重载）
uv run fastapi dev app/main.py

# 或：
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：`http://localhost:8000/docs`（Swagger UI）

### 3.4 Alembic 数据库迁移

```bash
# 初始化 alembic（仅首次）
uv run alembic init alembic

# 生成迁移文件
uv run alembic revision --autogenerate -m "create user table"

# 执行迁移
uv run alembic upgrade head

# 回滚一步
uv run alembic downgrade -1
```

---

## 四、Vue3 OP 初始化（后台管理）

### 4.1 创建项目（Vite + TypeScript）

```bash
# 在 service/ 目录下执行（注意：目标目录必须为 frontend）
cd HuatingRiichiClub/service

pnpm create vite frontend -- --template vue-ts

cd frontend

# 安装基础依赖
pnpm install

# 添加核心依赖
pnpm add vue-router@4          # 路由
pnpm add pinia                 # 状态管理
pnpm add axios                 # HTTP 客户端
pnpm add element-plus          # UI 框架（推荐，覆盖所有后台需求）
pnpm add @element-plus/icons-vue  # Element Plus 图标

# 按需导入 Element Plus（推荐）
pnpm add -D unplugin-vue-components unplugin-auto-import

# 工具库
pnpm add dayjs                 # 时间处理
pnpm add echarts               # 图表（仪表盘）
```

### 4.2 开发模式（代理 FastAPI）

```bash
pnpm dev
```

在 `vite.config.ts` 中配置代理，将 `/api` 请求转发到 FastAPI：

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 不需要 rewrite，FastAPI 路由就是 /api/...
      }
    }
  },
  build: {
    outDir: 'dist',      // 构建产物输出到 dist/
    emptyOutDir: true,
  }
})
```

### 4.3 生产构建

```bash
pnpm build
# 构建产物在 service/frontend/dist/
# FastAPI 通过 StaticFiles 挂载此目录
```

---

## 五、FastAPI 挂载 Vue3 OP 产物（单端口方案）

### 5.1 开发态（代理模式）

开发阶段前后端分别跑在不同端口，通过 Vite 代理联调：

- FastAPI：`localhost:8000`（API 服务）
- Vue3 Dev Server：`localhost:5173`（前端开发服务，代理 `/api` → `:8000`）

### 5.2 生产态（静态挂载）

FastAPI 挂载 `dist/` 目录，所有 API 路由在 `/api/` 前缀下，其他请求返回 Vue 的 `index.html`（SPA 回退）：

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

app = FastAPI(title="花听雀庄 API", version="2.0.0")

# 注册 API 路由（必须在静态文件挂载之前）
from app.api.v1 import router as api_router
app.include_router(api_router, prefix="/api/v1")

# 挂载 Vue3 OP 构建产物
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # 静态资源（JS/CSS/图片等）
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    # SPA 回退：非 /api 路径均返回 index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not built"}
```

### 5.3 路由隔离规则

| 请求路径      | 处理方                    | 说明            |
| ------------- | ------------------------- | --------------- |
| `/api/v1/*` | FastAPI Router            | 所有 REST API   |
| `/ws/*`     | FastAPI WebSocket         | 实时台桌状态    |
| `/docs`     | FastAPI Swagger UI        | 仅开发环境暴露  |
| `/assets/*` | 静态文件挂载              | Vue3 构建产物   |
| 其他所有路径  | SPA 回退 →`index.html` | Vue Router 接管 |

---

## 六、UniApp 小程序初始化

### 方式 A：HBuilderX（推荐，兼容性最佳）

1. 打开 HBuilderX 4.x
2. 文件 → 新建 → 项目
3. 选择：**uni-app** → **默认模板**
4. 项目名：`uniapp`（或自定义）
5. Vue 版本：**Vue3**
6. 选择创建位置：`HuatingRiichiClub/uniapp/`

### 方式 B：CLI 方式

```bash
# 安装 @dcloudio/uvm 统一版本管理
npm install -g @dcloudio/uvm

# 在powershell使用 cli 创建
cd F:\projects\riichi\HuatingRiichiClub

npx degit dcloudio/uni-preset-vue#vite-ts uniapp

cd .\uniapp
pnpm install

# 运行到微信小程序（需要 HBuilderX 或微信开发者工具）
pnpm dev:mp-weixin
# 或
npx uni dev:mp-weixin

# 构建微信小程序
pnpm build:mp-weixin
```

### 6.1 UniApp 推荐依赖

```bash
# 网络请求封装（替代原 utils/request.js）
pnpm add @uni-helper/uni-network   # 基于 uni.request 的 axios 风格封装

# UI 组件库
pnpm add @dcloudio/uni-ui          # 官方 UI 组件

# 状态管理
pnpm add pinia @pinia/nuxt         # Pinia（同构）

# TypeScript 类型支持
pnpm add -D @dcloudio/types
```

### 6.2 `src/utils/request.ts`（基础模板）

```typescript
import { useUserStore } from '@/stores/user'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.huating.cloud'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, unknown>
}

export async function request<T>(options: RequestOptions): Promise<T> {
  const userStore = useUserStore()
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Authorization': userStore.token ? `Bearer ${userStore.token}` : '',
        'Content-Type': 'application/json',
      },
      success: (res) => {
        const data = res.data as { success: boolean; data: T; message: string }
        if (data.success) {
          resolve(data.data)
        } else {
          reject(new Error(data.message))
        }
      },
      fail: reject,
    })
  })
}
```

---

## 七、Docker 容器化

### 7.1 FastAPI Dockerfile

```dockerfile
# service/backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖（利用层缓存）
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY app/ app/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Vue3 OP 构建 Dockerfile（多阶段）

```dockerfile
# service/frontend/Dockerfile
FROM node:20-slim AS builder

WORKDIR /app
RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
# 构建产物在 /app/dist

# 生产阶段：只保留构建产物（挂载到 FastAPI 容器）
FROM scratch AS dist
COPY --from=builder /app/dist /dist
```

### 7.3 docker-compose.yml

```yaml
# service/docker-compose.yml
version: "3.9"

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: huating
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --save 60 1 --loglevel warning

  frontend-builder:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: builder
    volumes:
      - frontend_dist:/app/dist
    profiles: ["build"]  # 仅在 docker compose --profile build up 时执行

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@db:3306/huating
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      WECHAT_APP_ID: ${WECHAT_APP_ID}
      WECHAT_APP_SECRET: ${WECHAT_APP_SECRET}
    volumes:
      # 挂载前端构建产物（生产模式）
      - frontend_dist:/app/frontend_dist:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

volumes:
  db_data:
  redis_data:
  frontend_dist:
```

### 7.4 常用 Docker 命令

```bash
# 开发模式（不含前端构建）
docker compose up -d db redis

# 构建前端产物
docker compose --profile build up frontend-builder

# 启动完整服务
docker compose up -d

# 查看 FastAPI 日志
docker compose logs -f backend

# 执行数据库迁移（容器内）
docker compose exec backend uv run alembic upgrade head

# 重建镜像
docker compose build backend

# 停止并清理
docker compose down
docker compose down -v  # 同时清理数据卷（危险！）
```

---

## 八、注意事项

### 8.1 WSL2 与 Windows 路径映射

- WSL2 中访问 Windows 文件：`/mnt/c/Users/...` 或 `/mnt/f/projects/riichi`
- Windows 中访问 WSL2 文件：`\\wsl$\Debian\home\...`
- **推荐**：所有项目文件存放在 WSL2 文件系统内（`~/projects/`），避免跨文件系统 IO 性能损耗

### 8.2 端口暴露

WSL2 的服务默认通过 `localhost` 转发到 Windows 主机，无需额外配置。若使用固定 IP 可在 `~/.wslconfig` 中调整。

### 8.3 `.env` 文件管理

```bash
# service/backend/.env.example（提交到版本控制）
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/huating
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

WECHAT_APP_ID=wx92b0665554e342e6
WECHAT_APP_SECRET=your-secret

COS_BUCKET=your-bucket
COS_REGION=ap-shanghai
COS_SECRET_ID=your-id
COS_SECRET_KEY=your-key
```

**不要将 `.env` 提交到 Git**，在 `.gitignore` 中排除：

```
.env
*.env.local
```
