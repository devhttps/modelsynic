# ModelSync Architecture

## 🏗️ Visão Geral da Arquitetura

O ModelSync foi projetado como um sistema de versionamento distribuído focado em projetos de IA, inspirado no Git mas otimizado para o ecossistema de machine learning.

## 📁 Estrutura do Projeto

```
modelsync/
├── __init__.py                 # Inicialização do pacote
├── config.py                   # Configurações globais
├── cli/                        # Interface de linha de comando
│   └── main.py                 # CLI principal com Typer
├── core/                       # Funcionalidades principais
│   ├── __init__.py
│   └── versioning.py           # Sistema de versionamento
├── api/                        # API REST
│   └── main.py                 # FastAPI application
├── metadata/                   # Gerenciamento de metadados
│   ├── __init__.py
│   └── model_metadata.py       # Metadados de modelos e datasets
└── utils/                      # Utilitários
    ├── __init__.py
    ├── helpers.py              # Funções auxiliares
    └── logger.py               # Sistema de logging
```

## 🔧 Componentes Principais

### 1. Sistema de Versionamento (`core/versioning.py`)

**Classe Principal:** `ModelSyncRepo`

**Funcionalidades:**
- Inicialização de repositórios
- Sistema de staging (área de preparação)
- Criação de commits com hash SHA-256
- Rastreamento de arquivos modificados
- Histórico de commits
- Estrutura de diretórios similar ao Git

**Estrutura de Dados:**
```json
{
  "tree": "hash_do_tree_object",
  "parent": "hash_do_commit_pai",
  "author": {
    "name": "Nome do Autor",
    "email": "email@exemplo.com",
    "timestamp": "2024-01-01T12:00:00"
  },
  "committer": {
    "name": "Nome do Committer",
    "email": "email@exemplo.com", 
    "timestamp": "2024-01-01T12:00:00"
  },
  "message": "Mensagem do commit",
  "hash": "hash_sha256_do_commit"
}
```

### 2. Interface de Linha de Comando (`cli/main.py`)

**Tecnologia:** Typer

**Comandos Implementados:**
- `init` - Inicializar repositório
- `add` - Adicionar arquivos ao staging
- `commit` - Criar commit
- `status` - Mostrar status do repositório
- `log` - Mostrar histórico de commits
- `diff` - Mostrar diferenças
- `restore` - Restaurar arquivo (placeholder)
- `reset` - Remover do staging (placeholder)
- `branch` - Gerenciar branches (placeholder)
- `checkout` - Trocar branch (placeholder)
- `merge` - Fazer merge (placeholder)
- `remote` - Gerenciar repositórios remotos (placeholder)
- `push` - Enviar para remoto (placeholder)
- `pull` - Baixar do remoto (placeholder)
- `clone` - Clonar repositório (placeholder)

### 3. API REST (`api/main.py`)

**Tecnologia:** FastAPI

**Endpoints Implementados:**
- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /init` - Inicializar repositório
- `GET /status` - Status do repositório
- `POST /add` - Adicionar arquivos
- `POST /commit` - Criar commit
- `GET /log` - Histórico de commits
- `GET /branches` - Listar branches (placeholder)
- `GET /diff` - Diferenças de arquivos
- `GET /config` - Configuração (placeholder)

### 4. Sistema de Metadados (`metadata/model_metadata.py`)

**Classes:**
- `ModelMetadata` - Metadados de modelos ML
- `DatasetMetadata` - Metadados de datasets

**Funcionalidades:**
- Criação de metadados para modelos e datasets
- Armazenamento de métricas de performance
- Rastreamento de hiperparâmetros
- Informações de treinamento
- Versionamento de metadados

### 5. Utilitários (`utils/`)

**helpers.py:**
- Cálculo de hash SHA-256
- Manipulação de arquivos
- Formatação de dados
- Operações de diretório

**logger.py:**
- Sistema de logging configurável
- Suporte a console e arquivo
- Diferentes níveis de log

## 🗂️ Estrutura de Repositório

```
projeto/
├── .modelsync/                 # Diretório do ModelSync
│   ├── config                  # Configuração do repositório
│   ├── HEAD                    # Referência para branch atual
│   ├── index                   # Área de staging
│   ├── objects/                # Objetos do repositório
│   │   └── [hash]/[hash]       # Commits e trees
│   ├── refs/                   # Referências
│   │   └── heads/              # Branches locais
│   ├── metadata/               # Metadados
│   │   ├── models/             # Metadados de modelos
│   │   └── datasets/           # Metadados de datasets
│   └── logs/                   # Logs do sistema
│       └── history.log         # Histórico de ações
└── [arquivos do projeto]       # Arquivos versionados
```

## 🔄 Fluxo de Trabalho

### 1. Inicialização
```bash
modelsync init --name "Usuário" --email "user@example.com"
```

### 2. Adicionar Arquivos
```bash
modelsync add arquivo1.py arquivo2.json
```

### 3. Fazer Commit
```bash
modelsync commit -m "Mensagem do commit"
```

### 4. Verificar Status
```bash
modelsync status
```

### 5. Ver Histórico
```bash
modelsync log
modelsync log --oneline
```

## 🧪 Testes

**Framework:** pytest

**Cobertura:**
- Inicialização de repositório
- Adição de arquivos
- Criação de commits
- Verificação de status
- Histórico de commits

**Executar Testes:**
```bash
python run_tests.py
```

## 🐳 Containerização

**Dockerfile:**
- Base: Python 3.10-slim
- Usuário não-root
- Porta 8000 exposta
- Otimizado para produção

**Docker Compose:**
- Serviço de API
- Serviço de CLI
- Volumes persistentes

## 🚀 Deploy e Desenvolvimento

### Desenvolvimento Local
```bash
# Setup inicial
python scripts/dev_setup.py

# Iniciar API
python scripts/start_api.py

# Usar CLI
python modelsync/cli/main.py --help
```

### Docker
```bash
# Build da imagem
docker build -t modelsync .

# Executar API
docker run -p 8000:8000 modelsync python modelsync/api/main.py

# Executar CLI
docker run -v $(pwd):/workspace modelsync python modelsync/cli/main.py init
```

## 🔮 Roadmap

### Funcionalidades Pendentes
- [ ] Sistema de branching completo
- [ ] Merge de branches
- [ ] Repositórios remotos
- [ ] Push/Pull
- [ ] Clone de repositórios
- [ ] Sistema de tags
- [ ] Interface web
- [ ] Integração com MLflow
- [ ] Suporte a DVC
- [ ] Backup automático

### Melhorias Planejadas
- [ ] Otimização de performance
- [ ] Compressão de objetos
- [ ] Cache inteligente
- [ ] Paralelização de operações
- [ ] Interface gráfica
- [ ] Plugins para IDEs
- [ ] Integração com CI/CD

## 📊 Métricas e Monitoramento

- Logs estruturados em JSON
- Métricas de performance
- Rastreamento de operações
- Health checks da API
- Monitoramento de uso de disco

## 🔒 Segurança

- Validação de entrada
- Sanitização de paths
- Controle de acesso (futuro)
- Criptografia de metadados (futuro)
- Auditoria de operações
