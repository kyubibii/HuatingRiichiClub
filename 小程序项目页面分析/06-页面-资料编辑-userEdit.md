# 页面分析：资料编辑（pages/mine/userEdit/userEdit）

---

**导航：** [← 上一篇：注册](05-页面-注册-regedit.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：会员 →](07-页面-会员-member.md)

---

## 1. 页面职责
- 展示并编辑用户头像、昵称、签名。
- 提供协议相关入口。

## 2. 关键函数
来源：[pages/mine/userEdit/userEdit.js](../pages/mine/userEdit/userEdit.js)

- `fetchUserEditInfo()`：获取可编辑资料。
- `onChooseAvatar()`：上传头像并让用户确认是否使用。
- `onSave()`：提交资料更新。
- `validateUsernameRule()`：昵称校验。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/user/getUserEdit/` | POST | `fetchUserEditInfo` | 获取编辑表单初始值 | `User::getUserEdit` |
| `/upload/uploadAvatarUrl/` | 上传 | `onChooseAvatar` | 上传新头像 | `Upload::uploadAvatarUrl` |
| `/user/updateUserEdit/` | POST | `onSave` | 提交资料更新 | `User::updateUserEdit` |

后端文件：
- [User.php](../../huatingquezhuang-service/application/miniprogram/controller/User.php)
- [Upload.php](../../huatingquezhuang-service/application/miniprogram/controller/Upload.php)

## 4. 交互特点
- 上传头像后弹窗确认是否启用新头像。
- 页面回显受 `onShow` 刷新控制，避免上传后被立刻覆盖。

## 5. uniapp 迁移注意事项
- 保留“上传成功后确认是否使用”步骤，避免误操作。
- 编辑页请求建议使用页面级 loading 锁，防止重复提交。
- 昵称规则与注册页复用同一校验函数，避免规则漂移。

---

**导航：** [← 上一篇：注册](05-页面-注册-regedit.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：会员 →](07-页面-会员-member.md)
