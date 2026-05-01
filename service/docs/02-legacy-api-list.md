# 遗留系统 Miniprogram API 清单

> 来源：`huatingquezhuang-service/application/miniprogram/`  
> 基础 URL：`https://miniprogram.huating.cloud/miniprogram`  
> 认证方式（旧）：请求头 `Referer` 包含 AppID `wx92b0665554e342e6` + 请求体携带 `openid`  
> 认证方式（重构后）：`Authorization: Bearer <JWT>`

---

## 一、通用规范

### 1.1 鉴权流程（旧系统）

```
客户端 → 携带 openid 参数 → MiniBase::initialize()
  → 校验 Referer 包含小程序 AppID
  → 校验 openid 参数存在
  → 从 Redis (select:1) 读取用户缓存
  → 注入 $baseUserInfo 供子控制器使用
```

### 1.2 统一响应格式

**成功**：
```json
{ "code": 1, "msg": "操作成功", "data": { ... } }
```

**失败**：
```json
{ "code": 0, "msg": "错误描述", "data": { "err": "详细错误" } }
```

**重构建议（FastAPI 统一响应模型）**：
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... },
  "error_code": null
}
```

---

## 二、User 模块（`miniprogram/controller/User.php`）

路由前缀：`/user/`

### 2.1 获取手机号

| 项 | 值 |
|----|-----|
| 路径 | `POST /user/getPhoneNumber` |
| 认证 | Referer + openid（不要求已注册） |
| 触发 | 注册页点击"微信授权手机号" |

**请求体**：
```json
{ "openid": "xxx", "code": "微信授权code" }
```

**响应**：
```json
{ "code": 1, "msg": "获取成功", "data": { "phone": "13812345678" } }
```

**依赖**：`TencentCloudModel::getPhoneNumber(code)` → 腾讯云手机号解密接口

**重构建议**：`code` 应由微信小程序前端通过 `wx.getPhoneNumber` 获取，后端调微信 API 解密；FastAPI 重构时封装为 `WechatService.get_phone_by_code(code)`。

---

### 2.2 用户注册

| 项 | 值 |
|----|-----|
| 路径 | `POST /user/regedit/` |
| 认证 | Referer + openid（不要求已注册） |

**请求体**：
```json
{
  "openid": "xxx",
  "username": "花听雀士",
  "avatarUrl": "https://cdn.huating.cloud/avatar/xxx.jpg",
  "phone": "13812345678",
  "gender": 1,
  "birthday": "1995-05-01",
  "signature": "麻将是人生"
}
```

**字段校验**：
- `openid`：必填
- `username`：必填，长度 2-20，前端还做了额外正则验证（不能纯数字、不能数字开头/结尾）
- `avatarUrl`：必填，URL 格式
- `phone`：必填，11位，以 `1` 开头
- `gender`：必填，`0`=男，`1`=女，`2`=未知
- `birthday`：必填，`YYYY-MM-DD`
- `signature`：可选，≤50字

**响应（成功）**：
```json
{ "code": 1, "msg": "注册成功", "data": { "code": 1, "msg": "注册成功" } }
```

**常见失败原因**：该微信已注册 / 用户昵称已存在 / 该手机号已注册

---

### 2.3 获取用户编辑信息

| 项 | 值 |
|----|-----|
| 路径 | `POST /user/getUserEdit/` |
| 认证 | Referer + openid（必须已注册） |

**请求体**：`{ "openid": "xxx" }`

**响应**：
```json
{
  "code": 1,
  "data": {
    "userInfo": {
      "id": 63,
      "uuid": "ABC12345",
      "openid": "...",
      "username": "花听雀士",
      "phone": "138****5678",
      "avatarUrl": "https://...",
      "gender": 1,
      "birthday": "1995-05-01",
      "signature": "麻将是人生",
      "groupId": 1
    }
  }
}
```

---

### 2.4 更新用户资料

| 项 | 值 |
|----|-----|
| 路径 | `POST /user/updateUserEdit/` |
| 认证 | Referer + openid（必须已注册） |

**请求体**：
```json
{
  "openid": "xxx",
  "username": "新昵称",
  "avatarUrl": "https://...",
  "signature": "新签名"
}
```

**可编辑字段**：`username`、`avatarUrl`、`signature`（性别和生日旧版不允许修改）

---

### 2.5 获取用户首页信息

| 项 | 值 |
|----|-----|
| 路径 | `GET /user/getuserInfo/` |
| 认证 | Referer + openid |

**响应关键字段**：
```json
{
  "code": 1,
  "data": {
    "id": 63,
    "username": "花听雀士",
    "avatarUrl": "https://...",
    "avatarFrame": null,
    "levelName": "初段",
    "levelColor": "#FF5733",
    "status": 1,
    "recordTotal": 120,
    "debtAmount": "0.00",
    "memberAmount": "50.00"
  }
}
```

**依赖**：`UserDataGradeModel`（段位信息）、`BillModel::getUserUnpayAmount()`（欠款）、`UserMemberModel`（会员余额）

---

### 2.6 获取用户个人数据

| 项 | 值 |
|----|-----|
| 路径 | `POST /user/getUserPersonalData` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "username": "花听雀士" }`

**响应结构**：
```json
{
  "data": {
    "userInfo": { "username": "...", "avatarUrl": "...", "levelName": "...", "tag": [...] },
    "recordData": {
      "total": 120,
      "one_total": 35, "two_total": 30, "three_total": 28, "four_total": 27,
      "fly_total": 5,
      "high_score": 42000,
      "low_score": -5000,
      "point": "120.500",
      "rate": "0.29"
    },
    "rankList": [{ "ranking": 3, "score": 120, "create_time": "2025-01-01" }],
    "recordList": [{ "id": 1, "model_name": "标准", "name1": "...", "score1": 40000, ... }]
  }
}
```

---

## 三、Bill 模块（`miniprogram/controller/Bill.php`）

路由前缀：`/bill/`

### 3.1 获取用户账单列表

| 项 | 值 |
|----|-----|
| 路径 | `GET /bill/getUserBillList/` |
| 认证 | Referer + openid |

**请求参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `openid` | string | 必填 |
| `tab` | string | 可选，`paid`=已付，`unpaid`=未付，`refunded`=已退款，默认全部 |
| `page` | int | 页码，默认 1 |
| `pageSize` | int | 每页数量，默认 10 |

**响应**：
```json
{
  "data": {
    "billList": [
      {
        "id": 1001,
        "type_name": "场代支付",
        "pay_name": "尚未支付",
        "amount": "20.00",
        "orderId": "HT202501010001",
        "create_time": "2025-01-01 18:00:00"
      }
    ],
    "count": 50
  }
}
```

**⚠️ 兼容性注意**：旧前端 `normalizeBillItem()` 同时兼容 `amount` / `money`，`pay_name` / `payName`，`type_name` / `typeName`。重构后统一使用 `snake_case`。

---

### 3.2 获取支付参数

| 项 | 值 |
|----|-----|
| 路径 | `POST /bill/getPayInfo/` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "id": 1001 }`

**响应**：
```json
{
  "data": {
    "payParams": {
      "prepay_id": "wx...",
      "timeStamp": "1735689600",
      "nonceStr": "abc123",
      "signature": "..."
    }
  }
}
```

**⚠️ 兼容性注意**：旧后端有时返回 `payParams`，有时返回 `payInfo`，旧前端通过 `pickPaymentParamsFromResponse()` 做容错。重构后统一为 `pay_params`。

---

## 四、Game 模块（`miniprogram/controller/Game.php`）

路由前缀：`/game/`  
**Redis 依赖**：`select: 14`，存储实时游戏状态，当前 TTL=0（永不过期，有泄漏风险）

### 4.1 获取游戏状态

| 项 | 值 |
|----|-----|
| 路径 | `GET /game/handlerGameStatus` |
| 认证 | Referer + openid（必须已注册且账号正常） |
| 轮询频率 | 5000ms（`PREPARING_POLL_MS`） |

**请求参数**：

| 参数 | 类型 | 校验 | 说明 |
|------|------|------|------|
| `groupId` | int | 必填，≥1 | 桌台编组 ID |
| `bearing` | int | 必填，1-4 | 座位方位（1=東，2=南，3=西，4=北） |
| `qrCode` | string | 必填，长度=32 | 设备二维码 |

**响应（未开始）**：
```json
{ "code": 1, "data": { "gameStatus": 0, "modelList": [{ "id": 1, "name": "标准" }] } }
```

**响应（游戏进行中）**：
```json
{
  "code": 1,
  "data": {
    "gameStatus": 1,
    "data": {
      "gameInfo": {
        "id": 500,
        "record_total": 3,
        "a_point": 45.5, "b_point": 12.0, "c_point": -15.0, "d_point": -42.5,
        "seatUsers": [
          { "bearing": 0, "userId": 63, "isSeated": true, "avatarUrl": "...", "username": "...", "totalScore": 45.5 }
        ]
      },
      "modelList": [...]
    }
  }
}
```

**业务逻辑**：
1. 校验设备 `qrCode` 与 `bearing` 是否匹配
2. 若座位为空（`userId=0`）且无进行中游戏 → 分配用户入座
3. 若座位为空且有进行中游戏 → 返回"设备使用中"
4. 若座位已有其他用户 → 返回"此位置有人就坐"
5. 若已在座且游戏进行中 → 返回完整游戏状态

---

### 4.2 开始游戏

| 项 | 值 |
|----|-----|
| 路径 | `POST /game/handlerStartGame` |
| 认证 | Referer + openid |

**请求体**：
```json
{
  "openid": "xxx",
  "groupId": 1,
  "bearing": 1,
  "qrCode": "32位字符串",
  "matchMode": 1
}
```

**业务逻辑**：创建 `huating_ktxx_log` 记录，`game_status=1`，写入四人用户 ID。

---

### 4.3 结束游戏

| 项 | 值 |
|----|-----|
| 路径 | `POST /game/handlerEndGame` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "groupId": 1, "bearing": 1, "qrCode": "..." }`

**业务逻辑**：将 `ktxx_log.game_status` 更新为 `0`，结算账单，清除 Redis 游戏状态。

---

### 4.4 用户离开设备

| 项 | 值 |
|----|-----|
| 路径 | `POST /game/handlerLeaveDevice` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "groupId": 1, "bearing": 1, "qrCode": "..." }`

**业务逻辑**：将 `table_config.userId` 清零，释放座位。

---

### 4.5 提交成绩

| 项 | 值 |
|----|-----|
| 路径 | `POST /game/handlerSubmitRecord` |
| 认证 | Referer + openid |

**请求体**：
```json
{
  "openid": "xxx",
  "groupId": 1,
  "bearing": 1,
  "qrCode": "...",
  "scores": [
    { "bearing": 0, "userId": 63, "point": 40000 },
    { "bearing": 1, "userId": 15, "point": 30000 },
    { "bearing": 2, "userId": 61, "point": 20000 },
    { "bearing": 3, "userId": 62, "point": 10000 }
  ],
  "eastFly": false
}
```

**业务逻辑链（关键，需事务保护）**：
```
提交分数
  → 校验：4人分数总和 == 模式 aggregate
  → 按分数降序排序 → 插入 huating_record
  → 计算各人点数 → 更新 huating_ktxx_log (record_total, *_point)
  → UserDataModel::addUserRecordData() → 更新个人统计
  → UserDataGradeModel::addUserDataGrade() → 更新段位（仅 isRank=1 的模式）
  → UserPlayerWarModel::addPlayerWar() → 更新战力
  → 返回 recordId
```

**⚠️ 风险**：旧代码无事务包裹，中途失败会导致数据不一致。

---

## 五、Member 模块（`miniprogram/controller/Member.php`）

路由前缀：`/member/`

### 5.1 获取会员信息

| 项 | 值 |
|----|-----|
| 路径 | `GET /member/getUserMemberInfo` |
| 认证 | Referer + openid |

**响应**：
```json
{
  "data": {
    "userInfo": { "username": "...", "avatarUrl": "..." },
    "userMemberInfo": {
      "member_money": "50.00",
      "status": 1
    },
    "memberConfigList": [
      { "id": 1, "pay_amount": "100.00", "recharge_amount": "120.00", "play_days": 30, "month_card_days": 1 }
    ]
  }
}
```

---

### 5.2 购买会员套餐

| 项 | 值 |
|----|-----|
| 路径 | `POST /member/memberBuyPay` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "id": 1 }`（id 为会员套餐 ID）

**响应**：
```json
{
  "data": {
    "payParams": {
      "prepay_id": "...",
      "timeStamp": "...",
      "nonceStr": "...",
      "signature": "..."
    }
  }
}
```

---

## 六、Record 模块（`miniprogram/controller/Record.php`）

路由前缀：`/record/`

### 6.1 获取牌谱列表

| 项 | 值 |
|----|-----|
| 路径 | `POST /record/getUserRecordList` |
| 认证 | Referer + openid |

**请求体**：`{ "openid": "xxx", "username": "花听雀士", "page": 1, "pageSize": 10 }`

**响应**：
```json
{
  "data": {
    "list": [
      {
        "id": 1,
        "model_name": "标准",
        "name1": "花听雀士", "score1": 40000,
        "name2": "对手A", "score2": 30000,
        "name3": "对手B", "score3": 20000,
        "name4": "对手C", "score4": 10000,
        "create_time": "2025-01-01 18:00:00"
      }
    ],
    "total": 120
  }
}
```

---

## 七、Rank 模块（`miniprogram/controller/Rank.php`）

路由前缀：`/rank/`

### 7.1 获取排行榜

| 项 | 值 |
|----|-----|
| 路径 | `GET /rank/getStoreRankList` |
| 认证 | Referer + openid |

**请求参数**：`{ "openid": "xxx", "page": 1 }`（固定每页 10 条）

**响应**：
```json
{
  "data": {
    "rankList": [
      {
        "ranking": 1,
        "username": "花听雀士",
        "avatarUrl": "...",
        "score": 520,
        "point": "310.500",
        "rate": "0.35"
      }
    ]
  }
}
```

---

## 八、System 模块（`miniprogram/controller/System.php`）

路由前缀：`/system/`

### 8.1 获取协议文本

| 项 | 值 |
|----|-----|
| 路径 | `POST /system/getPrivacy` |
| 认证 | 无需认证（无 openid 检查） |

**请求体**：
```json
{ "type": "agree" }
```

**type 枚举**：
- `agree`：用户协议与隐私政策
- `gamble`：雀庄禁赌承诺

**响应**：`{ "data": { "text": "<HTML 内容>" } }`

---

## 九、Upload 模块（`miniprogram/controller/Upload.php`）

路由前缀：`/upload/`

### 9.1 上传头像

| 项 | 值 |
|----|-----|
| 路径 | `POST /upload/uploadAvatarUrl` 或 `POST /upload/uploadAvatarUrl/` |
| 认证 | Referer + openid |
| Content-Type | `multipart/form-data` |

**请求参数**：
```
openid: xxx
avatarUrl: <文件二进制>（字段名 avatarUrl）
```

**响应**：
```json
{ "code": 1, "data": { "url": "https://cdn.huating.cloud/avatar/xxx.jpg" } }
```

**依赖**：腾讯云 COS / 对象存储（`AliyunModel` 或 `CosModel`）

### 9.2 上传役满图片

| 路径 | `POST /upload/uploadYakumanUrl` |
|------|------|
| 说明 | 同上，用于役满记录截图 |

---

## 十、接口汇总表

| 模块 | 方法 | 路径 | HTTP 方法 | 需注册 | 说明 |
|------|------|------|-----------|--------|------|
| User | getPhoneNumber | `/user/getPhoneNumber` | POST | 否 | 微信授权获取手机号 |
| User | regedit | `/user/regedit/` | POST | 否 | 用户注册 |
| User | getUserEdit | `/user/getUserEdit/` | POST | 是 | 获取可编辑用户信息 |
| User | updateUserEdit | `/user/updateUserEdit/` | POST | 是 | 更新用户资料 |
| User | getuserInfo | `/user/getuserInfo/` | GET | 是 | 首页用户信息 |
| User | getUserPersonalData | `/user/getUserPersonalData` | POST | 是 | 个人战绩数据 |
| Bill | getUserBillList | `/bill/getUserBillList/` | GET | 是 | 账单列表（分页+筛选） |
| Bill | getPayInfo | `/bill/getPayInfo/` | POST | 是 | 微信支付参数 |
| Game | handlerGameStatus | `/game/handlerGameStatus` | GET | 是 | 游戏状态轮询 |
| Game | handlerStartGame | `/game/handlerStartGame` | POST | 是 | 开始游戏 |
| Game | handlerEndGame | `/game/handlerEndGame` | POST | 是 | 结束游戏 |
| Game | handlerLeaveDevice | `/game/handlerLeaveDevice` | POST | 是 | 用户离桌 |
| Game | handlerSubmitRecord | `/game/handlerSubmitRecord` | POST | 是 | 提交成绩（核心） |
| Member | getUserMemberInfo | `/member/getUserMemberInfo` | GET | 是 | 会员信息 |
| Member | memberBuyPay | `/member/memberBuyPay` | POST | 是 | 购买会员套餐 |
| Record | getUserRecordList | `/record/getUserRecordList` | POST | 是 | 牌谱列表 |
| Rank | getStoreRankList | `/rank/getStoreRankList` | GET | 是 | 排行榜 |
| System | getPrivacy | `/system/getPrivacy` | POST | 否 | 协议隐私文本 |
| Upload | uploadAvatarUrl | `/upload/uploadAvatarUrl` | POST | 是 | 上传头像 |
| Upload | uploadYakumanUrl | `/upload/uploadYakumanUrl` | POST | 是 | 上传役满图片 |

---

## 十一、重构优先级建议

| 优先级 | 模块 | 理由 |
|--------|------|------|
| P0 | User（注册/登录/基本信息） | 认证机制重构入口，所有其他接口依赖 |
| P0 | System（协议） | 无依赖，可快速验证框架可用性 |
| P1 | Rank / Record | 纯查询，无写副作用，风险低 |
| P1 | Bill（查询部分） | 读接口先上，支付接口可保留旧系统代理 |
| P2 | Member（会员购买） | 涉及支付，需完整测试环境 |
| P2 | Bill（支付部分） | 同上 |
| P3 | Game（完整状态机） | 最复杂，涉及 Redis + 事务 + 多表写入，最后迁移 |
