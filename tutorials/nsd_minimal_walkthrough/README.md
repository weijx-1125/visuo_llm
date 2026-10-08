# NSD 初学者数据流实验

本教程使用服务器 Docker 的既有 visuo_llm Conda 环境。只通过 Git 同步代码；约 6 GB 的方案 B 数据仅在服务器下载，存放于仓库外。下载前应已完成 NSD 协议。代码校验不等于已经下载或运行真实实验。

## 先填写 NSD Data Access Agreement

官方入口：https://naturalscenesdataset.org/ → NSD Data Access Agreement。
官方表单：https://forms.gle/eT4jHxaWwYUDEf2i9

2026-10-08 只读查看到的实际字段：

| 字段 | 怎么填写 |
| --- | --- |
| Email（如果页面要求） | 填能收到邮件的真实邮箱；不要把账号密码发给助手 |
| Read the Terms and Conditions | 打开条款链接阅读；只有确实同意才自行勾选 |
| Your name | 真实姓名 |
| Department | 实际院系/部门，不要编造；无所属时填写真实情况，如 Independent learner / Not affiliated |
| Institution | 实际学校/机构；无所属则如实填写，不保证该情况一定符合条款 |
| Are you a student, postdoc, or faculty? | 本科 Undergraduate student；研究生 Graduate student；博士后 Postdoc；教职 Faculty；不属于这些选 Other 并如实说明 |
| Which data components… | 本教程涉及 Task fMRI data 与 Behavioral data；按你的实际兴趣选择 |
| Which format will you use? | 本教程使用 Prepared data，不必选 Raw data (BIDS) |
| Feedback/comments（选填） | 可写：I would like to learn the image-caption-fMRI data processing workflow using a small teaching subset. |

协议条款链接（表单提供）：https://cvnlab.slite.com/api/s/note/9dgh5HCqgZYhMoAESZBS86/Terms-and-Conditions

最后检查并自行 Submit。表单说明完成后会发送含 Data Manual 的邮件；检查垃圾邮件并保存提交后的页面/手册链接。若页面因网络打不开，先检查浏览器访问 Google Forms 的能力；不要为了继续而假装已经同意。无法确认条款是否允许你的身份/用途时，联系数据提供方。

完成后告诉助手“我已完成 NSD 协议，可以下载方案 B”即可，不需要发送邮箱、身份信息或完整表单。

## 方案 B 的精确定义

- 受试者 subj01，前 6 个 session，fsaverage，GLMdenoise + ridge 的官方 beta。
- 两半球共 12 个 MGH，每个 491,526,300 bytes，合计 5,898,315,600 bytes，即 5.898 GB / 5.493 GiB。
- 教学图像：上述 trial 中出现且有 shared1000 官方 PNG 的图像，最多 200 张；优先重复次数较多者，之后按 NSD ID 排序。不保证都是 3 次重复。
- 对这些教学图像下载完整 PNG，不下载全部 73,000 图像，也不下载约 39.56 GB 的整个刺激 HDF5。这里的“完整”指完整实验呈现图，不是未经裁剪的 COCO 原照片。
- caption 从本仓库已跟踪的 73,000 行 caption 表提取（`ms_coco_nsd_captions_test.pkl`），NSD ID 对应第 `ID-1` 行，固定源文件 SHA-256。
- 不下载 raw BOLD、模型权重、全量 COCO、GCC 候选库或 ROI。
- 原始 session beta 必须作为整文件下载，但教学只使用清单选中的图像；不是所有 beta trial 的图像都会下载。

2026-10-08 查询官方 S3 目录和响应头（未下载数据）：12 个 beta 合计 5,898,315,600 bytes；完整 responses.tsv 为 2,735,837 bytes；全部 1,000 张共享 PNG 合计 321,832,967 bytes，其中最大的 200 张合计 81,739,846 bytes。因此任意最多 200 张的教学子集，完整下载最多 5,982,791,283 bytes，约 5.983 GB / 5.572 GiB。常见估算约 5.97 GB，按约 6 GB 规划即可。

具体选中哪些 PNG、它们的精确合计，需要完成协议、读取 behavior 后才能确定；不需要先下载 6 GB beta 才知道图像选择。建议预留至少 10 GB 磁盘，含临时文件和教学输出；模型额外占用空间另算。

用户已选择仅在服务器下载。默认路径：

| 内容 | Docker 中位置 |
| --- | --- |
| 源码/notebook | /workspace/projects/visuo_llm/tutorials/nsd_minimal_walkthrough |
| 数据、清单、下载报告、.part | /workspace/datasets/nsd_teaching_b |
| 模型权重（本次不下载） | /workspace/checkpoints/nsd_teaching_b/sentence_model |
| notebook 运行结果 | /workspace/results/nsd_teaching_b |
| 下载日志（如记录） | /workspace/logs/nsd_teaching_b |

确认 /workspace 对应 Docker 的持久化挂载；仅看到目录存在不能证明持久化，不确定时先检查容器挂载配置，避免重建容器丢失数据。

## 文件的用途

- `nsd_data_flow.ipynb`：20 个单元，逐步显示 shape/dtype/数值范围，演示图像、caption、fMRI 与回归检索。数据缺失会明确停止。
- `download_data.py`：固定样本选择、官方文件下载、断点续传、ETag 检查、SHA-256 校验；无 AWS 账号要求，只依赖 Python 标准库和可用 HTTPS。
- `download_local.ps1`：本机 Anaconda 的进程级 DLL 路径修复和下载启动器；不改系统 PATH、不安装包。
- `data_manifest.json`：服务器首次初始化时生成在数据目录中，包含 ID、caption、文件路径、大小、ETag、SHA-256。续传重用同一清单；不要求先从本地生成。日后需要另一个机器使用完全相同数据时，单独同步清单，不重新选择图像。
- `download_report.json`：下载并完整校验后保存在数据目录，记录代码提交、清单哈希、文件总量和图像数量。
- 仓库内 `data/`、`models/`、`outputs/`、`cache/` 仅是可选本地路径，均被忽略；服务器实际使用上表的外部路径。
- `.gitignore`：仅在本教学目录排除大型数据/输出，不改原项目忽略规则。
- `requirements-core.txt`：图像与 fMRI 教学依赖建议；只是列表，不是已经验证的跨平台环境锁。
- `ENVIRONMENT_ISSUES.md`：本机启动/HTTPS 问题证据、边界和恢复步骤。

## 第一步：先在 Docker 中对齐代码

本地推送成功之后，在你已有的 Docker 终端执行。先检查是否有未提交修改；有修改就暂停，不使用 reset/强制覆盖：

```bash
hostname
whoami
test -f /.dockerenv && echo 'Inside Docker'
cd /workspace/projects/visuo_llm
git status --short
git branch -vv
git remote -v
git pull --ff-only origin main
git rev-parse HEAD
```

预期是 Docker 的 root 用户、main 跟踪 origin/main，origin 指向用户 fork，不是 upstream。将提交号与本地推送的提交号比较，确认已有文件对齐后再下载。不要只因为 pull 命令没有报错就假定环境和分支正确。

## 第二步：首次在服务器下载

确认代码、Docker 上下文、/workspace 持久化和磁盘空间后：

```bash
source /opt/conda/etc/profile.d/conda.sh
conda activate visuo_llm
which python
python --version
df -h /workspace/datasets
cd /workspace/projects/visuo_llm
python tutorials/nsd_minimal_walkthrough/download_data.py --init --download --verify --agreement-confirmed --data-dir /workspace/datasets/nsd_teaching_b
```

首次初始化只先下载约 2.74 MB 的 behavior，用于选图，再查询元数据生成固定清单。正式下载约 6 GB，脚本会检查剩余空间（额外保留 1 GiB），每个大文件传输期间打印进度；建议事先预留至少 10 GB。不安装包，不下载模型，不运行训练。

如果已经有清单（包括下载中断之后），**不要再次 --init**，使用以下续传命令：

```bash
python tutorials/nsd_minimal_walkthrough/download_data.py --download --verify --agreement-confirmed --data-dir /workspace/datasets/nsd_teaching_b
```

首次下载或续传成功后脚本会补齐 SHA-256，之后执行全量校验。multipart ETag 不当作单文件 MD5：脚本查询真实分块大小并重建 multipart ETag，之后记录全文件 SHA-256。损坏的已完成文件不会被自动覆盖。

可单独重新校验：

```bash
python tutorials/nsd_minimal_walkthrough/download_data.py --verify --data-dir /workspace/datasets/nsd_teaching_b
```

只有首次 `--init` 才会生成样本选择。普通 git pull 不影响外部数据和清单。代码提交、清单哈希、数据 SHA-256 用于追踪一致性；随机种子固定也不保证不同 GPU/依赖后端逐位一致。服务器执行后的 notebook 保存到 /workspace/results/nsd_teaching_b，原 notebook 保持无输出。

下载脚本支持 `--manifest /path/to/data_manifest.json` 复用另一个位置的固定清单。notebook 默认读取数据目录中的清单，因此使用自定义 manifest 路径时需同步调整 notebook 的 manifest_path。

## 在服务器运行 notebook

服务器 Docker 已有项目 Conda 环境；优先使用现有环境，不新建、不整批重装依赖。先检查运行上下文和解释器：

```bash
hostname
whoami
pwd
test -f /.dockerenv && echo 'Inside Docker'
source /opt/conda/etc/profile.d/conda.sh
conda activate visuo_llm
which python
python --version
python -m pip show numpy scipy pandas Pillow matplotlib nibabel fracridge nbformat jupyterlab ipykernel
```

预期 Python 路径 /opt/conda/envs/visuo_llm/bin/python，版本 3.10.21，需以现场检查为准。服务器已有 sentence-transformers、TensorFlow 等核心依赖；检查后仅处理确实缺少的 notebook 支持包。requirements-core.txt 是参考列表，不应直接用来升级现有环境；本次没有安装或连接服务器验证。

可先运行图像/fMRI 部分，不需要 GPU。实际 caption embedding 还需准备完整模型权重，不应把已有 Python 包误认为已有模型文件。教学 notebook 默认抽样约 512 顶点/半球，避免原 get_betas 的全脑加载；原函数对照默认关闭。先观察资源和每一步 shape，再开启额外部分。

首次成功运行后导出 `python -m pip freeze`，自行保存不含私有地址/令牌的环境快照，两个机器用相同依赖版本。第一次环境尚未测试，不要把这个依赖列表理解为保证可复现的锁文件。

## 如何把服务器结果发回来

notebook 最后会写 `/workspace/results/nsd_teaching_b/run_report.json`，包含代码提交、清单哈希、Python/包版本、参数、数组 shape/数值范围、ID 划分和已运行阶段。

只确认数据下载时，先发 `/workspace/datasets/nsd_teaching_b/download_report.json` 即可：

```bash
cat /workspace/datasets/nsd_teaching_b/download_report.json
```

从 VS Code 的容器文件视图保存小报告到本地，或直接复制其 JSON 到对话。不要假设 Docker 内的路径能直接从 SSH 主机使用 scp 读取；需先确认宿主机挂载路径。将报告附加到对话，并说清“运行到了哪一步，下一步想改什么”。出错时发送单元标题、代码、完整 traceback、Python 路径/版本；不要只截最后一行。也可分享执行后的 notebook，先检查敏感内容。没有运行语义模型的报告会明确标记未运行，不能据此评价解码效果。

## notebook 自定义路径

默认与下载命令的服务器路径一致。可以在启动 notebook 内核前设置 `NSD_TEACHING_DATA_DIR`、`NSD_TEACHING_OUTPUT_DIR`、`NSD_TEACHING_MODEL_DIR`，或修改首个单元的路径变量。不改变样本筛选、beta 处理和回归超参数，仅改变存储位置，不影响已有检查点。
