# 页面分析：记分（pages/score/score）

---

**导航：** [← 上一篇：牌谱](09-页面-牌谱-record.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：协议隐私 →](11-页面-协议隐私-privacy.md)

---

## 1. 页面职责
- 管理整场牌局生命周期：准备中 -> 对局中 -> 结束。
- 处理设备入座状态、开局、每局计分提交、结束/离开。

## 2. 关键函数
来源：[pages/score/score.js](../pages/score/score.js)

- 状态管理：`setScorePageStatus`、`syncPreparingPoll`
- 轮询：`startPreparingPoll`、`stopPreparingPoll`（5秒）
- 数据同步：`fetchGameStatus`、`applyHandlerGameStatusPayload`
- 对局操作：
  - `requestStartNewGame`
  - `requestSubmitGameRecord`
  - `requestEndGame`
  - `requestLeaveDevice`
- 表单校验：`validateHandSubmit`

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `game/handlerGameStatus` | GET | `fetchGameStatus` | 拉取牌桌状态、用户、模式、局数 | `Game::handlerGameStatus` |
| `game/handlerStartGame` | POST | `requestStartNewGame` | 开始新对局 | `Game::handlerStartGame` |
| `game/handlerSubmitRecord` | POST | `requestSubmitGameRecord` | 提交本局四人分数 | `Game::handlerSubmitRecord` |
| `game/handlerEndGame` | POST | `requestEndGame` | 结束对局 | `Game::handlerEndGame` |
| `game/handlerLeaveDevice` | POST | `requestLeaveDevice` | 准备中离开设备 | `Game::handlerLeaveDevice` |

后端文件：
- [Game.php](../../huatingquezhuang-service/application/miniprogram/controller/Game.php)

## 4. 业务约束
- 四人都入座才允许开局。
- 每局分数和必须等于 `handPointBudget`。
- 东飞模式要求至少一名玩家负分。
- 准备中状态会自动轮询刷新。

## 5. uniapp 迁移注意事项
- 轮询定时器生命周期需与页面显示/隐藏严格绑定。
- 将“局分校验 + 提交 + 刷新状态”封装为事务式动作，减少并发提交。
- `score` 页面建议先迁移逻辑层（store/composable），再迁移 UI。

---

**导航：** [← 上一篇：牌谱](09-页面-牌谱-record.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：协议隐私 →](11-页面-协议隐私-privacy.md)
