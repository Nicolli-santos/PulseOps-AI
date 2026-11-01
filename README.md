
# PulseOps AI

Sistema de análise e previsão de risco de atraso em entregas, desenvolvido como projeto de estudo e portfólio.

## Sobre o projeto

O PulseOps AI é um projeto que utiliza análise de dados e Machine Learning para identificar padrões associados a atrasos em entregas e estimar o risco de atraso de novos pedidos.

A proposta é explorar como a tecnologia pode apoiar a tomada de decisões e o acompanhamento de operações logísticas.

**Importante:** o projeto utiliza exclusivamente dados sintéticos, gerados para fins educacionais e de desenvolvimento. Não são dados reais de empresas ou clientes.

## Funcionalidades

- Geração de dados sintéticos de pedidos.
- Armazenamento e consulta de dados com MySQL.
- Análise exploratória de dados.
- Visualizações interativas.
- Treinamento de modelo de Machine Learning.
- Previsão de risco de atraso.
- API desenvolvida com FastAPI.
- Dashboard interativo com Streamlit.
- Testes automatizados da API.

## Tecnologias utilizadas

- Python
- MySQL
- Pandas e NumPy
- Plotly
- Scikit-learn
- FastAPI
- Streamlit
- Pytest
- Git e GitHub

## Estrutura do projeto

A estrutura inclui módulos para geração e análise de dados, visualizações, treinamento do modelo, API, dashboard e testes automatizados.

## Como executar

Clone o repositório e acesse a pasta do projeto.

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Inicie a API em um terminal:

```powershell
python -m uvicorn api:app --reload
```

Em outro terminal, inicie o dashboard:

```powershell
python -m streamlit run dashboard.py
```

A documentação interativa da API estará disponível em:

`http://127.0.0.1:8000/docs`

## Testes

Para executar os testes automatizados:

```powershell
python -m pytest test_api.py -v
```

## Objetivo de aprendizagem

Este projeto faz parte da minha evolução acadêmica e prática na área de tecnologia, com foco na integração entre desenvolvimento de software, análise de dados e inteligência artificial.

A proposta é aplicar conhecimentos, desenvolver novas habilidades e construir soluções funcionais por meio de projetos práticos.
