# FastAPI 快速开始指南

> 面向读者：有 ThinkPHP / PHP 背景，首次接触 FastAPI + Python 异步后端开发  
> 覆盖内容：分层架构设计 · ABP 框架对比 · JWT+RBAC 认证迁移 · 从模型到 API 的完整工作流 · Docker 单端口部署

---

## 目录

1. [为什么选 FastAPI](#1-为什么选-fastapi)
2. [分层架构设计](#2-分层架构设计)
3. [ABP 框架对比与认证迁移](#3-abp-框架对比与认证迁移)
4. [核心基础设施配置](#4-核心基础设施配置)
5. [从模型到 API 完整工作流](#5-从模型到-api-完整工作流)
6. [JWT + RBAC 认证实现](#6-jwt--rbac-认证实现)
7. [异常处理与响应规范](#7-异常处理与响应规范)
8. [测试指南](#8-测试指南)
9. [Docker 单端口部署](#9-docker-单端口部署)
10. [常见陷阱与最佳实践](#10-常见陷阱与最佳实践)

---

## 1. 为什么选 FastAPI

### 1.1 对比 ThinkPHP

| 维度 | ThinkPHP 5.x | FastAPI |
|------|-------------|---------|
| 语言 | PHP 7.x | Python 3.12+ |
| 并发模型 | 同步（每请求一进程/线程） | 异步（asyncio + uvicorn ASGI） |
| 路由定义 | 注解/方法名约定 | 显式装饰器 `@app.get("/path")` |
| 数据验证 | ThinkPHP Validate | Pydantic v2（类型推断，性能更高） |
| API 文档 | 无（需手写）| 自动生成 OpenAPI / Swagger UI |
| ORM | ThinkORM | SQLAlchemy 2.0（异步支持） |
| 迁移工具 | 无内置 | Alembic |
| 认证 | Session / openid（本项目） | JWT Bearer |
| 测试 | PHPUnit | pytest + httpx |

### 1.2 FastAPI 核心概念速览

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Pydantic 模型：定义请求/响应数据结构，自动验证
class UserCreate(BaseModel):
    username: str
    password: str

# 路由装饰器：直接标注路径、HTTP 方法
@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate):  # body 自动从请求 JSON 反序列化并验证
    return {"id": 1, "username": body.username}

# Depends：依赖注入（可用于鉴权、数据库会话等）
async def get_current_user(token: str = Depends(oauth2_scheme)):
    ...

@app.get("/me")
async def read_me(user = Depends(get_current_user)):
    return user
```

**三个关键点**：
1. `async def` — 异步协程，非阻塞 IO（数据库、Redis、HTTP 均可用 `await`）
2. `Pydantic BaseModel` — 替代 ThinkPHP Validate + 手工序列化
3. `Depends` — 替代 ThinkPHP 中间件和基类 `initialize()`

---

## 2. 分层架构设计

### 2.1 层次划分

```
app/
├── domain/            # 领域层（纯业务逻辑，无框架依赖）
│   ├── user/
│   │   ├── entity.py          # User 实体（数据类）
│   │   ├── value_objects.py   # 值对象（如 Email, Phone）
│   │   ├── repository.py      # 仓储接口（Abstract Base Class）
│   │   └── service.py         # 领域服务（跨实体业务逻辑）
│   ├── game/
│   ├── bill/
│   └── shared/
│       └── exceptions.py      # 领域异常基类
│
├── application/       # 应用层（用例编排，调用领域和基础设施）
│   ├── user/
│   │   ├── dto.py             # 数据传输对象（请求/响应 DTO）
│   │   ├── service.py         # 用例/应用服务
│   │   └── exceptions.py      # 应用层异常
│   ├── game/
│   └── bill/
│
├── infrastructure/    # 基础设施层（实现领域接口，框架/库相关）
│   ├── database/
│   │   ├── models.py          # SQLAlchemy ORM 模型
│   │   ├── session.py         # 异步数据库会话工厂
│   │   └── repositories/
│   │       ├── user_repo.py   # UserRepository 实现
│   │       └── bill_repo.py
│   ├── cache/
│   │   └── redis_client.py    # Redis 操作封装
│   ├── wechat/
│   │   └── auth_client.py     # 微信 code2session 封装
│   └── storage/
│       └── cos_client.py      # 腾讯云 COS 上传
│
├── api/               # 表现层（HTTP 接口，框架相关）
│   ├── v1/
│   │   ├── __init__.py        # 汇总所有路由器
│   │   ├── user.py            # User 路由器（RESTful 端点）
│   │   ├── game.py
│   │   ├── bill.py
│   │   └── admin/
│   │       ├── users.py
│   │       └── bills.py
│   └── dependencies.py        # 公共 Depends（鉴权、DB 会话等）
│
└── shared/            # 共享基础设施（各层均可使用）
    ├── config.py          # 环境变量配置（pydantic-settings）
    ├── exceptions.py      # 全局异常处理器注册
    ├── middleware.py      # CORS、请求日志等中间件
    └── security.py        # JWT 工具函数
```

### 2.2 依赖方向规则

```
表现层(api) → 应用层(application) → 领域层(domain) ← 基础设施层(infrastructure)
```

**关键原则**：
- `domain/` 不依赖任何外部库（纯 Python）
- `infrastructure/` 实现 `domain/` 中定义的接口
- `api/` 只调用 `application/`，不直接调 `infrastructure/`
- 依赖通过 FastAPI `Depends` 注入（可替换，便于测试）

### 2.3 对比 ThinkPHP MVC

| ThinkPHP 层 | FastAPI 等价层 | 说明 |
|------------|--------------|------|
| `Controller` | `api/v1/*.py` | 路由处理器 |
| `Model`（ORM） | `infrastructure/database/models.py` | SQLAlchemy ORM |
| `Model`（业务） | `domain/*/entity.py` + `application/*/service.py` | 领域实体 + 应用服务 |
| `Validate` | Pydantic `BaseModel` | 请求体自动验证 |
| `Common/Base.php` | `api/dependencies.py` | 公共依赖（鉴权等） |
| 没有等价 | `domain/*/repository.py` | 仓储接口（DI 解耦） |

---

## 3. ABP 框架对比与认证迁移

### 3.1 ABP Framework 层次映射

> ABP（ASP.NET Boilerplate / ABP Framework）是 .NET 生态的全栈应用框架，其分层思想与 DDD 高度契合。以下将 ABP 层级映射到 FastAPI 等价实现。

| ABP 层 | ABP 职责 | FastAPI 等价 |
|--------|---------|-------------|
| `Domain` | 实体（Entity）、值对象、领域服务、仓储接口 | `app/domain/` |
| `Domain.Shared` | 枚举、常量、DTO 基类 | `app/shared/` + `app/domain/shared/` |
| `Application.Contracts` | 应用接口（IService）、DTO | `app/application/*/dto.py` |
| `Application` | 应用服务实现（IService 实现） | `app/application/*/service.py` |
| `EntityFrameworkCore` | ORM 映射、DbContext、仓储实现 | `app/infrastructure/database/` |
| `HttpApi` | Controller + Swagger | `app/api/v1/` |
| `Identity` | 用户/角色/权限模块（内置） | `app/domain/auth/` + JWT |

### 3.2 ABP Identity 模块 vs. 本项目最小 JWT+RBAC 方案

ABP Identity 是企业级的完整方案（支持多租户、声明扩展、外部登录等），本项目仅需一个小型雀庄管理系统，采用最小化 RBAC 实现：

#### 3.2.1 权限模型对比

| ABP Identity | 本项目最小方案 | 说明 |
|-------------|--------------|------|
| `AbpUsers` | `admin_user` 表 | 管理员账户 |
| `AbpRoles` | `admin_role` 表 | 角色 |
| `AbpUserRoles` | `admin_user_role` 中间表 | 用户-角色多对多 |
| `AbpPermissionGrants` | `admin_node` 表 + `admin_role_node` 中间表 | 权限节点-角色多对多 |
| `IPermissionChecker` | FastAPI `Depends(require_permission("xxx"))` | 路由级权限检查 |

#### 3.2.2 最小 RBAC 表结构（SQLAlchemy）

```python
# app/infrastructure/database/models.py（鉴权相关部分）

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

# 角色-权限节点 多对多关联表
role_node_table = Table(
    "admin_role_node",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("admin_role.id"), primary_key=True),
    Column("node_id", Integer, ForeignKey("admin_node.id"), primary_key=True),
)

# 用户-角色 多对多关联表（简化版：每用户通常只有一个角色）
user_role_table = Table(
    "admin_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("admin_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("admin_role.id"), primary_key=True),
)


class AdminUser(Base):
    """管理员账户（对应旧 huating_admin 表）"""
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)  # bcrypt
    is_active = Column(Boolean, default=True)
    roles = relationship("AdminRole", secondary=user_role_table, lazy="selectin")


class AdminRole(Base):
    """角色（对应旧 huating_role 表）"""
    __tablename__ = "admin_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), default="")
    nodes = relationship("AdminNode", secondary=role_node_table, lazy="selectin")


class AdminNode(Base):
    """权限节点（对应旧 huating_node 表）"""
    __tablename__ = "admin_node"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)        # 节点显示名称
    code = Column(String(100), unique=True, nullable=False)  # 节点标识符，如 "user:edit"
    group = Column(String(50), default="")            # 分组，如 "user", "bill"
    description = Column(String(200), default="")
```

#### 3.2.3 从旧 openid 认证迁移到 JWT

**旧认证流程（insecure）**：
```
小程序 → POST /miniprogram/user/login { openid: "xxx" }
         服务端查 Redis: GET openid:xxx → 返回用户信息
         无签名验证，任何人都能伪造 openid
```

**新认证流程（JWT Bearer）**：
```
小程序 → POST /api/v1/auth/login { code: "wx_login_code" }
         服务端 → 调微信 code2session → 得到 openid
         查询/创建用户 → 生成 JWT(access_token, refresh_token)
         返回 tokens → 小程序存 token

小程序 → GET /api/v1/user/me
         Header: Authorization: Bearer <access_token>
         服务端解码 JWT → 验证签名 → 注入 current_user
```

**Redis Key 迁移**：

| 旧 Key 模式 | 新 Key 模式 | 说明 |
|------------|-----------|------|
| `openid:{openid}` | `user:{user_id}:info` | 用户缓存 |
| `game:{table_id}` (TTL=0) | `game:{table_id}:state` (TTL=86400) | 游戏状态（修复内存泄漏）|
| 无 | `token:{jti}:blacklist` | JWT 黑名单（登出）|

---

## 4. 核心基础设施配置

### 4.1 环境变量配置（pydantic-settings）

```python
# app/shared/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 数据库
    database_url: str = "mysql+aiomysql://user:pass@localhost:3306/huating"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_user_db: int = 1       # 对应旧 select:1（用户缓存）
    redis_game_db: int = 14      # 对应旧 select:14（游戏状态）

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7

    # 微信
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 腾讯云 COS
    cos_bucket: str = ""
    cos_region: str = "ap-shanghai"
    cos_secret_id: str = ""
    cos_secret_key: str = ""

    # 应用
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 4.2 异步数据库会话

```python
# app/infrastructure/database/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.shared.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 自动重连
    echo=settings.debug, # 开发模式打印 SQL
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 重要：提交后不过期（异步环境需要）
)


# FastAPI Depends 使用
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### 4.3 Redis 客户端

```python
# app/infrastructure/cache/redis_client.py
import redis.asyncio as aioredis
from app.shared.config import get_settings

settings = get_settings()

# 用户缓存（db=1）
user_cache: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    db=settings.redis_user_db,
    encoding="utf-8",
    decode_responses=True,
)

# 游戏状态（db=14）
game_cache: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    db=settings.redis_game_db,
    encoding="utf-8",
    decode_responses=True,
)


async def get_user_cache() -> aioredis.Redis:
    yield user_cache

async def get_game_cache() -> aioredis.Redis:
    yield game_cache
```

### 4.4 应用入口（main.py）

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.shared.config import get_settings
from app.shared.exceptions import register_exception_handlers
from app.api.v1 import router as api_v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭生命周期"""
    # 启动：可在此预热连接池、加载配置等
    yield
    # 关闭：清理资源
    from app.infrastructure.cache.redis_client import user_cache, game_cache
    await user_cache.aclose()
    await game_cache.aclose()


app = FastAPI(
    title="花听雀庄 API",
    version="2.0.0",
    docs_url="/docs" if settings.debug else None,  # 生产环境隐藏文档
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS（开发期放行 Vite Dev Server）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册路由（/api/v1/ 前缀）
app.include_router(api_v1_router, prefix="/api/v1")

# 生产环境挂载 Vue3 OP 静态文件（见第 9 节）
```

---

## 5. 从模型到 API 完整工作流

> 以「用户注册/登录」功能为例，演示端到端的完整开发流程。

### Step 1：定义 SQLAlchemy ORM 模型

```python
# app/infrastructure/database/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    """对应旧 huating_user 表"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False, index=True)
    session_key = Column(String(100), default="")    # 微信 session_key（加密存储，非 JWT）
    username = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), default="")
    avatar_url = Column(String(500), default="")
    gender = Column(Integer, default=0)              # 0=未知 1=男 2=女
    group_id = Column(Integer, default=0)            # 用户分组
    status = Column(Boolean, default=True)           # 是否启用
    is_admin = Column(Boolean, default=False)        # 是否管理员（兼容旧字段 admin）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Step 2：创建 Alembic 数据库迁移

```bash
# 确保 alembic/env.py 中已导入所有模型（否则 autogenerate 无法发现）
# alembic/env.py 中添加：
# from app.infrastructure.database.models import Base
# target_metadata = Base.metadata

# 生成迁移脚本
uv run alembic revision --autogenerate -m "create user table"

# 检查生成的迁移文件（alembic/versions/*.py）
# 确认 upgrade() 和 downgrade() 逻辑正确后执行

uv run alembic upgrade head
```

### Step 3：定义仓储接口（领域层）

```python
# app/domain/user/repository.py
from abc import ABC, abstractmethod
from typing import Optional
from app.domain.user.entity import UserEntity


class UserRepositoryInterface(ABC):
    
    @abstractmethod
    async def find_by_openid(self, openid: str) -> Optional[UserEntity]:
        ...

    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        ...

    @abstractmethod
    async def create(self, entity: UserEntity) -> UserEntity:
        ...

    @abstractmethod
    async def update(self, entity: UserEntity) -> UserEntity:
        ...
```

```python
# app/domain/user/entity.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    openid: str
    username: str
    id: Optional[int] = None
    phone: str = ""
    avatar_url: str = ""
    gender: int = 0
    group_id: int = 0
    status: bool = True
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
```

### Step 4：实现仓储（基础设施层）

```python
# app/infrastructure/database/repositories/user_repo.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.entity import UserEntity
from app.domain.user.repository import UserRepositoryInterface
from app.infrastructure.database.models import User as UserModel


class SQLAlchemyUserRepository(UserRepositoryInterface):
    
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            openid=model.openid,
            username=model.username,
            phone=model.phone,
            avatar_url=model.avatar_url,
            gender=model.gender,
            group_id=model.group_id,
            status=model.status,
            is_admin=model.is_admin,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def find_by_openid(self, openid: str) -> Optional[UserEntity]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.openid == openid)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: UserEntity) -> UserEntity:
        model = UserModel(
            openid=entity.openid,
            username=entity.username,
            phone=entity.phone,
            avatar_url=entity.avatar_url,
            gender=entity.gender,
        )
        self._session.add(model)
        await self._session.flush()  # 获取 auto-increment id（事务内）
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: UserEntity) -> UserEntity:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == entity.id)
        )
        model = result.scalar_one()
        model.username = entity.username
        model.phone = entity.phone
        model.avatar_url = entity.avatar_url
        model.gender = entity.gender
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
```

### Step 5：编写应用服务/用例

```python
# app/application/user/dto.py
from pydantic import BaseModel, Field
from typing import Optional


class WechatLoginRequest(BaseModel):
    code: str = Field(..., description="微信临时 code")
    username: str = Field(..., min_length=2, max_length=20, description="昵称")
    avatar_url: str = Field(default="", description="头像 URL")
    gender: int = Field(default=0, ge=0, le=2)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    avatar_url: str
    gender: int
    group_id: int
    is_admin: bool

    model_config = {"from_attributes": True}  # 支持从 ORM 对象直接构建
```

```python
# app/application/user/service.py
from app.domain.user.entity import UserEntity
from app.domain.user.repository import UserRepositoryInterface
from app.infrastructure.wechat.auth_client import WechatAuthClient
from app.shared.security import create_access_token, create_refresh_token
from app.application.user.dto import WechatLoginRequest, TokenResponse


class UserApplicationService:

    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        wechat_client: WechatAuthClient,
    ):
        self._user_repo = user_repo
        self._wechat = wechat_client

    async def wechat_login(self, request: WechatLoginRequest) -> TokenResponse:
        # 1. 微信 code 换取 openid
        wx_result = await self._wechat.code2session(request.code)
        openid = wx_result["openid"]

        # 2. 查询或创建用户
        user = await self._user_repo.find_by_openid(openid)
        if user is None:
            user = await self._user_repo.create(UserEntity(
                openid=openid,
                username=request.username,
                avatar_url=request.avatar_url,
                gender=request.gender,
            ))

        # 3. 生成 JWT
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
```

### Step 6：定义 FastAPI 路由器

```python
# app/api/v1/user.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.user_repo import SQLAlchemyUserRepository
from app.infrastructure.wechat.auth_client import WechatAuthClient
from app.application.user.service import UserApplicationService
from app.application.user.dto import WechatLoginRequest, TokenResponse, UserResponse
from app.api.dependencies import get_current_user
from app.domain.user.entity import UserEntity

router = APIRouter(prefix="/user", tags=["用户"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserApplicationService:
    """依赖工厂：构建 UserApplicationService（组装依赖树）"""
    user_repo = SQLAlchemyUserRepository(db)
    wechat_client = WechatAuthClient()
    return UserApplicationService(user_repo, wechat_client)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def wechat_login(
    body: WechatLoginRequest,
    service: UserApplicationService = Depends(get_user_service),
):
    """微信小程序登录（code 换 token）"""
    # 注意：service 内部会开启事务（通过 session.begin()）
    async with (await get_db().__anext__()).begin():
        pass  # 示例简化，实际由应用服务处理事务
    return await service.wechat_login(body)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserEntity = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        gender=current_user.gender,
        group_id=current_user.group_id,
        is_admin=current_user.is_admin,
    )
```

### Step 7：注册异常处理器

```python
# app/shared/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


class NotFoundError(AppError):
    def __init__(self, resource: str):
        super().__init__(f"{resource} 不存在", code=404)


class AuthError(AppError):
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code=401)


class PermissionError(AppError):
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.code,
            content={"success": False, "message": exc.message, "data": None},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "资源不存在", "data": None},
        )
```

### Step 8：统一响应格式

所有 API 响应应遵循统一格式，与旧系统兼容并便于前端处理：

```python
# app/shared/response.py
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "ok"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "ok") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, code: int = 400) -> "ApiResponse[None]":
        return cls(success=False, message=message, data=None)
```

```python
# 路由中使用
@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: UserEntity = Depends(get_current_user)):
    return ApiResponse.ok(UserResponse(
        id=current_user.id,
        username=current_user.username,
        # ...
    ))
```

### Step 9：编写 pytest 测试

```python
# tests/test_user_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_login_returns_tokens():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 测试时需 mock 微信 code2session 接口
        response = await client.post("/api/v1/user/login", json={
            "code": "test_code_123",
            "username": "测试用户",
        })
    # 断言（mock 微信接口返回固定 openid）
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
```

```bash
# 运行测试
uv run pytest tests/ -v

# 带覆盖率
uv run pytest tests/ -v --cov=app --cov-report=html
```

### Step 10：验证自动生成的 API 文档

启动开发服务器后，访问：
- `http://localhost:8000/docs` — Swagger UI（可直接测试接口）
- `http://localhost:8000/redoc` — ReDoc（阅读友好）
- `http://localhost:8000/openapi.json` — OpenAPI JSON Schema

---

## 6. JWT + RBAC 认证实现

### 6.1 JWT 工具函数

```python
# app/shared/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.shared.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None
```

### 6.2 公共依赖（鉴权 Depends）

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.user_repo import SQLAlchemyUserRepository
from app.domain.user.entity import UserEntity
from app.shared.security import decode_token
from app.shared.exceptions import AuthError, PermissionError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserEntity:
    """解码 JWT，返回当前用户实体"""
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise AuthError("无效的 access token")
    
    user_id = int(payload.get("sub", 0))
    if not user_id:
        raise AuthError("token 中缺少用户信息")
    
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.find_by_id(user_id)
    if user is None or not user.status:
        raise AuthError("用户不存在或已被禁用")
    
    return user


async def get_current_admin(
    current_user: UserEntity = Depends(get_current_user),
) -> UserEntity:
    """要求当前用户为管理员"""
    if not current_user.is_admin:
        raise PermissionError("需要管理员权限")
    return current_user


def require_permission(permission_code: str):
    """
    路由级权限检查 Depends 工厂
    用法：@router.get("/xxx", dependencies=[Depends(require_permission("user:edit"))])
    """
    async def _check(
        current_user: UserEntity = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        from app.infrastructure.database.repositories.admin_repo import AdminUserRepository
        admin_repo = AdminUserRepository(db)
        has_perm = await admin_repo.check_permission(current_user.id, permission_code)
        if not has_perm:
            raise PermissionError(f"缺少权限节点: {permission_code}")
    
    return _check
```

### 6.3 在路由中使用权限控制

```python
# app/api/v1/admin/users.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_admin, require_permission
from app.domain.user.entity import UserEntity

router = APIRouter(prefix="/admin/users", tags=["后台-用户管理"])


# 方式 1：仅验证登录（任意管理员可访问）
@router.get("/")
async def list_users(admin: UserEntity = Depends(get_current_admin)):
    ...


# 方式 2：验证具体权限节点
@router.put("/{user_id}")
async def update_user(
    user_id: int,
    _: None = Depends(require_permission("user:edit")),  # 权限检查
    admin: UserEntity = Depends(get_current_admin),      # 获取当前管理员
):
    ...


# 方式 3：路由级批量声明权限（不影响函数签名）
@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permission("user:delete"))],
)
async def delete_user(user_id: int):
    ...
```

---

## 7. 异常处理与响应规范

### 7.1 错误码规范

| HTTP 状态码 | 场景 | `success` |
|------------|------|-----------|
| 200 | 正常响应 | `true` |
| 201 | 创建成功 | `true` |
| 400 | 请求参数错误 / 业务逻辑错误 | `false` |
| 401 | 未认证（token 无效/过期） | `false` |
| 403 | 权限不足 | `false` |
| 404 | 资源不存在 | `false` |
| 422 | Pydantic 验证失败（FastAPI 默认） | `false` |
| 500 | 服务器内部错误 | `false` |

### 7.2 统一 422 响应格式

FastAPI 默认 422 响应格式与其他错误不一致，需覆盖：

```python
# 在 register_exception_handlers 中添加
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "data": {"errors": errors},
        },
    )
```

---

## 8. 测试指南

### 8.1 pytest 配置

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"          # 自动处理 async 测试函数
testpaths = ["tests"]
```

### 8.2 测试结构

```
tests/
├── conftest.py            # 共享 fixtures（测试数据库、客户端等）
├── test_user_api.py
├── test_game_api.py
└── test_bill_service.py   # 单元测试（直接测试应用服务）
```

### 8.3 测试 Fixture 示例

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import get_db


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB_URL)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试前重建数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """覆盖 get_db 依赖，使用测试数据库"""
    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
```

---

## 9. Docker 单端口部署

### 9.1 架构图

```
                       Internet
                           │
                     :8000 │
                    ┌──────┴──────┐
                    │   FastAPI   │
                    │  uvicorn    │
                    └──────┬──────┘
                    /api/* │   /* (SPA fallback)
                 ┌─────────┼──────────────┐
                 │         │              │
           REST API    WebSocket     StaticFiles
           /api/v1/*   /ws/*          /assets/*
                                     index.html
                                  (Vue3 OP 构建产物)
```

### 9.2 生产 docker-compose.yml（完整版）

```yaml
# service/docker-compose.prod.yml
version: "3.9"

services:
  db:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: huating
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${DB_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --save 60 1

  # 前端构建阶段（仅构建，不持续运行）
  frontend-build:
    image: node:20-slim
    working_dir: /app
    volumes:
      - ./frontend:/app
      - frontend_dist:/app/dist
    command: sh -c "npm install -g pnpm && pnpm install --frozen-lockfile && pnpm build"
    profiles: ["build"]

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      DATABASE_URL: mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@db:3306/huating
      REDIS_URL: redis://redis:6379
    volumes:
      - frontend_dist:/app/frontend_dist:ro  # 挂载 Vue3 构建产物
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

### 9.3 完整启动流程

```bash
# 1. 进入 service/ 目录
cd HuatingRiichiClub/service

# 2. 复制并配置环境变量
cp backend/.env.example .env
# 编辑 .env，填写生产环境配置

# 3. 构建前端（首次或前端代码变更后执行）
docker compose -f docker-compose.prod.yml --profile build up frontend-build

# 4. 构建后端镜像
docker compose -f docker-compose.prod.yml build backend

# 5. 启动所有服务
docker compose -f docker-compose.prod.yml up -d db redis backend

# 6. 执行数据库迁移
docker compose -f docker-compose.prod.yml exec backend uv run alembic upgrade head

# 7. 验证
curl http://localhost:8000/api/v1/health
```

### 9.4 完整的 FastAPI StaticFiles 挂载配置

```python
# app/main.py（生产静态文件挂载完整版）
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 注册所有 API 路由（必须在挂载静态文件之前）
app.include_router(api_v1_router, prefix="/api/v1")

# 挂载静态文件
FRONTEND_DIST = Path("/app/frontend_dist")  # Docker 卷挂载路径

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )

# SPA 回退路由（捕获所有非 /api 路径）
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # 排除 API 路径（防止误拦截）
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API route not found")
    
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    # 开发环境未构建前端时的提示
    return {"message": "Frontend not built. Run 'pnpm build' in service/frontend/"}
```

---

## 10. 常见陷阱与最佳实践

### 10.1 异步陷阱

```python
# ❌ 错误：在异步路由中调用同步阻塞 IO
@app.get("/users")
async def list_users():
    import time
    time.sleep(1)  # 阻塞整个事件循环！

# ✅ 正确：使用 asyncio.to_thread 或重写为异步
import asyncio
@app.get("/users")
async def list_users():
    await asyncio.sleep(1)  # 非阻塞
```

### 10.2 SQLAlchemy 会话管理

```python
# ❌ 错误：提交后访问延迟加载的关联对象（异步环境不支持）
async def bad_example(db):
    user = await db.get(User, 1)
    await db.commit()
    print(user.roles)  # DetachedInstanceError！

# ✅ 正确：使用 selectin 加载或在提交前访问
async def good_example(db):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == 1)
    )
    user = result.scalar_one()
    roles = user.roles  # 已经加载到内存
    await db.commit()
```

### 10.3 结算链事务（最高优先级迁移风险）

旧系统 `handlerAddRecord` 无事务，导致部分更新风险。新系统必须用 `session.begin()`：

```python
# app/application/game/service.py（结算事务示例）
async def settle_game(self, session: AsyncSession, game_id: int, scores: list[int]):
    """对局结算：Record → UserData → UserGrade → Bill，全部在一个事务内"""
    async with session.begin():  # 任何步骤失败，全部回滚
        record = await self._record_repo.create(session, ...)
        for user_id, score in zip(player_ids, scores):
            await self._user_data_repo.update_score(session, user_id, score)
            await self._user_grade_repo.update_grade(session, user_id, score)
            await self._bill_repo.create_game_bill(session, user_id, game_id, ...)
        # 清理 Redis 游戏状态
        await self._game_cache.delete(f"game:{game_id}:state")
    # 事务提交成功后，才发送通知等副作用
```

### 10.4 Pydantic v2 变化（与旧版对比）

```python
# Pydantic v2（FastAPI 0.100+ 使用）
class UserResponse(BaseModel):
    id: int
    username: str

    # v2: from_orm=True 改为 model_config
    model_config = {"from_attributes": True}

# v2: .dict() 改为 .model_dump()
user_dict = user_response.model_dump()

# v2: .json() 改为 .model_dump_json()
user_json = user_response.model_dump_json()
```

### 10.5 生产安全清单

- [ ] `JWT_SECRET` 使用随机长字符串（至少 32 字节），不在代码中硬编码
- [ ] 生产环境 `docs_url=None`（隐藏 Swagger UI）
- [ ] CORS `allow_origins` 限制为实际域名（不用 `["*"]`）
- [ ] 数据库密码从环境变量读取（不在 `docker-compose.yml` 明文写）
- [ ] Redis 设置密码（`requirepass`）
- [ ] 所有游戏 Redis Key 设置合理 TTL（修复内存泄漏）
- [ ] 文件上传校验 MIME 类型和文件大小
- [ ] SQL 查询全部通过 SQLAlchemy 参数化（禁止拼接 SQL）
- [ ] 管理员接口路由前缀 `/api/v1/admin/` 添加 `get_current_admin` 依赖

---

## 附录：快速参考命令

```bash
# 开发启动
uv run fastapi dev app/main.py

# 数据库迁移
uv run alembic revision --autogenerate -m "描述"
uv run alembic upgrade head
uv run alembic downgrade -1

# 运行测试
uv run pytest tests/ -v --cov=app

# 代码格式化与检查
uv run ruff check app/
uv run ruff format app/

# 生产构建（Docker）
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d

# 查看 API 文档
open http://localhost:8000/docs
```
