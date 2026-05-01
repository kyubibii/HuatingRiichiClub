# 页面分析：个人数据（pages/mine/personaldata/personaldata）

---

**导航：** [← 上一篇：我的](03-页面-我的-mine-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：注册 →](05-页面-注册-regedit.md)

---

## 1. 页面职责
- 展示用户对局统计、顺位分布、升段进度、近期对局。
- 支持通过 `username` 参数查看指定用户数据。

## 2. 关键函数
来源：[pages/mine/personaldata/personaldata.js](../pages/mine/personaldata/personaldata.js)

- `onLoad(options)`：解析 `username` 并初始化请求。
- `fetchPersonalData(username)`：核心数据请求与大量数据整形。
- `_drawRecentRanks()`：绘制近期排名图。
- `onGoRecord()`：跳转牌谱页。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/user/getUserPersonalData` | POST | `fetchPersonalData` | 获取个人数据总览、排名、记录等 | `User::getUserPersonalData` |

后端文件：
- [User.php](../../huatingquezhuang-service/application/miniprogram/controller/User.php)

## 4. 数据处理特点
- 兼容后端多层结构：`data.userInfo`、`data.recordData`、`data.rankList`、`data.recordList`。
- 计算指标：占比、均值、升段统计、最近对局转换。
- 请求失败或权限失败时做弹窗与回退。

## 5. uniapp 迁移注意事项
- 保留 `fetchPersonalData` 中数据整形函数，不建议直接写在模板层。
- Canvas 绘制建议封装为独立模块，优先保证数据一致性，再迁移视觉。
- `username` 外部查看模式可作为 uniapp 路由参数规范示例。

---

**导航：** [← 上一篇：我的](03-页面-我的-mine-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：注册 →](05-页面-注册-regedit.md)
