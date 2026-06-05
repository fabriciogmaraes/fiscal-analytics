# Fiscal Analytics

> 🚧 Em construção / Work in Progress

Aplicação web de gestão financeira pessoal com orçamento diário dinâmico.
Acesse pelo PC ou celular via navegador — sem instalar nada.

---

## Stack

Python 3.13 · FastAPI · SQLite · SQLAlchemy · HTML/CSS/JS

---

## Funcionalidades

- Cadastro de receitas fixas e despesas fixas
- Gestão de dívidas com controle de parcelas e projeção de quitação
- Lançamento de gastos variáveis (incluindo cartão de crédito)
- Orçamento diário dinâmico — redistribui o saldo pelos dias restantes do mês automaticamente
- Visão de dívida total e compromissos futuros
- Semáforo financeiro: verde / amarelo / vermelho
- Acesso via PC e celular na mesma rede

---

## Estrutura

```text
fiscal/
├── backend/
│   ├── main.py          # FastAPI — rotas da API
│   ├── database.py      # SQLite — modelos e conexão
│   ├── models.py        # Schemas Pydantic
│   └── calculos.py      # Lógica de orçamento dinâmico
├── frontend/
│   ├── index.html       # Dashboard principal
│   ├── dividas.html     # Gestão de dívidas
│   ├── gastos.html      # Lançar gastos
│   └── config.html      # Receitas e despesas fixas
├── requirements.txt
└── README.md
```

---

## Como rodar

**1. Clone o repositório**

**2. Crie e ative o ambiente virtual**

    python -m venv .venv
    .venv\Scripts\activate

**3. Instale as dependências**

    pip install -r requirements.txt

**4. Suba o servidor**

    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

**5. Acesse no navegador**

    PC:      http://localhost:8000
    Celular: http://SEU_IP_LOCAL:8000

Para descobrir seu IP local: `ipconfig` no terminal Windows, campo **Endereço IPv4**.

---

## Autor

Fabricio Guimarães — Analista de Dados · Mestrando em Inteligência Computacional (PPgTI/UFRN)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fabriciogmaraes)