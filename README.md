# Coletor de Artigos do Medium - UX + Inteligência Artificial (2025)

## 📋 Descrição

Ferramenta em Python para coleta automatizada de artigos do Medium relacionados a **UX Design** e **Inteligência Artificial**, publicados no ano de **2025**.

O projeto foi desenvolvido para apoiar pesquisas de referências em UX/UI, automatizando a coleta e organização de conteúdos relevantes.

## 🎯 Objetivo

- Coletar links de artigos do Medium a partir de páginas de _tag_
- Extrair metadados relevantes de cada artigo
- Aplicar filtro de cruzamento de tags (regra AND)
- Exportar dados finais em JSON e CSV

## 📁 Estrutura do Projeto

```
article_scrapper/
│
├── main.py          # Script principal - orquestra o pipeline
├── collector.py     # Coleta de links via Playwright
├── parser.py        # Extração de metadados (JSON-LD/HTML)
├── storage.py       # Persistência em JSON e CSV
│
├── data/
│   ├── raw_links_ux-design.json
│   ├── raw_links_artificial-intelligence.json
│   ├── artigos_filtrados_2025.json
│   └── artigos_filtrados_2025.csv
│
├── requirements.txt
└── README.md
```

## 🛠️ Instalação

### 1. Criar e ativar ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Instalar navegadores do Playwright

```bash
playwright install chromium
```

## 🚀 Uso

### Executar pipeline completo

```bash
python main.py
```

### Executar etapas individuais

```bash
# Apenas coleta de links
python main.py --collect

# Apenas extração de metadados
python main.py --parse

# Apenas filtragem e exportação
python main.py --filter
```

### Executar com navegador visível (debug)

```bash
python main.py --headful
```

## 📊 Estrutura dos Dados

Cada artigo é representado com a seguinte estrutura:

```json
{
  "titulo": "Título do artigo",
  "autor": "Nome do autor",
  "data_publicacao": "2025-01-15",
  "tags": ["ux-design", "artificial-intelligence", "..."],
  "tempo_leitura": "5 min read",
  "resumo": "Descrição ou resumo do artigo...",
  "fonte": "medium",
  "url": "https://medium.com/..."
}
```

## ⚙️ Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     ETAPA 1: COLETA                         │
│  • Acessa páginas de tag do Medium                          │
│  • Realiza scroll para carregar conteúdo dinâmico           │
│  • Extrai URLs de artigos de 2025                           │
│  • Salva em: data/raw_links_<tag>.json                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 ETAPA 2: EXTRAÇÃO                           │
│  • Visita cada URL coletada                                 │
│  • Extrai metadados via JSON-LD (Schema.org)                │
│  • Fallback para HTML quando necessário                     │
│  • Salva em: data/artigos_raw_2025.json                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 ETAPA 3: FILTRAGEM                          │
│  • Filtra por ano de publicação (2025)                      │
│  • Filtra por presença de AMBAS as tags (AND)               │
│  • Exporta JSON e CSV finais                                │
│  • Salva em: data/artigos_filtrados_2025.{json,csv}         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuração

As configurações principais estão no arquivo `main.py`:

```python
CONFIG = {
    "tags": ["ux-design", "artificial-intelligence"],
    "ano": 2025,
    "headless": True
}
```

## 📝 Critérios de Filtro

Um artigo é incluído no corpus final apenas se:

- ✅ Foi publicado em **2025**
- ✅ Contém **simultaneamente** as tags:
  - `ux-design`
  - `artificial-intelligence`

## ⚠️ Limitações

- O projeto coleta apenas **metadados**, não o texto completo dos artigos
- Depende da estrutura atual do Medium (pode quebrar com atualizações)
- A coleta pode demorar dependendo da quantidade de artigos
- Respeite os termos de uso do Medium

## 🧪 Desenvolvimento

### Testar coleta de um artigo específico

```python
from parser import run_parser

metadata = run_parser("https://medium.com/artigo-exemplo")
print(metadata)
```

### Testar coleta de links de uma tag

```python
from collector import run_collector

links = run_collector("ux-design", headless=False)
print(f"Coletados {len(links)} links")
```

## 📄 Licença

Este projeto é para fins educacionais e de pesquisa.

---

Desenvolvido para apoio à pesquisa em UX Design 🎨 + IA 🤖
