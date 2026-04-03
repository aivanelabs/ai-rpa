# Python 模块拆分与优化建议（agent_android）

## 结论（TL;DR）
建议**分阶段拆分**，不要维持现状。

当前最需要优先拆分的模块：
1. `clients/python/agent_android/client.py`（约 1846 行）
2. `clients/python/agent_android/repl.py`（约 880 行）

`cli.py`（约 250 行）目前可暂时保持，等前两者稳定后再考虑进一步解耦。

## 为什么建议拆分

- `client.py` 同时承担了 HTTP 通信、UI 树解析、快照匹配、操作执行等职责，属于“多职责聚合”文件，维护和回归成本高。
- `repl.py` 包含命令定义、解析、分发、交互流程、输出控制，命令扩展会持续推高复杂度。
- 从模块边界看，已经存在天然分层机会（transport/snapshot/config/formatting 已是独立模块），继续拆分的收益明显。

## 拆分优先级与建议边界

### P0：先拆 `client.py`
推荐拆成以下子模块（保持 `AgentAndroidClient` 对外 API 不变）：

- `client_http.py`
  - `_api_call`, `_get_raw`, `_download_binary`
  - 专注 HTTP 请求/响应与异常映射
- `client_operations.py`
  - `_execute_single_operation`, `_execute_template`, `_run_single_operation`
  - 专注模板执行与统一成功/失败处理
- `client_tree.py`
  - UI tree 拉取、缓存、元素定位、refId 解析
  - `_element_identity`, `_find_in_elements`, `_find_matching_snapshot_identity`, `_resolve_action_target`
- `client_xpath.py`
  - XPath 生成、验证、候选排序（若目前散落在 client.py，可集中）

迁移方式：
- 第 1 步只做“搬运+导入替换”，不改行为。
- 第 2 步补回归用例（或最少 smoke 脚本）后再做命名和参数标准化。

### P1：再拆 `repl.py`
推荐采用“命令注册表 + 命令处理器”模式：

- `repl_parser.py`
  - `_parse_line` 与命令参数解析逻辑
- `repl_handlers/` 目录
  - 每类命令单独文件，例如 `navigation.py`, `query.py`, `actions.py`, `system.py`
- `repl_session.py`
  - 主循环、历史记录、命令分发

这样可以避免单文件持续膨胀，并降低新增命令时的冲突概率。

## 是否可以先保持现状？
可以，但只适合短期（例如 1-2 周内不再扩展命令）。

如果你们近期还有以下计划，建议立即进入拆分：
- 增加更多 REPL 命令（尤其是 XPath、等待、断言类）
- 增加多设备/多会话能力
- 强化错误分类与重试策略

## 可执行的最小改造计划（两周内）

- 第 1-2 天：从 `client.py` 抽 `client_http.py`，保证行为一致。
- 第 3-5 天：抽 `client_tree.py`，增加 refId/快照匹配 smoke 验证。
- 第 2 周：对 `repl.py` 引入命令注册表并迁移 20-30% 命令，逐步替换。

## 质量门槛建议

- 单文件建议目标：
  - 常规模块 < 400 行
  - 聚合入口（如 `repl_session.py`）< 500 行
- 新增函数建议圈复杂度控制在 10-12 以内。
- 每次拆分 PR 限制在“单一主题 + 可回滚”。

## 风险控制

- 保持现有对外命令与参数兼容。
- 拆分过程中不做行为变更（先结构后语义）。
- 每迁移一个子模块就跑一次 smoke（至少覆盖 list/tap/input/screenshot/waitfor）。
