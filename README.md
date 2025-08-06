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
