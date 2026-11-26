# CobRecon - Motor de Conciliação de Dados

## 🚀 Visão Geral

O **CobRecon** é um motor avançado de conciliação automática de registros, desenvolvido para resolver o desafio empresarial de informações divergentes entre sistemas legados (COBOL) e plataformas modernas. Nossa solução bridges the gap entre tecnologias antigas e novas, garantindo consistência operacional.

## 🛠️ Stack Tecnológica

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/COBOL-5A5A5A?style=for-the-badge" alt="COBOL">

## ✨ Funcionalidades Principais

- **📊 Comparação de Arquivos e Bases de Dados**: Conciliação entre arquivos COBOL legados e bancos de dados modernos
- **🔍 Identificação de Registros Divergentes**: Detecção inteligente de inconsistências entre conjuntos de dados
- **🔢 Detecção de Registros Duplicados**: Remoção e flagging de duplicatas dentro e entre fontes
- **⚙️ Regras Personalizadas de Conciliação**: Sistema flexível para definir regras de match e exceções
- **🚀 Processamento de Grandes Volumes**: Otimizado para handlear arquivos e bancos de dados de escala enterprise
- **📈 Relatórios de Inconsistências**: Relatórios detalhados em formato estruturado com insights acionáveis
- **📤 Exportação em CSV e JSON**: Formatos de saída padronizados para integração com qualquer sistema
- **📦 Pacote Completo**: Estrutura pronta para publicação em repositório

## 📁 Estrutura do Projeto

```
CobRecon/
├── docker/              # Configurações Docker para deployment
├── data/                # Dados de exemplo e templates
├── src/                 # Código-fonte Python (motor de conciliação)
│   ├── engine.py        # Motor principal de conciliação
│   ├── comparator.py    # Comparador de registros
│   ├── detector.py      # Detetor de duplicatas
│   ├── rules.py         # Sistema de regras personalizadas
│   ├── reporter.py      # Gerador de relatórios
│   ├── exporter.py      # Exportador CSV/JSON
│   └── cobol_reader.py  # Leitor de arquivos COBOL
├── tests/               # Testes unitários e de integração
├── .github/             # Configurações GitHub (CI/CD)
├── requirements.txt     # Dependências Python
├── Dockerfile           # Imagem Docker otimizada
└── README.md            # Esta documentação
```

## ⚡ Quick Start

### Via Docker (Recomendado)

```bash
# Build da imagem
docker build -t cobrecon .

# Rodar o motor
docker run -v $(pwd)/data:/app/data cobrecon
```

### Via Python Direto

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o motor
python -m src.engine --help
```

## 📸 Funcionamento Visual

*( prints e GIFs ilustrando o fluxo de conciliação serão inseridos aqui )*

### Exemplo de Fluxo de Trabalho

1. **Upload/Leitura**: Carregar arquivos COBOL ou bases SQLite
2. **Comparação**: Motor analisa divergências entre datasets
3. **Classificação**: Identifica registros: iguais, divergentes, duplicados
4. **Regras**: Aplica regras personalizadas de negócio
5. **Relatório**: Gera relatório detalhado de inconsistências
6. **Export**: Exporta dados limpos em CSV/JSON

## 🎯 Casos de Uso

- Migração de dados legados para cloud
- Reconciliação entre sistemas financeiros
- Unificação de cadastros clientes
- Auditoria e compliance de dados
- Integração de sistemas enterprise

## 📄 Licença

MIT

---

*Desenvolvido com ❤️ usando Python, SQLite, Docker e COBOL*