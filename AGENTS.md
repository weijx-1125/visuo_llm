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

## Git topology

Expected remotes:

```text
origin
→ https://github.com/weijx-1125/visuo_llm.git

upstream
→ https://github.com/adriendoerig/visuo_llm.git
```

Meaning:

```text
origin
= user's GitHub fork

upstream
= original authors' repository
```

The local `main` branch on both the PC and server should normally track:

```text
origin/main
```

`upstream/main` is retained as the original-author reference branch and does not need to be updated unless explicitly requested.

Normal relationship:

```text
Original authors
adriendoerig/visuo_llm
        │
        │ upstream reference
        ▼
User development
        │
        │ origin
        ▼
weijx-1125/visuo_llm
```

Before important Git operations:

```bash
git status
git branch --show-current
git remote -v
```

Do not push to `upstream`.

Do not silently discard uncommitted changes.

Do not use destructive Git operations such as:

```bash
git reset --hard
git clean -fd
git push --force
```

unless explicitly requested.

---

## Development topology

There are four distinct layers:

```text
Local Windows PC
│
├── VS Code
├── Codex IDE extension
└── D:\Research\visuo_llm
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
        └── Docker environment
                │
                └── /workspace
```

The local and remote repositories are separate Git working copies.

A local file change does not automatically appear on the server.

A server-side file change does not automatically appear locally.

---

## Local PC

Local repository path:

```text
D:\Research\visuo_llm
```

Primary responsibilities:

- VS Code
- Codex
- source-code reading
- repository-wide search
- source-code modification
- Git diff review
- commits
- push to GitHub

The local computer does not need to contain the full datasets, model checkpoints, caches, or GPU runtime.

---

## Local-to-server access

The local Windows machine can directly access the remote research environment using:

```text
ssh weijx-153
```

Verified SSH behavior:

```text
Local:
D:\Research\visuo_llm

        │
        │ ssh weijx-153
        ▼

Remote:
hostname: weijx
user: root
initial directory: /root
```

The main server workspace is:

```text
/workspace
```

The project repository is:

```text
/workspace/projects/visuo_llm
```

Useful remote commands can be executed directly from the local machine, for example:

```bash
ssh weijx-153 "cd /workspace/projects/visuo_llm && git status"

ssh weijx-153 "ls -lah /workspace/results"

ssh weijx-153 "nvidia-smi"

ssh weijx-153 "cd /workspace/projects/visuo_llm && conda run -n visuo_llm python <script>"
```

Local Codex may use this existing SSH configuration to inspect and operate the remote environment when appropriate.

Use SSH primarily for:

- checking remote files
- inspecting datasets
- checking GPUs
- checking environment state
- running tests
- running training/evaluation
- reading logs
- reading experiment results
- inspecting checkpoints

---

## Source-code synchronization policy

There are two separate Git working copies:

```text
Local:
D:\Research\visuo_llm

Remote:
/workspace/projects/visuo_llm
```

Preferred ownership model:

```text
Local repository
→ primary place for Codex source-code edits

Remote repository
→ primary place for execution and experiments
```

Normal source-code flow:

```text
Local Codex edits
→ inspect git diff
→ commit
→ push origin
→ GitHub
→ server pull
→ execute remotely
```

Codex may automate remote `git pull`, inspection, testing, and execution through SSH.

Avoid independently editing the same source files in both local and remote working copies unless explicitly required.

Server-side datasets, checkpoints, logs, caches, and experiment results do not need to pass through Git.

---

## Remote server and Docker environment

Known remote environment:

```text
SSH target:        weijx-153
hostname:          weijx
user:              root
workspace root:    /workspace
repository:        /workspace/projects/visuo_llm
```

A shell such as:

```text
root@weijx:/workspace#
```

is inside the intended research environment.

Useful context checks:

```bash
hostname
whoami
pwd
test -f /.dockerenv && echo "Inside Docker"
```

Do not confuse the server host operating system with the intended research runtime.

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
→ Hugging Face, PyTorch, pip, matplotlib, and related caches

/workspace/config
→ server/workspace-level configuration

/workspace/scripts
→ server utility scripts

/workspace/tmp
→ temporary files
```

Do not move large research artifacts into the Git repository unless there is a clear reason.

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

Known environments:

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

Activate before interactive project execution:

```bash
conda activate visuo_llm
```

A fresh shell may have no active Conda environment and may not expose `python` in `PATH`.

After activation:

```text
Python 3.10.21
```

Before project execution:

```bash
conda activate visuo_llm
which python
python --version
```

For one-off remote commands, `conda run` is also appropriate:

```bash
conda run -n visuo_llm python <script>
```

Do not install a separate system Python merely because `python` is unavailable before Conda activation.

---

## Project installation

The repository contains:

```text
pyproject.toml
setup.cfg
```

The project package is installed in editable mode:

```text
nsd-visuo-semantics
1.1.dev3+ga60e0eafb

editable source:
/workspace/projects/visuo_llm
```

Therefore source-code changes in the repository are intended to be directly visible to the active environment unless package metadata or dependency definitions change.

Before changing dependencies, inspect:

```text
pyproject.toml
setup.cfg
README.md
```

Do not blindly use system-wide package installation.

---

## Core Python environment

Known important versions:

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

Do not casually upgrade core scientific or ML dependencies.

Dependency changes can affect experiment reproducibility.

---

## CUDA and GPUs

Available GPUs:

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

`nvidia-smi` reports:

```text
CUDA 13.0
```

Installed PyTorch build:

```text
torch 2.5.1+cu124
```

Relevant CUDA runtime packages are based on CUDA 12.4.

Important distinction:

```text
nvidia-smi CUDA 13.0
→ CUDA capability supported by the installed NVIDIA driver

PyTorch +cu124
→ current PyTorch build uses CUDA 12.4 runtime
```

Do not reinstall PyTorch merely because these two version numbers differ.

GPU-heavy execution should happen remotely.

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

determine whether the change is actually required.

If dependency changes are necessary:

1. record the previous version;
2. record the new version;
3. state why the change is needed;
4. consider reproducibility impact.

---

## Codex execution model

Codex is primarily used on the local Windows PC through the VS Code Codex extension.

Local Codex authentication is functional.

Remote Codex authentication previously failed because of regional service availability.

Therefore use:

```text
Local Codex
D:\Research\visuo_llm
        │
        ├── read/edit local source code
        ├── Git operations
        └── SSH commands
                ↓
        ssh weijx-153
                ↓
        /workspace
                ↓
        datasets / checkpoints / logs / results / GPU runtime
```

Local Codex may directly use SSH to inspect server state and execute approved remote commands.

Do not attempt to bypass regional authentication restrictions on the remote system.

Before remote destructive or expensive actions, inspect the target first.

Do not unintentionally:

- delete datasets
- delete checkpoints
- overwrite results
- modify system-wide environments
- launch expensive training runs

For long-running GPU experiments, prefer persistent remote execution such as `tmux`.

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
→ training / loss
→ evaluation
```

For important findings, reference concrete:

- file paths
- functions
- classes
- configuration values

For model/data code, include tensor shapes when reliably inferable.

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
6. run appropriate validation when possible;
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
Codex or user triggers server pull through SSH
        ↓
conda environment
        ↓
remote GPU execution
        ↓
/workspace/results and /workspace/logs
        ↓
Codex inspects results through SSH
        ↓
next source-code iteration
```

Source code moves through Git.

Datasets, checkpoints, caches, logs, and large experiment artifacts remain on server storage.

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
