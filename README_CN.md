# AIVane AI RPA

这是 `aivanelabs/ai-rpa` 在 GitHub 上的对外仓库。

当前首发公开面是 **AIVane Android REPL Beta**：提供 Python CLI、公开文档、示例和 sample skills，让 AI agent 可以在局域网内逐步查看 Android UI 状态并控制手机。

## 当前状态

- 仓库结构和公开 CLI 已经可以评估和试用。
- GitHub 是当前 beta 的唯一正式入口。
- APK 通过 [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) 分发。

## 适合谁

- 使用 Codex、Claude Code、OpenClaw 等工具的 AI agent 用户
- 想要按“查看状态 -> 点击/输入/滑动 -> 再查看状态”方式控制 Android 手机的自动化用户
- 愿意在可信局域网内，通过 Python CLI 做早期验证的体验者

## 本仓公开的内容

- `clients/python/agent-android.py`
- 公开协议和用户文档
- smoke 示例和启动辅助脚本
- `skills/` 下的 sample agent skills
- [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) 中的 beta APK

## 本仓未公开的内容

- Java 核心流程引擎内部实现
- 超出公开面的 Android runtime 内部实现
- 内部部署与发布流水线
- 私有更新渠道、凭据和商业化打包部分

## 安全提示

- 当前 beta 只建议在可信局域网中使用。
- 不建议把设备端口暴露到公网。
- 无障碍和截图等敏感能力都需要用户在手机上手动授权。

## 快速开始

1. 在手机上安装 AIVane Android REPL beta APK。
2. 确保手机和电脑在同一 Wi-Fi 网络。
3. 运行客户端：
   ```bash
   python clients/python/agent-android.py --repl --url http://<device-ip>:8080
   ```
4. 在 REPL 中保存地址（`set url http://<device-ip>:8080`），然后跑第一条 smoke 路径：
   - `health`
   - `apps`
   - `la <package>`
   - `list`
   - `tap <refId>`
   - `input <refId> "hello"`
   - `back`
   - `press home`
   - `screenshot`

## 公开资料

- `clients/python/agent-android.py`：Android REPL 的对外客户端入口。
- `docs/`：包含 quickstart、协议说明、权限说明、known limitations、反馈、release notes、repo scope。
- `examples/`：提供 smoke 流、操作矩阵和启动脚本示例。
- `skills/agent-android/`：公开技能定义、提示词和 agents 元数据。

## 安装与启动

- `docs/install-agent-android.md`：说明如何安装 APK、确认局域网连接并完成首次 smoke。
- `examples/start-app-repl.sh`：公开版启动脚本示例，用于在设备上打开 `aivane.apprepl`。

## 附加资源

- `docs/agent-examples.md`：针对 Codex / Claude Code / OpenClaw 的最简提示。
- `.github/ISSUE_TEMPLATE/`：bug/feature 报告模板，帮助收集可操作信息。

## 已知限制

详见 `docs/known-limitations.md`（权限弹窗、仅限 LAN 等 Beta 限制）。

## 联系方式

如需讨论/协作，请发邮件至 `aivanelabs@gmail.com`。


