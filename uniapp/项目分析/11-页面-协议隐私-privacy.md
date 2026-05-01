# 页面分析：协议隐私（pages/privacy/privacy）

---

**导航：** [← 上一篇：记分](10-页面-记分-score.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：接口总表 →](12-接口总表-按页面归类.md)

---

## 1. 页面职责
- 根据 `type` 参数拉取协议内容并展示。
- 支持不同标题（用户协议、隐私政策、禁赌承诺）。

## 2. 关键函数
来源：[pages/privacy/privacy.js](../pages/privacy/privacy.js)

- `onLoad(options)`：读取 `type/title`。
- `fetchPrivacy(type)`：请求协议文本。
- `pickTextFromResponse(res)`：提取文本内容。

## 3. 页面接口调用

| 接口路径 | 方法 | 调用点 | 用途 | 后端映射 |
|---|---|---|---|---|
| `/system/getPrivacy` | POST | `fetchPrivacy` | 按类型获取协议文本 | `System::getPrivacy` |

后端文件：
- [System.php](../../huatingquezhuang-service/application/miniprogram/controller/System.php)

## 4. 异常处理
- `type` 缺失直接报错。
- 返回文本为空时展示“未获取到协议内容”。

## 5. uniapp 迁移注意事项
- 继续保留 `type/title` 路由参数协议。
- 协议文本若为富文本，建议统一使用安全渲染组件。

---

**导航：** [← 上一篇：记分](10-页面-记分-score.md) | [📋 总览](00-项目与接口总览.md) | [下一篇：接口总表 →](12-接口总表-按页面归类.md)
