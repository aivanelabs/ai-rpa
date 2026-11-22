# 面向 AI agent 的 AIVane

英文版见 [README.md](README.md)。**官方网站：**[aivane.net](https://aivane.net/)

这里存放让 AI agent 使用 [AIVane](https://aivane.net/) 的 skill、插件和示例自动化。AIVane 把网页任务变成可复用的无代码自动化：先构建一次（描述任务，或在 AIVane 桌面应用中录制一次），之后就能带着新的输入在 AIVane 云端浏览器或你自己的电脑上再次运行。

## 选择你的路径

| 我想要… | 使用 | 详情 |
| --- | --- | --- |
| **① 运行和创建浏览器/桌面自动化**，从 Claude、ChatGPT、Codex、Cursor、Hermes 或 OpenClaw 中 | [`skills/aivane`](skills/aivane/SKILL.md) + AIVane MCP 服务器 `https://app.aivane.net/mcp` | [浏览器和桌面自动化](#浏览器和桌面自动化) |
| **② 通过局域网控制 Android 手机**（beta） | [`skills/agent-android`](skills/agent-android/SKILL.md) + `agent-android` CLI | [通过局域网控制 Android 手机](#通过局域网控制-android-手机beta) |

## 浏览器和桌面自动化

典型任务：抓取网站并把数据提取到 CSV、Excel 或 Google Sheets，填写表单，登录门户并下载报表或发票，重复检查价格和库存。通过 AIVane MCP 服务器，agent 可以列出你的自动化、带新输入运行、跟踪运行并读回输出、保存的文件和截图，也可以发起创建新的自动化。

连接一个 MCP 服务器：

- **云端服务器**（任意系统）：`https://app.aivane.net/mcp`（Streamable HTTP，OAuth 登录，免费 AIVane 账号）。
- **本地桌面服务器**（Windows）：从 [aivane.net/download](https://aivane.net/download) 安装 AIVane，然后在 Settings > AI tools (MCP) 中复制连接配置。

添加 skill，它告诉 agent 如何使用 AIVane MCP 工具：

```bash
# skills.sh CLI（Codex、Claude Code、Cursor 等 agent）
npx skills add aivanelabs/ai-rpa --skill aivane

# Claude Code 插件（skill 加云端 MCP 服务器）；之后运行 /mcp，选择 aivane 并完成认证
claude plugin marketplace add aivanelabs/ai-rpa
claude plugin install aivane@aivane

# Hermes Agent
hermes skills install aivanelabs/ai-rpa/skills/aivane
```

Claude（claude.ai、Claude Desktop）、ChatGPT 和 VS Code 在各自的连接器或 MCP 设置中使用同一地址连接。各客户端的配置方法见 [aivane.net/docs/ai-tools](https://aivane.net/docs/ai-tools/) 和 [`skills/aivane/SKILL.md`](skills/aivane/SKILL.md)，更多安装方式见 [skills/README.md](skills/README.md)。

## 通过局域网控制 Android 手机（beta）

**AIVane Android REPL Beta** 让桌面端或 AI agent 控制 Android 手机：查看 UI、点击、输入、启动应用、截图，全部通过局域网本地完成。

先从 [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) 下载 APK 安装到手机，并开启 AIVane 无障碍服务。然后：

```bash
uv tool install aivane-agent-android
npx skills add aivanelabs/ai-rpa --skill agent-android
agent-android --health --url http://<device-ip>:8080
```

包含演示视频、快速上手、REPL 命令、模板上传和校验的完整指南：[docs/android/README_CN.md](docs/android/README_CN.md)。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| [`skills/`](skills/README.md) | 可安装的 agent skill：`aivane/`（通过 MCP 运行浏览器和桌面自动化）和 `agent-android/`（Android 局域网 beta） |
| [`plugins/`](plugins/aivane/README.md) | Claude Code 插件；`plugins/aivane/` 打包了 `aivane` skill 和云端 MCP 服务器。插件市场文件是 [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) |
| [`examples/`](examples/README.md) | AIVane 示例自动化（Application），以及 Android smoke flow 和 ADB 启动辅助脚本 |
| `clients/` | 可发布的 Python 包：[`clients/python/`](clients/python/README.md)（`aivane-agent-android`，命令 `agent-android`）和 [`clients/template-linter/`](clients/template-linter/README.md)（`aivane-template-linter`，命令 `aivane-template-lint`） |
| `docs/` | [`docs/android/`](docs/android/README_CN.md) Android beta 指南（链接 `docs/` 下的 quickstart、安装、协议、权限、发布文档）；[`docs/templates/`](docs/templates/README.md) 模板编写和校验；[`docs/operation-types/`](docs/operation-types/README.md) OperationType 参考；`docs/assets/` 媒体资源 |
| `scripts/` | 仓库工具，例如把 `skills/aivane/` 复制进插件的 `sync_plugin_skills.py` |
| `aivane.apk` | Android REPL beta 的 APK 构建（正式版本见 [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)） |

## 贡献、安全、许可证

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [LICENSE](LICENSE)（MIT）
- 支持：`support@aivane.net` · 隐私：[aivane.net/privacy](https://aivane.net/privacy/) · 条款：[aivane.net/terms](https://aivane.net/terms/)
