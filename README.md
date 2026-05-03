# OpenClaw Control UI 汉化方案

## 项目简介

本方案实现了 OpenClaw Control UI（v2026.5.2）的完整中文化，通过 DOM 文本替换脚本注入到 `index.html`，无需修改任何 JS 源文件。

## 背景与问题分析

OpenClaw 的 UI 使用 Lit 框架构建，存在两类英文文本：

1. **通过 `t()` 函数调用的文本**：这些可以通过语言包（`zh-CN-CTWdflWA.js`）覆盖
2. **硬编码在 Lit `html\`...\`` 模板里的文本**：语言包无法覆盖，因为框架不会对这些文本调用 `t()`

实测发现，**绝大多数 UI 标签（按钮、导航、设置项、下拉选项）都是硬编码的**，语言包只能覆盖少量动态文本。

## 解决方案

在 `index.html` 的 `</head>` 前注入一段 JavaScript 脚本，实现：

- **文本节点替换**：遍历所有 DOM 文本节点，匹配替换表中的英文
- **属性替换**：处理 `aria-label`、`title`、`placeholder` 属性
- **动态监听**：通过 `MutationObserver` 监听 DOM 变化，自动替换新增内容
- **延迟执行**：设置 200ms/800ms/2000ms 延迟，确保 Lit 渲染完成后再替换
- **路由切换**：监听 `popstate` 事件，页面切换后重新应用替换

## 文件结构

```
openclaw-i18n/
├── README.md              # 本文件
├── zh_inject.py           # 注入脚本（在服务器上执行）
├── zh_replacements.json   # 替换规则表
└── openclaw-index.html.example  # 注入后的 index.html 示例
```

## 使用方法

### 前提条件

- OpenClaw 已安装并运行（v2026.5.2）
- 文件路径：`/root/openclaw/core/dist/control-ui/index.html`

### 执行步骤

1. **备份原始文件**
   ```bash
   cp /root/openclaw/core/dist/control-ui/index.html \
      /root/openclaw/core/dist/control-ui/index.html.bak
   ```

2. **运行注入脚本**
   ```bash
   python3 zh_inject.py
   ```

3. **刷新浏览器**，验证中文化效果

### 自定义替换规则

编辑 `zh_replacements.json`，添加新的 `"英文": "中文"` 对，然后重新运行注入脚本。

## 替换规则覆盖范围

共 **106 条**替换规则，覆盖：

| 类别 | 数量 | 示例 |
|------|------|------|
| 导航菜单 | 18 | 聊天、控制、概览、频道... |
| 按钮标签 | 25 | 删除消息、复制为 Markdown、发送消息... |
| 设置项 | 30 | 模型与思考、网关认证、外观... |
| 下拉选项 | 15 | 关闭/最小/低/中/高... |
| 页面标题 | 10 | 设置、高级、安全... |
| 其他 | 8 | 颜色模式、折叠侧边栏... |

## 已知限制

- **品牌名保留**：OpenClaw、LongCat 等品牌名不翻译
- **动态内容**：AI 助手发送的消息内容不翻译
- **时间格式**：日期时间格式保持原样
- **代码相关**：错误日志中的代码/路径不翻译

## 技术细节

### 为什么不直接修改 JS 源文件？

`index-Dqolf6WA.js` 是 1MB 的压缩文件，直接替换字符串可能：
- 破坏代码逻辑（变量名、CSS 类名、HTML 属性中可能包含相同字符串）
- 导致框架崩溃（Lit 的注释节点 `<!--?lit$...-->` 被破坏）
- 难以维护（每次更新 OpenClaw 都需要重新修改）

### 为什么不扩展语言包？

语言包只能覆盖通过 `t()` 函数调用的文本。实测发现 OpenClaw 的 Lit 模板中约 70% 的英文是直接写在模板字符串里的，没有调用 `t()`。

### MutationObserver 配置

```javascript
observer.observe(document.body, {
  childList: true,        // 监听子节点变化
  subtree: true,          // 监听所有后代节点
  characterData: true,    // 监听文本内容变化
  attributes: true,       // 监听属性变化
  attributeFilter: ["aria-label", "title", "placeholder"]  // 只监听这些属性
});
```

## 更新日志

- **2026-05-04**：初始版本，106 条替换规则，覆盖聊天页和设置页
