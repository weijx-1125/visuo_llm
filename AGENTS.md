# AGENTS.md

## Project

This repository is the user's working fork of the code associated with:

**High-level visual representations in the human brain are aligned with large language models**

Original repository:

`https://github.com/adriendoerig/visuo_llm`

User fork:

`https://github.com/weijx-1125/visuo_llm`

Primary workflow:

1. Understand the original implementation.
2. Reproduce the original experiments.
3. Establish paper-to-code correspondence.
4. Make controlled research modifications.
5. Keep all changes reproducible and traceable.

Prefer minimal modifications over broad refactoring.

---

---

## Git topology

Expected remotes:

```text
origin
→ https://github.com/weijx-1125/visuo_llm.git

upstream
→ https://github.com/adriendoerig/visuo_llm.git
```

The local `<span>main</span>` branch on both the PC and server should normally track:

```text
origin/main
```

`<span>upstream/main</span>` is only the reference branch for updates from the original authors.

Normal flow:

```text
Original authors
upstream/main
     ↓
user reviews/syncs updates when needed

Local PC
D:\Research\visuo_llm
     ↓ push

origin/main
weijx-1125/visuo_llm
     ↓ pull

Server Docker
/workspace/projects/visuo_llm
```


## Development topology

There are four distinct layers:

```text
Local PC
│
├── VS Code
├── Codex IDE extension
└── local visuo_llm Git working copy
        │
        │ Git
        ▼
GitHub
weijx-1125/visuo_llm
        │
        │ Git
        ▼
Remote server
        │
        └── Docker container: weijx
                │
                └── /workspace
```

These are not assumed to share a live filesystem.

A modification on the local PC does not automatically appear on the server.

Normal source-code synchronization is:

```text
local edit
→ git commit
→ git push origin
→ GitHub
→ git pull/fetch on server
```

Large datasets, checkpoints and experiment outputs should not be synchronized through normal Git commits.

---

## Local PC

Local repository path:

```text
D:\Research\visuo_llm
```

Primary responsibilities:

* VS Code
* Codex
* source-code reading and modification
* Git diff review
* commits
* push to GitHub

Path relationship:

```text
Local:
D:\Research\visuo_llm

GitHub:
https://github.com/weijx-1125/visuo_llm

Server Docker:
/workspace/projects/visuo_llm
```

These are separate Git working copies. Source-code changes are synchronized through Git, not through a shared filesystem.

## Remote server and Docker

VS Code connects to the remote machine through SSH.

Known SSH target:

```text
weijx-153
```

The research runtime is inside Docker.

Known container state:

```text
container hostname: weijx
container user:     root
workspace root:     /workspace
repository:         /workspace/projects/visuo_llm
```

A shell such as:

```text
root@weijx:/workspace#
```

is inside the intended Docker container.

Useful execution-context checks:

```bash
hostname
whoami
pwd
test -f /.dockerenv && echo "Inside Docker"
```

Do not confuse the server host operating system with the Docker runtime.

---

## Workspace layout

Actual workspace layout:

```text
/workspace/
├── cache/
│   ├── huggingface/
│   ├── matplotlib/
│   ├── pip/
│   └── torch/
│
├── checkpoints/
├── config/
│   └── server/
│
├── datasets/
├── logs/
├── projects/
│   └── visuo_llm/
│
├── results/
├── scripts/
└── tmp/
```

Directory responsibilities:

```text
/workspace/projects/visuo_llm
→ Git-managed project source

/workspace/datasets
→ research datasets

/workspace/checkpoints
→ model checkpoints and downloaded weights

/workspace/results
→ experiment results and generated outputs

/workspace/logs
→ runtime and experiment logs

/workspace/cache
→ shared caches for Hugging Face, PyTorch, pip, matplotlib, etc.

/workspace/config
→ server/workspace-level configuration

/workspace/scripts
→ server/workspace utility scripts

/workspace/tmp
→ temporary files
```

Do not move large research artifacts into the Git repository without a clear reason.

---

## Path relationship

The same source repository exists in multiple places:

```text
Local PC
<local-path>/visuo_llm
        │
        │ Git synchronization
        ▼
GitHub
weijx-1125/visuo_llm
        │
        │ Git synchronization
        ▼
Docker
/workspace/projects/visuo_llm
```

The Git repository should contain source code, configuration, scripts and documentation.

Large runtime artifacts belong under `/workspace`, outside the repository whenever practical.

---

## Conda environment

Conda installation:

```text
/opt/conda
```

Conda executable:

```text
/opt/conda/condabin/conda
```

Known Conda environments:

```text
base
→ /opt/conda

visuo_llm
→ /opt/conda/envs/visuo_llm
```

The intended project environment is:

```text
visuo_llm
```

Activate it before project execution:

```bash
conda activate visuo_llm
```

Do not assume the environment is automatically active in a fresh shell.

A fresh shell may have:

```text
CONDA_DEFAULT_ENV=
python not found in PATH
```

This is expected until the project environment is activated.

After activation:

```text
Python 3.10.21
```

Before running project code, verify:

```bash
conda activate visuo_llm
which python
python --version
```

Do not install a separate system Python merely because `python` is unavailable before Conda activation.

---

## Project installation

The repository contains:

```text
pyproject.toml
setup.cfg
```

The project package is currently installed as an editable package:

```text
nsd-visuo-semantics
1.1.dev3+ga60e0eafb

editable source:
 /workspace/projects/visuo_llm
```

Therefore, changes made to the repository source are intended to be directly visible to the active environment without repeatedly reinstalling the package, unless package metadata or dependencies change.

Before changing dependency installation, inspect:

```text
pyproject.toml
setup.cfg
README
```

and existing environment state.

Do not blindly run global `pip install` or `apt install python`.

---

## Core Python environment

Known important package versions in `visuo_llm`:

```text
Python                  3.10.21

torch                   2.5.1+cu124
torchvision             0.20.1+cu124
torchaudio              2.5.1+cu124
triton                  3.1.0

numpy                   1.26.4
scipy                   1.15.3
pandas                  2.3.3
scikit-learn            1.7.2
scikit-image            0.25.2

transformers            5.18.0
sentence-transformers   6.1.0
huggingface-hub         1.33.0
timm                    1.0.30
clip                    1.0

tensorflow              2.15.0
tensorflow-hub          0.16.1
tensorflow-probability  0.23.0
keras                   2.15.0
tf-keras                2.15.0

nibabel                 5.4.2
nilearn                 0.14.1
cifti                   1.1

nsd-access              0.0.1.dev0
nsdcode                 1.0.0
fracridge               2.0

matplotlib              3.10.9
tensorboard             2.15.2
```

Do not upgrade core scientific or ML dependencies casually.

Dependency changes can alter experiment behavior and should be treated as reproducibility-affecting changes.

---

## CUDA and GPUs

Server GPUs:

```text
GPU 0: NVIDIA GeForce RTX 4090
GPU 1: NVIDIA GeForce RTX 4090
```

Each GPU has approximately:

```text
24 GB VRAM
```

NVIDIA driver:

```text
580.178.04
```

`nvidia-smi` reports host-supported CUDA:

```text
CUDA 13.0
```

The installed PyTorch build is:

```text
torch 2.5.1+cu124
```

with CUDA 12.4 runtime packages such as:

```text
nvidia-cuda-runtime-cu12  12.4.127
nvidia-cublas-cu12        12.4.5.8
nvidia-cudnn-cu12         9.1.0.70
nvidia-nccl-cu12          2.21.5
```

Important distinction:

```text
nvidia-smi CUDA 13.0
→ maximum CUDA compatibility reported by the installed NVIDIA driver

PyTorch +cu124
→ current PyTorch runtime is built for CUDA 12.4
```

Do not attempt to reinstall PyTorch solely because these two version numbers differ.

GPU-heavy execution should happen inside the Docker `visuo_llm` environment.

---

## Environment modification rules

Before changing packages:

```bash
conda activate visuo_llm

which python
python --version

pip show <package>
conda list <package>
```

Before upgrading major packages such as:

```text
torch
tensorflow
transformers
numpy
scipy
scikit-learn
```

determine whether the change is required by the repository or experiment.

Avoid casual environment upgrades.

If dependency changes are necessary:

1. record the previous version;
2. record the new version;
3. state why the change is required;
4. consider its impact on reproducibility;
5. update project environment documentation when appropriate.

---

## Codex usage

Codex is primarily used on the local PC through the VS Code Codex extension.

Local Codex authentication is functional.

The Codex extension running through the remote SSH environment previously failed authentication because of regional service availability.

Therefore use:

```text
Local VS Code + Codex
→ repository analysis and source modification

Remote Docker environment
→ execution, testing, training, evaluation
```

Do not attempt to bypass regional authentication restrictions on the server.

---

## Repository analysis

When analyzing unfamiliar code, prefer tracing actual execution paths.

Recommended order:

```text
README / documentation
→ execution entry point
→ configuration
→ dataset loading
→ preprocessing
→ model construction
→ forward pass
→ training/loss
→ evaluation
```

For important findings, reference concrete:

- file paths
- functions
- classes
- configuration values

For model/data code, include tensor shapes when they can be reliably determined.

Distinguish repository-defined logic from third-party library behavior.

---

## Modification rules

Before modifying source code:

```bash
git status
git branch --show-current
```

Then:

1. inspect the existing implementation;
2. identify the smallest relevant file set;
3. make minimal changes;
4. avoid unrelated refactoring;
5. inspect the resulting Git diff;
6. run appropriate validation where possible;
7. report what was and was not tested.

Substantial research modifications should normally use a dedicated branch.

Examples:

```text
experiment/<name>
feature/<name>
fix/<name>
```

Never silently delete or overwrite:

- datasets
- checkpoints
- results
- logs
- existing user changes

---

## Research reproducibility

When modifying:

- model architecture
- training behavior
- preprocessing
- dataset handling
- loss functions
- evaluation

identify:

1. original behavior;
2. modified behavior;
3. scientific reason;
4. affected hyperparameters;
5. expected consequences;
6. checkpoint compatibility;
7. comparability with baseline results.

Do not silently alter experiment-critical defaults.

---

## Git and large files

Git should normally track:

```text
source code
configuration files
scripts
documentation
small metadata files
```

Git should normally not track:

```text
datasets
large model weights
checkpoints
large experiment results
cache directories
temporary files
credentials
```

Never commit:

- passwords
- API keys
- access tokens
- SSH private keys
- other credentials

---

## Normal workflow

Expected development cycle:

```text
Local VS Code + Codex
        ↓
analyze / modify source
        ↓
git diff
        ↓
commit
        ↓
push origin
        ↓
GitHub fork
        ↓
server pull/fetch
        ↓
conda activate visuo_llm
        ↓
Docker GPU execution
        ↓
/workspace/results and /workspace/logs
        ↓
analyze experiment
        ↓
next source-code iteration
```

Source code moves through Git.

Datasets, checkpoints, caches and large experiment artifacts remain on the server/workspace storage.

---

## Documentation

Keep `AGENTS.md` focused on stable infrastructure and operating rules.

Detailed project knowledge should eventually live in:

```text
docs/
├── architecture.md
├── environment.md
├── paper_code_mapping.md
└── experiments.md
```

Use `AGENTS.md` as the stable entry point rather than turning it into an experiment diary.
