# 页面分析：首页（pages/index/index）

---

**导航：** [← 上一篇：项目与接口总览](00-项目与接口总览.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：排名 →](02-页面-排名-rank-index.md)

---

## 1. 页面职责
- 提供扫码进入牌局入口。
- 对扫码结果做合法性校验，然后跳转记分页。

## 2. 关键函数
来源：[pages/index/index.js](../pages/index/index.js)

- `onScan()`：调用 `wx.scanCode` 读取二维码。
- `isValidScanPayload(obj)`：校验 `groupId`、`bearing`、`qrCode(32位)`。
- `parseQueryString(qs)`：解析扫码 URL 参数。
- `normalizeScorePath(p)`：标准化扫码路径。
- `onRank()`：跳到个人数据页。

## 3. 页面接口调用
该页面不调用后端 HTTP 接口；主要调用微信原生能力。

| 类型 | API | 用途 |
|---|---|---|
| 微信原生 | `wx.requestSubscribeMessage` | 请求订阅消息授权 |
| 微信原生 | `wx.scanCode` | 扫码获取参数 |
| 微信原生 | `wx.navigateTo` | 跳转到 `score` |

## 4. 入参与流程
- 扫码结果支持两种：
  - 直接路径：`/pages/score/score?groupId=...&bearing=...&qrCode=...`
  - JSON 字符串：包含 `groupId/bearing/qrCode`
- 校验失败统一提示“扫码失败”。

## 5. 前后端映射
- 无直接后端调用。

## 6. uniapp 迁移注意事项
- `wx.scanCode` 替换为 `uni.scanCode`。
- `wx.navigateTo` 替换为 `uni.navigateTo`，参数拼接保持一致。
- 继续保留扫码参数合法性函数，避免后端收到异常参数。

---

**导航：** [← 上一篇：项目与接口总览](00-项目与接口总览.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：排名 →](02-页面-排名-rank-index.md)
