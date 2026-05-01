# 页面分析：会员（pages/mine/member/member）

---

**导航：** [← 上一篇：资料编辑](06-页面-资料编辑-userEdit.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：账单 →](08-页面-账单-bill.md)

---

## 1. 页面职责
- 展示会员余额、权益、套餐列表。
- 支持会员套餐支付购买。

## 2. 关键函数
来源：[pages/mine/member/member.js](../pages/mine/member/member.js)

- `fetchUserMemberInfo(options)`：获取会员信息。
- `onBuyPackage(e)`：请求支付参数并拉起微信支付。
- `pickPaymentParamsFromResponse(res)`：适配多种返回结构。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/member/getUserMemberInfo` | GET | `fetchUserMemberInfo` | 获取会员信息与套餐列表 | `Member::getUserMemberInfo` |
| `/member/memberBuyPay` | POST | `onBuyPackage` | 获取支付参数 | `Member::memberBuyPay` |

其他调用：
- `wx.requestPayment`：发起微信支付。

后端文件：
- [Member.php](../../huatingquezhuang-service/application/miniprogram/controller/Member.php)

## 4. 业务状态
- `loading/loaded`
- `userInfo/userMemberInfo/memberConfigList`
- 支付互斥锁：`_payingMember`

## 5. uniapp 迁移注意事项
- `wx.requestPayment` 替换为 `uni.requestPayment`。
- 支付参数提取函数必须保留，后端返回结构层级不稳定。
- 购买完成后保留“静默刷新会员信息”逻辑。

---

**导航：** [← 上一篇：资料编辑](06-页面-资料编辑-userEdit.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：账单 →](08-页面-账单-bill.md)
