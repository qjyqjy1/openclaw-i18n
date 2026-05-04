#!/usr/bin/env python3
"""
OpenClaw Control UI 汉化注入脚本
================================
将 DOM 文本替换脚本注入到 index.html 中，实现全中文化。

使用方法:
  1. 修改 INDEX_FILE 路径为你的 OpenClaw index.html 路径
  2. python3 zh_inject.py
  3. 刷新浏览器

作者: Hermes Agent
日期: 2026-05-04
版本: 1.0
"""

import re
import sys
import shutil
import os

# ============ 配置 ============
INDEX_FILE = "/usr/lib/node_modules/openclaw/dist/control-ui/index.html"
BACKUP_SUFFIX = ".bak"

# ============ 替换规则 ============
REPLACEMENTS = [
    # --- 聊天页面 ---
    ("You", "你"),
    ("Assistant", "助手"),
    ("Delete message", "删除消息"),
    ("Copy as markdown", "复制为 Markdown"),
    ("Message Assistant", "发送消息给助手"),
    ("Message Assistant （回车发送）", "发送消息给助手（回车发送）"),
    ("Message Assistant (Enter to send)", "发送消息给助手（回车发送）"),
    ("Context", "上下文"),

    # --- 设置页面 - 标题和标签 ---
    ("Settings", "设置"),
    ("Advanced", "高级"),
    ("Model & Thinking", "模型与思考"),
    ("Model", "模型"),
    ("Thinking", "思考"),
    ("Fast mode", "快速模式"),
    ("Channels", "频道"),
    ("Connect →", "连接 →"),
    ("Security", "安全"),
    ("Configure →", "配置 →"),
    ("Gateway auth", "网关认证"),
    ("Password", "密码"),
    ("Exec policy", "执行策略"),
    ("Allowlist", "白名单"),
    ("Device auth", "设备认证"),
    ("Disabled", "已禁用"),
    ("Personal", "个人"),
    ("Avatar is browser-local", "头像仅保存在浏览器本地"),
    ("Choose image", "选择图片"),
    ("Clear avatar", "清除头像"),
    ("Stored in this browser only.", "仅保存在此浏览器中。"),
    ("Appearance", "外观"),
    ("Theme", "主题"),
    ("Mode", "模式"),
    ("Light", "浅色"),
    ("Dark", "深色"),
    ("System", "系统"),
    ("Roundness", "圆角"),
    ("None", "无"),
    ("Slight", "轻微"),
    ("Default", "默认"),
    ("Round", "圆形"),
    ("Full", "完整"),
    ("Import", "导入"),
    ("Automations", "自动化"),
    ("scheduled tasks", "定时任务"),
    ("Manage →", "管理 →"),
    ("skills installed", "已安装技能"),
    ("Browse →", "浏览 →"),
    ("MCP servers", "MCP 服务器"),
    ("Context Profile", "上下文配置"),
    ("Custom", "自定义"),
    ("BOOTSTRAP CONTEXT", "引导上下文"),
    ("Choose how much workspace context OpenClaw injects into each run. These profiles do not change your model, tools, channels, or theme.",
     "选择 OpenClaw 每次运行注入多少工作区上下文。这些配置不会改变您的模型、工具、频道或主题。"),
    ("Custom bootstrap settings are active.", "自定义引导设置已激活。"),
    ("Choose a built-in profile to replace the current custom values.", "选择内置配置以替换当前自定义值。"),
    ("Balanced default for daily use.", "日常使用的平衡默认值。"),
    ("Highest context budget for repo work.", "仓库工作的最高上下文预算。"),
    ("Lean follow-ups for shared bots.", "共享机器人的精简跟进。"),
    ("Minimal", "最小化"),
    ("Smallest context budget and lowest cost.", "最小上下文预算和最低成本。"),
    ("Skip safe follow-ups", "跳过安全的后续"),
    ("Matches current default", "匹配当前默认值"),
    ("This config does not currently match one of the built-in profiles.", "此配置目前与内置配置不匹配。"),
    ("Pick a profile to stage a focused change to bootstrap size and follow-up behavior.",
     "选择配置以暂存对引导大小和跟进行为的聚焦更改。"),
    ("Maximum context injected from any single bootstrap file.", "从任何单个引导文件注入的最大上下文。"),
    ("Total combined context allowed across all bootstrap files.", "所有引导文件允许的总组合上下文。"),
    ("Reinject workspace bootstrap context on every turn.", "每轮重新注入工作区引导上下文。"),
    ("Current values are custom. Choose a profile to stage a change.", "当前值为自定义。选择配置以暂存更改。"),
    ("Connected", "已连接"),

    # --- 下拉选项 ---
    ("Off", "关闭"),
    ("Low", "低"),
    ("Medium", "中"),
    ("High", "高"),
    ("minimal", "最小"),
    ("off", "关闭"),
    ("low", "低"),
    ("medium", "中"),
    ("high", "高"),

    # --- 按钮标签 ---
    ("Attach file", "附加文件"),
    ("Start conversation", "开始对话"),
    ("New session", "新会话"),
    ("Export chat", "导出聊天"),
    ("Send message", "发送消息"),
    ("Refresh chat data", "刷新聊天数据"),
    ("Toggle assistant thinking/working output", "切换助手思考/工作输出"),
    ("Toggle tool calls and tool results", "切换工具调用和工具结果"),
    ("Toggle focus mode (hide sidebar + page header)", "切换专注模式（隐藏侧边栏和页眉）"),
    ("Show scheduled task sessions", "显示定时任务会话"),
    ("Color mode", "颜色模式"),
    ("Collapse sidebar", "折叠侧边栏"),
    ("Open command palette", "打开命令面板"),
    ("Search", "搜索"),
    ("Documentation", "文档"),
    ("Version", "版本"),

    # --- 其他 ---
    ("file not found", "文件未找到"),
    ("File not found", "文件未找到"),
    ("Select image", "选择图片"),
    ("Backup avatar", "备用头像"),
    ("AVATAR TEXT / EMOJI", "头像文字 / 表情"),
    ("Color mode: 系统", "颜色模式：系统"),
    ("Color mode: 浅色", "颜色模式：浅色"),
    ("Color mode: 深色", "颜色模式：深色"),
    ("Color mode: 浅睡", "颜色模式：浅色"),
    ("Default (off)", "默认（关闭）"),
    ("Default (LongCat)", "默认（LongCat）"),
    ("optional", "可选"),
    ("Gateway password missing", "网关密码缺少"),
]


def build_js(replacements):
    """构建注入的 JavaScript 代码"""
    js = '<script>(function(){'
    js += 'var M={'
    for en, zh in replacements:
        en_esc = en.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        zh_esc = zh.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        js += '"' + en_esc + '":"' + zh_esc + '",'
    js += '};'
    js += 'function rep(n){'
    js += 'if(n.nodeType===3){var t=n.textContent;if(M[t]){n.textContent=M[t]}return}'
    js += 'if(n.tagName==="SCRIPT"||n.tagName==="STYLE")return;'
    js += 'if(n.nodeType===1){'
    js += 'var a=n.getAttribute("aria-label");if(a&&M[a])n.setAttribute("aria-label",M[a]);'
    js += 'var b=n.getAttribute("title");if(b&&M[b])n.setAttribute("title",M[b]);'
    js += 'var c=n.getAttribute("placeholder");if(c&&M[c])n.setAttribute("placeholder",M[c]);'
    js += '}'
    js += 'var ch=Array.from(n.childNodes);for(var i=0;i<ch.length;i++)rep(ch[i])'
    js += '}'
    js += 'function apply(){if(document.body)rep(document.body)}'
    js += 'if(document.body)apply();'
    js += 'setTimeout(apply,200);setTimeout(apply,800);setTimeout(apply,2000);'
    js += 'var obs=new MutationObserver(function(){if(window.__zht)clearTimeout(window.__zht);window.__zht=setTimeout(apply,80)});'
    js += 'var s=function(){if(document.body)obs.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["aria-label","title","placeholder"]});else setTimeout(s,50)};s();'
    js += 'window.addEventListener("popstate",function(){setTimeout(apply,200)});'
    js += '})();</script>'
    return js


def inject(filepath, replacements):
    """将替换脚本注入到 index.html"""

    if not os.path.exists(filepath):
        print(f"错误: 文件不存在: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已经注入
    if "window.__zht" in content:
        print("检测到已有注入脚本，先清除...")
        content = re.sub(r'<script>\(function\(\)\{window __zht.*?</script>', '', content, flags=re.DOTALL)

    js = build_js(replacements)

    if "</head>" not in content:
        print("错误: 未找到 </head> 标签")
        sys.exit(1)

    content = content.replace("</head>", js + "</head>")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"成功注入 {len(replacements)} 条替换规则到 {filepath}")


def restore(filepath):
    """从备份恢复原始文件"""
    backup = filepath + BACKUP_SUFFIX
    if os.path.exists(backup):
        shutil.copy2(backup, filepath)
        print(f"已从备份恢复: {backup} -> {filepath}")
    else:
        print(f"备份文件不存在: {backup}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore(INDEX_FILE)
    else:
        # 先备份
        backup = INDEX_FILE + BACKUP_SUFFIX
        if not os.path.exists(backup):
            shutil.copy2(INDEX_FILE, backup)
            print(f"已备份原始文件: {INDEX_FILE} -> {backup}")
        else:
            print(f"备份已存在: {backup}")

        inject(INDEX_FILE, REPLACEMENTS)
        print("\n完成！刷新浏览器查看效果。")
        print("如需恢复原始文件，运行: python3 zh_inject.py restore")
