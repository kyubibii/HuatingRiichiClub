# 遗留后台管理系统页面映射

> 来源：`huatingquezhuang-service/application/admin/`  
> 框架：ThinkPHP 5.x + Layui 2.x  
> 认证：Session（`admin_id`） + RBAC（`Rbac::instance()`）  
> 整理目的：为 Vue3 后台管理（OP）重构提供页面/功能完整映射基线

---

## 一、技术架构说明

### 1.1 旧系统结构

```
admin/
├── common/
│   ├── controller/Base.php     # 基类：Session 校验 + RBAC 注入
│   ├── model/                  # 28 个数据模型
│   └── validate/Admin.php      # 仅 Admin 用户登录验证
├── controller/                 # 13 个业务控制器
└── view/                       # Layui 模板（.html 文件）
    ├── admin/   ├── bill/   ├── config/  ├── index/
    ├── ktxx/    ├── login/  ├── member/  ├── node/
    ├── record/  ├── role/   ├── user/    └── yakuman/
```

### 1.2 鉴权机制

```php
// Base.php initialize()
if (!Session::get('admin_id')) {
    $this->redirect('/admin/login/index');
}
Rbac::instance()->check($currentPath, Session::get('admin_id'));
```

**重构建议（Vue3 + FastAPI）**：
- 用 JWT（`access_token`）替代 Session
- 用 FastAPI Depends 实现路由级权限装饰器
- Vue3 OP 用 `vue-router` 路由守卫拦截未授权访问
- 权限节点表（`huating_node`）可迁移为 FastAPI 的资源-动作权限模型

---

## 二、控制器与页面映射总表

### 2.1 登录模块（`Login.php` → `view/login/`）

| Action | 视图 | 功能 | HTTP 方法 |
|--------|------|------|-----------|
| `index()` | `login/index.html` | 登录页 | GET |
| `doLogin()` | - | 处理登录表单 | POST |
| `logout()` | - | 退出登录，清除 Session | GET |

**登录表单字段**：`username`、`password`（MD5 或直接明文？需确认）  
**验证器**：`Admin.php`（`application/admin/common/validate/Admin.php`）  
**重构说明**：Vue3 OP 用独立 `/login` 路由，POST `/api/admin/auth/login` 换取 JWT。

---

### 2.2 首页仪表盘（`Index.php` → `view/index/` + `view/admin/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `index()` | `admin/index.html` | 后台框架主页（菜单 + iframe 容器） |
| `home()` | `index/home.html` | 仪表盘首页（统计数据卡片） |

**仪表盘展示内容**：
- 今日开桌数
- 今日营业额
- 注册雀士总数
- 当前在线游戏桌数

**重构说明**：用 Vue3 + ECharts 替代 Layui 模板，数据由 FastAPI `/api/admin/dashboard/stats` 提供。

---

### 2.3 用户管理（`User.php` → `view/user/`）

| Action | 视图 | 功能 | 涉及接口 |
|--------|------|------|---------|
| `userIndex()` | `user/userIndex.html` | 雀士列表（搜索/分页） | `getUserList()` |
| `userEditForm()` | `user/userEditForm.html` | 雀士信息编辑表单 | `getUserInfo()`, `updateUserInfo()` |
| `userGradeIndex()` | `user/userGradeIndex.html` | 段位管理列表 | `getUserGradeList()` |

**用户列表字段**：`id`、`username`、`phone`、`groupId`（分组名）、`ratename`、`avatarUrl`、`gender`、`debt_amount`、`status`、`admin`、`levelName`、`update_time`

**操作功能**：
- 关键词搜索（用户名 / 手机号模糊匹配）
- 修改用户状态（启用/禁用）
- 修改用户分组
- 充值/退款操作（跳转账务模块）
- 查看欠款金额

**重构说明**：Vue3 OP 对应 `/admin/users` 路由，FastAPI `/api/admin/users` REST 接口。

---

### 2.4 账务管理（`Bill.php` → `view/bill/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `billIndex()` | `bill/billIndex.html` | 账务总览（按用户聚合，今日账单） |
| `userBillListIndex()` | `bill/userBillListIndex.html` | 指定用户账单详情列表 |
| `addUserBillIndex()` | `bill/addUserBillIndex.html` | 手动新增账单表单 |

**billIndex 字段（聚合视图）**：`userId`、`username`、`phone`、`avatarUrl`、`amount`（未付合计）、`status`（是否有未付账单）

**账单列表字段**：`id`、`type_name`、`pay_name`、`amount`、`admin`、`remark`、`create_time`、退款相关字段

**手动新增账单表单**：
- 选择用户（搜索）
- 账务类型（`TYPE_ID_CONFIG`：场代支付/场代退回/会员储值/会员退回）
- 金额
- 支付方式（`PAY_ID_CONFIG`）
- 备注

**操作功能**：
- 结账（将 `payId=1` 更新为指定支付方式）
- 退款
- 删除（软删除）
- 批量结账

**重构说明**：Vue3 OP 对应 `/admin/bills`，需要复刻聚合视图逻辑与结账流程。

---

### 2.5 对局记录（`Record.php` → `view/record/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `recordIndex()` | `record/recordIndex.html` | 对局记录列表（搜索/分页） |
| `recordDetail()` | `record/recordDetail.html` | 对局详情（4人分数 + 点数） |

**记录列表字段**：`id`、`model_name`、四位玩家姓名与分数、`create_time`、`status`

**操作功能**：
- 按日期/用户名搜索
- 删除（软删除，`status=0`）
- 查看详情

---

### 2.6 开桌日志（`Ktxx.php` → `view/ktxx/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `ktxxIndex()` | `ktxx/ktxxIndex.html` | 开桌记录列表 |
| `tableStatusIndex()` | `ktxx/tableStatusIndex.html` | 实时台桌状态监控 |

**开桌记录字段**：`id`、`groupId`、`model_name`、四家用户名、`record_total`、`amount`、`game_status`、`create_time`、`close_time`

**实时台桌状态字段**：每台设备的当前用户（姓名/头像）、游戏状态、当前打了几局、点数情况

**重构说明**：实时台桌状态建议用 WebSocket 或 SSE 替代 Layui 定时刷新。

---

### 2.7 配置管理（`Config.php` → `view/config/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `modelConfigIndex()` | `config/modelConfigIndex.html` | 麻将模式配置列表 |
| `modelConfigForm()` | `config/modelConfigForm.html` | 模式配置新增/编辑 |
| `tableConfigIndex()` | `config/tableConfigIndex.html` | 台桌设备配置列表 |
| `tableConfigForm()` | `config/tableConfigForm.html` | 台桌设备配置表单 |
| `memberConfigIndex()` | `config/memberConfigIndex.html` | 会员套餐配置 |
| `memberConfigForm()` | `config/memberConfigForm.html` | 会员套餐新增/编辑 |
| `calendarIndex()` | `config/calendarIndex.html` | 营业日历配置 |
| `userGroupIndex()` | `config/userGroupIndex.html` | 用户分组配置 |

**模式配置表单字段**：`name`、`aggregate`（总分）、`point`（基准点）、`one/two/three/four`（顺位积分）、`score`（奖励积分）、`isRank`、`sameScore`、`status`

**台桌设备配置字段**：`groupId`、`bearing`、`qrCode`、`price`（标准台费）、`member_price`、`month_price`、`status`

**重构说明**：配置管理是低频修改页面，Vue3 OP 用标准 CRUD 表格组件即可覆盖。

---

### 2.8 会员管理（`Member.php` → `view/member/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `memberIndex()` | `member/memberIndex.html` | 会员套餐列表（等价于 memberConfigIndex） |
| `userMemberIndex()` | `member/userMemberIndex.html` | 用户会员状态列表 |

**用户会员字段**：`username`、`phone`、`member_money`（余额）、`status`、购买记录

---

### 2.9 役满管理（`Yakuman.php` → `view/yakuman/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `yakumanIndex()` | `yakuman/yakumanIndex.html` | 役满记录列表 |

**字段**：`username`、`yakuman_type`（役满类型）、图片 URL、`create_time`

---

### 2.10 IP 查询工具（`IPQuery.php`）

| Action | 视图 | 功能 |
|--------|------|------|
| `index()` | - | 根据 IP 查询地理位置（qqwry.dat 离线库） |

**重构说明**：可选择集成第三方 IP 查询 API 替代本地离线库，或直接移除。

---

### 2.11 登录日志（`Loginlog.php` → `view/loginlog/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `loginlogIndex()` | `loginlog/loginlogIndex.html` | 管理员登录日志列表 |

**字段**：`admin_username`、IP、登录时间、登录结果

---

### 2.12 RBAC 权限系统（`Role.php` + `Node.php` + `Admin.php`）

#### 2.12.1 角色管理（`Role.php` → `view/role/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `roleIndex()` | `role/roleIndex.html` | 角色列表 |
| `roleForm()` | `role/roleForm.html` | 角色新增/编辑 |
| `roleNode()` | `role/roleNode.html` | 角色权限节点配置（树形结构） |

#### 2.12.2 权限节点管理（`Node.php` → `view/node/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `nodeIndex()` | `node/nodeIndex.html` | 权限节点列表（模块/控制器/方法三级） |
| `nodeForm()` | `node/nodeForm.html` | 节点新增/编辑 |

**节点结构**：`module` / `controller` / `action` 三级，对应 ThinkPHP 路由

#### 2.12.3 管理员账户（`Admin.php` → `view/admin/`）

| Action | 视图 | 功能 |
|--------|------|------|
| `adminIndex()` | `admin/adminIndex.html` | 管理员列表 |
| `adminForm()` | `admin/adminForm.html` | 管理员新增/编辑（分配角色） |

**管理员字段**：`username`、`password`（加密存储）、`roleId`、`status`

---

## 三、后台菜单结构（推断）

```
后台系统
├── 仪表盘
│   └── 首页数据
├── 用户管理
│   ├── 雀士列表
│   └── 段位管理
├── 账务管理
│   ├── 今日账单总览
│   └── 账单明细
├── 对局管理
│   ├── 对局记录
│   └── 开桌日志
│       └── 实时台桌状态
├── 配置管理
│   ├── 麻将模式配置
│   ├── 台桌设备配置
│   ├── 会员套餐配置
│   ├── 用户分组配置
│   └── 营业日历
├── 会员管理
│   └── 用户会员状态
├── 役满记录
├── 系统管理
│   ├── 管理员账户
│   ├── 角色管理
│   ├── 权限节点
│   ├── 登录日志
│   └── IP 查询工具
```

---

## 四、Vue3 OP 重构映射建议

| 旧模块 | Vue3 OP 路由 | FastAPI 端点前缀 | 优先级 |
|--------|-------------|----------------|--------|
| Login | `/login` | `POST /api/admin/auth/login` | P0 |
| 仪表盘 | `/` | `/api/admin/dashboard` | P0 |
| 用户管理 | `/users` | `/api/admin/users` | P1 |
| 账务管理 | `/bills` | `/api/admin/bills` | P1 |
| 对局记录 | `/records` | `/api/admin/records` | P1 |
| 开桌日志 | `/sessions` | `/api/admin/sessions` | P2 |
| 实时台桌 | `/sessions/live` | `WS /ws/admin/table-status` | P2 |
| 配置管理 | `/configs` | `/api/admin/configs` | P2 |
| 会员管理 | `/members` | `/api/admin/members` | P2 |
| 役满记录 | `/yakuman` | `/api/admin/yakuman` | P3 |
| RBAC | `/system/roles` `/system/nodes` `/system/admins` | `/api/admin/system` | P3 |
| 登录日志 | `/system/logs` | `/api/admin/system/logs` | P3 |

---

## 五、关键 UI 组件需求

| 组件 | 应用场景 |
|------|---------|
| 数据表格（含搜索+分页） | 用户列表、账单列表、对局记录等 |
| 卡片统计（Dashboard） | 今日营业额、开桌数等 |
| 树形权限选择器 | 角色权限节点配置 |
| 时间范围选择器 | 账单日期筛选、开桌记录筛选 |
| 模态框表单 | 用户编辑、新增账单等 |
| 金额输入（带校验） | 新增账单、会员套餐配置 |
| 实时刷新面板 | 台桌实时状态 |
| 文件上传 | 役满图片、用户头像 |

**推荐 UI 框架**：Element Plus（与 Vue3 生态匹配，组件覆盖上述所有需求）
