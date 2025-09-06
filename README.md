<p align="center">
  <img src="img/modelsynic.png" alt="ModelSync logo" width="200"/>
</p>

<h1 align="center">🧠 ModelSync</h1>
<p align="center">
  A modern versioning system for Artificial Intelligence projects.
</p>

---

## 🚀 Overview

**ModelSync** is a distributed version control tool inspired by Git, but entirely focused on the Artificial Intelligence ecosystem.

While Git is great for versioning code, it fails when dealing with:
- 🗂️ Large datasets
- 🧠 Trained models (binaries)
- 🧪 Experiments with multiple parameters
- 📈 Performance metrics and comparisons

The goal of **ModelSync** is to fill this gap, offering a data and experiment-oriented versioning environment.

---

## 🧰 Technologies Used

| Component | Technology |
|-----------|-------------|
| CLI       | [Typer](https://github.com/tiangolo/typer) |
| API       | [FastAPI](https://fastapi.tiangolo.com) |
| Server    | [Uvicorn](https://www.uvicorn.org/) |
| Git       | [GitPython](https://gitpython.readthedocs.io/) |
| Data      | [Pandas](https://pandas.pydata.org/) |
| Container | [Docker](https://www.docker.com/) |

---

## ⚙️ MVP Features

- `modelsync init` → Initializes a `.modelsync/` repository
- `modelsync commit -m "message"` → Saves a snapshot with metadata
- Simple versioning with file hashing
- Basic API for queries and external interactions

---

## 📦 How to Use

### ✅ Prerequisites

- Python 3.10+
- Linux, macOS or Windows (WSL recommended)

### 🔧 Installation

```bash
git clone https://github.com/your-username/modelsync.git
cd modelsync
pip install -r requirements.txt
```

### 🧪 CLI Usage

```bash
# Initialize ModelSync repository
python modelsync/cli/main.py init

# Create a commit with message
python modelsync/cli/main.py commit -m "Model with 92% accuracy"
```

---

## 📋 Basic Commands Reference

### **Core Commands**
| Command | Description |
|---------|-------------|
| `modelsync init` | Creates a new ModelSync repository |
| `modelsync status` | Shows the status of tracked files and changes |
| `modelsync add [file]` | Adds a file to the staging area |
| `modelsync add .` | Adds all files to the staging area |
| `modelsync commit -m "[message]"` | Saves changes with a descriptive message |
| `modelsync log` | Shows commit history |
| `modelsync log --oneline` | Shows commit history in one line per commit |
| `modelsync diff` | Shows differences between working directory and staging area |

### **AI-Specific Commands**
| Command | Description |
|---------|-------------|
| `modelsync dataset add ./data.csv --name "Training Data"` | Add dataset to version control |
| `modelsync model add model.pkl --framework sklearn --metrics '{"accuracy": 0.95}'` | Add model to version control |
| `modelsync experiment create feature_engineering` | Create experiment branch |
| `modelsync llm start` | Start vLLM API server |
| `modelsync llm generate --prompt "Hello world"` | Generate text with vLLM |
| `modelsync llm_status` | Check vLLM service status |
| `modelsync web` | Start web interface |

### **Advanced Commands**
| Command | Description |
|---------|-------------|
| `modelsync restore [file]` | Discards changes in a file |
| `modelsync reset [file]` | Unstages a file from the staging area |
| `modelsync branch [name]` | Creates a new branch for experiments |
| `modelsync checkout [branch]` | Switches to another branch |
| `modelsync merge [branch]` | Merges changes from a branch |
| `modelsync remote add [name] [url]` | Adds a remote repository |
| `modelsync push` | Uploads changes to remote repository |
| `modelsync pull` | Downloads updates from remote repository |
| `modelsync clone [url]` | Clones a remote ModelSync repository |
