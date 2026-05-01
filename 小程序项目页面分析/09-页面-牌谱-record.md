# 页面分析：牌谱（pages/mine/record/record）

---

**导航：** [← 上一篇：账单](08-页面-账单-bill.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：记分 →](10-页面-记分-score.md)

---

## 1. 页面职责
- 分页展示用户对局记录。
- 支持按 `username` 查看指定用户记录。

## 2. 关键函数
来源：[pages/mine/record/record.js](../pages/mine/record/record.js)

- `fetchList({ reset })`：核心分页查询。
- `onPullDownRefresh()`：下拉刷新。
- `onReachBottom()`：上拉加载。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/record/getUserRecordList` | POST | `fetchList` | 获取用户对局记录分页数据 | `Record::getUserRecordList` |

后端文件：
- [Record.php](../../huatingquezhuang-service/application/miniprogram/controller/Record.php)

## 4. 状态字段
- `page/pageSize/finished/loading`
- `list/total`
- `username`（可选筛选）

## 5. uniapp 迁移注意事项
- 保持分页结束判定逻辑（`list.length===0` 或 `merged>=total`）。
- 将 `pickListFromResponse` 迁移为 shared adapter，供个人数据页复用。

---

**导航：** [← 上一篇：账单](08-页面-账单-bill.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：记分 →](10-页面-记分-score.md)
