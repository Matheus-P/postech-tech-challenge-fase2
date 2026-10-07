# src/

Funções reutilizadas por mais de um notebook. Se você copiou e colou um bloco de código
entre notebooks, ele deveria estar aqui.

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | caminhos, semente, definição do alvo, constantes |
| `data.py` | carregar os dados brutos, montar a base de contas, criar o alvo |
| `preprocessing.py` | nulos, variáveis do formulário, histórico interno do proponente |
| `models.py` | pipelines dos modelos candidatos |
| `evaluation.py` | métricas, varredura de ponto de corte, intervalo de confiança |
| `viz.py` | estilo dos gráficos e exportação para `results/figures/` |

Nos notebooks: `from src.config import RANDOM_STATE`
