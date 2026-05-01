# 页面分析：注册（pages/mine/regedit/regedit）

---

**导航：** [← 上一篇：个人数据](04-页面-个人数据-personaldata.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：资料编辑 →](06-页面-资料编辑-userEdit.md)

---

## 1. 页面职责
- 新用户注册/补全资料。
- 获取手机号授权、上传头像、提交注册信息。
- 打开用户协议/隐私/禁赌承诺页面。

## 2. 关键函数
来源：[pages/mine/regedit/regedit.js](../pages/mine/regedit/regedit.js)

- `onGetPhoneNumber(e)`：用微信授权 `code` 换手机号。
- `onChooseAvatar()`：选择头像。
- `onConfirmRegister()`：校验、上传头像、提交注册。
- `_validateRegisterForm()`：表单校验。
- `validateUsernameRule()`：昵称规则校验。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/user/getPhoneNumber` | POST | `onGetPhoneNumber` | 授权码换手机号 | `User::getPhoneNumber` |
| `/upload/uploadAvatarUrl` | 上传 | `onConfirmRegister` | 上传头像文件 | `Upload::uploadAvatarUrl` |
| `/user/regedit/` | POST | `onConfirmRegister` | 提交注册信息 | `User::regedit` |

后端文件：
- [User.php](../../huatingquezhuang-service/application/miniprogram/controller/User.php)
- [Upload.php](../../huatingquezhuang-service/application/miniprogram/controller/Upload.php)

## 4. 关键校验
- 必须勾选协议。
- 头像、昵称、生日、手机号均必填。
- 昵称 2-20 字符，不能数字开头或结尾，限制特殊字符。

## 5. uniapp 迁移注意事项
- `wx.chooseMedia` -> `uni.chooseImage` 或 `uni.chooseMedia`。
- 上传逻辑统一走 uniapp request/upload 适配层，保留“先上传再注册”流程。
- 协议页跳转参数（`type/title`）保持不变，保证业务文案一致。

---

**导航：** [← 上一篇：个人数据](04-页面-个人数据-personaldata.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：资料编辑 →](06-页面-资料编辑-userEdit.md)
