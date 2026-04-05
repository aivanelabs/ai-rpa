# REPL 操作测试矩阵（真实设备）

此文档记录在真机环境对公开 Python REPL 工具所做的检查。注意：skill 执行环境自身不能直接连接内网设备，因此真实设备验证由可访问该局域网设备的主机执行。以下结果来自在 `192.168.3.207:8080` 设备上手工执行的 smoke 路径（确认 ADB 连接 -> health -> apps -> launch -> list -> tap -> input -> swipe -> back -> home -> screenshot -> stop），以及相关的 CLI 操作。

| 操作 | 命令 / 说明 | 结果 | 备注 |
|------|-------------|------|------|
| health | `curl http://192.168.3.207:8080/health` | ✅ 成功返回 `{"service":"aivane-repl","status":"running",...}` | HTTP 服务可访问 |
| apps | `curl http://192.168.3.207:8080/apps` + `python ... agent-android.py --apps` | ✅ 列出 50+ 个 launcher 应用 | `apps` 命令返回与 curl 相同的列表 |
| launch | `python agent-android.py --launch aivane.apprepl` | ✅ 返回 `Launched: aivane.apprepl` | 也已对其它 launcher app 做过启动验证 |
| list | `python agent-android.py --wait 2 --list` | ✅ 能列出桌面和 `AIVane REPL` 页面 ARIA 树 | 界面刷新后可重复调用 |
| tap | `python agent-android.py --tap <refId>` | ✅ 已在真机上成功点按按钮/图标 | 示例：成功点按 `复制 BASE URL` 等元素 |
| input | `python agent-android.py --input 4 "smoke123"` | ✅ 在 `AIVane REPL` 输入框中成功输入 | 真机日志和界面状态已验证 |
| swipe | `python agent-android.py --swipe up` | ✅ `Swiped up (duration=300ms, distance=0.5)` | Android touch swipe 接口可用 |
| back | `python agent-android.py --back` | ✅ `Pressed back` | Android back 操作执行成功 |
| press home | `python agent-android.py --press home` | ✅ `Pressed: home` | 启动器已回到主屏 |
| screenshot | `python agent-android.py --screenshot` | ✅ 已成功保存截图文件 | 首次需在设备上完成 MediaProjection 授权 |
| stop | `curl -X POST http://192.168.3.207:8080/stop` | ✅ 返回 `{\"success\":true,\"message\":\"Stop signal dispatched\"}` | 远程 stop 端点已可用 |
| 地址显示 | REPL `vars` / README 说明 | ✅ REPL 会打 “Server: http://...” | URL 已经支持 persisted config，并在 README 中说明 |
| start-app-repl.sh | `bash start-app-repl.sh` | ✅ 已在主机侧验证 | 可自动拉起 app、配置无障碍、启动服务并检查 `/health` 与 `/apps` |

## 结论

当前公开 REPL 路径的主要操作已经在真实设备上验证通过：`health`、`apps`、`launch`、`list`、`tap`、`input`、`swipe`、`back`、`press home`、`screenshot`、`stop`。仍需注意的是，skill 子环境本身不能直接访问该局域网设备，因此真实 smoke 仍需在可访问该 IP 的主机上执行，然后把结果回填到这份矩阵。


