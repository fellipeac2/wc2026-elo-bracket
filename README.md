# Copa do Mundo 2026 — Simulador ELO

Aplicação interativa em Streamlit para explorar probabilidades do mata-mata da Copa 2026 com base no modelo ELO do Ranking FIFA.

![Python](https://img.shields.io/badge/python-3.10-blue) ![Streamlit](https://img.shields.io/badge/streamlit-%3E%3D1.40-red) ![Plotly](https://img.shields.io/badge/plotly-5.x-purple)

## O que faz

- **Bracket interativo** — visualização do chaveamento R32 → Final em Plotly; clique em qualquer partida para ver as probabilidades daquela fase
- **Painel de probabilidades** — lista todos os times com barra de progresso mostrando a chance de cada um vencer a fase selecionada
- **Decomposição por adversário** — clique em um time no painel para ver, adversário a adversário, como cada possível duelo contribui para a probabilidade total
- **Ranking FIFA com multi-seleção** — selecione times no menu lateral para calcular a probabilidade combinada de pelo menos um deles avançar
- **"Selecionar todos"** — seleciona automaticamente todos os times de uma fase no ranking
- **Registro de resultados reais** — formulário por fase na sidebar para registrar o vencedor de cada jogo; as probabilidades recalculam em tempo real considerando os resultados como certeza (P=100%), propagando o impacto por todas as fases seguintes

## Modelo ELO

A probabilidade de vitória em um confronto direto segue a fórmula logística do sistema ELO:

```
              1
P(A vence B) = ─────────────────────────────
               1 + 10^((ELO_B − ELO_A) / 600)
```

| Diferença ELO | Prob. do favorito |
|:---:|:---:|
| 0 | 50% |
| +100 | ≈ 60% |
| +200 | ≈ 68% |
| +600 | ≈ 91% |

Para fases com múltiplos jogos, a probabilidade é calculada **recursivamente**:

```
P(X vence fase N) = Σ_Y [ P(X vence seu lado) × P(Y vence o outro lado) × P(X vence Y) ]
```

Os pontos ELO usados são do **Ranking FIFA/Coca-Cola Men's World Ranking** de junho de 2026 (fonte: [inside.fifa.com](https://inside.fifa.com)).

## Instalação

```bash
pip install streamlit plotly pandas
```

## Rodando

```bash
streamlit run copa2026_elo.py
```

Para expor na rede local (ex.: acessar pelo celular):

```bash
streamlit run copa2026_elo.py --server.address 0.0.0.0
```

O arquivo `.streamlit/config.toml` já configura `address = "0.0.0.0"` e habilita compressão WebSocket — basta rodar o comando acima sem flags extras.

## Estrutura

```
copa2026_elo/
├── copa2026_elo.py        # app principal
└── .streamlit/
    └── config.toml        # configurações do servidor
```

## Chaveamento

O chaveamento reflete o sorteio oficial da FIFA para o mata-mata da Copa 2026 (28 jun 2026).

| Fase | Jogos |
|---|---|
| 16-avos | 28 jun – 3 jul |
| Oitavas | 4 – 7 jul |
| Quartas | 9 – 11 jul |
| Semifinais | 14 – 15 jul |
| Final | 19 jul |
