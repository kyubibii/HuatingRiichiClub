# 页面分析：我的（pages/mine/index/index）

---

**导航：** [← 上一篇：排名](02-页面-排名-rank-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：个人数据 →](04-页面-个人数据-personaldata.md)

---

## 1. 页面职责
- 个人中心聚合入口。
- 展示用户基本信息与功能菜单。
- 跳转注册、编辑、账单、个人数据、会员等页面。

## 2. 关键函数
来源：[pages/mine/index/index.js](../pages/mine/index/index.js)

- `onShow()`：每次显示都刷新用户信息。
- `fetchUserInfo()`：拉取用户信息。
- `onGoRegedit/onGoUserEdit/onGoBill/onGoPersonaldata/onGoUserMember()`：导航到子页面。
- `onMenuTap(e)`：菜单点击。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/user/getuserInfo/` | GET | `fetchUserInfo` | 获取当前用户信息 | `User::getUserInfo` |

说明：前端使用 `getuserInfo` 小写写法，后端方法名为 `getUserInfo`，由框架路由解析。

后端文件：
- [User.php](../../huatingquezhuang-service/application/miniprogram/controller/User.php)

## 4. 页面数据
- `userInfo`、`userInfoLoading`
- `menuList`

## 5. uniapp 迁移注意事项
- 将“进入页面自动刷新”放在 `onShow`，保持现有交互预期。
- 订阅消息授权逻辑可封装成通用函数，在多页面复用。
- 菜单配置建议提取到常量文件，便于后续动态化。

---

**导航：** [← 上一篇：排名](02-页面-排名-rank-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：个人数据 →](04-页面-个人数据-personaldata.md)
