# 页面分析：排名（pages/rank/index/index）

---

**导航：** [← 上一篇：首页](01-页面-首页-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：我的 →](03-页面-我的-mine-index.md)

---

## 1. 页面职责
- 展示排行榜（Top3 + 列表）。
- 支持分页加载与榜单类型切换。

## 2. 关键函数
来源：[pages/rank/index/index.js](../pages/rank/index/index.js)

- `onLoad()`：初始化拉取排行榜。
- `onReachBottom()`：触底分页。
- `fetchStoreRankList(page, append)`：请求并合并榜单数据。
- `onSelectRank(e)`：切换榜单 tab。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `rank/getStoreRankList` | GET | `fetchStoreRankList` | 获取门店排行榜分页数据 | `Rank::getStoreRankList` |

后端文件：
- [Rank.php](../../huatingquezhuang-service/application/miniprogram/controller/Rank.php)

## 4. 状态字段
- `rankTab`、`page`、`rankHasMore`、`rankListLoading`
- `topList`、`rankList`
- 展示辅助：`podiumAvatarUrls`、`podiumNicknames`、`podiumScores`

## 5. 异常与降级
- 请求失败时首屏清空列表并停止继续加载。
- `append` 模式失败不清空已加载数据。

## 6. uniapp 迁移注意事项
- `onReachBottom` 迁移到 uniapp 页面生命周期同名钩子。
- 将 `fetchStoreRankList` 抽到 composable，避免 tab 切换时重复逻辑。
- 保留接口 `debounce: false` 行为，防止分页请求被去抖动吞掉。

---

**导航：** [← 上一篇：首页](01-页面-首页-index.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：我的 →](03-页面-我的-mine-index.md)
