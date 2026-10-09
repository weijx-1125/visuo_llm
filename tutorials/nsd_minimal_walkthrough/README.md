# NSD 脑数据流教学

打开 [nsd_data_flow.ipynb](nsd_data_flow.ipynb)，按顺序阅读“输入 → 做法 → 原因 → 输出”及紧接着的代码单元。主线是 **官方 fMRI beta → 每张图像的脑活动特征向量**。原始 BOLD→GLM beta 属于已完成的官方上游处理，教程解释但不重跑。

本次不下载模型、不调用 caption 编码、不训练回归、不安装依赖。脑特征向量不是语言语义向量；最后仅解释脑→语义映射所需的输入、训练与预测。

2026-10-09 已在 Docker 的 `visuo_llm` 内核执行全部25个代码单元，无错误输出，所有断言通过；实际得到 `(200,1022)` float32 脑特征矩阵，仅保留三次重复时为 `(36,1022)`。执行输出保存在这份notebook内，无额外运行结果文件。

## 现有方案 B 与存放位置

- subj01 前6个session，fsaverage，官方 `betas_fithrf_GLMdenoise_RR` 左右半球共12个MGH，包含4500个trial。
- 200张完整实验呈现PNG（425×425 RGB，非全部73000张、非未经裁剪COCO原照片），及对应1000句caption。所选图像出现349次：87张一次、77张两次、36张三次。
- 数据源文件总计 **5,965,796,291 bytes，约5.966 GB / 5.556 GiB**：beta 5,898,315,600 bytes、行为表2,735,837 bytes、PNG 64,744,854 bytes；清单/下载报告另计少量空间。
- 数据只在服务器 `/workspace/datasets/nsd_teaching_b`，不提交Git。源代码与这份带输出的notebook在 `/workspace/projects/visuo_llm/tutorials/nsd_minimal_walkthrough`。
- `data_manifest.json` 保存固定图像ID、caption、路径及校验值；不要重新初始化选样本。现有 `download_report.json` 是下载校验记录，不是本次新增运行报告。

## 教学顺序

1. 解释BOLD与beta的区别，检查参数与清单。
2. 行为表确定每个trial对应的NSD图像ID。
3. 打开MGH，观察4维文件到“顶点×trial”的变化。
4. 固定抽样约512顶点/半球（实际511），合并左右半球。
5. 手算并执行每个session、每个顶点沿750 trial的z-score。
6. 按session顺序拼接4500 trial，过滤无效顶点。
7. 筛选200张教学图像对应349 trial，手算重复平均，再调用原函数。
8. 转置为“图像×有效顶点”的脑特征矩阵，检查真实图像/caption对齐。
9. 对照标准化、特征数量、重复汇总、仅保留三次重复的影响。
10. 解释caption语义向量及脑→语义回归；仅展示形状，不运行。

抽样只是降低教学内存，不是视觉ROI，不等于论文全脑复现。每个session用完整750 trial标准化，然后才筛选教学图像。改参数后从头执行，不能混用旧变量。未来正式训练还需审查标准化与训练/测试隔离。

## 在服务器查看与运行

使用Docker已有 `visuo_llm` Conda环境与同名Jupyter内核。打开上述仓库中的同一份notebook查看保存的输出；需要重跑时选择该内核并从第一格执行至末尾。只保存这份notebook，不另导出报告、npy或过程文件。可通过SSH直接读取单元格输出，不必复制日志给我。

```bash
cd /workspace/projects/visuo_llm
source /opt/conda/etc/profile.d/conda.sh
conda activate visuo_llm
which python
python --version
```

若更换数据路径，可设置 `NSD_TEACHING_DATA_DIR` 或修改第02节变量。不存在的文件会明确报错，不自动下载。依赖清单仅作参考，不批量升级服务器现有包。

## 文件与原函数对应

| 文件 | 用途 |
| --- | --- |
| `nsd_data_flow.ipynb` | 本教程、实际代码及单元格输出 |
| `download_data.py` | 现有数据的初始化、下载、续传、完整校验；本次不需要重新下载 |
| `requirements-core.txt` | 依赖参考，不是环境锁或自动安装要求 |
| `.gitignore` | 排除教学数据、缓存及大型输出 |

原项目 `src/nsd_visuo_semantics/utils/nsd_get_data_light.py`：

- `read_behavior`：按SESSION读trial表。
- `get_conditions` / `get_subject_conditions`：图像ID与重复筛选。
- `get_betas`：加载beta、左右合并、每session z-score。本教程将该分支拆开，先抽样再标准化；逐行独立，保留行的计算一致，避免全脑加载。
- `average_over_conditions`：按图像ID排序并平均重复。本教程真实调用它。
- `load_or_compute_betas_average`：原完整加载/平均/保存流程；本教程不调用，避免额外生成文件。

脑→语义：`src/nsd_visuo_semantics/encoding_decoding_analyses/nsd_decode_llm.py::nsd_decode_llm` 使用 `FracRidgeRegressorCV.fit/predict`，训练出映射后才能从脑特征预测语义。

文本模型：`src/nsd_visuo_semantics/get_embeddings/embedding_models_zoo.py::get_embedding_model/get_embeddings`；caption平均见 `encoding_decoding_analyses/encoding_decoding_utils.py::make_subj_conditional_nsd_embeddings`。

## 可选模型：只说明，不下载

通常 `SentenceTransformer("sentence-transformers/all-mpnet-base-v2")` 在缺少缓存时自动下载，然后 `model.encode(sentences)` 得到语义向量；也可使用已下载完整模型目录。安装模型库不等于已经拥有模型权重。

MiniLM输出384维，[单个权重90.9 MB](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/main/model.safetensors)，加配置/tokenizer约100 MB；MPNet输出768维，[单个权重438 MB](https://huggingface.co/sentence-transformers/all-mpnet-base-v2/blob/main/model.safetensors)，最小文件集约450 MB。完整仓库含多种格式时会更大。API无需本地权重，但需要网络服务、可能付费及隐私评估，本次不用。

TF-IDF不下载预训练权重，但生成词频特征，不能当作论文同一语义模型；PCA只是脑特征降维。理解当前脑数据流程不需要以上方法。

## 推荐阅读路线

README → notebook中的参数/清单 → 行为表 → beta读取 → session标准化 → trial对齐 → 重复平均 → 脑向量 → 最后的语义映射说明 → 原解码入口。

先认识样本和轴，再理解数值处理，最后理解监督学习，能避免把trial、图像ID、顶点、语义维度混为一谈。看完各单元格后，可以指定要深入的步骤或要比较的参数。
