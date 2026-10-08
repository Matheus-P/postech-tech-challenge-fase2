# Tech Challenge — Fase 2 | POSTECH Data Analytics

Previsão de inadimplência na concessão de cartão de crédito: qual o risco de um novo
cartão atrasar 60 dias ou mais nos primeiros 12 meses?

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Turma | 2DTATBB |
| Grupo | Grupo 30 |
| Data de entrega | 08/10/2026 |

### Integrantes

| Nome completo | RM | E-mail |
|---|---|---|
| Matheus Prado | RM377776 | matheus.morais.prado@gmail.com |

---

## 2. Links da entrega

| Item | Link |
|---|---|
| Repositório | https://github.com/Matheus-P/postech-tech-challenge-fase2 |
| Vídeo executivo (≤ 5 min) | https://drive.google.com/file/d/1NHALEIdGL6Kez6QtB6AquKxHDx1qIr8I/view?usp=sharing |
| Apresentação | [`docs/apresentacao_executiva.pdf`](docs/apresentacao_executiva.pdf) |

---

## 3. O problema

Uma instituição financeira precisa decidir, no momento do pedido, se aprova um cartão de
crédito. Aprovar um mau pagador gera perda; recusar um bom pagador desperdiça receita.
Menos de 2% das contas chegam a um atraso grave, então regras simples não separam os dois
grupos, e a taxa de acerto geral não serve como medida: aprovar todos os pedidos acerta
mais de 98% das vezes sem evitar um único calote. Machine Learning entra para ordenar os
pedidos por risco a partir do que o banco sabe no dia do pedido.

### Variável alvo

`target = 1` quando a conta atinge **atraso de 60 dias ou mais** (`STATUS` 2 a 5) em algum
dos **12 primeiros meses** após a abertura. Só entram contas com pelo menos 12 meses de
observação.

A base não traz o alvo pronto; ele foi construído a partir do histórico mensal, e os dois
limiares vêm da distribuição dos dados:

- **60 dias:** atrasos de até 29 dias aparecem em 37% dos registros mensais e não
  distinguem ninguém; atrasos de 60+ dias são 0,30% dos registros e representam
  inadimplência de fato.
- **12 meses:** contas observadas por mais tempo acumulam mais atrasos (0,3% nas
  observadas por até 6 meses, 3,0% nas observadas por mais de 4 anos). Uma janela fixa
  mede todas pela mesma régua. Em 12 meses já ocorreram 75% dos primeiros atrasos graves,
  e 76% das contas têm essa janela completa.

Resultado: 27.638 contas, 394 más (1,43%).

### Dataset

| Campo | Valor |
|---|---|
| Fonte | [Credit Card Approval Prediction (Kaggle)](https://www.kaggle.com/datasets/rikdifos/credit-card-approval-prediction); cópia usada no curso em [`data/README.md`](data/README.md) |
| Linhas × colunas | `application_record.csv`: 438.557 × 18 · `credit_record.csv`: 1.048.575 × 3 |
| Período / versão | histórico mensal de até 60 meses antes da extração; versão de 24/03/2020 |
| Licença de uso | CC0: Public Domain |

Só 36.457 contas aparecem nas duas tabelas e podem ser usadas.

Descrição das variáveis:

| Variável | Tipo | Descrição |
|---|---|---|
| `ID` | inteiro | identificador da conta |
| `CODE_GENDER` | categórica | gênero |
| `FLAG_OWN_CAR`, `FLAG_OWN_REALTY` | binária | possui carro / imóvel |
| `CNT_CHILDREN`, `CNT_FAM_MEMBERS` | numérica | filhos / pessoas na família |
| `AMT_INCOME_TOTAL` | numérica | renda anual |
| `NAME_INCOME_TYPE` | categórica | origem da renda |
| `NAME_EDUCATION_TYPE` | categórica | escolaridade |
| `NAME_FAMILY_STATUS` | categórica | estado civil |
| `NAME_HOUSING_TYPE` | categórica | tipo de moradia |
| `DAYS_BIRTH` | numérica | dias desde o nascimento (negativo) |
| `DAYS_EMPLOYED` | numérica | dias desde a admissão (negativo); 365243 = sem vínculo |
| `FLAG_MOBIL`, `FLAG_WORK_PHONE`, `FLAG_PHONE`, `FLAG_EMAIL` | binária | meios de contato informados |
| `OCCUPATION_TYPE` | categórica | ocupação (31% ausente) |
| `MONTHS_BALANCE` | inteiro | mês do registro (0 = mês da extração, -1 = anterior...) |
| `STATUS` | categórica | `X` sem uso, `C` quitado, `0` atraso de 1-29 dias, `1` 30-59, `2` 60-89, `3` 90-119, `4` 120-149, `5` 150+ |

Variáveis criadas no projeto (detalhes no notebook 02): idade e tempo de emprego em anos,
indicador de ausência de vínculo, renda per capita e 12 variáveis de **histórico interno**
(`HIST_*`), que resumem como o proponente pagou as contas que já tinha antes da conta
analisada.

---

## 4. Como reproduzir

Requer **Python 3.11.17** (o mesmo fixado em `.tool-versions` e no CI).

```bash
git clone https://github.com/Matheus-P/postech-tech-challenge-fase2.git
cd postech-tech-challenge-fase2

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-lock.txt
python -m ipykernel install --user --name=postech_venv --display-name "Python (.venv)"
```

`requirements.txt` lista as dependências diretas; `requirements-lock.txt` fixa também as
transitivas e é o que garante o mesmo ambiente.

Baixe o dataset e coloque os dois arquivos em `data/raw/` (os dados **não** são
versionados — veja [`data/README.md`](data/README.md)).

Execute os notebooks nesta ordem, de cima para baixo:

```bash
cd notebooks
for nb in 01_eda 02_preprocessamento 03_modelagem 04_avaliacao; do
  jupyter nbconvert --to notebook --execute --inplace $nb.ipynb
done
cd .. && python docs/gerar_apresentacao.py     # regenera o PDF da apresentação
```

| # | Notebook | O que faz |
|---|---|---|
| 1 | `notebooks/01_eda.ipynb` | Análise exploratória e definição do alvo |
| 2 | `notebooks/02_preprocessamento.ipynb` | Nulos, alvo, feature engineering |
| 3 | `notebooks/03_modelagem.ipynb` | Split, validação cruzada, comparação, ajuste e ponto de corte |
| 4 | `notebooks/04_avaliacao.ipynb` | Métricas no teste, importância de variáveis e conclusões |

**Semente fixa:** `RANDOM_STATE = 42`, definida em `src/config.py` e importada na primeira
célula de cada notebook. O notebook 03 leva de 10 a 15 minutos; os demais, cerca de 1 minuto cada.
Rodar na ordem acima, em ambiente limpo, reproduz os números da seção 5, que também ficam
gravados em `results/metrics/`.

---

## 5. Resultados

Validação cruzada de 5 folds no treino, estratificada e **agrupada por proponente**
(a mesma pessoa nunca está no treino e na validação ao mesmo tempo). Acurácia, precisão,
recall e F1 no corte padrão de 0,50.

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| Random Forest | 0,949 | 0,076 | 0,238 | 0,113 | 0,741 |
| Regressão Logística | 0,703 | 0,028 | 0,614 | 0,054 | 0,741 |
| Extra Trees | 0,880 | 0,042 | 0,350 | 0,074 | 0,730 |
| Gradient Boosting (Hist) | 0,718 | 0,028 | 0,573 | 0,053 | 0,717 |
| Árvore de Decisão | 0,574 | 0,025 | 0,772 | 0,048 | 0,707 |
| Naive Bayes Gaussiano | 0,083 | 0,014 | 0,971 | 0,028 | 0,620 |
| Baseline (taxa média) | 0,986 | 0,000 | 0,000 | 0,000 | 0,500 |

**Modelo escolhido:** Regressão Logística (`C = 0,0003`, `class_weight="balanced"`) — após
o ajuste de hiperparâmetros ela empata com a Random Forest (AUC-ROC de 0,749 contra 0,747,
diferença menor que a variação entre folds). Entre dois modelos equivalentes, ficou o mais
simples e explicável.

**No conjunto de teste** (5.644 contas de 1.737 proponentes nunca vistos, 94 más):

| Corte | Acurácia | Precisão | Recall | F1 | MCC | AUC-ROC |
|---|---|---|---|---|---|---|
| 0,50 | 0,659 | 0,032 | 0,670 | 0,061 | 0,088 | 0,712 |
| 0,84 (definido no treino) | 0,975 | 0,195 | 0,160 | 0,175 | 0,164 | 0,712 |

O AUC-ROC de 0,712 tem intervalo de 95% de 0,653 a 0,767: com 94 contas más no teste, a
margem de erro é larga.

**Métricas priorizadas:** AUC-ROC para escolher o modelo e MCC para escolher o corte. Com
1,4% de maus pagadores, a acurácia premia quem aprova todo mundo (a maior acurácia da
tabela é a do baseline). O AUC-ROC mede a capacidade de ordenar pedidos por risco sem
depender de corte; o MCC usa as quatro células da matriz de confusão e só é alto quando o
modelo vai bem nas duas classes. Aprovar um mau pagador custa mais por cliente do que
recusar um bom, mas os bons são 60 vezes mais numerosos, então o corte precisa equilibrar
os dois erros. Como a base não traz valores financeiros, esse equilíbrio foi buscado pelo
MCC e complementado por faixas de risco.

---

## 6. Principais conclusões

1. **O histórico de pagamento prevê o risco; o formulário, quase nada.** Só com renda,
   idade, ocupação e demais dados declarados, o AUC-ROC fica em 0,55. Só com o histórico
   do cliente em cartões anteriores, chega a 0,74.
2. **Quem já atrasou 60 dias volta a atrasar.** Clientes com atraso grave em um cartão
   anterior repetem o atraso em 17,6% dos casos, contra 1,2% dos demais. É a variável mais
   importante do modelo.
3. **O modelo concentra o risco.** Os 20% de pedidos com maior score reúnem 46% dos maus
   pagadores do teste; os 60% de menor score têm 0,8% de atraso grave. Isso permite três
   tratamentos (aprovação automática, limite inicial menor, análise reforçada) em vez de
   um sim ou não.
4. **Cliente novo é o ponto cego.** Para quem pede o primeiro cartão (35% dos pedidos e
   metade dos maus pagadores), o AUC-ROC é 0,55. Esse público exige dados externos.
5. **Atraso curto não é sinal de alerta.** Atrasos frequentes de até 29 dias não se
   associam a risco maior.

### Limitações e próximos passos

- Sem histórico interno o modelo não funciona: integrar dados de bureau de crédito.
- Poucos maus pagadores (394 na base), o que deixa as estimativas com margem larga.
- A base não tem identificador de pessoa: cadastros idênticos foram tratados como o mesmo
  proponente.
- O arquivo de histórico tem 1.048.575 linhas, o limite de uma planilha, e pode estar
  truncado.
- Falta validação no tempo, calibração do score e análise de impacto por grupo (gênero,
  idade) antes de qualquer uso real.

Uma versão anterior do projeto reportava AUC-ROC de 0,74 com um modelo que tinha duas
fontes de vazamento: a mesma pessoa em treino e teste, e uma variável (tempo de
observação da conta) que não existe no momento do pedido. Sem elas, aquele modelo caía
para 0,60. Os resultados acima já estão livres dos dois problemas.

---

## 7. Estrutura do repositório

```
.
├── data/          dados brutos (raw) e tratados (processed) — não versionados
├── notebooks/     análise em ordem numerada
├── src/           funções compartilhadas pelos notebooks
├── results/       figuras e métricas geradas pelos notebooks
├── docs/          apresentação executiva (PDF) e o script que a gera
└── submissao/     gerador do PDF de submissão
```

Detalhes e convenções em [`ESTRUTURA.md`](ESTRUTURA.md).
Antes de enviar, percorra o [`CHECKLIST.md`](CHECKLIST.md).

---

## 8. Tecnologias

Python 3.11.17 · pandas 2.2.3 · NumPy 2.1.3 · SciPy 1.14.1 · scikit-learn 1.5.2 ·
Matplotlib 3.9.2 · seaborn 0.13.2 · Jupyter · ReportLab 4.2.5 (PDF de submissão)
