# AIVane AI RPA

这是 `aivanelabs/ai-rpa` 在 GitHub 上的对外仓库。

当前公开面是 **AIVane Android REPL Beta**：提供可发布的 Python CLI、公开文档、示例，以及可直接从 GitHub 安装的 `agent-android` skill，让 AI agent 可以在局域网内逐步查看 Android UI 状态并控制手机。

## 为什么让手机本身充当 Web Server

- 当前 beta 会直接在手机本地启动一个轻量 HTTP 服务，电脑通过 `http://<device-ip>:8080` 直连手机。
- 所有操作都在本地执行：UI 树读取、点击、输入、截图都不会上传到云端。
- 首次 smoke flow 不依赖云服务。
- 当前限制是只能在局域网内控制。

## 从 PyPI 安装 CLI

默认包名是：

```bash
python -m pip install aivane-agent-android
```

升级命令：

```bash
python -m pip install --upgrade aivane-agent-android
```

如果你在 Windows 上安装后找不到 `agent-android`，先运行：

```powershell
py -m site --user-base
```

然后检查输出目录下的 `Scripts` 子目录是否已加入 `PATH`，必要时加入后重新打开终端再试。

安装后直接使用：

```bash
agent-android --help
agent-android --repl --url http://<device-ip>:8080
```

## 从 GitHub 安装 Skill

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android -a claude-code -a codex -a openclaw -g -y
```

这个 skill 依赖本机已经能直接运行 `agent-android`。

## 本地可编辑开发

在 [`clients/python`](clients/python) 目录下执行：

```bash
cd clients/python
python -m pip install -e .
```

本地构建发行包：

```bash
cd clients/python
python -m pip install --upgrade build
python -m build
```

## 快速开始

1. 在手机上安装 AIVane Android REPL beta APK。
2. 开启 AIVane 的无障碍服务。
3. 确保手机和电脑在同一 Wi-Fi 网络。
4. 先确认服务可达：
   - `curl http://<device-ip>:8080/health`
5. 启动 REPL：

```bash
agent-android --repl --url http://<device-ip>:8080
```

6. 在 REPL 中保存地址后跑第一条 smoke 路径：
   - `set url http://<device-ip>:8080`
   - `health`
   - `apps`
   - `la <package>`
   - `list`
   - `tap <refId>`
   - `input <refId> "hello"`
   - `back`
   - `press home`
   - `screenshot`

## 仓库内容

- `clients/python/`：采用标准 `src` 布局的可发布 Python CLI 包
- `docs/`：quickstart、安装、协议、权限、发布说明等文档
- `examples/`：smoke flow 和启动辅助脚本
- `skills/agent-android/`：可安装的公开 skill
- [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)：APK 分发入口

## 附加资源

- [docs/quickstart.md](docs/quickstart.md)
- [docs/install-agent-android.md](docs/install-agent-android.md)
- [docs/agent-examples.md](docs/agent-examples.md)
- [docs/release-checklist.md](docs/release-checklist.md)
- [docs/known-limitations.md](docs/known-limitations.md)

## 联系方式

如需讨论或协作，请发邮件至 `aivanelabs@gmail.com`。
