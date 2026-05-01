# 遗留系统数据结构分析

> 来源：`huatingquezhuang-service`（ThinkPHP 5.x）  
> 数据库：MySQL，库名 `huating`，表前缀 `ht_`  
> 整理目的：为 FastAPI 重构提供字段口径基线，避免字段二义性与数据迁移偏差

---

## 一、数据库总览

| 分类 | 表名 | 说明 |
|------|------|------|
| 用户体系 | `huating_user` | 雀士基础信息 |
| 用户体系 | `huating_user_data` | 雀士个人战绩统计 |
| 用户体系 | `huating_user_grade` | 雀士段位/等级 |
| 用户体系 | `huating_user_member` | 雀士会员储值 |
| 用户体系 | `huating_user_group_config` | 雀士分组配置 |
| 游戏核心 | `huating_ktxx_log` | 开桌记录（一场多局） |
| 游戏核心 | `huating_record` | 单局对局记录 |
| 游戏核心 | `huating_model_config` | 日麻模式配置 |
| 游戏核心 | `huating_table_config` | 台桌设备配置 |
| 游戏核心 | `huating_calendar_config` | 营业日历配置 |
| 账务 | `huating_bill` | 账务记录 |
| 账务 | `huating_online_pay_order` | 在线支付订单 |
| 账务 | `huating_member_config` | 会员套餐配置 |
| 扩展 | `huating_yakuman_log` | 役满记录 |
| 扩展 | `huating_media_check_log` | 媒体内容审核日志 |
| 扩展 | `huating_user_player_war` | 对战战力记录 |
| RBAC | `huating_admin` | 后台管理员 |
| RBAC | `huating_role` | 角色 |
| RBAC | `huating_node` | 权限节点 |
| 日志 | `huating_login_log` | 管理员登录日志 |

---

## 二、核心实体字段详解

### 2.1 huating_user（雀士信息）

**源文件**：`application/admin/common/model/User.php`

| 字段 | 类型 | 可空 | 默认 | 说明 |
|------|------|------|------|------|
| `id` | int(10) unsigned | NOT NULL | AUTO_INCREMENT | 主键 |
| `uuid` | varchar(8) | YES | NULL | 用户唯一短标识（8位，用于展示） |
| `openid` | varchar(64) | YES | NULL | 微信小程序 OpenID |
| `username` | varchar(20) | YES | NULL | 雀士昵称（2-20字符） |
| `groupId` | int(10) unsigned | NOT NULL | 1 | 所属分组 ID → `huating_user_group_config.id` |
| `ratename` | varchar(20) | YES | '' | 公式战昵称（可与 username 不同） |
| `phone` | varchar(11) | YES | NULL | 手机号（UNIQUE，11位数字） |
| `avatarUrl` | varchar(255) | YES | NULL | 头像 URL（COS 对象存储路径） |
| `gender` | tinyint(1) unsigned | YES | 2 | 性别：`0`=男，`1`=女，`2`=未知 |
| `birthday` | date | YES | NULL | 生日 |
| `signature` | varchar(50) | YES | NULL | 个性签名（≤50字符） |
| `debt_amount` | decimal(10,2) | YES | 0.00 | 欠款金额（未支付账单合计，实时更新） |
| `admin` | tinyint(1) unsigned | YES | 0 | 是否管理员：`0`=否，`1`=是 |
| `status` | tinyint(1) unsigned | YES | 1 | 账号状态：`1`=正常，`0`=禁用 |
| `create_time` | datetime | YES | NULL | 注册时间 |
| `update_time` | datetime | YES | NULL | 最后更新时间 |

**索引**：`UNIQUE KEY idx_phone (phone)`

**缓存策略**：Redis，`select: 1`，key=`openid`，TTL=7天（604800s），序列化 JSON。

**注册验证规则**（`regeditUserInfo`）：
- `openid`：必填
- `username`：必填，长度 2-20
- `avatarUrl`：必填，URL 格式
- `phone`：必填（前端已通过腾讯云/微信获取标准化手机号）
- `gender`：必填，枚举 `0/1/2`
- `birthday`：必填
- `signature`：可选，长度 ≤ 50

**迁移注意**：
- `uuid` 由后端生成（`generateUUID(username, phone)`），重构后应保持唯一性算法一致。
- `openid` 在旧系统中同时承担认证 token 的职责，重构后需要替换为 JWT。
- `gender` 枚举值与微信小程序不同（微信: `0`=未知，`1`=男，`2`=女），旧系统已做转换。

---

### 2.2 huating_user_data（雀士战绩统计）

**源文件**：`application/admin/common/model/UserData.php`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int unsigned | 主键 |
| `userId` | int unsigned | → `huating_user.id`（UNIQUE） |
| `total` | int unsigned | 对局总数 |
| `point` | decimal(10,3) | 总点数（含小数，结算四舍五入） |
| `rate` | decimal(10,2) | RATE 值（对局胜率衍生指标） |
| `top_total` | tinyint unsigned | 当前连续一位次数 |
| `top_total_temp` | tinyint unsigned | 连续一位次数临时值（结算时暂存） |
| `high_score` | int | 历史最高单局分 |
| `low_score` | int | 历史最低单局分 |
| `one_total` | int unsigned | 一位总次数 |
| `one_score` | int unsigned | 一位时总分数 |
| `two_total` | int unsigned | 二位总次数 |
| `two_score` | int | 二位时总分数（可为负） |
| `three_total` | int unsigned | 三位总次数 |
| `three_score` | int | 三位时总分数 |
| `four_total` | int unsigned | 四位总次数 |
| `four_score` | int | 四位时总分数 |
| `fly_total` | int unsigned | 负分（飞出）总次数 |
| `fly_score` | int | 负分时总分数 |
| `score` | int | 总得分（分数累计，非点数） |
| `visitor_count` | int unsigned | 被访次数 |

**积分规则常量**（`UserData::POINT_CONFIG`）：
```php
const POINT_CONFIG = [
    'score' => 25000,          // 基准分（对局中每人初始持有分）
    'point' => [30, 10, -10, -30]  // 一/二/三/四位对应获得的点数
];
```

**点数计算公式**（`ModelConfig::handlerModelPointList`）：
```
用户最终得分 = round((用户实际分数 - 模式基准点) / 1000 + 对应顺位积分, 2)
```

---

### 2.3 huating_record（单局对局记录）

**源文件**：`application/admin/common/model/Record.php`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int unsigned | 主键 |
| `modelId` | int unsigned | → `huating_model_config.id` |
| `userId_a` | int unsigned | 一位雀士 ID |
| `score_a` | int unsigned | 一位雀士分数 |
| `userId_b` | int unsigned | 二位雀士 ID |
| `score_b` | int | 二位雀士分数（可为负） |
| `userId_c` | int unsigned | 三位雀士 ID |
| `score_c` | int | 三位雀士分数 |
| `userId_d` | int unsigned | 四位雀士 ID |
| `score_d` | int | 四位雀士分数 |
| `status` | tinyint unsigned | `1`=正常，`0`=已删除 |
| `create_time` | datetime | 记录时间 |

**约束**：四人分数之和必须等于模式的 `aggregate`（如标准日麻为 100000）。  
**索引**：`KEY idx_user (userId_a, userId_b, userId_c, userId_d)`

---

### 2.4 huating_ktxx_log（开桌记录）

**源文件**：`application/admin/common/model/KtxxLog.php`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int unsigned | 主键 |
| `groupId` | int unsigned | 桌子编组号（物理桌台标识） |
| `modelId` | int unsigned | → `huating_model_config.id` |
| `record_total` | tinyint unsigned | 已打局数 |
| `price` | decimal(10,2) | 标准台费 |
| `member_price` | decimal(10,2) | 会员台费 |
| `month_price` | decimal(10,2) | 月卡减免 |
| `amount` | decimal(10,2) | 合计金额 |
| `a_userId` | int unsigned | 東家用户 ID |
| `b_userId` | int unsigned | 南家用户 ID |
| `c_userId` | int unsigned | 西家用户 ID |
| `d_userId` | int unsigned | 北家用户 ID |
| `a_point` ~ `d_point` | decimal(10,2) | 東/南/西/北家累计点数 |
| `game_status` | tinyint unsigned | `1`=游戏进行中，`0`=已结束 |
| `change_user` | tinyint unsigned | `0`=人员未变更，`1`=有换人 |
| `notify_status` | tinyint unsigned | `1`=播报通知，`0`=禁用 |
| `create_time` | datetime | 开桌时间 |
| `close_time` | datetime | 关桌时间 |

**索引**：`KEY idx_ktxx_groupId_status (groupId, game_status)`，`KEY idx_user (a_userId, b_userId, c_userId, d_userId)`

**座位映射**（bearing 参数）：`0`=東，`1`=南，`2`=西，`3`=北

---

### 2.5 huating_bill（账务记录）

**源文件**：`application/admin/common/model/Bill.php`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `userId` | int unsigned | → `huating_user.id` |
| `onlineId` | varchar(100) | → 在线支付订单号（`huating_online_pay_order`） |
| `ktxxId` | int unsigned | → `huating_ktxx_log.id`（防止重复账单） |
| `typeId` | tinyint unsigned | 账务类型（见枚举） |
| `last_member_money` | decimal(10,2) | 结算前余额快照 |
| `amount` | decimal(10,2) | 本单金额 |
| `log_json` | text | 账单说明（JSON 字符串） |
| `payId` | tinyint unsigned | 支付状态（见枚举） |
| `admin` | varchar(20) | 操作管理员 username |
| `remark` | varchar(50) | 备注 |
| `discount` | decimal(10,0) | 折扣金额 |
| `refund` | varchar(100) | 退款申请信息 |
| `refund_money` | decimal(10,2) | 退款金额 |
| `back_time` | datetime | 退款时间 |
| `delete_time` | datetime | 软删除时间 |

**枚举常量**：

`Bill::PAY_ID_CONFIG`（支付状态，9 种）：

| id | name |
|----|------|
| 1 | 尚未支付 |
| 2 | 微信支付 |
| 3 | 现金支付 |
| 4 | 支付宝支付 |
| 5 | 会员支付 |
| 6 | 在线支付 |
| 7 | 门店赠送 |
| 8 | 已经退款 |
| 9 | 他人代付 |

`Bill::TYPE_ID_CONFIG`（账务类型，4 种）：

| id | name |
|----|------|
| 1 | 场代支付（打牌场费） |
| 2 | 场代退回 |
| 3 | 会员储值 |
| 4 | 会员退回 |

---

### 2.6 huating_model_config（麻将模式配置）

**源文件**：`application/admin/common/model/ModelConfig.php`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int unsigned | 主键 |
| `name` | varchar(10) | 模式名称（UNIQUE） |
| `aggregate` | int unsigned | 模式总分（四人之和必须等于此值） |
| `point` | int unsigned | 基准点（返点基准，参与点数计算） |
| `one` | tinyint unsigned | 一位顺位积分 |
| `two` | tinyint | 二位顺位积分（可为负） |
| `three` | tinyint | 三位顺位积分 |
| `four` | tinyint | 四位顺位积分 |
| `score` | tinyint unsigned | 对局奖励积分数 |
| `isRank` | tinyint unsigned | `1`=参与排名，`0`=不参与 |
| `sameScore` | tinyint unsigned | `0`=不允许同分，`1`=允许同分 |
| `status` | tinyint unsigned | `1`=启用，`0`=禁用 |

---

### 2.7 huating_user_grade（雀士段位）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int unsigned | 主键 |
| `userId` | int unsigned | → `huating_user.id` |
| `levelId` | int unsigned | 段位 ID（参照段位配置表） |
| `currentScore` | int | 当前段位积分 |

---

### 2.8 huating_user_member（会员储值）

| 字段 | 类型 | 说明 |
|------|------|------|
| `userId` | int unsigned | → `huating_user.id` |
| `member_money` | decimal(10,2) | 当前会员余额 |
| `status` | tinyint unsigned | 会员状态 |

---

### 2.9 huating_member_config（会员套餐）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `pay_amount` | decimal(10,2) | 实付金额 |
| `recharge_amount` | decimal(10,2) | 充值到账金额 |
| `play_days` | int | 赠送打牌天数 |
| `month_card_days` | int | 月卡天数 |

---

### 2.10 huating_table_config（台桌设备配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `groupId` | int unsigned | 桌台编组（对应一张麻将桌） |
| `bearing` | tinyint | 座位方位：`1`=東，`2`=南，`3`=西，`4`=北 |
| `qrCode` | varchar(32) | 设备二维码（32位唯一标识） |
| `userId` | int unsigned | 当前就座用户 ID（0=空座） |
| `price` | decimal(10,2) | 标准台费 |
| `member_price` | decimal(10,2) | 会员台费 |
| `month_price` | decimal(10,2) | 月卡减免 |
| `status` | tinyint | `1`=启用，`0`=禁用 |

---

## 三、表间关系

```
huating_user (1) ─────────────────── (N) huating_bill
                 ─────────────────── (1) huating_user_data
                 ─────────────────── (1) huating_user_grade
                 ─────────────────── (1) huating_user_member

huating_ktxx_log (1) ────────────── (N) huating_record
                     ────────────── (N) huating_bill (via ktxxId)
                     ─── groupId ── (N) huating_table_config

huating_record   ─── modelId ────── (1) huating_model_config

huating_user_member ─────────────── (N) huating_member_config (套餐购买)
```

---

## 四、迁移风险与建议

### 4.1 字段冗余 / 别名问题（前端兼容性）

旧小程序前端在 `bill.js` 中存在 `normalizeBillItem()` 方法，同时兼容以下字段别名：

| 标准字段（后端可能返回） | 别名（后端也可能返回） |
|-------------------------|----------------------|
| `amount` | `money` |
| `pay_name` | `payName` |
| `type_name` | `typeName` |

**重构建议**：FastAPI 重构后统一使用 `snake_case`，Pydantic 响应模型强制规范输出，消除别名。

### 4.2 支付参数多结构问题

旧小程序前端 `member.js` 和 `bill.js` 均实现了 `pickPaymentParamsFromResponse()` 以应对后端返回 `data.payParams` 或 `data.payInfo` 或 `d1.payParams` 等多种嵌套格式。

**重构建议**：FastAPI 统一返回：
```json
{
  "pay_params": {
    "prepay_id": "...",
    "timestamp": "...",
    "nonce_str": "...",
    "sign": "..."
  }
}
```

### 4.3 openid 认证机制

旧系统以 `openid` 作为用户标识，每次请求都携带 `openid` 并通过 `Referer` 头做简单校验。

**重构建议**：
1. 登录阶段通过 `code` 换取 `openid`，并签发 JWT（`access_token` + `refresh_token`）。
2. 后续请求携带 `Authorization: Bearer <token>` 标头。
3. Redis 缓存用户信息的机制可保留，但 key 改为 `user:{user_id}`。

### 4.4 游戏状态 Redis 依赖

`Game` 控制器使用 Redis `select: 14` 存储实时游戏状态，`expire: 0`（不过期），存在内存泄漏风险。

**重构建议**：FastAPI 重构时为游戏状态 key 设置 TTL（建议 24h），并在游戏结束时主动清理。

### 4.5 事务安全

`Record::handlerAddRecord()` 涉及多表写入（record / user_data / user_grade / bill），旧代码未使用数据库事务。

**重构建议**：FastAPI 重构时使用 SQLAlchemy 事务（`async with session.begin()`）包裹整个结算流程。

---

## 五、字段命名规范建议（重构后）

| 旧系统（camelCase） | 重构后（snake_case） | 说明 |
|--------------------|--------------------|------|
| `userId` | `user_id` | 外键统一 `_id` 后缀 |
| `avatarUrl` | `avatar_url` | URL 类字段加 `_url` |
| `groupId` | `group_id` | |
| `modelId` | `model_id` | |
| `ktxxId` | `session_id`（建议重命名） | ktxx 为拼音缩写，重构时语义化 |
| `payId` | `pay_status` | 语义化，避免与 `id` 混淆 |
| `typeId` | `bill_type` | |
| `isRank` | `is_rank` | 布尔字段加 `is_` 前缀 |
| `sameScore` | `allow_same_score` | |
| `game_status` | `is_active` 或 `status` | |
| `notify_status` | `notify_enabled` | 布尔语义化 |
