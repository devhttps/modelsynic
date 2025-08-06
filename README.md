<p align="center">
  <img src="img/modelsynic.png" alt="ModelSync logo" width="200"/>
</p>

<h1 align="center">🧠 ModelSync</h1>
<p align="center">
  Um sistema de versionamento moderno para projetos de Inteligência Artificial.
</p>

---

## 🚀 Visão Geral

**ModelSync** é uma ferramenta de controle de versão distribuído, inspirada no Git, mas totalmente voltada para o ecossistema de Inteligência Artificial.

Enquanto o Git é ótimo para versionar código, ele falha quando lidamos com:
- 🗂️ Datasets grandes
- 🧠 Modelos treinados (binários)
- 🧪 Experimentos com múltiplos parâmetros
- 📈 Métricas de desempenho e comparações

O objetivo do **ModelSync** é preencher essa lacuna, oferecendo um ambiente de versionamento orientado a dados e experimentos.

---

## 🧰 Tecnologias Utilizadas

| Componente | Tecnologia |
|-----------|-------------|
| CLI       | [Typer](https://github.com/tiangolo/typer) |
| API       | [FastAPI](https://fastapi.tiangolo.com) |
| Server    | [Uvicorn](https://www.uvicorn.org/) |
| Git       | [GitPython](https://gitpython.readthedocs.io/) |
| Dados     | [Pandas](https://pandas.pydata.org/) |
| Container | [Docker](https://www.docker.com/) |

---

## ⚙️ Funcionalidades do MVP

- `modelsync init` → Inicializa um repositório `.modelsync/`
- `modelsync commit -m "mensagem"` → Salva um snapshot com metadados
- Versionamento simples com hash dos arquivos
- API básica para consultas e interações externas

---

## 📦 Como Usar

### ✅ Pré-requisitos

- Python 3.10+
- Linux, macOS ou Windows (WSL recomendado)

### 🔧 Instalação

```bash
git clone https://github.com/seu-usuario/modelsync.git
cd modelsync
pip install -r requirements.txt

