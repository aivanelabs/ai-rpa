# AIVane AI RPA

几分钟内让桌面端或 AI agent 控制 Android 手机：查看 UI、点击、输入、启动应用、截图，全部通过局域网本地完成。

这是 `aivanelabs/ai-rpa` 的公开仓库。当前公开面是 **AIVane Android REPL Beta**：一个可直接安装的 `agent-android` CLI，加上一个可从 GitHub 安装的 `agent-android` skill，面向 Codex、Claude Code、OpenClaw 等工具。

## 从这里开始

- 现在已经有现成可安装的 CLI 和 skill 入口，优先使用下面这些命令，不再把仓库内相对路径脚本当作主入口。
- 下载 APK：[GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)
- 安装 CLI：`uv tool install aivane-agent-android`
- 安装 skill：`npx skills add aivanelabs/ai-rpa --skill agent-android`

## 3 步跑通

1. 在手机上安装 APK，并开启 AIVane 无障碍服务。
2. 安装 CLI：

```bash
uv tool install aivane-agent-android
```

如果之后找不到 `agent-android`，先运行：

```bash
uv tool update-shell
```

然后重新打开终端。如果你想让当前 Linux shell 立刻生效，可以执行：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. 验证手机可达：

```bash
agent-android --health --url http://<device-ip>:8080
```

如果成功，再启动 REPL：

```bash
agent-android --repl --url http://<device-ip>:8080
```

## 选一条路径

### 给人手动使用

如果你想在桌面端手动控制手机，直接用 CLI：

1. 从 [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) 下载 APK
2. 用 `uv tool install aivane-agent-android` 安装 CLI
3. 运行 `agent-android --repl --url http://<device-ip>:8080`
4. 在 REPL 中按这个短循环操作：`health` -> `apps` -> `la <package>` -> `list` -> 一个动作 -> `list`

### 给 AI Agent 使用

如果你想让 Codex、Claude Code 或其他 agent 驱动手机：

1. 用 `uv tool install aivane-agent-android` 安装 CLI
2. 安装 skill：

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android
```

3. 给 agent 一个明确任务，例如：

```text
Use the installed agent-android skill to:
1. check phone health
2. list launcher apps
3. launch Settings
4. inspect visible UI nodes
5. tap the Wi-Fi entry
```

## 第一条成功路径

手机可达后，最短可行的 smoke flow 是：

1. `agent-android --repl --url http://<device-ip>:8080`
2. `set url http://<device-ip>:8080`
3. `health`
4. `apps`
5. `la <package>`
6. `list`
7. `tap <refId>`
8. `list`

如果你想看完整安装路径，请看 [docs/install-agent-android.md](docs/install-agent-android.md) 和 [docs/quickstart.md](docs/quickstart.md)。

## 这个 Beta 是什么

- 基于局域网的本地优先 Android 自动化
- 既支持人工使用的 REPL，也支持 agent 使用的 skill
- 对外命令是 `agent-android`
- 适合 inspect -> act -> inspect 的工作流

## 这个 Beta 不是什么

- 不是云端手机农场
- 不是默认可跨公网远程控制
- 不是 iOS 工具
- 不是可视化录制器工作流

## 为什么让手机本身充当 Web Server

- 手机本地运行轻量 HTTP 服务，电脑直接连接 `http://<device-ip>:8080`
- UI 读取、点击、输入、截图都留在手机和控制端之间
- 第一条 smoke flow 不依赖云端中转
- 当前代价是只支持局域网

## 安装来源

- PyPI 包名：`aivane-agent-android`
- 对外命令：`agent-android`
- Skill：[`skills/agent-android/`](skills/agent-android/)
- APK 下载：[GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)

## 仓库内容

- `clients/python/`：采用标准 `src` 布局的可发布 Python CLI 包
- `docs/`：quickstart、安装、协议、权限、发布说明等文档
- `examples/`：smoke flow 和启动辅助脚本
- `skills/agent-android/`：可安装的公开 skill

## 附加资源

- [docs/quickstart.md](docs/quickstart.md)
- [docs/install-agent-android.md](docs/install-agent-android.md)
- [docs/agent-examples.md](docs/agent-examples.md)
- [docs/release-checklist.md](docs/release-checklist.md)
- [docs/known-limitations.md](docs/known-limitations.md)

## 联系方式

如需讨论或协作，请发邮件至 `aivanelabs@gmail.com`。
