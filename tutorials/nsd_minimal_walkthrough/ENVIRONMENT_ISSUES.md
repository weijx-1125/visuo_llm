# 本机环境诊断记录（2026-10-08）

## Codex setup refresh

普通沙箱 exec 在启动进程前失败：`helper_unknown_error: setup refresh had errors`。
授权提权后的命令能执行。使用 openai-docs 技能核对官方文档后，只读检查配置/日志。
配置已经是 `[windows] sandbox = "elevated"`，未修改。

日志：`C:\Users\79810\.codex\.sandbox\sandbox.2026-10-08.log`。
关键证据：`runtime read/execute validation failed`、`open ACL target for root-only update`、`another process using file (os error 32)`，目标是 `...\runtimes\cua_node\...\bin\node_repl.exe`。
进程清单显示多个 node_repl 实例、多个父进程。日志说明当前刷新因文件占用而失败；仅凭现有证据不能保证这是所有历史间歇错误的唯一原因。

尚未永久修复：当前对话也依赖这些进程，无法安全判断哪些是其他窗口正在用的实例，因此没有批量杀进程、删沙箱、改 ACL 或关闭安全保护。授权提权只是临时继续工作的方式，不是修复。

建议保存工作 → 关闭全部相关 Codex/VS Code 窗口 → 必要时重启 Windows 清除残留 → 先只开一个工作区重新初始化沙箱。之后用不提权的只读命令测试，并多次重开确认。若仍复发，保留新日志，报告运行时文件锁/ACL 刷新问题给 OpenAI；长期产品层修复可能需要运行时或启动逻辑更新。不能承诺仅重启永久解决。

官方说明：https://learn.chatgpt.com/docs/windows/windows-sandbox
文档推荐 elevated，允许失败时临时 fallback，但本机已有 elevated；没有为了绕过错误切换 full access。不要发送 `.sandbox-secrets`、身份令牌、auth 文件等敏感内容。

## Python HTTPS / SSL

直接运行 `D:\Anaconda3\python.exe`，`import ssl` 失败：`ImportError: DLL load failed while importing _ssl`，urllib 因而没有 HTTPSHandler，报 `unknown url type: https`。
在启动 Python 之前，仅给子进程 PATH 增加 `D:\Anaconda3\Library\bin` 后，`ssl` 正常显示 OpenSSL 1.1.1n，公开 Google Form HTML 读取成功。
在 Python 已经启动后只用 os.add_dll_directory 的尝试无效，未保留该修复。

仓库新增 `download_local.ps1` 在启动子进程前设置该进程 DLL 路径，finally 恢复 PATH；不改系统设置。长期使用建议从正确激活的 Conda 环境启动 Python/Jupyter。旧 OpenSSL/环境升级需要单独规划，本次不安装或更新依赖。

## PowerShell profile

默认 login shell 还会报告 profile.ps1 被执行策略阻止；之后检查使用 `-NoProfile`/login=false 不再触发。此问题与启动前 setup refresh、Python SSL 是三个独立问题。没有永久放宽系统执行策略。
