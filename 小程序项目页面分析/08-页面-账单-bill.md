# 页面分析：账单（pages/mine/bill/bill）

---

**导航：** [← 上一篇：会员](07-页面-会员-member.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：牌谱 →](09-页面-牌谱-record.md)

---

## 1. 页面职责
- 展示账单列表（全部/已付款/待付款/已退款）。
- 支持复制订单号与账单支付。

## 2. 关键函数
来源：[pages/mine/bill/bill.js](../pages/mine/bill/bill.js)

- `refresh()`：重置分页并刷新。
- `fetchBills({ reset })`：分页获取账单。
- `requestPayInfo(billId)`：获取支付参数。
- `onPayBill(e)`：拉起微信支付。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/bill/getUserBillList/` | GET | `fetchBills` | 获取账单列表（分页+筛选） | `Bill::getUserBillList` |
| `/bill/getPayInfo/` | POST | `onPayBill` | 获取支付参数 | `Bill::getPayInfo` |

其他调用：
- `wx.requestPayment`：账单支付。

后端文件：
- [Bill.php](../../huatingquezhuang-service/application/miniprogram/controller/Bill.php)

## 4. 数据与分页
- `page/pageSize/hasMore`
- `loading/loadingMore`
- `activeTab` 切换后会刷新列表。

## 5. uniapp 迁移注意事项
- 保持下拉刷新与触底加载的组合行为。
- 支付流程建议封装为可复用 `usePayment`，供会员与账单复用。
- 保留 `pickListFromResponse` 的多结构兼容逻辑。

---

**导航：** [← 上一篇：会员](07-页面-会员-member.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：牌谱 →](09-页面-牌谱-record.md)
